# Counting agent work honestly

weekship can only count what the history marks. It sorts every merged PR and direct commit into three buckets:

| Bucket | Evidence |
|---|---|
| agent | the author account is a coding agent, the branch starts with an agent prefix (`claude/`, `codex/`, `copilot/`, `cursor/`, ...), a commit author identity looks like an agent (`agents@...`), a `Co-authored-by`, `Generated-by` or `Assisted-by` trailer names an agent, or the body says "Generated with ..." |
| bot | dependency and CI automation: `dependabot[bot]`, `renovate`, `github-actions[bot]`, `dependabot/` branches |
| human | none of the above |

"Human" means "no agent marker". It does not prove a person typed the change.

## The attribution gap

Many setups run agents under the owner's own git identity. Every commit then looks human. The brief flags this when one account authored at least 80% of the changes and fewer than 30% carry an agent marker. In that case the agent count is a floor.

The fix is a marker at commit time. Ask each agent to add a trailer, or add one with a hook.

### `prepare-commit-msg` hook

Agents set `WEEKSHIP_AGENT` (for example `claude`, `codex`, `omp`). Humans leave it unset.

```sh
#!/bin/sh
# .git/hooks/prepare-commit-msg   (chmod +x)
[ -n "$WEEKSHIP_AGENT" ] || exit 0
grep -qi '^Assisted-by:' "$1" || printf '\nAssisted-by: %s\n' "$WEEKSHIP_AGENT" >> "$1"
```

weekship treats any `Assisted-by:` or `Generated-by:` trailer as an agent marker.

### Your own conventions

Add rules in `.weekship.toml`. Every list extends the defaults.

```toml
[detect]
agent_logins = ["acme-ci-agent"]
agent_branch_prefixes = ["lane/", "slice/"]
agent_identity_patterns = ["@agents\\.acme\\.example"]
agent_trailer_patterns = ["acme-agent"]
agent_body_patterns = ["Opened by Acme Agent"]

[exclude]
repos = ["acme/archive-*"]
```

Run with `--config path/to/.weekship.toml`, or keep the file at the repository root.
