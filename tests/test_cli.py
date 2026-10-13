from datetime import datetime, timezone

import pytest
from weekship import cli

NOW = datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc)


def test_parse_since_durations_and_dates():
    assert cli.parse_since("7d", NOW) == datetime(2026, 10, 5, 12, tzinfo=timezone.utc)
    assert cli.parse_since("2w", NOW) == datetime(2026, 9, 28, 12, tzinfo=timezone.utc)
    assert cli.parse_since("36h", NOW) == datetime(2026, 10, 11, 0, tzinfo=timezone.utc)
    assert cli.parse_since("2026-10-01", NOW) == datetime(2026, 10, 1, tzinfo=timezone.utc)


def test_requires_a_repo_or_owner(capsys):
    assert cli.main([]) == 2
    assert "--repo" in capsys.readouterr().err


def test_end_to_end_with_fake_github(monkeypatch, tmp_path, capsys):
    from conftest import FakeGitHub
    from weekship.github import Client

    merged = datetime.now(timezone.utc).isoformat()
    pr = {"number": 5, "title": "feat: ship it", "html_url": "https://x/5", "user": {"login": "alice", "type": "User"},
          "merged_at": merged, "updated_at": merged, "labels": [], "head": {"ref": "claude/ship"}, "body": ""}
    fake = FakeGitHub({"/repos/o/r": {"full_name": "o/r", "private": False},
                       "/repos/o/r/pulls": [pr], "/repos/o/r/pulls/5": {"additions": 10, "deletions": 0, "changed_files": 1},
                       "/repos/o/r/pulls/5/commits": [], "/repos/o/r/commits": [], "/repos/o/r/releases": []})
    monkeypatch.setattr(cli, "Client", lambda token=None: Client(token, transport=fake, sleep=lambda s: None))
    out = tmp_path / "out"
    assert cli.main(["--repo", "o/r", "--no-llm", "--quiet", "--format", "post", "--out", str(out)]) == 0
    assert "1 of them (100%)" in capsys.readouterr().out
    assert sorted(p.name for p in out.iterdir()) == ["brief.md", "notes.md", "post.md", "week.json"]
