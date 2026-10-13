"""Categorize each item and score its impact so a week can be ordered by what mattered."""
from __future__ import annotations

import math
import re

from .model import Item

# (category, pattern over "labels + title"); the first match wins, so order is priority.
_RULES: list[tuple[str, re.Pattern]] = [
    ("security", re.compile(
        r"^security\b|\bsecurity (fix|patch|hardening|advisory|vulnerab)|\bcve-\d|\bvulnerab|\bxss\b|\bcsrf\b"
        r"|\bsql injection\b|\bexploit", re.I)),
    ("deps", re.compile(r"\b(bump|dependabot|renovate|lockfile|dependenc(y|ies) (update|upgrade|bump)|upgrade .* to \d)", re.I)),
    ("feature", re.compile(r"^(feat|feature|add|introduce|support|implement|new)\b|\benhancement\b", re.I)),
    ("fix", re.compile(r"^(fix|bugfix|hotfix|patch|resolve|correct)\b|\bbug\b|\bregression\b", re.I)),
    ("perf", re.compile(r"^perf\b|\b(performance|faster|speed ?up|latency|throughput)\b", re.I)),
    ("docs", re.compile(r"^docs?\b|\b(readme|documentation|changelog)\b", re.I)),
    ("test", re.compile(r"^tests?\b|\b(coverage|regression test)\b", re.I)),
    ("ci", re.compile(r"^(ci|build)\b|\b(workflow|github actions?|pipeline)\b", re.I)),
    ("refactor", re.compile(r"^refactor\b|\b(cleanup|clean up|simplify|rename|restructure|remove dead)\b", re.I)),
    ("chore", re.compile(r"^chore\b|\b(release|version|housekeeping)\b", re.I)),
]
_CONVENTIONAL = re.compile(r"^(\w+)(\([^)]*\))?(!)?:\s*")
_ALIASES = {"feat": "feature", "docs": "docs", "doc": "docs", "tests": "test", "build": "ci",
            "style": "chore", "revert": "fix", "bugfix": "fix", "hotfix": "fix"}

WEIGHTS = {"security": 40, "feature": 30, "fix": 22, "perf": 22, "refactor": 12, "docs": 8,
           "test": 8, "ci": 6, "deps": 4, "chore": 4, "other": 10}
HIGH, MEDIUM = 50, 28
ORDER = ["security", "feature", "fix", "perf", "refactor", "docs", "test", "ci", "deps", "chore", "other"]
TITLES = {"security": "Security", "feature": "Features", "fix": "Fixes", "perf": "Performance",
          "refactor": "Refactoring", "docs": "Docs", "test": "Tests", "ci": "Build and CI",
          "deps": "Dependencies", "chore": "Maintenance", "other": "Other changes"}


def categorize(item: Item) -> str:
    title = item.title.strip()
    conv = _CONVENTIONAL.match(title)
    if conv:
        kind = _ALIASES.get(conv.group(1).lower(), conv.group(1).lower())
        if kind in WEIGHTS:
            return kind
    haystack = f"{' '.join(item.labels)} {title}"
    for category, pattern in _RULES:
        if pattern.search(haystack):
            return category
    return "other"


def score(item: Item) -> int:
    if item.kind == "release":
        return 35 + WEIGHTS["feature"]
    points = WEIGHTS[item.category]
    if item.kind == "pr":
        points += min(30, round(5 * math.log2(1 + item.lines / 20)))
    breaking = _CONVENTIONAL.match(item.title)
    if (breaking and breaking.group(3)) or any("breaking" in label.lower() for label in item.labels):
        points += 20
    return points


def rate(item: Item) -> Item:
    item.category = categorize(item)
    item.impact = score(item)
    item.tier = "high" if item.impact >= HIGH else "medium" if item.impact >= MEDIUM else "low"
    return item
