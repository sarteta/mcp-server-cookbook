# Safety boundaries — when to add a write tool, when to refuse

The single biggest design decision in an MCP server is what NOT to
expose. Read-only servers are easier to:

- Approve in security review (no `*:Delete*` policies needed)
- Run in production (no incident risk from a hallucinated argument)
- Reason about (the agent can suggest actions, the human approves)

Below: when read-only is right, and when you genuinely need write.

## Default: read-only

For these domains, ship read-only and you'll be glad:

- **Cost / billing** — agent helps find waste, human deletes
- **Production database** — agent diagnoses, human runs migrations
- **Observability / monitoring** — agent triages, human pages on-call
- **Cloud account audit** — agent surfaces, human remediates

The agent's superpower is *correlation* (this metric + that log + that
spend = root cause). It does not need write access to be useful for
correlation.

## Concession: idempotent writes are sometimes OK

Acceptable: tools that are safe to call repeatedly with no side effect:
- `acknowledge_alarm` (PagerDuty / Opsgenie) — idempotent
- `add_tag` — additive, easy to reverse
- `create_snapshot` — additive, no destructive ambiguity

Unacceptable in default mode:
- `delete_*`, `terminate_*`, `revoke_*`, `modify_*`
- Anything that costs money to call (e.g., `start_instance`)
- Anything that pages humans (`send_alert`, `email_oncall`)

## The `--write` flag

If you do need destructive actions, gate them behind an explicit
opt-in flag:

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--allow-write", action="store_true",
                    help="enable destructive tools (off by default)")
args = parser.parse_args()

if args.allow_write:
    @mcp.tool()
    def delete_orphan_volume_tool(volume_id: str):
        ...
```

The default mode ships safe. The operator opts into write per
deployment. Reviewers see exactly what they're approving.

## Why this matters more in 2026

LLMs hallucinate arguments. The probability that an agent calls
`terminate_instance("i-prod-database")` when the user said "the test
one" is non-zero. Read-only by construction makes that non-event a
non-incident.
