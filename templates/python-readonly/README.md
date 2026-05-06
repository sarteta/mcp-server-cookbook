# python-readonly — minimal MCP server template

A minimal-but-production-shaped Python MCP server. Read-only by
construction. Includes:

- FastMCP server with 1 example tool (`echo`)
- Scanner module separated from server (testable in isolation)
- Tests with `pytest` (unit + dispatch)
- `pyproject.toml` with `dev` extras
- GitHub Actions CI for Python 3.11–3.13
- MIT license

## Use

```bash
# Copy template to your new repo location
cp -r templates/python-readonly ~/my-mcp-server
cd ~/my-mcp-server

# Rename the package to your server name
# (sed below works on Linux/Mac; on Windows use search-replace in your editor)
sed -i '' 's/my_mcp_server/your_server_name/g' src/my_mcp_server/*.py pyproject.toml tests/*.py

# Install + test
pip install -e ".[dev]"
pytest

# Run
python -m my_mcp_server.server
```

## What it gives you

| File | Why |
|---|---|
| `src/my_mcp_server/scanners.py` | Pure functions you can unit-test without MCP wiring |
| `src/my_mcp_server/server.py` | FastMCP app — wires scanners as tools |
| `tests/test_scanners.py` | Unit tests of scanners |
| `tests/test_mcp_e2e.py` | E2E tests that dispatch through FastMCP — catches wiring bugs |
| `pyproject.toml` | Standard packaging |
| `.github/workflows/tests.yml` | CI on push + PR |

## Add a tool

1. Write a pure function in `scanners.py`:

```python
def list_widgets() -> list[dict]:
    return [{"id": "w1", "name": "Widget 1"}]
```

2. Wire it in `server.py`:

```python
from .scanners import list_widgets

@mcp.tool()
def list_widgets_tool() -> dict:
    """List widgets currently in the system.

    Use this when the user asks what widgets exist. Returns id + name only —
    use get_widget_tool for detail.
    """
    return {"count": len(list_widgets()), "widgets": list_widgets()}
```

3. Test it both ways:

```python
# tests/test_scanners.py
def test_list_widgets():
    out = list_widgets()
    assert len(out) == 1

# tests/test_mcp_e2e.py — catches dispatch bugs
import asyncio
from my_mcp_server.server import mcp

def test_list_widgets_tool_dispatches():
    result = asyncio.run(mcp.call_tool("list_widgets_tool", {}))
    assert result
```

That's the whole loop.

## License

MIT.
