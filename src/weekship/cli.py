"""weekship command line."""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import load_config
from .github import Client, GitHubError, find_token
from .llm import LLM
from .model import Window
from .pipeline import collect_week, summarize
from .render import build_outputs

_DURATION = re.compile(r"^(\d+)([dwh])$")


def parse_since(text: str, now: datetime) -> datetime:
    """Accept 7d, 2w, 36h or an ISO date/time."""
    match = _DURATION.match(text)
    if match:
        unit = {"d": "days", "w": "weeks", "h": "hours"}[match.group(2)]
        return now - timedelta(**{unit: int(match.group(1))})
    parsed = datetime.fromisoformat(text)
    return (parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="weekship", description="Write what shipped: release notes, an owner brief and a post.")
    p.add_argument("--repo", action="append", default=[], metavar="OWNER/NAME", help="repository to read (repeatable)")
    p.add_argument("--owner", help="GitHub user or organization: read every repository it owns")
    p.add_argument("--since", default="7d", help="window start: 7d, 2w, 36h or an ISO date (default 7d)")
    p.add_argument("--until", help="window end, ISO date/time (default now)")
    p.add_argument("--tz", default="UTC", help="time zone for dates in the output, e.g. America/Chicago")
    p.add_argument("--public-only", action="store_true", help="skip private repositories")
    p.add_argument("--include-forks", action="store_true")
    p.add_argument("--exclude", action="append", default=[], metavar="GLOB", help="skip repos matching this owner/name glob")
    p.add_argument("--config", help="path to a .weekship.toml (default: ./.weekship.toml if present)")
    p.add_argument("--format", choices=["notes", "brief", "post", "all", "json", "none"], default="all")
    p.add_argument("--out", help="directory to write notes.md, brief.md, post.md and week.json into")
    p.add_argument("--no-llm", action="store_true", help="skip the language model; write deterministic text")
    p.add_argument("--llm-base-url", help="OpenAI-compatible base URL (env WEEKSHIP_LLM_BASE_URL or OPENAI_BASE_URL)")
    p.add_argument("--llm-model", help="model name (env WEEKSHIP_MODEL)")
    p.add_argument("--redact-private", action="store_true", help="hide private repo names in notes and brief (the post always hides them)")
    p.add_argument("--quiet", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.repo and not args.owner:
        print("weekship: give --repo OWNER/NAME or --owner USER_OR_ORG", file=sys.stderr)
        return 2
    now = datetime.now(timezone.utc)
    until = parse_since(args.until, now) if args.until else now
    window = Window(since=parse_since(args.since, now), until=until)
    cfg = load_config(args.config)
    cfg.exclude_repos.extend(args.exclude)
    client = Client(token=find_token())
    log = (lambda msg: None) if args.quiet else (lambda msg: print(msg, file=sys.stderr))
    try:
        week = collect_week(client, window, cfg, owner=args.owner, repos=args.repo,
                            public_only=args.public_only, include_forks=args.include_forks, progress=log)
    except GitHubError as err:
        print(f"weekship: {err}", file=sys.stderr)
        return 1
    stats = summarize(week)
    tz = ZoneInfo(args.tz)

    llm = None if args.no_llm else LLM.from_env(args.llm_base_url, args.llm_model)
    outputs = build_outputs(week, stats, tz, llm=llm, redact=args.redact_private)
    if args.format == "none":
        pass
    elif args.format == "json":
        print(outputs["week.json"])
    elif args.format == "all":
        for name in ("brief.md", "post.md", "notes.md"):
            print(f"\n===== {name} =====\n{outputs[name]}")
    else:
        print(outputs[{"notes": "notes.md", "brief": "brief.md", "post": "post.md"}[args.format]])
    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        for name, text in outputs.items():
            (out / name).write_text(text)
    for line in week.skipped:
        print(f"weekship: skipped {line}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
