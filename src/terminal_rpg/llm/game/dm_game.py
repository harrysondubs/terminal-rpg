"""
Dungeon Master game loop using Claude API.
"""

import importlib
import json
import logging
import sys
from typing import Optional

from anthropic import APIError
from rich.console import Console
from rich.panel import Panel

from ...storage.database import Database
from ...storage.models import GameState
from ...storage.repositories import CampaignRepository
from ..claude_api import ClaudeModel, create_message


logger = logging.getLogger(__name__)
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
    GOLD_TOOL,
    HP_TOOL,
    INVENTORY_TOOL,
    LOCATION_TOOL,
    execute_ability_check,
    execute_gold,
    execute_hp,
    execute_inventory,
    execute_location,
)

console = Console()

# All available tools
TOOLS = [INVENTORY_TOOL, LOCATION_TOOL, GOLD_TOOL, HP_TOOL, ABILITY_CHECK_TOOL]

MAX_TOOL_ITERATIONS = 5  # Prevent infinite tool loops


class DMGame:
    """
    Manages the DM conversation loop with Claude.
    """

    def __init__(self, db: Database, campaign_id: int):
        """
        Initialize DM game session.

        Args:
            db: Connected Database instance
            campaign_id: Campaign to run
        """
        self.db = db
        self.campaign_id = campaign_id
        self.game_state: Optional[GameState] = None
        self.running = False

    def start(self):
        """Start the game loop."""
        # Load game state
        campaign_repo = CampaignRepository(self.db)
        self.game_state = campaign_repo.load_game_state(self.campaign_id)

        if not self.game_state:
            console.print("[red]Error: Could not load game state[/red]")
            return

        # Display welcome
        self._display_welcome()

        # Main loop
        self.running = True
        while self.running:
            try:
                self._game_loop_iteration()
            except KeyboardInterrupt:
                console.print("\n[yellow]Game paused. Type 'quit' to exit or press Enter to continue.[/yellow]")
                user_input = console.input("> ").strip().lower()
                if user_input == 'quit':
                    self.running = False
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                console.print("[yellow]An error occurred. The game will continue.[/yellow]")

    def _display_welcome(self):
        """Display welcome message and current location."""
        player = self.game_state.player
        location = self.game_state.location

        welcome = f"""[bold cyan]Welcome back, {player.name}![/bold cyan]

[bold]Current Location:[/bold] {location.name}
{location.description}

[dim]Type your actions or questions. Type 'quit' to exit. Type '/reload' to reload code changes.[/dim]"""

        console.print(Panel(welcome, title="Adventure Continues", border_style="cyan"))

    def _reload_modules(self):
        """Reload game modules for hot-reload during development."""
        console.print()
        console.print("[yellow]🔄 Reloading game modules...[/yellow]")

        try:
            # List of modules to reload in dependency order
            modules_to_reload = [
                'terminal_rpg.engines.dice',
                'terminal_rpg.llm.game.tools.inventory_tool',
                'terminal_rpg.llm.game.tools.location_tool',
                'terminal_rpg.llm.game.tools.gold_tool',
                'terminal_rpg.llm.game.tools.hp_tool',
                'terminal_rpg.llm.game.tools.ability_check_tool',
                'terminal_rpg.llm.game.tools',
                'terminal_rpg.llm.game.prompts.dm_game_prompts',
                'terminal_rpg.llm.game.message_history',
            ]

            reloaded_count = 0
            for module_name in modules_to_reload:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                    reloaded_count += 1
                    logger.info(f"Reloaded module: {module_name}")

            # Update global references before reimporting
            global TOOLS, execute_inventory, execute_location, execute_gold, execute_hp, execute_ability_check
            global reconstruct_message_history, save_assistant_message, save_tool_call, save_tool_results, save_user_message
            global create_dm_system_prompt

            # Reimport the tools to get fresh definitions
            from .tools import (
                ABILITY_CHECK_TOOL,
                GOLD_TOOL,
                HP_TOOL,
                INVENTORY_TOOL,
                LOCATION_TOOL,
                execute_ability_check,
                execute_gold,
                execute_hp,
                execute_inventory,
                execute_location,
            )

            # Reimport message history functions
            from .message_history import (
                reconstruct_message_history,
                save_assistant_message,
                save_tool_call,
                save_tool_results,
                save_user_message,
            )

            # Reimport prompt generation
            from .prompts.dm_game_prompts import create_dm_system_prompt

            # Update global TOOLS list
            TOOLS = [INVENTORY_TOOL, LOCATION_TOOL, GOLD_TOOL, HP_TOOL, ABILITY_CHECK_TOOL]

            console.print(f"[green]✓ Reloaded {reloaded_count} modules successfully![/green]")
            console.print("[dim]Changes to tools, prompts, and game logic are now active.[/dim]")

        except Exception as e:
            console.print(f"[red]✗ Error reloading modules: {e}[/red]")
            logger.error(f"Module reload failed: {e}", exc_info=True)

    def _game_loop_iteration(self):
        """Single iteration of game loop: get input, call API, handle response."""
        # Get user input
        console.print()
        user_input = console.input("[bold cyan]>[/bold cyan] ").strip()

        if not user_input:
            return

        if user_input.lower() in ['quit', 'exit']:
            self.running = False
            console.print("[cyan]Farewell, adventurer![/cyan]")
            return

        # Handle reload command
        if user_input.lower() == '/reload':
            self._reload_modules()
            return

        # Save user message
        save_user_message(
            self.campaign_id,
            self.game_state.world.id,
            self.game_state.location.id,
            user_input,
            self.db
        )

        # Get response from Claude (with tool handling)
        with console.status("[bold green]The DM is thinking...", spinner="dots"):
            response_text = self._get_dm_response(user_input)

        # Display response
        if response_text:
            console.print()
            console.print(Panel(response_text, border_style="green", title="Dungeon Master"))

    def _get_dm_response(self, user_input: str) -> str:
        """
        Get response from Claude, handling tools automatically.

        Args:
            user_input: User's message

        Returns:
            Final text response from Claude
        """
        # Reconstruct conversation history
        messages = reconstruct_message_history(self.campaign_id, self.db)

        # Generate system prompt
        system_prompt = create_dm_system_prompt(self.game_state)

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
                console.print(f"[red]API Error: {e}[/red]")
                return "I apologize, but I'm having trouble connecting right now. Please try again."

            # Check if response contains tool calls
            tool_use_blocks = [block for block in response.content if block.type == "tool_use"]

            if not tool_use_blocks:
                # No tools, extract text and save
                text_blocks = [block.text for block in response.content if hasattr(block, 'text')]
                final_text = "\n\n".join(text_blocks)

                save_assistant_message(
                    self.campaign_id,
                    self.game_state.world.id,
                    self.game_state.location.id,
                    final_text,
                    self.db
                )

                return final_text

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
                self.game_state.world.id,
                self.game_state.location.id,
                response.id,
                content_blocks,
                self.db
            )

            # Execute tools
            tool_results = []
            for tool_block in tool_use_blocks:
                result = self._execute_tool(tool_block.name, tool_block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result
                })

            # Save tool results
            save_tool_results(
                self.campaign_id,
                self.game_state.world.id,
                self.game_state.location.id,
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
        return "I apologize, something went wrong with processing your request. Please try rephrasing."

    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """
        Execute a tool and return the result.

        Args:
            tool_name: Name of tool to execute
            tool_input: Tool input parameters

        Returns:
            Tool result as string
        """
        try:
            if tool_name == "view_player_inventory":
                return execute_inventory(self.game_state)

            elif tool_name == "change_location":
                return execute_location(
                    tool_input["location_name"],
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
                    self.game_state
                )

            else:
                return f"Error: Unknown tool '{tool_name}'"

        except Exception as e:
            return f"Error executing tool: {str(e)}"
