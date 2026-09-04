# -*- coding: utf-8 -*-
"""Run the anchored source once with a bounded wall-clock guard.

This wrapper does not modify the source, input configurations, or documents.
It writes only run artifacts in this directory.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = Path(r"C:\提示词\工具\节页码定位.py")
RECORD = Path(r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步7\盖章记录_子步7.md")
EXPECTED_SHA = "844d244a3cb91d5ca8e7c2c17e35963d293aeff623478f76610f39e651bcde85"
TIMEOUT_SECONDS = 180


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"A", "B"}:
        print("usage: python __run_source.py A|B", file=sys.stderr)
        return 2
    name = sys.argv[1]
    cfg = HERE / "_输入_配置A.json" if name == "A" else HERE.parent.parent / "子步7" / "parts_mirror.json"
    cfg = cfg.resolve()
    out_path = HERE / f"复测_配置{name}.json"
    err_path = HERE / f"复测_配置{name}.err"
    run_log = HERE / f"__运行记录_{name}.json"

    source_hash = sha256(SOURCE)
    if source_hash != EXPECTED_SHA:
        record = {
            "configuration": name,
            "run_status": "blocked_source_sha_mismatch",
            "source": str(SOURCE),
            "source_sha256": source_hash,
            "expected_sha256": EXPECTED_SHA,
        }
        out_path.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        err_path.write_text("source sha256 mismatch; COM not started\n", encoding="utf-8")
        run_log.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        return 3

    cmd = [sys.executable, str(SOURCE), "@" + str(cfg), "--record", str(RECORD), "--json"]
    started = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        timed_out = True
        proc.kill()
        stdout, stderr = proc.communicate()
        stderr += f"\nwrapper: timeout after {TIMEOUT_SECONDS}s; source process killed; no global WINWORD action\n".encode()

    # Preserve the source's JSON stdout exactly on success. On failure, retain
    # a structured record instead of presenting empty output as a measurement.
    if not timed_out and proc.returncode == 0:
        try:
            payload = json.loads(stdout.decode("utf-8-sig"))
        except Exception as exc:
            payload = {
                "run_status": "failed_invalid_json_stdout",
                "parse_error": repr(exc),
                "source_stdout": stdout.decode("utf-8", errors="replace"),
            }
            proc_return = 1
        else:
            proc_return = proc.returncode
            out_path.write_bytes(stdout)
    else:
        proc_return = 124 if timed_out else proc.returncode
        payload = {
            "run_status": "timeout" if timed_out else "source_failed",
            "source": str(SOURCE),
            "source_sha256": source_hash,
            "configuration": name,
            "source_exit_code": proc.returncode,
            "source_stdout_bytes": len(stdout),
            "source_stderr": stderr.decode("utf-8-sig", errors="replace"),
        }

    if not (not timed_out and proc.returncode == 0 and out_path.exists()):
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    err_path.write_bytes(stderr)
    log = {
        "configuration": name,
        "source": str(SOURCE),
        "source_sha256": source_hash,
        "config": str(cfg),
        "record": str(RECORD),
        "command": cmd,
        "started_epoch": started,
        "elapsed_seconds": round(time.time() - started, 3),
        "timeout_seconds": TIMEOUT_SECONDS,
        "timed_out": timed_out,
        "source_exit_code": proc.returncode,
        "reported_exit_code": proc_return,
        "stdout_bytes": len(stdout),
        "stderr_bytes": len(stderr),
        "output_json": str(out_path),
        "stderr_file": str(err_path),
    }
    run_log.write_text(json.dumps(log, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(log, ensure_ascii=False))
    return proc_return


if __name__ == "__main__":
    raise SystemExit(main())
