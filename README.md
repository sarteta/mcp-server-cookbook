# mcp-server-cookbook

Production patterns for building MCP servers in Python — extracted from
building 4+ servers in the open ecosystem.

If you're about to build your first MCP server (or your tenth), this is
the cookbook I wish I'd had when I started. It is not a tutorial. It's
the set of design decisions that pay off later, in the order they
matter.

## Who this is for

- DevOps / SRE / Platform engineers wrapping internal tools as MCP
  servers so AI agents can use them.
- Backend engineers exposing existing APIs over MCP.
- Anyone wondering "should this tool be `read_*` or `do_*`?"

## The 4 patterns that matter most

### 1. Read-only by construction

The single highest-value design choice. Tools should be named
`list_*`, `get_*`, `summarize_*` — never `delete_*`, `terminate_*`,
`modify_*`. If a user asks the agent "delete the orphan EBS volumes"
and your server has no delete tools, the worst case is the agent says
"I can list them but you'll need to delete them" — that's a
*feature*, not a limitation. It's a hard safety gate.

See: [`mcp-postgres-doctor`](https://github.com/sarteta/mcp-postgres-doctor)
ships with `list_locks`, `top_queries`, `bloat_check` — never `kill_query`,
even though the implementation would be trivial.

### 2. Scope IAM tighter than you think

Production agents reach for `*Read*` policies. Rare are the cases where
an agent needs `ec2:*` or `rds:*`. For each tool, identify the *minimum*
verbs (`Describe`, `Get`, `List`, `Filter`) and ship a policy file
beside the README. Reviewers approve narrow policies; they reject wide
ones.

```hcl
# iam/policy.json — example for an EC2 cost scanner
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ec2:DescribeVolumes",
      "ec2:DescribeAddresses",
      "ec2:DescribeSnapshots",
      "cloudwatch:GetMetricStatistics"
    ],
    "Resource": "*"
  }]
}
```

### 3. Tool docstrings are the agent's spec

The agent reads your tool's docstring — that's its only documentation.
Docstrings should:

- Open with one sentence the agent can use to decide *whether* to call
  the tool.
- Document every argument with example values.
- Say what NOT to use the tool for if there's a near-miss alternative.

```python
@mcp.tool()
def list_orphaned_ebs_tool(region: str = "us-east-1") -> dict:
    """List unattached EBS volumes that are billing without being mounted.

    Use this when the user wants to find cost waste from forgotten
    volumes. Don't use this for snapshots — use `list_old_snapshots_tool`
    for that. Each finding includes estimated monthly waste.

    Args:
        region: AWS region to scan, e.g. "us-east-1" or "eu-west-1"
    """
```

### 4. Test the dispatch, not just the helpers

Unit tests of your scanner functions cover the happy path. They miss
the bug where you left a placeholder line `sts = client.meta.client...`
in a function that the unit tests don't exercise but the MCP dispatch
does. Always have at least one E2E test per tool that calls
`mcp.call_tool("tool_name", {...})` end-to-end.

```python
def test_summarize_findings_mcp_tool_returns_real_data(seeded_aws):
    from my_server.server import mcp
    result = asyncio.run(mcp.call_tool("summarize_findings_tool", {"region": "us-east-1"}))
    data = _extract_data(result)
    assert data["total_findings"] >= 1
```

## Examples in production

| Server | Domain | Tools | Repo |
|---|---|---|---|
| **mcp-postgres-doctor** | Postgres | 9 read-only diagnostic tools, 37 tests, Docker compose | [→](https://github.com/sarteta/mcp-postgres-doctor) |
| **mcp-aws-cost-doctor** | AWS cost | 4 scanners (EBS orphan, EIP unused, snapshot, summary) | [→](https://github.com/sarteta/mcp-aws-cost-doctor) |
| **mcp-cloudwatch-explorer** | AWS observability | 4 tools: alarms in ALARM, metric stats, log error filter, health summary | [→](https://github.com/sarteta/mcp-cloudwatch-explorer) |
| **mcp-supabase-latam** | Supabase | LATAM SMB-focused administration | [→](https://github.com/sarteta/mcp-supabase-latam) |

## Templates

A minimal MCP server skeleton lives in [`templates/python-readonly/`](./templates/python-readonly/).
It's the smallest thing that's still production-shaped: scanners
module, FastMCP server, pyproject, tests with moto, GitHub Actions CI.

```bash
cp -r templates/python-readonly my-mcp-server
cd my-mcp-server
pip install -e ".[dev]"
pytest
python -m my_mcp_server.server
```

## Pattern catalog (deeper dives)

- [`patterns/safety-boundaries.md`](./patterns/safety-boundaries.md) — when to add a `--write` flag and when to refuse
- [`patterns/iam-narrowing.md`](./patterns/iam-narrowing.md) — building tight IAM policies per tool
- [`patterns/test-strategy.md`](./patterns/test-strategy.md) — unit + dispatch + integration with moto
- [`patterns/docstring-contract.md`](./patterns/docstring-contract.md) — what makes a docstring agent-readable

## Why this exists

Built while shipping MCP servers in the open. Recurring patterns kept
emerging — read-only by default, scoped IAM, dispatch-level tests —
and I started writing them down. This cookbook is that collection,
publicly so others don't have to re-derive them.

## License

MIT — fork it, use it, send patches.
