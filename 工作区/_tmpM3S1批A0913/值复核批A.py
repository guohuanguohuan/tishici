# -*- coding: utf-8 -*-
r"""值复核批A.py —— 答案侧值 ↔ 定稿【答案】栏逐键复核（防转录滑差；仅比对，不生成值）。

规则：与 首批 值复核.py 同规——答案侧 `值：` 行与定稿件【答案】行去首尾空白后逐键全等。
批A 特情：05 空号席/占位行无【答案】行（跳过）；定稿【答案】行出现序＝题面库键序
（导学→练习实席→拓展，两序同步跳空号席）。
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', 'M3-第2章量产0913'))
TMUB = os.path.join(ROOT, '成卷', '题面库')
DING = os.path.join(ROOT, '定稿')

SLICES = {
    '课时01': ('坐标法', '批A-课时01-坐标法.md'),
    '课时02': ('倾斜角与斜率', '批A-课时02-倾斜角与斜率.md'),
    '课时03': ('方向向量与法向量', '批A-课时03-方向向量与法向量.md'),
    '课时04': ('点斜式与斜截式', '批A-课时04-点斜式与斜截式.md'),
    '课时05': ('两点式与一般式', '批A-课时05-两点式与一般式.md'),
}


def qkeys(path):
    ks = []
    for ln in open(path, encoding='utf-8').read().splitlines():
        if ln.startswith('### '):
            ks.append(ln[4:].split('｜')[0].strip())
    return ks


def avalues(path):
    vals, cur = {}, None
    for ln in open(path, encoding='utf-8').read().splitlines():
        m = re.match(r'^% ans:(\S+)\s*$', ln)
        if m:
            cur = m.group(1)
        elif cur and ln.startswith('值：'):
            vals[cur] = ln[2:].strip()
            cur = None
    return vals


bad = 0
total = 0
for name, (title, src) in SLICES.items():
    src_text = open(os.path.join(DING, src), encoding='utf-8').read()
    ref = [ln[len('【答案】'):].strip() for ln in src_text.splitlines() if ln.startswith('【答案】')]
    qp = os.path.join(TMUB, '%s-%s.md' % (name, title))
    keys = qkeys(qp)
    got = avalues(os.path.join(TMUB, '%s-%s-答案侧.md' % (name, title)))
    if len(ref) != len(keys):
        print('%s 定稿【答案】行数 %d ≠ 键数 %d' % (name, len(ref), len(keys)))
        bad += 1
        continue
    for k, r in zip(keys, ref):
        total += 1
        if got.get(k) != r:
            print('%s｜%s\n  侧值：%r\n  定稿：%r' % (name, k, got.get(k), r))
            bad += 1
print('值复核：%d 键逐键比对，%s（不符 %d 处）' % (total, '全等 ✓' if bad == 0 else '存在不符 ✗', bad))
sys.exit(1 if bad else 0)
