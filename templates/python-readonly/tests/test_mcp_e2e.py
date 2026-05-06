"""E2E tests: dispatch through FastMCP. Catches wiring bugs."""
import asyncio
import json


def _extract(result):
    """FastMCP may return (TextContent_list, structured_dict)."""
    if isinstance(result, tuple) and len(result) == 2:
        return result[1]
    if isinstance(result, list) and result and hasattr(result[0], "text"):
        return json.loads(result[0].text)
    raise AssertionError(f"unexpected result shape: {type(result)}")


def test_echo_tool_dispatches():
    from my_mcp_server.server import mcp
    result = asyncio.run(mcp.call_tool("echo_tool", {"message": "hi"}))
    assert result
    data = _extract(result)
    assert data == {"echo": "hi", "length": "2"}
