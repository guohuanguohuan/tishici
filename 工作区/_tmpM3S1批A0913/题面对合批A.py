# -*- coding: utf-8 -*-
r"""题面对合批A.py —— 题面库题面侧逐键 ↔ 定稿题块题干逐字对合（防转录滑差；只比对，不生成）。

规则：定稿件按【NN-XX｜…】题块取题干行（至【答案】行止）；题面库按 `### 键` 块取正文行
（与 对号门/冻manifest 同一提取规则：去【注】行/空行/`---`）。逐键逐行全等比对。
05 空号席（E1/E4/E8/E12/E13/E14）与 T1 占位行非键，不在对合射程。
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
# 05 定稿内非题块（空号席＋占位行），对合跳过
SKIP_BLOCKS = {'05-E1', '05-E4', '05-E8', '05-E12', '05-E13', '05-E14', '05-T1'}


def parse_tiku(path):
    """题面库 → {键: [正文行]}"""
    text = open(path, encoding='utf-8').read()
    out, cur = {}, None
    for ln in text.splitlines():
        if ln.startswith('### '):
            cur = ln[4:].split('｜')[0].strip()
            out[cur] = []
        elif cur is not None:
            if ln.strip() == '---':
                cur = None
            elif ln.startswith('【注】') or not ln.strip():
                continue
            else:
                out[cur].append(ln)
    return out


def parse_ding(path):
    """定稿 → {块号: [题干行]}（块号如 01-G1；至【答案】止；跳过空号/占位块）"""
    text = open(path, encoding='utf-8').read()
    out, cur = {}, None
    for ln in text.splitlines():
        m = re.match(r'^【(\d{2}-[A-Z]\d*)｜', ln)
        if m:
            cur = m.group(1)
            if cur in SKIP_BLOCKS:
                cur = None
                continue
            out[cur] = []
        elif cur is not None:
            if ln.startswith('【答案】'):
                cur = None
            elif ln.startswith('【详解】') or not ln.strip():
                continue
            else:
                out[cur].append(ln)
    return out


bad = 0
total = 0
for name, (title, src) in SLICES.items():
    ding = parse_ding(os.path.join(DING, src))
    tiku = parse_tiku(os.path.join(TMUB, '%s-%s.md' % (name, title)))
    if len(ding) != len(tiku):
        print('%s 块数不等：定稿%d vs 题面库%d' % (name, len(ding), len(tiku)))
        bad += 1
    for key, lines in tiku.items():
        tag = key.split('-')[-2].replace('课时', '') + '-' + key.split('-')[-1]  # …课时01-G1 → 01-G1
        ref = ding.get(tag)
        if ref is None:
            print('%s｜%s：定稿无对应题块 %s' % (name, key, tag))
            bad += 1
            continue
        total += 1
        if lines != ref:
            print('%s｜%s 题干不符：' % (name, key))
            for i in range(max(len(lines), len(ref))):
                a = lines[i] if i < len(lines) else '〈缺行〉'
                b = ref[i] if i < len(ref) else '〈缺行〉'
                if a != b:
                    print('  库：%r' % a)
                    print('  稿：%r' % b)
            bad += 1
print('对合：%d 键逐字比对，%s（不符 %d 键）' % (total, '全等 ✓' if bad == 0 else '存在不符 ✗', bad))
sys.exit(1 if bad else 0)
