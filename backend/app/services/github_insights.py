"""
GitHub pattern mining — makes generated projects mirror how the best real
open-source projects are engineered.

How it works
------------
1. Search the GitHub API for the most-starred repos matching the user's tech
   stack, keeping only permissively-licensed ones (MIT / Apache-2.0 / BSD).
2. Pull each repo's file tree and distill *structural engineering patterns*:
   directory layout, presence of tests / CI / Docker / lint configs, docs, etc.
3. Cache the digest in the DB for CACHE_TTL_DAYS so generation stays fast and
   we respect GitHub rate limits. A Celery beat task refreshes digests weekly
   for whatever stacks users actually generate — the system keeps "learning"
   with zero manual work.
4. The digest is rendered into a compact prompt block that generation stages
   use as reference. We only ever transfer *patterns and attribution*, never
   copied source code, which keeps this clean legally and ethically.

All public functions are best-effort: on any failure they return cached data
or empty context — generation must never break because GitHub is down.
"""
import logging
import re
from collections import Counter
from datetime import datetime, timedelta
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.github_pattern import GitHubPatternCache

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
PERMISSIVE_LICENSES = {"mit", "apache-2.0", "bsd-2-clause", "bsd-3-clause", "isc", "unlicense"}
CACHE_TTL_DAYS = 7
TOP_REPOS_PER_KEY = 3
REQUEST_TIMEOUT = 8.0

# Signals we look for in repo file trees → human-readable practice labels.
_PRACTICE_SIGNALS = [
    (re.compile(r"(^|/)tests?/", re.I), "dedicated test suite (tests/ directory)"),
    (re.compile(r"^\.github/workflows/", re.I), "CI pipeline (GitHub Actions)"),
    (re.compile(r"(^|/)Dockerfile$"), "containerized (Dockerfile)"),
    (re.compile(r"(^|/)docker-compose\.ya?ml$", re.I), "docker-compose for local dev"),
    (re.compile(r"(^|/)\.env\.example$", re.I), "documented env config (.env.example)"),
    (re.compile(r"(^|/)(\.eslintrc|\.ruff\.toml|ruff\.toml|\.flake8|\.pylintrc|\.prettierrc)", re.I), "linting/formatting config"),
    (re.compile(r"(^|/)(tsconfig\.json|mypy\.ini|pyrightconfig\.json)$", re.I), "static type checking"),
    (re.compile(r"(^|/)docs?/", re.I), "docs/ directory"),
    (re.compile(r"(^|/)(CONTRIBUTING|CODE_OF_CONDUCT)\.md$", re.I), "contributor guidelines"),
    (re.compile(r"(^|/)(Makefile|justfile|taskfile\.ya?ml)$", re.I), "task runner (Makefile/just)"),
    (re.compile(r"(^|/)\.pre-commit-config\.ya?ml$", re.I), "pre-commit hooks"),
    (re.compile(r"(^|/)(migrations|alembic)/", re.I), "database migrations"),
]


def _normalize_key(tech_stack: str, domain: str) -> str:
    tech = (tech_stack or "general").strip().lower()
    dom = (domain or "general").strip().lower()
    # Primary technology = first comma/space-separated token, keeps keys stable
    primary = re.split(r"[,/+&]| and ", tech)[0].strip() or "general"
    return f"{primary}|{dom}"[:200]


def _headers() -> dict:
    h = {"Accept": "application/vnd.github+json", "User-Agent": "axion-pilot-pattern-miner"}
    if settings.GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
    return h


def _is_relevant(repo: dict, tech: str) -> bool:
    """Require the primary tech term to actually appear in the repo's identity,
    keeping junk results (e.g. dotfiles repos) out of the study set."""
    term = tech.split()[0].lower() if tech else ""
    if not term:
        return True
    haystack = " ".join([
        repo.get("full_name", ""),
        repo.get("description") or "",
        " ".join(repo.get("topics", []) or []),
        repo.get("language") or "",
    ]).lower()
    return term in haystack


def _search_top_repos(client: httpx.Client, tech: str, domain: str) -> list[dict]:
    """Top-starred repos for the stack, filtered to permissive licenses client-side."""
    query = f"{tech} {domain}".strip()
    resp = client.get(
        f"{GITHUB_API}/search/repositories",
        params={"q": f"{query} stars:>500", "sort": "stars", "order": "desc", "per_page": 20},
        headers=_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    items = resp.json().get("items", [])
    picked = []
    for repo in items:
        lic = ((repo.get("license") or {}).get("key") or "").lower()
        if lic in PERMISSIVE_LICENSES and not repo.get("archived") and _is_relevant(repo, tech):
            picked.append(repo)
        if len(picked) >= TOP_REPOS_PER_KEY:
            break
    return picked


def _fetch_tree_paths(client: httpx.Client, repo: dict) -> list[str]:
    """File paths of the repo's default branch (single recursive trees call)."""
    branch = repo.get("default_branch", "main")
    resp = client.get(
        f"{GITHUB_API}/repos/{repo['full_name']}/git/trees/{branch}",
        params={"recursive": "1"},
        headers=_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return [t.get("path", "") for t in resp.json().get("tree", [])][:4000]


def _build_digest(repos_with_paths: list[tuple[dict, list[str]]]) -> dict:
    """Distill repos into a compact structural-pattern digest (no source code)."""
    sources, practice_counter, top_dir_counter = [], Counter(), Counter()

    for repo, paths in repos_with_paths:
        sources.append({
            "name": repo["full_name"],
            "stars": repo.get("stargazers_count", 0),
            "license": (repo.get("license") or {}).get("spdx_id", ""),
            "description": (repo.get("description") or "")[:140],
        })
        seen_practices = set()
        for path in paths:
            for pattern, label in _PRACTICE_SIGNALS:
                if label not in seen_practices and pattern.search(path):
                    seen_practices.add(label)
        # Count each top-level directory once per repo
        for d in {p.split("/", 1)[0] + "/" for p in paths if "/" in p}:
            top_dir_counter[d] += 1
        practice_counter.update(seen_practices)

    n = max(len(repos_with_paths), 1)
    return {
        "sources": sources,
        # Practices adopted by the majority of the top repos
        "common_practices": [lbl for lbl, c in practice_counter.most_common() if c >= (n + 1) // 2],
        "common_top_dirs": [d for d, c in top_dir_counter.most_common(8) if c >= (n + 1) // 2],
        "mined_at": datetime.utcnow().isoformat(),
    }


def fetch_patterns(tech_stack: str, domain: str) -> Optional[dict]:
    """Network path: mine GitHub and return a digest, or None on any failure."""
    key = _normalize_key(tech_stack, domain)
    tech = key.split("|", 1)[0]
    try:
        with httpx.Client() as client:
            repos = _search_top_repos(client, tech, domain or "")
            if not repos:
                logger.info("github_insights: no permissive repos found for %r", key)
                return None
            repos_with_paths = []
            for repo in repos:
                try:
                    repos_with_paths.append((repo, _fetch_tree_paths(client, repo)))
                except Exception as e:  # tree fetch can 409 on empty repos etc.
                    logger.debug("github_insights: tree fetch failed for %s: %s", repo["full_name"], e)
            if not repos_with_paths:
                return None
            digest = _build_digest(repos_with_paths)
            logger.info("github_insights: mined %d repos for %r", len(repos_with_paths), key)
            return digest
    except Exception as e:
        logger.warning("github_insights: mining failed for %r: %s", key, e)
        return None


def refresh_patterns(db: Session, tech_stack: str, domain: str) -> Optional[dict]:
    """Mine GitHub and upsert the cache row. Returns the digest (or None)."""
    key = _normalize_key(tech_stack, domain)
    digest = fetch_patterns(tech_stack, domain)
    if digest is None:
        return None
    row = db.query(GitHubPatternCache).filter(GitHubPatternCache.cache_key == key).first()
    if row is None:
        row = GitHubPatternCache(cache_key=key)
        db.add(row)
    row.digest = digest
    row.refreshed_at = datetime.utcnow()
    db.commit()
    return digest


def get_github_context(db: Session, tech_stack: str, domain: str) -> str:
    """Cache-first prompt context. Never raises; returns "" when nothing usable."""
    key = _normalize_key(tech_stack, domain)
    try:
        row = db.query(GitHubPatternCache).filter(GitHubPatternCache.cache_key == key).first()
        fresh_cutoff = datetime.utcnow() - timedelta(days=CACHE_TTL_DAYS)
        if row and row.refreshed_at and row.refreshed_at >= fresh_cutoff:
            return format_digest(row.digest)
        # Stale or missing → try one refresh, fall back to stale data if it fails
        digest = refresh_patterns(db, tech_stack, domain)
        if digest:
            return format_digest(digest)
        if row and row.digest:
            return format_digest(row.digest)
        return ""
    except Exception as e:
        logger.warning("github_insights: context lookup failed for %r: %s", key, e)
        return ""


def format_digest(digest: dict) -> str:
    """Render a digest as a compact prompt block (≈ ≤1200 chars)."""
    if not digest or not digest.get("sources"):
        return ""
    lines = [
        "REFERENCE PATTERNS — mined from top permissively-licensed open-source projects.",
        "Emulate their engineering standards and structure. Do NOT copy any code verbatim.",
        "Studied projects:",
    ]
    for s in digest["sources"][:TOP_REPOS_PER_KEY]:
        lines.append(f"- {s['name']} ({s['stars']:,}★, {s.get('license', '?')}): {s.get('description', '')}")
    if digest.get("common_top_dirs"):
        lines.append("Typical directory layout: " + ", ".join(digest["common_top_dirs"]))
    if digest.get("common_practices"):
        lines.append("Engineering practices they share — include equivalents in your output:")
        for p in digest["common_practices"][:8]:
            lines.append(f"- {p}")
    return "\n".join(lines)[:1400]
