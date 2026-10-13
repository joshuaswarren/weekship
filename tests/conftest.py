import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest  # noqa: E402

from weekship.github import Client  # noqa: E402
from weekship.model import Item, Window  # noqa: E402

NOW = datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc)
WINDOW = Window(since=datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc), until=NOW)


def make_item(**kw) -> Item:
    base = dict(kind="pr", repo="o/r", ref="#1", title="Fix a bug", url="https://x/1", author="alice",
                at=NOW, additions=10, deletions=2)
    base.update(kw)
    return Item(**base)


class FakeGitHub:
    """Routes URL path prefixes to canned JSON; records requests; supports Link pagination."""

    def __init__(self, routes: dict[str, object]):
        self.routes = routes
        self.requests: list[str] = []

    def __call__(self, url, headers):
        self.requests.append(url)
        path = url.split("api.github.com", 1)[-1].split("?", 1)[0]
        body = self.routes[path]
        if callable(body):
            return body(url)
        return 200, {}, json.dumps(body).encode()


@pytest.fixture
def client_for():
    def make(routes):
        fake = FakeGitHub(routes)
        return Client(token="t", transport=fake, sleep=lambda s: None), fake
    return make
