import json

import pytest
from conftest import NOW, WINDOW
from weekship.github import GitHubError, parse_time

REPO = {"full_name": "o/r", "private": False}


def pr(number, merged, **extra):
    return {"number": number, "title": f"PR {number}", "html_url": f"https://x/pull/{number}",
            "user": {"login": "alice", "type": "User"}, "merged_at": merged, "updated_at": merged or "2026-10-10T00:00:00Z",
            "labels": [], "head": {"ref": "work"}, "body": "", **extra}


def commit(sha, message, parents=1, login="alice"):
    return {"sha": sha, "html_url": f"https://x/c/{sha}", "parents": [{}] * parents,
            "author": {"login": login, "type": "User"},
            "commit": {"message": message, "author": {"name": login, "date": "2026-10-10T00:00:00Z"}}}


def routes(prs, commits, pr_commits=None, releases=()):
    out = {"/repos/o/r/pulls": prs, "/repos/o/r/commits": commits, "/repos/o/r/releases": list(releases)}
    for p in prs:
        out[f"/repos/o/r/pulls/{p['number']}"] = {"additions": 30, "deletions": 4, "changed_files": 2}
        out[f"/repos/o/r/pulls/{p['number']}/commits"] = (pr_commits or {}).get(p["number"], [])
    return out


def test_merged_pr_is_collected_with_size_and_trailers(client_for):
    prs = [pr(1, "2026-10-10T00:00:00Z")]
    pcs = {1: [commit("a1", "work\n\nCo-authored-by: Claude <noreply@anthropic.com>")]}
    client, _ = client_for(routes(prs, [], pcs))
    [item] = client.collect(REPO, WINDOW.since, WINDOW.until)
    assert (item.kind, item.ref, item.lines, item.files) == ("pr", "#1", 34, 2)
    assert item.trailers == ("Co-authored-by: Claude <noreply@anthropic.com>",)


def test_unmerged_and_out_of_window_prs_are_ignored(client_for):
    prs = [pr(1, None), pr(2, "2026-09-01T00:00:00Z", updated_at="2026-10-11T00:00:00Z")]
    client, _ = client_for(routes(prs, []))
    assert client.collect(REPO, WINDOW.since, WINDOW.until) == []


def test_scan_stops_at_first_pr_older_than_window(client_for):
    prs = [pr(1, "2026-10-10T00:00:00Z"), pr(2, "2026-08-01T00:00:00Z"), pr(3, "2026-10-09T00:00:00Z")]
    client, fake = client_for(routes(prs, []))
    numbers = [i.ref for i in client.collect(REPO, WINDOW.since, WINDOW.until)]
    assert numbers == ["#1"]


def test_commits_already_in_a_pr_are_not_counted_twice(client_for):
    prs = [pr(7, "2026-10-10T00:00:00Z")]
    pcs = {7: [commit("rb1", "rebase merged change")]}
    commits = [commit("s1", "Squash merged (#7)"), commit("rb2", "rebase merged change"),
               commit("m1", "Merge pull request #7 from x/y", parents=2), commit("d1", "direct to main")]
    client, _ = client_for(routes(prs, commits, pcs))
    items = client.collect(REPO, WINDOW.since, WINDOW.until)
    assert sorted(i.ref for i in items) == ["#7", "d1"]


def test_releases_in_window_only_and_drafts_skipped(client_for):
    rels = [{"tag_name": "v1", "name": "One", "html_url": "u", "published_at": "2026-10-10T00:00:00Z",
             "author": {"login": "a"}, "body": "notes"},
            {"tag_name": "v0", "published_at": "2026-01-01T00:00:00Z", "html_url": "u"},
            {"tag_name": "v2", "draft": True, "published_at": "2026-10-10T00:00:00Z", "html_url": "u"}]
    client, _ = client_for(routes([], [], releases=rels))
    [item] = client.collect(REPO, WINDOW.since, WINDOW.until)
    assert (item.kind, item.ref, item.title) == ("release", "v1", "One")


def test_pagination_follows_link_header():
    from weekship.github import Client

    def transport(url, headers):
        if "page=2" in url:
            return 200, {}, json.dumps([{"n": 3}]).encode()
        return 200, {"link": '<https://api.github.com/x?page=2>; rel="next"'}, json.dumps([{"n": 1}, {"n": 2}]).encode()

    assert [r["n"] for r in Client(transport=transport).pages("/x")] == [1, 2, 3]


def test_retries_transient_errors_then_succeeds():
    from weekship.github import Client
    seen = []

    def transport(url, headers):
        seen.append(1)
        return (502, {}, b"") if len(seen) < 3 else (200, {}, b'{"ok": true}')

    assert Client(transport=transport, sleep=lambda s: None).get("/x") == {"ok": True}
    assert len(seen) == 3


def test_rate_limit_is_reported_with_reset_time():
    from weekship.github import Client
    transport = lambda url, headers: (403, {"x-ratelimit-remaining": "0", "x-ratelimit-reset": "1791860000"}, b"{}")
    with pytest.raises(GitHubError, match="rate limit"):
        Client(transport=transport).get("/x")


def test_list_repos_skips_forks_archived_and_idle(client_for):
    repos = [{"full_name": "o/a", "pushed_at": "2026-10-11T00:00:00Z"},
             {"full_name": "o/fork", "fork": True, "pushed_at": "2026-10-11T00:00:00Z"},
             {"full_name": "o/old", "pushed_at": "2026-01-01T00:00:00Z"},
             {"full_name": "o/gone", "archived": True, "pushed_at": "2026-10-11T00:00:00Z"}]
    client, _ = client_for({"/users/o": {"type": "Organization"}, "/orgs/o/repos": repos})
    assert [r["full_name"] for r in client.list_repos("o", since=WINDOW.since)] == ["o/a"]


def test_parse_time_is_utc():
    assert parse_time("2026-10-12T07:00:00-05:00") == NOW
