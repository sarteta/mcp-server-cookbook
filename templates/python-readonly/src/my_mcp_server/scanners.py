"""Pure functions that the MCP tools wrap.

Keep these free of MCP imports. They should be testable on their own
with `pytest tests/test_scanners.py` and not require the MCP server
to be running.
"""
from __future__ import annotations


def echo(message: str) -> dict[str, str]:
    """Trivial example: returns the message back wrapped in a dict.

    Replace with your real read-only scanner — query a DB, list AWS
    resources, fetch from an API, etc.
    """
    return {"echo": message, "length": str(len(message))}
