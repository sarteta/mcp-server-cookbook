"""Unit tests for scanner functions (no MCP wiring)."""
from my_mcp_server.scanners import echo


def test_echo_returns_message():
    assert echo("hello") == {"echo": "hello", "length": "5"}


def test_echo_handles_empty_string():
    assert echo("") == {"echo": "", "length": "0"}
