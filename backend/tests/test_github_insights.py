"""Tests for the GitHub pattern-mining service (no network — all mocked)."""
from datetime import datetime, timedelta

import pytest


def _fake_repo(name="octo/webapp", stars=12000, license_key="mit", spdx="MIT"):
    return {
        "full_name": name,
        "stargazers_count": stars,
        "default_branch": "main",
        "archived": False,
        "description": "A great example project",
        "license": {"key": license_key, "spdx_id": spdx},
    }


FAKE_PATHS = [
    "README.md",
    "Dockerfile",
    ".env.example",
    ".github/workflows/ci.yml",
    "src/app.py",
    "src/models/user.py",
    "tests/test_app.py",
    "docs/architecture.md",
    "migrations/001_init.py",
]


# ── Digest building ────────────────────────────────────────────────────────────

def test_build_digest_detects_practices():
    from app.services.github_insights import _build_digest

    digest = _build_digest([(_fake_repo(), FAKE_PATHS)])
    assert digest["sources"][0]["name"] == "octo/webapp"
    practices = digest["common_practices"]
    assert "dedicated test suite (tests/ directory)" in practices
    assert "CI pipeline (GitHub Actions)" in practices
    assert "containerized (Dockerfile)" in practices
    assert "documented env config (.env.example)" in practices
    assert "database migrations" in practices
    assert "src/" in digest["common_top_dirs"]


def test_build_digest_majority_rule():
    """Practices only count as 'common' when a majority of repos share them."""
    from app.services.github_insights import _build_digest

    repo_a = (_fake_repo("a/x"), ["tests/test_x.py", "src/x.py"])
    repo_b = (_fake_repo("b/y"), ["tests/test_y.py", "lib/y.py"])
    repo_c = (_fake_repo("c/z"), ["Dockerfile", "z.py"])  # no tests
    digest = _build_digest([repo_a, repo_b, repo_c])

    assert "dedicated test suite (tests/ directory)" in digest["common_practices"]
    # Only 1/3 repos has a Dockerfile → not common
    assert "containerized (Dockerfile)" not in digest["common_practices"]


# ── Prompt formatting ──────────────────────────────────────────────────────────

def test_format_digest_prompt_block():
    from app.services.github_insights import _build_digest, format_digest

    text = format_digest(_build_digest([(_fake_repo(), FAKE_PATHS)]))
    assert "Do NOT copy any code verbatim" in text
    assert "octo/webapp" in text
    assert len(text) <= 1400


def test_format_digest_empty_is_blank():
    from app.services.github_insights import format_digest

    assert format_digest({}) == ""
    assert format_digest({"sources": []}) == ""


# ── Cache behavior ─────────────────────────────────────────────────────────────

def test_get_context_uses_fresh_cache_without_network(db_session, monkeypatch):
    from app.services import github_insights as gi
    from app.models.github_pattern import GitHubPatternCache

    digest = gi._build_digest([(_fake_repo(), FAKE_PATHS)])
    db_session.add(GitHubPatternCache(
        cache_key=gi._normalize_key("flask", "web"),
        digest=digest,
        refreshed_at=datetime.utcnow(),
    ))
    db_session.commit()

    def _boom(*a, **k):
        raise AssertionError("network must not be touched when cache is fresh")

    monkeypatch.setattr(gi, "fetch_patterns", _boom)
    ctx = gi.get_github_context(db_session, "flask", "web")
    assert "octo/webapp" in ctx


def test_get_context_falls_back_to_stale_cache(db_session, monkeypatch):
    from app.services import github_insights as gi
    from app.models.github_pattern import GitHubPatternCache

    digest = gi._build_digest([(_fake_repo("old/repo"), FAKE_PATHS)])
    db_session.add(GitHubPatternCache(
        cache_key=gi._normalize_key("django", "web"),
        digest=digest,
        refreshed_at=datetime.utcnow() - timedelta(days=30),  # stale
    ))
    db_session.commit()

    monkeypatch.setattr(gi, "fetch_patterns", lambda *a, **k: None)  # refresh fails
    ctx = gi.get_github_context(db_session, "django", "web")
    assert "old/repo" in ctx  # stale data still served


def test_get_context_never_raises(db_session, monkeypatch):
    from app.services import github_insights as gi

    monkeypatch.setattr(gi, "fetch_patterns", lambda *a, **k: None)
    assert gi.get_github_context(db_session, "some new stack", "space tech") == ""


# ── Key normalization ──────────────────────────────────────────────────────────

def test_normalize_key_uses_primary_tech():
    from app.services.github_insights import _normalize_key

    assert _normalize_key("Flask, SQLite, Bootstrap", "Web Development") == "flask|web development"
    assert _normalize_key("", "") == "general|general"
