#!/usr/bin/env python3
"""Shared utilities for tool-call probing."""

from __future__ import annotations

import json
from typing import Any


def parse_arguments(raw: Any) -> tuple[dict[str, Any] | None, str | None]:
    """Parse tool call arguments from various formats.
    
    Args:
        raw: Arguments in dict, JSON string, or other format
        
    Returns:
        Tuple of (parsed_dict, error_message)
    """
    if raw is None:
        return None, "missing arguments"
    if isinstance(raw, dict):
        return raw, None
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            return None, f"arguments not valid JSON ({exc})"
        if not isinstance(parsed, dict):
            return None, "arguments JSON is not an object"
        return parsed, None
    return None, f"unsupported arguments type: {type(raw).__name__}"


def validate_add_call(message: dict[str, Any]) -> tuple[bool, str]:
    """Validate that a message contains a valid 'add' tool call with a=2, b=3.
    
    Args:
        message: The message dict from API response
        
    Returns:
        Tuple of (is_valid, reason)
    """
    tool_calls = message.get("tool_calls")
    if not tool_calls:
        content = message.get("content", "")
        return False, f"missing tool_calls (content={content})"
    if not isinstance(tool_calls, list) or not tool_calls:
        return False, "tool_calls is not a non-empty list"
    first = tool_calls[0]
    if not isinstance(first, dict):
        return False, "tool_calls[0] is not an object"
    function = first.get("function")
    if not isinstance(function, dict):
        return False, "tool_calls[0].function missing or invalid"
    if function.get("name") != "add":
        return False, f"unexpected function name ({function.get('name')})"
    args, err = parse_arguments(function.get("arguments"))
    if err:
        return False, err
    if args.get("a") != 2 or args.get("b") != 3:
        return False, f"unexpected arguments (a={args.get('a')}, b={args.get('b')})"
    return True, "ok"


def create_add_tool_payload(model: str) -> dict[str, Any]:
    """Create a standard tool call probe payload for the 'add' function.
    
    Args:
        model: Model name to use
        
    Returns:
        API request payload dict
    """
    return {
        "model": model,
        "messages": [{"role": "user", "content": "Call tool add with a=2 and b=3."}],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "add",
                    "description": "Add two integers",
                    "parameters": {
                        "type": "object",
                        "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                        "required": ["a", "b"],
                    },
                },
            }
        ],
        "tool_choice": "auto",
        "temperature": 0,
    }
