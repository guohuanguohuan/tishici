# -*- coding: utf-8 -*-
r"""值复核.py —— 答案侧值 ↔ 定稿【答案】栏逐键复核（防转录滑差；仅比对，不生成值）。
规则：定稿件内按出现序取【答案】行（G1~G5→T1~T16），与答案侧键序一一比对字符串（去首尾空白）。
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', 'M3-第2章量产0913'))
TMUB = os.path.join(ROOT, '成卷', '题面库')

SLICES = {
    '课时06':  ('两条直线的位置关系', r'定稿/批B-课时06-两条直线的位置关系.md'),
    '课时06B': ('2.2.4点到直线距离', r'定稿/批B补-课时06B-2.2.4 点到直线距离.md'),
    '课时07':  ('圆的方程', r'定稿/批B-课时07-圆的方程（2.3.1加2.3.2合）.md'),
    '课时08':  ('直线与圆的位置关系', r'定稿/批B-课时08-直线与圆的位置关系.md'),
    '课时09':  ('圆与圆的位置关系', r'定稿/批B-课时09-圆与圆的位置关系.md'),
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
for name, (title, src_rel) in SLICES.items():
    src = open(os.path.join(ROOT, src_rel), encoding='utf-8').read()
    ref = [ln[len('【答案】'):].strip() for ln in src.splitlines() if ln.startswith('【答案】')]
    qp = os.path.join(TMUB, '%s-%s.md' % (name, title))
    keys = qkeys(qp)
    got = avalues(os.path.join(TMUB, '%s-%s-答案侧.md' % (name, title)))
    if len(ref) != len(keys):
        print('%s 定稿【答案】行数 %d ≠ 键数 %d' % (name, len(ref), len(keys)))
        bad += 1
        continue
    for k, r in zip(keys, ref):
        if got.get(k) != r:
            print('%s｜%s\n  侧值：%r\n  定稿：%r' % (name, k, got.get(k), r))
            bad += 1
print('复核：105 键逐键比对，%s（不符 %d 处）' % ('全等 ✓' if bad == 0 else '存在不符 ✗', bad))
sys.exit(1 if bad else 0)
