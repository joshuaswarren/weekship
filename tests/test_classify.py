from conftest import make_item
from weekship.classify import classify_origin
from weekship.config import Config, load_config


def origin(**kw):
    return classify_origin(make_item(**kw), Config())


def test_plain_human():
    assert origin().origin == "human"


def test_agent_branch_prefix():
    item = origin(branch="claude/add-cache")
    assert item.origin == "agent" and item.signals == ("branch:claude/add-cache",)


def test_agent_login_outranks_bot_type():
    assert origin(author="copilot-swe-agent[bot]", author_type="Bot").origin == "agent"


def test_dependency_bot_is_bot_not_agent():
    assert origin(author="dependabot[bot]", author_type="Bot", branch="dependabot/pip/x").origin == "bot"


def test_coauthor_trailer_marks_agent():
    item = origin(trailers=("Co-authored-by: Claude <noreply@anthropic.com>",))
    assert item.origin == "agent" and item.signals[0].startswith("trailer:")


def test_human_coauthor_named_like_agent_word_is_not_flagged():
    assert origin(trailers=("Co-authored-by: Devin Smith <devin@example.com>",)).origin == "human"


def test_body_marker():
    assert origin(body="Done.\n\nGenerated with Claude Code").origin == "agent"


def test_agent_beats_bot_when_both_signal():
    assert origin(author="dependabot[bot]", author_type="Bot", branch="codex/x").origin == "agent"


def test_config_extends_defaults(tmp_path):
    file = tmp_path / "w.toml"
    file.write_text('[detect]\nagent_branch_prefixes = ["fleet/"]\n[exclude]\nrepos = ["o/private*"]\n')
    cfg = load_config(file)
    assert classify_origin(make_item(branch="fleet/x"), cfg).origin == "agent"
    assert classify_origin(make_item(branch="claude/x"), cfg).origin == "agent"
    assert cfg.exclude_repos == ["o/private*"]


def test_user_level_config_supplies_llm_settings_and_a_repo_file_wins(tmp_path, monkeypatch):
    home = tmp_path / "cfg" / "weekship"
    home.mkdir(parents=True)
    (home / "config.toml").write_text('[llm]\nbase_url = "http://fleet/v1"\nmodel = "advisor"\napi_key_env = "FLEET_KEY"\n')
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    cfg = load_config()
    assert (cfg.llm_base_url, cfg.llm_model, cfg.llm_api_key_env) == ("http://fleet/v1", "advisor", "FLEET_KEY")
    (work / ".weekship.toml").write_text('[llm]\nbase_url = "http://repo/v1"\n')
    assert load_config().llm_base_url == "http://repo/v1"
