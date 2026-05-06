"""FastMCP server. Wires scanner functions as MCP tools."""
from __future__ import annotations

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:
    raise SystemExit(
        "mcp-server is not installed. `pip install 'mcp[cli]'`"
    ) from exc

from .scanners import echo

mcp = FastMCP("my-mcp-server")


@mcp.tool()
def echo_tool(message: str) -> dict[str, str]:
    """Echo a message back. Trivial example showing the tool wiring.

    Use this only as a starting point — replace with your real
    read-only tool. Keep tools idempotent; never expose `delete_*`
    or `modify_*` here without an explicit `--allow-write` flag.

    Args:
        message: any text to echo back
    """
    return echo(message)


if __name__ == "__main__":
    mcp.run()
