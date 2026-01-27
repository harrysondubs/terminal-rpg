"""
Dungeon Master API interaction layer using Claude API.
Handles message creation, tool execution, and response processing.
"""

import json
import logging
from typing import Optional

from anthropic import APIError

from ...storage.database import Database
from ...storage.models import GameState
from ..claude_api import ClaudeModel, create_message
from .message_history import (
    reconstruct_message_history,
    save_assistant_message,
    save_tool_call,
    save_tool_results,
    save_user_message,
)
from .prompts.dm_game_prompts import create_dm_system_prompt
from .tools import (
    ABILITY_CHECK_TOOL,
    ADD_ARMOR_TOOL,
    ADD_ITEM_TOOL,
    ADD_WEAPON_TOOL,
    CHANGE_LOCATION_TOOL,
    CREATE_LOCATION_TOOL,
    GOLD_TOOL,
    HP_TOOL,
    REMOVE_INVENTORY_TOOL,
    VIEW_INVENTORY_TOOL,
    VIEW_LOCATIONS_TOOL,
    add_armor_execute,
    add_item_execute,
    add_weapon_execute,
    change_location_execute,
    create_location_execute,
    execute_ability_check,
    execute_gold,
    execute_hp,
    remove_inventory_execute,
    view_inventory_execute,
    view_locations_execute,
)

logger = logging.getLogger(__name__)

# All available tools
TOOLS = [
    VIEW_INVENTORY_TOOL,
    ADD_ITEM_TOOL,
    ADD_WEAPON_TOOL,
    ADD_ARMOR_TOOL,
    REMOVE_INVENTORY_TOOL,
    CHANGE_LOCATION_TOOL,
    VIEW_LOCATIONS_TOOL,
    CREATE_LOCATION_TOOL,
    GOLD_TOOL,
    HP_TOOL,
    ABILITY_CHECK_TOOL
]

MAX_TOOL_ITERATIONS = 5  # Prevent infinite tool loops


class DMGame:
    """
    Manages Claude API interactions and tool execution for the DM.
    Pure API/tool layer with no UI or game loop logic.
    """

    def __init__(self, db: Database, campaign_id: int):
        """
        Initialize DM API session.

        Args:
            db: Connected Database instance
            campaign_id: Campaign to run
        """
        self.db = db
        self.campaign_id = campaign_id
        self.game_state: Optional[GameState] = None
        self.status = None

    def get_response(self, user_input: str, game_state: GameState, status=None) -> tuple[str, Optional[str]]:
        """
        Get response from Claude for user input, handling tools automatically.

        Args:
            user_input: User's message
            game_state: Current game state
            status: Optional Rich Status object to pause during interactive tools

        Returns:
            Tuple of (response_text, error_message)
            - response_text: Final text response from Claude (empty string if error)
            - error_message: Error message if request failed, None if successful
        """
        self.game_state = game_state
        self.status = status

        # Save user message
        save_user_message(
            self.campaign_id,
            game_state.world.id,
            game_state.location.id,
            user_input,
            self.db
        )

        # Reconstruct conversation history
        messages = reconstruct_message_history(self.campaign_id, self.db)

        # Generate system prompt
        system_prompt = create_dm_system_prompt(game_state)

        # Call Claude API with tools
        iteration = 0
        while iteration < MAX_TOOL_ITERATIONS:
            iteration += 1

            try:
                # Log the messages being sent to API
                logger.info(f"Sending {len(messages)} messages to Claude API (iteration {iteration})")
                logger.debug("Messages payload:")
                # Convert messages to JSON-serializable format for logging
                serializable_messages = []
                for msg in messages:
                    serializable_msg = {"role": msg["role"]}
                    content = msg["content"]
                    if isinstance(content, str):
                        serializable_msg["content"] = content
                    elif isinstance(content, list):
                        serializable_msg["content"] = []
                        for block in content:
                            if isinstance(block, dict):
                                serializable_msg["content"].append(block)
                            elif hasattr(block, '__dict__'):
                                # Convert SDK objects to dict
                                serializable_msg["content"].append(str(block))
                    serializable_messages.append(serializable_msg)
                logger.debug(json.dumps(serializable_messages, indent=2))

                response = create_message(
                    messages=messages,
                    model=ClaudeModel.SONNET_4_5,
                    system=system_prompt,
                    max_tokens=4096,
                    temperature=1.0,
                    tools=TOOLS
                )
            except APIError as e:
                logger.error(f"API Error: {e}")
                return "", f"API Error: {e}"

            # Check if response contains tool calls
            tool_use_blocks = [block for block in response.content if block.type == "tool_use"]

            if not tool_use_blocks:
                # No tools, extract text and save
                text_blocks = [block.text for block in response.content if hasattr(block, 'text')]
                final_text = "\n\n".join(text_blocks)

                save_assistant_message(
                    self.campaign_id,
                    game_state.world.id,
                    game_state.location.id,
                    final_text,
                    self.db
                )

                return final_text, None

            # Has tool calls - execute them
            # First, save the full response content (includes text + tool_use blocks)
            # Convert response.content to the proper format for saving
            content_blocks = []
            for block in response.content:
                if hasattr(block, 'text'):
                    # Text block
                    content_blocks.append({
                        "type": "text",
                        "text": block.text
                    })
                elif block.type == "tool_use":
                    # Tool use block
                    content_blocks.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })

            save_tool_call(
                self.campaign_id,
                game_state.world.id,
                game_state.location.id,
                response.id,
                content_blocks,
                self.db
            )

            # Execute tools
            tool_results = []
            for tool_block in tool_use_blocks:
                result = self._execute_tool(tool_block.name, tool_block.input, self.status)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result
                })

            # Save tool results
            save_tool_results(
                self.campaign_id,
                game_state.world.id,
                game_state.location.id,
                tool_results,
                self.db
            )

            # Add assistant message with tool calls and tool results to messages
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            messages.append({
                "role": "user",
                "content": tool_results
            })

            # Continue loop to get next response

        # If we hit max iterations, return error
        return "", "Max tool iterations reached. Please try rephrasing your request."

    def _execute_tool(self, tool_name: str, tool_input: dict, status=None) -> str:
        """
        Execute a tool and return the result.

        Args:
            tool_name: Name of tool to execute
            tool_input: Tool input parameters
            status: Optional Rich Status object to pause during interactive tools

        Returns:
            Tool result as string
        """
        try:
            if tool_name == "view_player_inventory":
                return view_inventory_execute(self.game_state)

            elif tool_name == "add_item_to_inventory":
                return add_item_execute(
                    tool_input["name"],
                    tool_input["description"],
                    tool_input["rarity"],
                    tool_input["value"],
                    self.game_state,
                    self.db,
                    tool_input.get("quantity", 1)
                )

            elif tool_name == "add_weapon_to_inventory":
                return add_weapon_execute(
                    tool_input["name"],
                    tool_input["description"],
                    tool_input["rarity"],
                    tool_input["type"],
                    tool_input["hands_required"],
                    tool_input["attack"],
                    tool_input["value"],
                    self.game_state,
                    self.db,
                    tool_input.get("quantity", 1)
                )

            elif tool_name == "add_armor_to_inventory":
                return add_armor_execute(
                    tool_input["name"],
                    tool_input["description"],
                    tool_input["rarity"],
                    tool_input["type"],
                    tool_input["defense"],
                    tool_input["value"],
                    self.game_state,
                    self.db,
                    tool_input.get("quantity", 1)
                )

            elif tool_name == "remove_from_inventory":
                return remove_inventory_execute(
                    tool_input["type"],
                    tool_input["name"],
                    self.game_state,
                    self.db,
                    tool_input.get("quantity", 1)
                )

            elif tool_name == "change_location":
                return change_location_execute(
                    tool_input["location_name"],
                    self.game_state,
                    self.db
                )

            elif tool_name == "view_locations":
                return view_locations_execute(
                    self.game_state,
                    self.db
                )

            elif tool_name == "create_location":
                return create_location_execute(
                    tool_input["location_name"],
                    tool_input["description"],
                    self.game_state,
                    self.db
                )

            elif tool_name == "adjust_player_gold":
                return execute_gold(
                    tool_input["amount"],
                    self.game_state,
                    self.db
                )

            elif tool_name == "adjust_player_hp":
                return execute_hp(
                    tool_input["amount"],
                    self.game_state,
                    self.db
                )

            elif tool_name == "ability_check":
                return execute_ability_check(
                    tool_input["ability_type"],
                    tool_input["difficulty_class"],
                    tool_input["context"],
                    self.game_state,
                    self.db,
                    status
                )

            else:
                return f"Error: Unknown tool '{tool_name}'"

        except Exception as e:
            return f"Error executing tool: {str(e)}"
