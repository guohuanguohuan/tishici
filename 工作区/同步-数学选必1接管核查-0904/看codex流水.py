# -*- coding: utf-8 -*-
"""codex CLI 会话流水随读器（纯本地只读，零token消耗）。
用法：
  python 看codex流水.py            # 显示最新会话最后20条可读事件
  python 看codex流水.py -f         # 跟随模式（Ctrl+C退出）——实时看正在跑的会话
  python 看codex流水.py <文件>     # 指定某个 rollout jsonl
"""
import glob
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.expanduser(r'~\.codex\sessions')


def newest():
    files = glob.glob(os.path.join(ROOT, '**', '*.jsonl'), recursive=True)
    return max(files, key=os.path.getmtime) if files else None


def show(line):
    try:
        d = json.loads(line)
    except Exception:
        return None
    p = d.get('payload', d)
    t = p.get('type', '')
    if t == 'function_call':
        return f'[调用工具] {p.get("name", "?")}  {str(p.get("arguments", ""))[:200]}'
    if t == 'custom_tool_call':
        return f'[执行] {str(p.get("input", ""))[:250]}'
    if t in ('function_call_output', 'custom_tool_call_output'):
        out = p.get('output', '')
        if isinstance(out, list):
            out = ' '.join(str(x.get('text', '')) for x in out if isinstance(x, dict))
        return f'[输出] {str(out)[:250]}'
    if t == 'message' and p.get('role') == 'assistant':
        c = p.get('content', [])
        txt = ' '.join(x.get('text', '') for x in c if isinstance(x, dict))
        return f'[消息] {txt[:300]}' if txt.strip() else None
    if t == 'agent_message':
        return f'[消息] {str(p.get("message", ""))[:300]}'
    return None


def main():
    args = [a for a in sys.argv[1:] if a != '-f']
    follow = '-f' in sys.argv
    path = args[0] if args else newest()
    if not path:
        print('未找到 rollout 文件')
        return
    print('文件:', path)
    if not follow:
        lines = open(path, encoding='utf-8').read().splitlines()
        shown = [s for s in (show(ln) for ln in lines) if s]
        for s in shown[-20:]:
            print(s)
        print(f'（共{len(lines)}行，可读事件{len(shown)}条；-f 可实时跟随）')
        return
    with open(path, encoding='utf-8') as f:
        f.seek(0, os.SEEK_END)
        while True:
            ln = f.readline()
            if not ln:
                time.sleep(1)
                continue
            s = show(ln)
            if s:
                print(s, flush=True)


if __name__ == '__main__':
    main()
