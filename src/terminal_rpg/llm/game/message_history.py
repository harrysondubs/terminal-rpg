"""
Message history management for Claude API conversations.
"""

import json
import logging
from typing import Optional

from ...storage.database import Database
from ...storage.models import CampaignLog, LogType
from ...storage.repositories import CampaignLogRepository


logger = logging.getLogger(__name__)


def reconstruct_message_history(
    campaign_id: int,
    db: Database,
    limit: int = 50
) -> list[dict]:
    """
    Reconstruct Claude API message format from campaign logs.

    Args:
        campaign_id: Campaign to load history for
        db: Database connection
        limit: Maximum number of log entries to retrieve

    Returns:
        List of messages in Claude API format
    """
    log_repo = CampaignLogRepository(db)
    logs = log_repo.get_by_campaign(campaign_id, limit=limit)

    # Logs come in DESC order, reverse for chronological
    logs.reverse()

    messages = []
    pending_tool_call_index = None  # Track index of last tool_call message
    pending_tool_use_ids = None     # Track expected tool_use IDs

    for log in logs:
        if log.type == LogType.USER_MESSAGE:
            # If we have a pending tool_call without matching result, remove it
            if pending_tool_call_index is not None:
                messages.pop(pending_tool_call_index)
                pending_tool_call_index = None
                pending_tool_use_ids = None

            messages.append({
                "role": "user",
                "content": log.content
            })

        elif log.type == LogType.ASSISTANT_MESSAGE:
            # If we have a pending tool_call without matching result, remove it
            if pending_tool_call_index is not None:
                messages.pop(pending_tool_call_index)
                pending_tool_call_index = None
                pending_tool_use_ids = None

            messages.append({
                "role": "assistant",
                "content": log.content
            })

        elif log.type == LogType.TOOL_CALL:
            # If we have a pending tool_call without matching result, remove it
            if pending_tool_call_index is not None:
                messages.pop(pending_tool_call_index)

            # Parse tool call data
            data = json.loads(log.content)
            content_blocks = data["tool_calls"]  # This contains full content blocks

            # Store this message and its expected tool_use IDs
            pending_tool_call_index = len(messages)
            pending_tool_use_ids = {
                block["id"] for block in content_blocks
                if block.get("type") == "tool_use"
            }

            messages.append({
                "role": "assistant",
                "content": content_blocks
            })

        elif log.type == LogType.TOOL_RESULT:
            # Parse tool result data
            data = json.loads(log.content)

            # Validate that we have a pending tool_call
            if pending_tool_use_ids is None:
                # Skip orphaned tool_result
                continue

            # Check if tool_results match expected tool_use_ids
            result_ids = {result["tool_use_id"] for result in data["tool_results"]}
            if result_ids != pending_tool_use_ids:
                # Mismatch - remove the pending tool_call and skip this tool_result
                if pending_tool_call_index is not None:
                    messages.pop(pending_tool_call_index)
                pending_tool_call_index = None
                pending_tool_use_ids = None
                continue

            # Valid match - add tool_result and clear pending state
            messages.append({
                "role": "user",
                "content": data["tool_results"]
            })
            pending_tool_call_index = None
            pending_tool_use_ids = None

    # If we end with a pending tool_call without result, remove it
    if pending_tool_call_index is not None:
        logger.warning(f"Removing incomplete tool_call at end of history (index {pending_tool_call_index})")
        messages.pop(pending_tool_call_index)

    # Debug log the reconstructed messages
    logger.info(f"Reconstructed {len(messages)} messages from campaign {campaign_id}")
    for i, msg in enumerate(messages):
        role = msg["role"]
        content = msg["content"]
        if isinstance(content, str):
            logger.debug(f"  [{i}] {role}: {content[:100]}...")
        elif isinstance(content, list):
            logger.debug(f"  [{i}] {role}: {len(content)} content blocks")
            for j, block in enumerate(content):
                if isinstance(block, dict):
                    block_type = block.get("type", "unknown")
                    if block_type == "text":
                        logger.debug(f"      [{j}] text: {block.get('text', '')[:50]}...")
                    elif block_type == "tool_use":
                        logger.debug(f"      [{j}] tool_use: {block.get('name')} (id: {block.get('id')})")
                    elif block_type == "tool_result":
                        logger.debug(f"      [{j}] tool_result: (tool_use_id: {block.get('tool_use_id')})")

    return messages


def save_user_message(
    campaign_id: int,
    world_id: int,
    location_id: int,
    content: str,
    db: Database,
    battle_id: Optional[int] = None
) -> CampaignLog:
    """Save user message to campaign logs."""
    log_repo = CampaignLogRepository(db)
    return log_repo.create(CampaignLog(
        campaign_id=campaign_id,
        world_id=world_id,
        location_id=location_id,
        battle_id=battle_id,
        type=LogType.USER_MESSAGE,
        content=content
    ))


def save_assistant_message(
    campaign_id: int,
    world_id: int,
    location_id: int,
    content: str,
    db: Database,
    battle_id: Optional[int] = None
) -> CampaignLog:
    """Save assistant message to campaign logs."""
    log_repo = CampaignLogRepository(db)
    return log_repo.create(CampaignLog(
        campaign_id=campaign_id,
        world_id=world_id,
        location_id=location_id,
        battle_id=battle_id,
        type=LogType.ASSISTANT_MESSAGE,
        content=content
    ))


def save_tool_call(
    campaign_id: int,
    world_id: int,
    location_id: int,
    message_id: str,
    tool_calls: list[dict],
    db: Database,
    battle_id: Optional[int] = None
) -> CampaignLog:
    """Save tool call to campaign logs."""
    log_repo = CampaignLogRepository(db)

    content = json.dumps({
        "message_id": message_id,
        "tool_calls": tool_calls
    })

    return log_repo.create(CampaignLog(
        campaign_id=campaign_id,
        world_id=world_id,
        location_id=location_id,
        battle_id=battle_id,
        type=LogType.TOOL_CALL,
        content=content
    ))


def save_tool_results(
    campaign_id: int,
    world_id: int,
    location_id: int,
    tool_results: list[dict],
    db: Database,
    battle_id: Optional[int] = None
) -> CampaignLog:
    """Save tool results to campaign logs."""
    log_repo = CampaignLogRepository(db)

    content = json.dumps({
        "tool_results": tool_results
    })

    return log_repo.create(CampaignLog(
        campaign_id=campaign_id,
        world_id=world_id,
        location_id=location_id,
        battle_id=battle_id,
        type=LogType.TOOL_RESULT,
        content=content
    ))


def get_recent_messages_for_display(
    campaign_id: int,
    db: Database,
    limit: int = 6
) -> list[str]:
    """
    Get recent user/assistant messages for display when loading game.

    Args:
        campaign_id: Campaign to load history for
        db: Database connection
        limit: Maximum number of messages to retrieve

    Returns:
        List of formatted message strings (alternating user/assistant)
    """
    log_repo = CampaignLogRepository(db)
    logs = log_repo.get_by_campaign(campaign_id, limit=limit)

    # Logs come in DESC order, reverse for chronological
    logs.reverse()

    messages = []
    for log in logs:
        if log.type == LogType.USER_MESSAGE:
            messages.append(f"[bold cyan]You:[/bold cyan] {log.content}")
        elif log.type == LogType.ASSISTANT_MESSAGE:
            messages.append(f"[bold green]DM:[/bold green] {log.content}")
        # Skip tool calls and results for display

    return messages
