"""Data model shared by every weekship stage."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

HUMAN, AGENT, BOT = "human", "agent", "bot"


@dataclass
class Item:
    """One unit of shipped work: a merged PR, a direct commit or a release."""

    kind: str  # "pr" | "commit" | "release"
    repo: str  # owner/name
    ref: str  # "#123", short sha, or tag
    title: str
    url: str
    author: str
    at: datetime
    private: bool = False
    additions: int = 0
    deletions: int = 0
    files: int = 0
    labels: tuple[str, ...] = ()
    branch: str = ""
    body: str = ""
    author_type: str = "User"  # GitHub account type: "User" | "Bot" | ...
    trailers: tuple[str, ...] = ()  # Co-authored-by / Generated-by lines from commits
    identities: tuple[str, ...] = ()  # "Name <email>" of each commit author behind this item
    origin: str = HUMAN
    signals: tuple[str, ...] = ()  # why origin was chosen
    category: str = "other"
    impact: int = 0
    tier: str = "low"  # "high" | "medium" | "low"

    @property
    def lines(self) -> int:
        return self.additions + self.deletions


@dataclass
class Window:
    since: datetime
    until: datetime


@dataclass
class Week:
    """Everything that shipped in a window, classified and scored."""

    window: Window
    scope: str  # human label, e.g. "joshuaswarren (14 repos)"
    repos: list[str] = field(default_factory=list)
    items: list[Item] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)  # repos that could not be read
