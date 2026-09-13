# -*- coding: utf-8 -*-
"""跑全程.py — M3 S2 波1 补位臂3·三片门谱全项终检复跑，读数落盘 门谱记录-补位臂3-0914.txt。
只读跑门（值快照门写底稿＝本目录过程件），不做任何改制。
"""
import hashlib
import io
import json
import os
import re
import subprocess
import sys

import fitz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 片规 import piece

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
M3 = 'C:/提示词/工作区/M3-第2章量产0913'
TOOL = 'C:/提示词/工具'
REC = os.path.join(HERE, '门谱记录-补位臂3-0914.txt')

out = []
def say(s=''):
    out.append(s)
    print(s)

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

def run(cmd, cwd=None):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                       errors='replace', cwd=cwd)
    return (r.stdout or '') + (r.stderr or '')

say('M3 成卷轮 S2 波1 补位臂3·门谱全项终检复跑记录｜2026-09-14')
say('＝'.join([''] * 40))
allred = []
for k in ('09', '14', '15'):
    p = piece(k)
    pdir = p['piece']
    say(f'◆ 课时{k} {p["dir"]}')
    say(f'  sty锁 md5={md5(os.path.join(pdir, "qp-m3.sty"))} '
        f'{"合" if md5(os.path.join(pdir, "qp-m3.sty")) == p["sty_md5"] else "漂!"}')
    for t in ('false', 'true'):
        log = open(os.path.join(pdir, f'main-{t}.log'), encoding='utf-8', errors='replace').read()
        say(f'  编译 main-{t}（×2 遍后读数）: 错{log.count(chr(10) + "! ")} 溢{log.count("Overfull")} '
            f'under{log.count("Underfull")} 缺字{log.count("Missing character")} '
            f'ANSKEY{log.count("M3-ANSKEY")}')
    docr = {}
    for t in ('true', 'false'):
        d = fitz.open(os.path.join(pdir, f'main-{t}.pdf'))
        docr[t] = len(d)
        d.close()
    say(f'  页数双档: true={docr["true"]} false={docr["false"]}（false≤true '
        f'{"合" if docr["false"] <= docr["true"] else "违!"}）')
    for gate in ('门-守恒对号.py', '门-值快照键型判模.py', '门-回流.py'):
        o = run([sys.executable, os.path.join(HERE, gate), k])
        tail = [l for l in o.strip().split('\n') if l.strip()]
        verdict = tail[-1] if tail else '(无输出)'
        reds = [l for l in o.split('\n') if '[红]' in l]
        say(f'  {gate}: {verdict}')
        for r in reds:
            say(f'    {r}')
            allred.append(f'{k}/{gate}: {r}')
    o = run([sys.executable, os.path.join(TOOL, '键账对平门.py'),
             '--piece', f'片={pdir}/main.tex',
             '--ledger', f'台账={os.path.join(pdir, f"值台账-课时{k}.json")}',
             '--expect', f'manifest键序={os.path.join(HERE, f"键表-课时{k}.txt")}'])
    verdict = [l for l in o.split('\n') if 'PASS' in l or 'FAIL' in l]
    say(f'  键账对平门: {verdict[-1] if verdict else "(无输出)"}')
    if any('FAIL' in v for v in verdict):
        allred.append(f'{k}/对平门')
    for mode in ('zero-fp', 'strict'):
        o = run([sys.executable, os.path.join(TOOL, 'makebox槽宽门.py'), pdir, '--mode', mode])
        verdict = [l for l in o.split('\n') if 'PASS' in l or 'FAIL' in l]
        say(f'  makebox槽宽门 --mode {mode}: {verdict[-1] if verdict else "(无输出)"}')
        if any('FAIL' in v for v in verdict):
            allred.append(f'{k}/槽宽门{mode}')
    o = run(['rg', '-c', '\\[a-zA-Z]+\\p{Han}', os.path.join(pdir, 'main.tex')])
    say(f'  CJK 审计: {"零命中" if not o.strip() else "命中!" + o.strip()}')
    if o.strip():
        allred.append(f'{k}/CJK')
    led = json.load(open(os.path.join(pdir, f'值台账-课时{k}.json'), encoding='utf-8'))
    ok1 = led['指纹']['main.tex.md5'] == md5(os.path.join(pdir, 'main.tex'))
    ok2 = led['指纹']['main-true.pdf.md5'] == md5(os.path.join(pdir, 'main-true.pdf'))
    ok3 = led['指纹']['main-false.pdf.md5'] == md5(os.path.join(pdir, 'main-false.pdf'))
    say(f'  台账指纹↔盘上: tex{"合" if ok1 else "漂!"} true{"合" if ok2 else "漂!"} '
        f'false{"合" if ok3 else "漂!"}｜items {len(led["items"])} 键')
    if not (ok1 and ok2 and ok3):
        allred.append(f'{k}/指纹')
    say()

say('＝'.join([''] * 40))
say('终检判定：' + ('三片门谱全项全绿' if not allred else f'红 {len(allred)} 项：{allred}'))

open(REC, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('记录 →', REC)
sys.exit(0 if not allred else 1)
