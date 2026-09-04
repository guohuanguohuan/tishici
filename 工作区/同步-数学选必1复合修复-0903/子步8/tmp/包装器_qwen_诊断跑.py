# -*- coding: utf-8 -*-
# qwen臂 第二跑包装器：诊断变体对配置A（原件+清单1镜像），300s总护栏，运行记录落tmp新名；
# stdout逐行到达时刻记录（供逐件开卷耗时表与挂点定位）；WINWORD按PID差分只清自己，绝不动受保护五实例、无全局杀。
import io, json, os, queue, subprocess, sys, threading, time

TMP = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步8\tmp"
SRC = os.path.join(TMP, "诊断变体_节页码定位.py")
CFG = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步8\复测_补签_codex\_输入_配置A.json"
REC = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步7\盖章记录_子步7.md"
LOG = os.path.join(TMP, "复测_诊断跑_日志.txt")
OUT = os.path.join(TMP, "复测_诊断跑_输出.json")
ERRLOG = os.path.join(TMP, "复测_诊断跑_stderr_qwen.txt")
RUNLOG = os.path.join(TMP, "运行记录_诊断跑_qwen.json")
GUARD = 300
PROTECTED = {28012, 26168, 5988, 13320, 10308}  # 用户WINWORD实例，禁动


def winword_pids():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq WINWORD.EXE", "/FO", "CSV", "/NH"],
                         capture_output=True, text=True, timeout=20).stdout
    pids = set()
    for line in out.splitlines():
        parts = [x.strip('"') for x in line.split('","')]
        if len(parts) >= 2 and parts[0].upper() == "WINWORD.EXE":
            try:
                pids.add(int(parts[1]))
            except ValueError:
                pass
    return pids


def clock(t):
    return time.strftime("%H:%M:%S", time.localtime(t)) + ".%03d" % int((t % 1) * 1000)


def main():
    attempt = sys.argv[1] if len(sys.argv) > 1 else "1"
    cmd = [sys.executable, SRC, "@" + CFG, "--record", REC, "--json"]
    before = winword_pids()
    t0 = time.time()
    q = queue.Queue()

    def reader(stream):
        for line in iter(stream.readline, ''):
            q.put((time.time(), line.rstrip('\n')))
        stream.close()

    errfh = open(ERRLOG, 'wb')
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=errfh)
    th = threading.Thread(target=reader, args=(io.TextIOWrapper(proc.stdout, encoding='utf-8', errors='replace'),),
                          daemon=True)
    th.start()
    timed_out = False
    code = None
    logfh = open(LOG, 'w', encoding='utf-8')
    payload, diag = [], []
    while True:
        remain = t0 + GUARD - time.time()
        if remain <= 0:
            timed_out = True
            break
        try:
            ts, line = q.get(timeout=min(remain, 2.0))
        except queue.Empty:
            if proc.poll() is not None and q.empty():
                break
            continue
        rec = "[%s +%.2fs] %s" % (clock(ts), ts - t0, line)
        logfh.write(rec + "\n")
        logfh.flush()
        if line.startswith('[diag]'):
            diag.append((ts, line))
        else:
            payload.append(line)
        if proc.poll() is not None and q.empty() and th.is_alive() is False:
            break
    if not timed_out:
        th.join(timeout=5)
        while not q.empty():  # 收尾兜底：线程结束后队列残余行
            ts, line = q.get_nowait()
            logfh.write("[%s +%.2fs] %s\n" % (clock(ts), ts - t0, line))
            (diag if line.startswith('[diag]') else payload).append((ts, line) if line.startswith('[diag]') else line)
    try:
        code = proc.wait(timeout=5)
    except Exception:
        proc.kill()
        code = proc.returncode
    if timed_out:
        proc.kill()
        code = None
        time.sleep(0.5)  # 冲刷：kill前最后一批已到达行落日志
        while not q.empty():
            ts, line = q.get_nowait()
            logfh.write("[%s +%.2fs] %s\n" % (clock(ts), ts - t0, line))
            (diag if line.startswith('[diag]') else payload).append((ts, line) if line.startswith('[diag]') else line)
    logfh.close()
    errfh.close()
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write("\n".join(payload) + ("\n" if payload else ""))

    cleaned = []
    mid = winword_pids()
    mine = sorted(mid - before - PROTECTED)
    time.sleep(3)  # 正常路径下仿A′跑后复查：自建Word自行退出者不杀
    late = winword_pids()
    still = [p for p in mine if p in late]
    for p in still:
        subprocess.run(["taskkill", "/F", "/PID", str(p)], capture_output=True)
        cleaned.append(p)

    items, last_marker = {}, None
    for ts, line in diag:
        _, mark, name = line.split(' ', 2)
        it = items.setdefault(name, {})
        it[mark] = ts
        last_marker = (mark, name, ts)
    per = {}
    for name, it in items.items():
        per[name] = {
            "open_start": clock(it['open_start']) if 'open_start' in it else None,
            "open_done": clock(it['open_done']) if 'open_done' in it else None,
            "scan_done": clock(it['scan_done']) if 'scan_done' in it else None,
            "open_s": round(it['open_done'] - it['open_start'], 2) if 'open_done' in it and 'open_start' in it else None,
            "scan_s": round(it['scan_done'] - it['open_done'], 2) if 'scan_done' in it and 'open_done' in it else None,
            "total_s": round(it['scan_done'] - it['open_start'], 2) if 'scan_done' in it and 'open_start' in it else None,
        }
    hanging = None
    if last_marker and last_marker[0] != 'scan_done':
        hanging = {"mark": last_marker[0], "name": last_marker[1], "at": clock(last_marker[2])}
    record = {
        "arm": "qwen", "run": "diag-on-A", "attempt": attempt, "command": cmd,
        "guard_seconds": GUARD, "started": clock(t0), "elapsed_seconds": round(time.time() - t0, 2),
        "timed_out": timed_out, "source_exit_code": code,
        "diag_lines": len(diag), "payload_lines": len(payload),
        "per_item": per, "hanging_item": hanging,
        "winword_pids_before": sorted(before), "winword_pids_after": sorted(mid),
        "winword_mine_after_diff": mine, "winword_still_alive_killed": cleaned,
        "log_file": LOG, "output_file": OUT, "stderr_file": ERRLOG,
    }
    with open(RUNLOG, 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(json.dumps(record, ensure_ascii=False, indent=1))
    sys.exit(124 if timed_out else (code if code is not None else 1))


if __name__ == '__main__':
    main()
