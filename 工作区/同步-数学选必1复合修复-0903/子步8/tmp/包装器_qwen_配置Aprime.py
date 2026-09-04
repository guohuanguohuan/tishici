# -*- coding: utf-8 -*-
# qwen臂 复测包装器：跑锚定脚本（配置A′），180s护栏；运行记录落tmp新名；WINWORD按PID差分快照（不全局杀）
import json, os, subprocess, sys, time

SRC = r"C:\提示词\工具\节页码定位.py"
CFG = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步8\tmp\_输入_配置A_全同副本.json"
REC = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步7\盖章记录_子步7.md"
OUT = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步8\tmp\复测_配置Aprime.json"
RUNLOG = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步8\tmp\运行记录_复测_配置Aprime_qwen.json"
ERRLOG = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步8\tmp\复测_配置Aprime_stderr_qwen.txt"
GUARD = 180
PROTECTED = {28012, 26168, 5988, 13320, 10308}  # 用户WINWORD实例，禁动

def winword_pids():
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq WINWORD.EXE", "/FO", "CSV", "/NH"],
                             capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return set()
    pids = set()
    for line in out.splitlines():
        parts = [x.strip('"') for x in line.split('","')]
        if len(parts) >= 2 and parts[0].upper() == "WINWORD.EXE":
            try:
                pids.add(int(parts[1]))
            except ValueError:
                pass
    return pids

cmd = [sys.executable, SRC, "@" + CFG, "--record", REC, "--json"]
before = winword_pids()
t0 = time.time()
timed_out = False
stdout_b = b""
stderr_b = b""
code = None
try:
    p = subprocess.run(cmd, capture_output=True, timeout=GUARD)
    stdout_b, stderr_b, code = p.stdout, p.stderr, p.returncode
except subprocess.TimeoutExpired as e:
    timed_out = True
    code = None
    stdout_b = e.stdout if isinstance(e.stdout, (bytes, bytearray)) else b""
    stderr_b = e.stderr if isinstance(e.stderr, (bytes, bytearray)) else b""

after = winword_pids()
mine = sorted(after - before - PROTECTED)
elapsed = round(time.time() - t0, 2)

with open(OUT, "wb") as f:
    f.write(stdout_b)
with open(ERRLOG, "wb") as f:
    f.write(stderr_b)

record = {
    "arm": "qwen",
    "configuration": "Aprime",
    "command": cmd,
    "guard_seconds": GUARD,
    "attempt": int(sys.argv[1]) if len(sys.argv) > 1 else 1,
    "started_epoch": t0,
    "elapsed_seconds": elapsed,
    "timed_out": timed_out,
    "source_exit_code": code,
    "stdout_bytes": len(stdout_b),
    "stderr_bytes": len(stderr_b),
    "output_json": OUT,
    "stderr_file": ERRLOG,
    "winword_pids_before": sorted(before),
    "winword_pids_after": sorted(after),
    "winword_unexpected_residue_pids": mine,
}
with open(RUNLOG, "w", encoding="utf-8") as f:
    json.dump(record, f, ensure_ascii=False, indent=1)
    f.write("\n")

print(json.dumps(record, ensure_ascii=False, indent=1))
sys.exit(124 if timed_out else (code if code is not None else 1))
