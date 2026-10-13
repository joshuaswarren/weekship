from datetime import timezone

from conftest import WINDOW, make_item
from weekship.classify import classify_origin
from weekship.config import Config
from weekship.impact import rate
from weekship.llm import LLM, LLMError, numbers_ok
from weekship.model import Week
from weekship.pipeline import summarize
from weekship.render import build_outputs


def week_of(*items):
    cfg = Config()
    week = Week(window=WINDOW, scope="o", repos=sorted({i.repo for i in items}))
    week.items = sorted((rate(classify_origin(i, cfg)) for i in items), key=lambda i: -i.impact)
    return week


def sample():
    return week_of(
        make_item(ref="#1", title="feat: add export", branch="claude/export", additions=900),
        make_item(ref="#2", title="Fix crash on empty input", author="alice"),
        make_item(ref="#3", title="Fix private thing", repo="o/secret", private=True, branch="codex/x"),
        make_item(kind="commit", ref="abc1234", title="docs: tweak", author="dependabot[bot]", author_type="Bot"),
        make_item(kind="release", ref="v1.0.0", title="v1.0.0"),
    )


def test_stats_count_origins_and_percentages():
    stats = summarize(sample())
    assert stats.by_origin == {"human": 1, "agent": 2, "bot": 1}
    assert (stats.changes, stats.prs, stats.commits, stats.releases) == (4, 3, 1, 1)
    assert stats.agent_pct == 50 and stats.automated_pct == 75
    assert stats.top_signals == [("branch", 2)]


def test_stats_on_an_empty_week_do_not_divide_by_zero():
    stats = summarize(week_of())
    assert (stats.changes, stats.agent_pct) == (0, 0)


def test_outputs_without_llm_state_the_hard_number(tmp_path):
    week = sample()
    out = build_outputs(week, summarize(week), timezone.utc, llm=None)
    assert "2 agent-authored (50%)" in out["brief.md"]
    assert "2 of them (50%)" in out["post.md"]
    assert "## Releases" in out["notes.md"] and "## Highlights" in out["notes.md"]
    assert "(agent)" in out["notes.md"]


def test_post_never_names_private_repos_but_brief_does_unless_redacted():
    week = sample()
    stats = summarize(week)
    assert "o/secret" not in build_outputs(week, stats, timezone.utc)["post.md"]
    assert "o/secret" in build_outputs(week, stats, timezone.utc)["brief.md"]
    assert "o/secret" not in build_outputs(week, stats, timezone.utc, redact=True)["brief.md"]


class Scripted(LLM):
    def __init__(self, reply):
        super().__init__("http://x/v1", "k", "m")
        self.reply = reply
        self.http = lambda url, payload, headers: {"choices": [{"message": {"content": self.reply}}]}


def test_llm_prose_is_used_when_its_numbers_check_out():
    week = sample()
    reply = "Agents wrote 50% of the 4 changes this week."
    out = build_outputs(week, summarize(week), timezone.utc, llm=Scripted(reply))
    assert reply in out["notes.md"] and reply in out["brief.md"]


def test_llm_prose_with_an_invented_number_is_rejected():
    week = sample()
    out = build_outputs(week, summarize(week), timezone.utc, llm=Scripted("Agents wrote 50% and shipped 9000 things."))
    assert "9000" not in out["notes.md"] and "9000" not in out["post.md"]
    assert "2 agent-authored (50%)" in out["brief.md"]


def test_unreachable_llm_falls_back_to_plain_text():
    class Down(LLM):
        def complete(self, *a, **k):
            raise LLMError("connection refused")
    week = sample()
    out = build_outputs(week, summarize(week), timezone.utc, llm=Down("http://x/v1", "k", "m"))
    assert "2 of them (50%)" in out["post.md"]


def test_numbers_ok():
    assert numbers_ok("12 of 40 (30%)", "we merged 12 of 40, 30% agent")
    assert not numbers_ok("13 of 40", "12 of 40")


def test_think_tags_and_model_discovery():
    calls = []

    def http(url, payload, headers):
        calls.append(url)
        if url.endswith("/models"):
            return {"data": [{"id": "first"}, {"id": "second"}]}
        assert payload["model"] == "first"
        return {"choices": [{"message": {"content": "<think>hmm</think>Answer"}}]}

    llm = LLM("http://x/v1", "k", None, http=http)
    assert llm.complete("s", "u") == "Answer"
    assert calls[0].endswith("/models")


def test_llm_from_env_prefers_weekship_vars(monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", "http://openai/v1/")
    monkeypatch.setenv("WEEKSHIP_LLM_BASE_URL", "http://fleet/v1")
    monkeypatch.setenv("WEEKSHIP_MODEL", "big")
    llm = LLM.from_env()
    assert (llm.base_url, llm.model) == ("http://fleet/v1", "big")


def test_attribution_gap_is_flagged_when_one_account_does_everything_without_markers():
    items = [make_item(ref=f"#{n}", title=f"Fix {n}", author="owner") for n in range(30)]
    items.append(make_item(ref="#99", title="Fix agent", author="owner", branch="claude/x"))
    week = week_of(*items)
    brief = build_outputs(week, summarize(week), timezone.utc)["brief.md"]
    assert "## Attribution gap" in brief and "owner" in brief and "docs/attribution.md" in brief


def test_no_gap_warning_when_agents_are_visible():
    items = [make_item(ref=f"#{n}", author="owner", branch="claude/x") for n in range(30)]
    week = week_of(*items)
    assert "Attribution gap" not in build_outputs(week, summarize(week), timezone.utc)["brief.md"]


def test_commit_identity_marks_agent_work():
    from weekship.classify import classify_origin
    item = classify_origin(make_item(identities=("Ops Agent <agents@example.com>",)), Config())
    assert item.origin == "agent" and item.signals[0].startswith("identity:")


def test_many_releases_in_one_repo_collapse_to_a_range():
    rels = [make_item(kind="release", ref=f"v1.0.{n}", title=f"v1.0.{n}", at=WINDOW.since.replace(day=6 + n)) for n in range(5)]
    notes = build_outputs(week_of(*rels), summarize(week_of(*rels)), timezone.utc)["notes.md"]
    assert "o/r: 5 releases, v1.0.0 to v1.0.4" in notes


def test_the_word_security_alone_does_not_make_a_change_a_security_fix():
    from weekship.impact import categorize
    assert categorize(make_item(title="outline: security move to One")) != "security"
    assert categorize(make_item(title="Fix XSS in comment form")) == "security"
    assert categorize(make_item(title="security: rotate session keys")) == "security"


def test_model_cannot_reuse_digits_from_dates_or_titles():
    week = week_of(make_item(ref="#1", title="Bump to 4.17.21", branch="claude/x"))
    out = build_outputs(week, summarize(week), timezone.utc,
                        llm=Scripted("Agents wrote 100% of the 12 changes in 2026."))
    assert "12 changes in 2026" not in out["post.md"]
    assert "1 of them (100%)" in out["post.md"]


def test_private_titles_stay_out_of_the_post_the_llm_facts_and_redacted_outputs():
    week = week_of(make_item(ref="#1", title="Rotate production vault keys", repo="o/secret", private=True),
                   make_item(ref="#2", title="Add public export", repo="o/open", branch="claude/x"))
    stats = summarize(week)
    seen = []

    class Spy(Scripted):
        def complete(self, system, user, max_tokens=700):
            seen.append(user)
            return super().complete(system, user, max_tokens)

    out = build_outputs(week, stats, timezone.utc, llm=Spy("Agents wrote 50% of 2 changes."), redact=True)
    assert "vault keys" not in "".join(seen) + out["post.md"] + out["notes.md"] + out["brief.md"] + out["week.json"]
    assert "o/secret" not in out["week.json"] + out["notes.md"] + out["brief.md"]
    assert "Add public export" in build_outputs(week, stats, timezone.utc, redact=True)["post.md"]
    unredacted = build_outputs(week, stats, timezone.utc)
    assert "vault keys" in unredacted["notes.md"] and "vault keys" not in unredacted["post.md"]


def test_human_named_like_an_agent_is_not_flagged_by_commit_identity():
    from weekship.classify import classify_origin
    for who in ("Devin Smith <devin@example.com>", "Gemini Cruz <gemini@example.org>", "Cursor Lee <c@example.net>"):
        assert classify_origin(make_item(identities=(who,)), Config()).origin == "human"


def test_llm_settings_precedence_flag_env_file_default(monkeypatch):
    for var in ("WEEKSHIP_LLM_BASE_URL", "OPENAI_BASE_URL", "WEEKSHIP_MODEL", "WEEKSHIP_LLM_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("FLEET_KEY", "secret")
    from weekship.llm import DEFAULT_BASE_URL
    assert LLM.from_env().base_url == DEFAULT_BASE_URL
    file_only = LLM.from_env(file_base_url="http://file/v1", file_model="m-file", key_env="FLEET_KEY")
    assert (file_only.base_url, file_only.model, file_only.api_key) == ("http://file/v1", "m-file", "secret")
    monkeypatch.setenv("WEEKSHIP_LLM_BASE_URL", "http://env/v1")
    assert LLM.from_env(file_base_url="http://file/v1").base_url == "http://env/v1"
    assert LLM.from_env("http://flag/v1", file_base_url="http://file/v1").base_url == "http://flag/v1"


def test_titles_reach_the_model_with_digits_masked():
    from weekship.render import facts_text
    week = week_of(make_item(title="speed up decode from 34 to 51 tok/s", branch="claude/x"))
    facts = facts_text(week, summarize(week), redact=True)
    assert "from N to N tok/s" in facts and "34" not in facts and "51" not in facts


def test_percent_spelled_out_counts_as_the_real_percentage():
    week = sample()
    out = build_outputs(week, summarize(week), timezone.utc, llm=Scripted("Agents wrote 50 percent of the 4 changes."))
    assert "50% of the 4 changes" in out["brief.md"]


def test_a_rejected_model_answer_is_retried_once_then_accepted():
    import itertools
    replies = itertools.chain(["Agents wrote 9000 things."], itertools.repeat("Agents wrote 50% of the 4 changes."))

    class Flaky(LLM):
        def complete(self, system, user, max_tokens=700):
            return next(replies)

    week = sample()
    out = build_outputs(week, summarize(week), timezone.utc, llm=Flaky("http://x/v1", "k", "m"))
    assert "Agents wrote 50% of the 4 changes." in out["brief.md"]
