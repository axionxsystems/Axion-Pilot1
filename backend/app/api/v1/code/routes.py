"""Code runner and improver endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import time
import json
import os

from app.database import get_db
from app.services.sandbox import run_code_in_docker
from app.llm.code_improver import improve_code
from app.auth.dependencies import get_current_user
from app.models.user import User
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/code", tags=["Code"])

# Dedicated workspace root for user-editable/executable code — never the backend
# source tree itself, so a path-traversal bug here can't expose app source/secrets.
_DEFAULT_WORKSPACE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../../workspaces")
)
BASE = os.path.abspath(os.environ.get("CODE_BASE_DIR", _DEFAULT_WORKSPACE))
os.makedirs(BASE, exist_ok=True)


def _resolve_within_base(relative_path: str) -> str:
    """Resolve a user-supplied relative path inside BASE, rejecting any escape."""
    target = os.path.abspath(os.path.join(BASE, relative_path or ""))
    try:
        if os.path.commonpath([BASE, target]) != BASE:
            raise HTTPException(status_code=400, detail="Invalid path")
    except ValueError:
        # commonpath raises ValueError on mismatched drives (Windows) — treat as invalid
        raise HTTPException(status_code=400, detail="Invalid path")
    return target


class ExecuteRequest(BaseModel):
    language: str
    code: str
    timeout: Optional[int] = 30


class ExecuteResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: int


@router.post("/execute", response_model=ExecuteResponse)
async def execute_code(
    req: ExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start = time.time()
    try:
        result = run_code_in_docker(req.language, req.code, timeout=req.timeout)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    elapsed = int((time.time() - start) * 1000)

    record_dir = os.path.join(os.path.dirname(__file__), "../../../exec_results")
    os.makedirs(record_dir, exist_ok=True)
    rec = {
        "user_id": current_user.id,
        "language": req.language,
        "timestamp": int(time.time()),
        "stdout": result.get("stdout"),
        "stderr": result.get("stderr"),
        "exit_code": result.get("exit_code"),
        "execution_time_ms": elapsed,
    }
    try:
        with open(os.path.join(record_dir, f"exec_{int(time.time())}.json"), "w", encoding="utf-8") as fh:
            json.dump(rec, fh)
    except Exception:
        pass

    return ExecuteResponse(
        stdout=result.get("stdout", ""),
        stderr=result.get("stderr", ""),
        exit_code=result.get("exit_code", 1),
        execution_time_ms=elapsed,
    )


class ImproveRequest(BaseModel):
    file_id: str
    current_code: str
    user_request: str


@router.post("/improve")
async def improve(
    req: ImproveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Call LLM based improver
    try:
        updated = await improve_code(req.file_id, req.current_code, req.user_request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"updated_code": updated}


@router.get("/tree")
async def file_tree(
    root: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a minimal file tree for the requested root inside the workspace."""
    start = _resolve_within_base(root)
    if not os.path.isdir(start):
        raise HTTPException(status_code=404, detail="Not found")

    nodes = []
    for entry in os.listdir(start):
        path = os.path.join(start, entry)
        nodes.append({
            "id": entry,
            "name": entry,
            "path": os.path.relpath(path, BASE),
            "isDir": os.path.isdir(path),
        })

    return nodes


@router.get("/file")
async def get_file(
    path: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = _resolve_within_base(path)
    if not os.path.exists(target):
        raise HTTPException(status_code=404, detail="Not found")
    with open(target, "r", encoding="utf-8", errors="replace") as fh:
        content = fh.read()
    return {"content": content}


class SaveFileReq(BaseModel):
    path: str
    content: str


@router.post("/file")
async def save_file(
    req: SaveFileReq,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = _resolve_within_base(req.path)
    # ensure parent exists
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as fh:
        fh.write(req.content)
    return {"saved": True}


@router.get("/preview")
async def preview(
    file: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Render a simple preview for the given file path by executing it and embedding output in HTML."""
    if not file:
        return HTMLResponse(content="<html><body><p>No file specified</p></body></html>")
    target = _resolve_within_base(file)
    if not os.path.exists(target):
        return HTMLResponse(content="<html><body><p>File not found</p></body></html>")

    # Read file and attempt to execute
    with open(target, "r", encoding="utf-8", errors="replace") as fh:
        code = fh.read()

    # Infer language from extension
    ext = os.path.splitext(target)[1].lstrip(".")
    lang = ext or "python"
    result = run_code_in_docker(lang, code, timeout=10)

    html = f"""
    <html>
        <body style='background:#0b1220;color:#e6eef8;font-family:system-ui;padding:16px;'>
            <h3>Preview: {file}</h3>
            <pre style='white-space:pre-wrap;background:#071024;padding:12px;border-radius:8px;color:#d1ffea;'>Stdout:\n{result.get('stdout','')}</pre>
            <pre style='white-space:pre-wrap;background:#240711;padding:12px;border-radius:8px;color:#ffd1d1;'>Stderr:\n{result.get('stderr','')}</pre>
        </body>
    </html>
    """

    return HTMLResponse(content=html)
