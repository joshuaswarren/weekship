from conftest import make_item
from weekship.impact import categorize, rate


def test_conventional_prefix_wins():
    assert categorize(make_item(title="feat(api): add export")) == "feature"
    assert categorize(make_item(title="docs: tidy readme")) == "docs"


def test_keyword_and_label_fallbacks():
    assert categorize(make_item(title="Patch XSS in comment form")) == "security"
    assert categorize(make_item(title="Bump lodash to 4.17.21")) == "deps"
    assert categorize(make_item(title="Crash on empty input", labels=("bug",))) == "fix"


def test_bigger_prs_score_higher_within_a_category():
    small = rate(make_item(title="feat: a", additions=5))
    big = rate(make_item(title="feat: b", additions=2000, deletions=500))
    assert big.impact > small.impact


def test_security_feature_and_breaking_are_high_tier_chores_are_low():
    assert rate(make_item(title="fix security hole", additions=300)).tier == "high"
    assert rate(make_item(title="feat!: drop v1 api", additions=50)).tier == "high"
    assert rate(make_item(title="chore: bump version", additions=1, deletions=1)).tier == "low"


def test_releases_are_always_high():
    assert rate(make_item(kind="release", ref="v1.0.0", title="v1.0.0")).tier == "high"
