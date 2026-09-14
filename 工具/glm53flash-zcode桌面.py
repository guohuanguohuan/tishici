#!/usr/bin/env python
# -*- coding: utf-8 -*-
# GLM-5.3-Flash 专用子智能体·桌面可见通道(2026-09-14 用户令:glm 只能经 ZCode 执行)
# 机制:向 ZCode 桌面端任务索引库插入一次性定时任务(automations 表),桌面端 cron 调度器
#       每 20s 轮询认领 → 任务实时出现在 ZCode 桌面端并执行,回执落 rollout jsonl。
# 用法:
#   python 工具/glm53flash-zcode桌面.py dispatch "任务书" ["标题"]   # 仅派发
#   python 工具/glm53flash-zcode桌面.py run "任务书" ["标题"]        # 派发并等回执(默认)
#   python 工具/glm53flash-zcode桌面.py wait <automation_id>        # 等回执
# 钉死: model=builtin:zai-coding-plan/GLM-5.3-Flash, thought_level=max, mode=yolo(完全访问)
import sqlite3, sys, time, uuid, json, glob, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DB = r"C:\Users\28120\.zcode\v2\tasks-index.sqlite"
WS = "C:\\提示词"
MODEL = "builtin:zai-coding-plan/GLM-5.3-Flash"
COLS = ["automation_id","title","cron_expr","prompt","model","provider",
        "workspace_key","workspace_path","workspace_identity","target_task_id","bot_delivery_target","location_kind",
        "recurring","max_runs","end_at","schedule_rule","schedule_edited_by_user",
        "run_count","scheduled_run_count","enabled","lifecycle_status",
        "next_run_at","last_run_at","running","claimed_at",
        "dispatch_status","dispatch_attempts","retry_at","last_error",
        "mode","thought_level","created_at","updated_at"]

def dispatch(prompt, title):
    now = int(time.time() * 1000)
    aid = "automation-" + uuid.uuid4().hex[:12]
    vals = [aid, title, "* * * * *", prompt, MODEL, None,
            WS, WS, None, None, None, "local",
            0, 1, None, None, 0,
            0, 0, 1, "active",
            now + 5000, None, 0, None,
            "idle", 0, None, None,
            "yolo", "max", now, now]
    db = sqlite3.connect(DB, timeout=15)
    db.execute(f"INSERT INTO automations ({','.join(COLS)}) VALUES ({','.join('?'*len(vals))})", vals)
    db.commit(); db.close()
    return aid

def final_reply(session_id):
    hits = glob.glob(rf"C:\Users\28120\.zcode\cli\rollout\model-io-{session_id}.jsonl")
    if not hits:
        return None
    text = None
    for line in open(hits[0], encoding="utf-8", errors="replace"):
        try:
            t = (json.loads(line).get("response") or {}).get("text")
            if t: text = t
        except Exception:
            pass
    return text

def wait_result(aid, timeout_s=1800):
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        db = sqlite3.connect(rf"file:{DB}?mode=ro", uri=True, timeout=10)
        row = db.execute("SELECT outcome, session_id, error FROM automation_runs WHERE automation_id=? ORDER BY created_at DESC LIMIT 1", (aid,)).fetchone()
        db.close()
        if row and row[0] in ("succeeded", "failed", "cancelled"):
            outcome, sid, err = row
            reply = final_reply(sid) if sid else None
            return outcome, sid, err, reply
        time.sleep(5)
    return "timeout", None, None, None

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "dispatch":
        prompt = sys.argv[2]; title = sys.argv[3] if len(sys.argv) > 3 else prompt[:24]
        print("automation_id:", dispatch(prompt, title), flush=True)
    elif cmd in ("run", "wait"):
        if cmd == "run":
            prompt = sys.argv[2]; title = sys.argv[3] if len(sys.argv) > 3 else prompt[:24]
            aid = dispatch(prompt, title)
            print("automation_id:", aid, flush=True)
        else:
            aid = sys.argv[2]
        outcome, sid, err, reply = wait_result(aid)
        print("outcome:", outcome, "| session:", sid, flush=True)
        if err: print("error:", err, flush=True)
        if reply: print("=== 回执 ==="); print(reply)
    else:
        sys.exit("未知子命令: " + cmd)
