"""Minimal GitHub REST collector (stdlib only)."""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterator
from datetime import datetime, timezone
from typing import Any

from .model import Item

API = "https://api.github.com"
Transport = Callable[[str, dict[str, str]], tuple[int, dict[str, str], bytes]]


class GitHubError(RuntimeError):
    pass


def find_token() -> str | None:
    for var in ("GITHUB_TOKEN", "GH_TOKEN"):
        if os.environ.get(var):
            return os.environ[var]
    try:
        out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None if out.returncode == 0 else None


def _urllib_transport(url: str, headers: dict[str, str]) -> tuple[int, dict[str, str], bytes]:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, {k.lower(): v for k, v in resp.headers.items()}, resp.read()
    except urllib.error.HTTPError as err:
        return err.code, {k.lower(): v for k, v in err.headers.items()}, err.read()


def parse_time(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)


class Client:
    def __init__(self, token: str | None = None, transport: Transport | None = None,
                 sleep: Callable[[float], None] = time.sleep) -> None:
        self.token = token
        self.transport = transport or _urllib_transport
        self.sleep = sleep
        self.calls = 0

    def get(self, path: str, **params: Any) -> Any:
        return self._request(path, params)[0]

    def _request(self, path: str, params: dict[str, Any]) -> tuple[Any, dict[str, str]]:
        url = path if path.startswith("http") else API + path
        if params:
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
                   "User-Agent": "weekship"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        for attempt in range(4):
            self.calls += 1
            status, resp_headers, body = self.transport(url, headers)
            if status in (502, 503, 504) and attempt < 3:
                self.sleep(2 ** attempt)
                continue
            if status == 403 and resp_headers.get("retry-after") and attempt < 3:
                self.sleep(min(int(resp_headers["retry-after"]), 60))
                continue
            if status == 403 and resp_headers.get("x-ratelimit-remaining") == "0":
                reset = datetime.fromtimestamp(int(resp_headers.get("x-ratelimit-reset", "0")), timezone.utc)
                raise GitHubError(f"GitHub rate limit exhausted; resets {reset:%H:%M} UTC")
            if status >= 400:
                raise GitHubError(f"GET {url} -> HTTP {status}: {body[:200].decode('utf-8', 'replace')}")
            return (json.loads(body) if body else None), resp_headers
        raise GitHubError(f"GET {url} failed after retries")

    def pages(self, path: str, **params: Any) -> Iterator[Any]:
        """Yield every item of a paginated list, following Link rel=next."""
        params.setdefault("per_page", 100)
        url: str | None = path
        first = True
        while url:
            data, headers = self._request(url, params if first else {})
            first = False
            yield from data
            link = headers.get("link", "")
            match = re.search(r'<([^>]+)>;\s*rel="next"', link)
            url = match.group(1) if match else None

    # ---- repo discovery -------------------------------------------------
    def list_repos(self, owner: str, *, public_only: bool = False, include_forks: bool = False,
                   since: datetime | None = None) -> list[dict]:
        kind = self.get(f"/users/{owner}")["type"]
        if kind == "Organization":
            repos = self.pages(f"/orgs/{owner}/repos", type="public" if public_only else "all")
        elif self.token and self.get("/user")["login"].lower() == owner.lower():
            repos = self.pages("/user/repos", affiliation="owner", visibility="public" if public_only else "all")
        else:
            repos = self.pages(f"/users/{owner}/repos", type="owner")
        keep = []
        for repo in repos:
            if repo.get("archived") or (repo.get("fork") and not include_forks):
                continue
            if since and (not repo.get("pushed_at") or parse_time(repo["pushed_at"]) < since):
                continue
            keep.append(repo)
        return sorted(keep, key=lambda r: r["full_name"].lower())

    # ---- collectors -------------------------------------------------------
    def collect(self, repo: dict, since: datetime, until: datetime) -> list[Item]:
        """Everything that shipped in one repo: merged PRs, direct commits, releases."""
        prs, covered = self._merged_prs(repo, since, until)
        return prs + self._direct_commits(repo, since, until, prs, covered) + self._releases(repo, since, until)

    def _merged_prs(self, repo: dict, since: datetime, until: datetime) -> tuple[list[Item], set[str]]:
        """Merged PRs, plus the shas and subjects that identify their commits on the default branch."""
        full = repo["full_name"]
        items: list[Item] = []
        covered: set[str] = set()
        for pr in self.pages(f"/repos/{full}/pulls", state="closed", sort="updated", direction="desc"):
            if parse_time(pr["updated_at"]) < since:
                break
            if not pr.get("merged_at"):
                continue
            merged = parse_time(pr["merged_at"])
            if not since <= merged < until:
                continue
            detail = self.get(f"/repos/{full}/pulls/{pr['number']}")
            if detail.get("merge_commit_sha"):
                covered.add(detail["merge_commit_sha"])
            trailers: list[str] = []
            identities: list[str] = []
            for commit in self.pages(f"/repos/{full}/pulls/{pr['number']}/commits"):
                message = commit["commit"]["message"]
                identities.append(_identity(commit["commit"].get("author")))
                covered.update((commit["sha"], message.splitlines()[0] if message else ""))
                trailers.extend(_trailers(message))
            items.append(Item(
                kind="pr", repo=full, ref=f"#{pr['number']}", title=pr["title"], url=pr["html_url"],
                author=pr["user"]["login"], author_type=pr["user"].get("type", "User"), at=merged,
                private=bool(repo.get("private")), additions=detail.get("additions", 0),
                deletions=detail.get("deletions", 0), files=detail.get("changed_files", 0),
                labels=tuple(label["name"] for label in pr.get("labels", [])),
                branch=pr["head"]["ref"], body=pr.get("body") or "",
                trailers=tuple(dict.fromkeys(trailers)), identities=tuple(dict.fromkeys(identities)),
            ))
        return items, covered

    def _direct_commits(self, repo: dict, since: datetime, until: datetime,
                        prs: list[Item], covered: set[str]) -> list[Item]:
        """Default-branch commits that did not arrive through a merged PR."""
        full = repo["full_name"]
        numbers = {pr.ref[1:] for pr in prs}
        items = []
        for c in self.pages(f"/repos/{full}/commits", since=since.isoformat(), until=until.isoformat()):
            message = c["commit"]["message"]
            subject = message.splitlines()[0] if message else ""
            if (len(c.get("parents", [])) > 1 or c["sha"] in covered or subject in covered
                    or _mentions_pr(subject, numbers)):
                continue
            user = c.get("author") or {}
            who = c["commit"].get("author") or {}
            items.append(Item(
                kind="commit", repo=full, ref=c["sha"][:7], title=subject, url=c["html_url"],
                author=user.get("login") or who.get("name", "unknown"),
                author_type=user.get("type", "User"), at=parse_time(who.get("date") or c["commit"]["committer"]["date"]),
                private=bool(repo.get("private")), body=message, trailers=tuple(_trailers(message)),
                identities=(_identity(who),),
            ))
        return items

    def _releases(self, repo: dict, since: datetime, until: datetime) -> list[Item]:
        full = repo["full_name"]
        items = []
        for rel in self.pages(f"/repos/{full}/releases"):
            if rel.get("draft") or not rel.get("published_at"):
                continue
            rel.setdefault("created_at", rel["published_at"])
            at = parse_time(rel["published_at"])
            if at < since and parse_time(rel["created_at"]) < since:
                break  # newest first: nothing later in the list can fall in the window
            if not since <= at < until:
                continue
            items.append(Item(
                kind="release", repo=full, ref=rel["tag_name"], title=rel.get("name") or rel["tag_name"],
                url=rel["html_url"], author=(rel.get("author") or {}).get("login", ""),
                author_type=(rel.get("author") or {}).get("type", "User"), at=at,
                private=bool(repo.get("private")), body=rel.get("body") or "",
            ))
        return items


_TRAILER = re.compile(r"^(co-authored-by|generated-by|assisted-by):\s*.+$", re.I | re.M)


def _trailers(message: str) -> list[str]:
    return [m.group(0).strip() for m in _TRAILER.finditer(message or "")]


def _identity(author: dict | None) -> str:
    author = author or {}
    return f"{author.get('name', '')} <{author.get('email', '')}>"


def _mentions_pr(subject: str, numbers: set[str]) -> bool:
    found = re.findall(r"\(#(\d+)\)|pull request #(\d+)", subject)
    return any(n in numbers for pair in found for n in pair if n)
