"""Simple Docker-backed sandbox runner.

Note: This is a minimal implementation. Docker must be available on the host.
"""
import tempfile
import subprocess
import os
import uuid
from typing import Dict


LANG_IMAGE = {
    "python": "python:3.11-slim",
    "py": "python:3.11-slim",
    "javascript": "node:18-bullseye-slim",
    "js": "node:18-bullseye-slim",
    "typescript": "node:18-bullseye-slim",
}


def _write_temp_file(content: str, suffix: str = "") -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(content)
    return path


def run_code_in_docker(language: str, code: str, timeout: int = 30) -> Dict[str, any]:
    lang = (language or "").lower()
    image = LANG_IMAGE.get(lang, LANG_IMAGE.get("python"))

    fname = f"code_{uuid.uuid4().hex}"
    if lang in ("python", "py"):
        path = _write_temp_file(code, suffix=".py")
        container_cmd = ["python", f"/data/{os.path.basename(path)}"]
    elif lang in ("javascript", "js"):
        path = _write_temp_file(code, suffix=".js")
        container_cmd = ["node", f"/data/{os.path.basename(path)}"]
    elif lang == "typescript":
        path = _write_temp_file(code, suffix=".ts")
        # Run using ts-node if available; fallback to transpile+node (not implemented here)
        container_cmd = ["node", f"/data/{os.path.basename(path)}"]
    else:
        # default to python
        path = _write_temp_file(code, suffix=".py")
        container_cmd = ["python", f"/data/{os.path.basename(path)}"]

    # Run docker CLI with limited privileges
    # Hardened docker options: no network, limited memory/CPU, drop capabilities
    docker_cmd = [
        "docker",
        "run",
        "--rm",
        "--network=none",
        "--pids-limit=64",
        "--memory=256m",
        "--memory-swap=256m",
        "--cpus=0.5",
        "--read-only",
        "--security-opt",
        "no-new-privileges",
        "--cap-drop=ALL",
        "-v",
        f"{os.path.dirname(path)}:/data:ro",
        image,
    ] + container_cmd

    try:
        proc = subprocess.run(docker_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)
        stdout = proc.stdout.decode("utf-8", errors="replace")
        stderr = proc.stderr.decode("utf-8", errors="replace")
        return {"stdout": stdout, "stderr": stderr, "exit_code": proc.returncode}
    except subprocess.TimeoutExpired as e:
        return {"stdout": "", "stderr": "Execution timed out", "exit_code": -1}
    except FileNotFoundError:
        if os.environ.get("ENV", "development") == "production":
            # Never run untrusted code unsandboxed in production.
            raise RuntimeError("Docker is required to execute code but is not available on this host")
        # Docker not available; run locally as fallback (dangerous - dev only, never in production)
        try:
            proc = subprocess.run(container_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)
            stdout = proc.stdout.decode("utf-8", errors="replace")
            stderr = proc.stderr.decode("utf-8", errors="replace")
            return {"stdout": stdout, "stderr": stderr, "exit_code": proc.returncode}
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "exit_code": -2}
