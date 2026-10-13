"""Collect -> classify -> rate -> summarize."""
from __future__ import annotations

import fnmatch
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from .classify import classify_origin
from .config import Config
from .github import Client, GitHubError
from .impact import rate
from .model import AGENT, BOT, HUMAN, Item, Week, Window


def collect_week(client: Client, window: Window, cfg: Config, *, owner: str | None = None,
                 repos: list[str] | None = None, public_only: bool = False,
                 include_forks: bool = False, workers: int = 8, progress=lambda msg: None) -> Week:
    """Read one window of work for an owner (user or org), an explicit repo list, or both."""
    selected: dict[str, dict] = {}
    if owner:
        for repo in client.list_repos(owner, public_only=public_only, include_forks=include_forks,
                                      since=window.since):
            selected[repo["full_name"]] = repo
    for name in repos or []:
        selected[name] = client.get(f"/repos/{name}")
    selected = {n: r for n, r in selected.items() if not any(fnmatch.fnmatch(n, p) for p in cfg.exclude_repos)}

    week = Week(window=window, scope=owner or ", ".join(repos or []))

    def read(name: str) -> tuple[str, list[Item] | str]:
        progress(f"reading {name}")
        try:
            return name, client.collect(selected[name], window.since, window.until)
        except GitHubError as err:
            return name, str(err)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for name, result in pool.map(read, sorted(selected)):
            if isinstance(result, str):
                week.skipped.append(f"{name}: {result}")
                continue
            if result:
                week.repos.append(name)
            week.items.extend(rate(classify_origin(item, cfg)) for item in result)
    week.items.sort(key=lambda i: (-i.impact, i.at))
    return week


@dataclass
class Stats:
    changes: int  # merged PRs + direct commits
    prs: int
    commits: int
    releases: int
    by_origin: dict[str, int]
    lines_by_origin: dict[str, int]
    agent_pct: int
    automated_pct: int
    agent_line_pct: int
    repos_active: int
    top_repos: list[tuple[str, int]]
    top_signals: list[tuple[str, int]]
    top_author: str
    top_author_pct: int


def _pct(part: int, whole: int) -> int:
    return round(100 * part / whole) if whole else 0


def summarize(week: Week) -> Stats:
    work = [i for i in week.items if i.kind != "release"]
    by_origin = {o: sum(1 for i in work if i.origin == o) for o in (HUMAN, AGENT, BOT)}
    lines = {o: sum(i.lines for i in work if i.origin == o and i.kind == "pr") for o in (HUMAN, AGENT, BOT)}
    pr_lines = sum(lines.values())
    signals = Counter(s.split(":", 1)[0] for i in work if i.origin == AGENT for s in i.signals)
    repo_counts = Counter(i.repo for i in work)
    authors = Counter(i.author for i in work).most_common(1)
    top_author, top_count = authors[0] if authors else ("", 0)
    return Stats(
        changes=len(work),
        prs=sum(1 for i in work if i.kind == "pr"),
        commits=sum(1 for i in work if i.kind == "commit"),
        releases=sum(1 for i in week.items if i.kind == "release"),
        by_origin=by_origin,
        lines_by_origin=lines,
        agent_pct=_pct(by_origin[AGENT], len(work)),
        automated_pct=_pct(by_origin[AGENT] + by_origin[BOT], len(work)),
        agent_line_pct=_pct(lines[AGENT], pr_lines),
        repos_active=len({i.repo for i in week.items}),
        top_repos=repo_counts.most_common(5),
        top_signals=signals.most_common(),
        top_author=top_author,
        top_author_pct=_pct(top_count, len(work)),
    )

