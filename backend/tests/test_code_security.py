"""
Security tests for the code editor/runner endpoints.

These guard the two properties that were previously broken:
  1. Every /api/v1/code/* route requires authentication.
  2. Path parameters cannot escape the sandbox workspace directory.
"""
import pytest


CODE_ENDPOINTS = [
    ("post", "/api/v1/code/execute", {"language": "python", "code": "print(1)"}),
    ("post", "/api/v1/code/improve", {"file_id": "a", "current_code": "x", "user_request": "y"}),
    ("get", "/api/v1/code/tree", None),
    ("get", "/api/v1/code/file?path=x.py", None),
    ("post", "/api/v1/code/file", {"path": "x.py", "content": "x"}),
    ("get", "/api/v1/code/preview?file=x.py", None),
]


@pytest.mark.parametrize("method,url,body", CODE_ENDPOINTS)
def test_code_endpoints_require_auth(client, method, url, body):
    resp = getattr(client, method)(url, json=body) if body else getattr(client, method)(url)
    assert resp.status_code == 401, f"{method.upper()} {url} should require auth, got {resp.status_code}"


def test_resolve_within_base_rejects_traversal():
    """The path resolver must reject any path that escapes the workspace root."""
    from app.api.v1.code.routes import _resolve_within_base
    from fastapi import HTTPException

    for evil in ["../secrets.txt", "../../etc/passwd", "foo/../../../etc/passwd"]:
        with pytest.raises(HTTPException) as exc:
            _resolve_within_base(evil)
        assert exc.value.status_code == 400


def test_resolve_within_base_allows_inside():
    """A normal relative path inside the workspace resolves without error."""
    from app.api.v1.code.routes import _resolve_within_base, BASE
    import os

    resolved = _resolve_within_base("project/app.py")
    assert os.path.commonpath([BASE, resolved]) == BASE
