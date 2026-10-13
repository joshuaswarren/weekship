"""Detection rules. Defaults cover the common coding agents; a `.weekship.toml` extends them."""
from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# Account names of AI coding agents that open PRs under their own identity.
AGENT_LOGINS = [
    "copilot", "copilot-swe-agent", "devin-ai-integration", "claude", "codex", "cursor",
    "cursoragent", "google-labs-jules", "openhands-agent", "sweep-ai", "codegen-sh",
]
# Plain automation: dependency updaters and CI bots. Counted as "bot", not "agent".
BOT_LOGINS = ["dependabot", "renovate", "github-actions", "release-please", "mergify", "snyk-bot"]
AGENT_BRANCH_PREFIXES = [
    "claude/", "codex/", "copilot/", "cursor/", "devin/", "jules/", "openhands/", "aider/",
    "sweep/", "agent/", "omp/",
]
BOT_BRANCH_PREFIXES = ["dependabot/", "renovate/", "release-please--"]
# Regexes matched against Co-authored-by / Generated-by / Assisted-by trailers.
AGENT_TRAILER_PATTERNS = [
    r"\bclaude\b", r"@anthropic\.com", r"\bcodex\b", r"@openai\.com", r"copilot", r"\bcursor(agent)?\b",
    r"devin-ai|devin\.ai", r"\bgemini\b", r"\baider\b", r"openhands", r"google-labs-jules|jules\[bot\]",
    r"^(generated|assisted)-by:",
]
# Regexes matched against each commit author identity, "Name <email>".
AGENT_IDENTITY_PATTERNS = [
    r"\bagents?@", r"@anthropic\.com", r"@openai\.com", r"\bclaude\b", r"\bcodex\b", r"copilot", r"cursoragent",
    r"devin-ai|devin\.ai", r"openhands", r"google-labs-jules|jules\[bot\]", r"gemini-code-assist",
]
# Regexes matched against the PR or commit body.
AGENT_BODY_PATTERNS = [
    r"generated with \[?claude", r"generated (with|by) (codex|copilot|cursor|devin|gemini|aider)",
    r"co-authored-by:.*(claude|codex|copilot|cursor|devin|gemini)", r"🤖 generated",
]


@dataclass
class Config:
    agent_logins: list[str] = field(default_factory=lambda: list(AGENT_LOGINS))
    bot_logins: list[str] = field(default_factory=lambda: list(BOT_LOGINS))
    agent_branch_prefixes: list[str] = field(default_factory=lambda: list(AGENT_BRANCH_PREFIXES))
    bot_branch_prefixes: list[str] = field(default_factory=lambda: list(BOT_BRANCH_PREFIXES))
    agent_trailer_patterns: list[str] = field(default_factory=lambda: list(AGENT_TRAILER_PATTERNS))
    agent_body_patterns: list[str] = field(default_factory=lambda: list(AGENT_BODY_PATTERNS))
    agent_identity_patterns: list[str] = field(default_factory=lambda: list(AGENT_IDENTITY_PATTERNS))
    exclude_repos: list[str] = field(default_factory=list)  # fnmatch against owner/name

    def trailer_res(self) -> list[re.Pattern]:
        return [re.compile(p, re.I) for p in self.agent_trailer_patterns]

    def identity_res(self) -> list[re.Pattern]:
        return [re.compile(p, re.I) for p in self.agent_identity_patterns]

    def body_res(self) -> list[re.Pattern]:
        return [re.compile(p, re.I) for p in self.agent_body_patterns]


def load_config(path: str | Path | None = None) -> Config:
    """Read `.weekship.toml`; every list in it is added to the defaults."""
    cfg = Config()
    file = Path(path) if path else Path(".weekship.toml")
    if not file.is_file():
        if path:
            raise FileNotFoundError(path)
        return cfg
    data = tomllib.loads(file.read_text())
    detect = data.get("detect", {})
    for key in ("agent_logins", "bot_logins", "agent_branch_prefixes", "bot_branch_prefixes",
                "agent_trailer_patterns", "agent_body_patterns", "agent_identity_patterns"):
        getattr(cfg, key).extend(detect.get(key, []))
    cfg.exclude_repos = list(data.get("exclude", {}).get("repos", []))
    return cfg
