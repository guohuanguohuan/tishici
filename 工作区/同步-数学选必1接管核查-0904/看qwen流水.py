# -*- coding: utf-8 -*-
"""看qwen流水：读 qwen CLI 本地会话日志，纯本地文件操作，不消耗任何 token。

用法：
  python 看qwen流水.py        —— 最新会话末 20 条
  python 看qwen流水.py 50     —— 最新会话末 50 条
  python 看qwen流水.py -f     —— 实时跟随最新会话（Ctrl+C 退出）
  python 看qwen流水.py <会话jsonl路径> [N|-f]  —— 指定会话
"""
import glob
import json
import os
import sys
import time

ROOT = os.path.join(os.path.expanduser("~"), ".qwen", "projects")
CLIP = 300


def newest():
    fs = glob.glob(os.path.join(ROOT, "*", "chats", "*.jsonl"))
    return max(fs, key=os.path.getmtime) if fs else None


def fmt(line):
    try:
        r = json.loads(line)
    except Exception:
        return None
    t = r.get("type")
    if t == "system":
        return None
    out = []
    for p in (r.get("message") or {}).get("parts") or []:
        fc, fr, tx = p.get("functionCall"), p.get("functionResponse"), p.get("text")
        if tx and tx.strip():
            if t == "user":
                tag = "[用户]"
            elif p.get("thought"):
                tag = "[思考]"
            else:
                tag = "[模型]"
            out.append(f"{tag} {tx.strip()[:CLIP]}")
        elif fc:
            args = json.dumps(fc.get("args", {}), ensure_ascii=False)[:CLIP]
            out.append(f"[工具→] {fc.get('name')} {args}")
        elif fr:
            resp = json.dumps(fr.get("response", {}), ensure_ascii=False)[:CLIP]
            out.append(f"[工具回] {fr.get('name')} {resp}")
    return "\n".join(out) if out else None


def show(path, n):
    hits = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            s = fmt(line)
            if s:
                hits.append(s)
    for s in hits[-n:]:
        print(s)
        print("---")


def follow(path):
    print(f"跟随: {path}（Ctrl+C 退出）")
    pos = 0
    cur = path
    while True:
        try:
            new = newest()
            if new and new != cur:
                cur = new
                pos = 0
                print(f"=== 切到更新会话: {cur} ===")
            with open(cur, encoding="utf-8", errors="replace") as f:
                f.seek(0, 2)
                end = f.tell()
                if end > pos:
                    f.seek(pos)
                    for line in f:
                        s = fmt(line)
                        if s:
                            print(s)
                            print("---")
                    pos = f.tell()
        except KeyboardInterrupt:
            return
        except Exception:
            pass
        time.sleep(2)


def main():
    args = sys.argv[1:]
    path = next((a for a in args if a.endswith(".jsonl")), None) or newest()
    if not path:
        sys.exit("未找到任何 qwen 会话日志（~/.qwen/projects/*/chats/*.jsonl）")
    print(f"文件: {path}")
    if "-f" in args:
        follow(path)
    else:
        n = next((int(a) for a in args if a.lstrip("-").isdigit() and a != "-f"), 20)
        show(path, n)


if __name__ == "__main__":
    main()
