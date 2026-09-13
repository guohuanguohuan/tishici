# -*- coding: utf-8 -*-
r"""值复核批C.py —— 批C 四片 题面保真＋答案值照录 复核器（工序件）。

核对双向：
  ①题面保真：题面库各键题面全文（按 对号门.py 提取规则：剔【注】行/空行/`---` 行）
    ≡ 定稿件对应块题面行（§9 补产区块；课时10 简7/中1~中4 特例→§4 定稿题块；
    命制块首行剥 `题面：` 前缀）。
  ②值照录：答案侧 `值：` ≡ 定稿对应块 `【答案】` 行原文。
跑法：python 值复核批C.py   # 全零漂 → VERDICT: OK
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
    '课时10': '批C-课时10-2.4曲线与方程.md',
    '课时11': '批C-课时11-2.5.1椭圆的标准方程.md',
    '课时12': '批C-课时12-2.5.2椭圆的几何性质.md',
    '课时13': '批C-课时13-2.6.1双曲线的标准方程.md',
}

# 键 → 定稿件内块定位。块定位：(块头标, 'prefix_strip'|None) 或 ('§4 定稿2.4-新N', None)
MAP = {}
for g, blk in zip(['G1', 'G2', 'G3', 'G4', 'G5'], ['单1', '单2', '单3', '填1', '填2']):
    MAP['课时12-' + g] = ('12-' + blk, None)
    MAP['课时13-' + g] = ('13-' + blk, None)
for g in ['G1', 'G2', 'G3', 'G4', 'G5']:
    MAP['课时10-' + g] = ('10-' + g, None)
    MAP['课时11-' + g] = ('11-' + g, None)
for n in range(1, 11):
    MAP['课时10-简%d' % n] = ('10-简%d' % n, '题面：' if n in (8, 9, 10) else None)
    MAP['课时11-简%d' % n] = ('11-简%d' % n, '题面：' if n in (8, 9, 10) else None)
    MAP['课时13-简%d' % n] = ('13-简%d' % n, '题面：' if n in (9, 10) else None)
    MAP['课时12-简%d' % n] = ('12-简%d' % n, None)
for n in range(1, 5):
    MAP['课时10-中%d' % n] = ('定稿2.4-新%d' % (n + 1), None)
    MAP['课时11-中%d' % n] = ('11-中%d' % n, None)
    MAP['课时12-中%d' % n] = ('12-中%d' % n, None)
    MAP['课时13-中%d' % n] = ('13-中%d' % n, None)
for n in (1, 2):
    MAP['课时10-难%d' % n] = ('10-难%d' % n, None)
    MAP['课时11-难%d' % n] = ('11-难%d' % n, None)
    MAP['课时12-难%d' % n] = ('12-难%d' % n, None)
    MAP['课时13-难%d' % n] = ('13-难%d' % n, None)
MAP['课时10-简7'] = ('定稿2.4-新1', None)


def parse_questions(path):
    """与 对号门.py 完全一致的题面提取。"""
    text = open(path, encoding='utf-8', newline='').read()
    out, cur = [], None
    for ln in text.splitlines():
        if ln.startswith('### '):
            if cur:
                out.append(cur)
            head = ln[4:]
            key = head.split('｜')[0].strip()
            cur = [key, []]
        elif cur is not None:
            if ln.strip() == '---':
                out.append(cur)
                cur = None
            elif ln.startswith('【注】') or not ln.strip():
                continue
            else:
                cur[1].append(ln)
    if cur:
        out.append(cur)
    return [(k, '\n'.join(body)) for k, body in out]


def parse_answers(path):
    text = open(path, encoding='utf-8', newline='').read()
    out, cur = [], None
    for ln in text.splitlines():
        m = re.match(r'^% ans:(\S+)\s*$', ln)
        if m:
            if cur:
                out.append(cur)
            cur = [m.group(1), '']
        elif cur is not None and ln.startswith('值：'):
            cur[1] = ln[2:].strip()
    if cur:
        out.append(cur)
    return dict(out)


def ding_blocks(path):
    """定稿件 → {块头标: (题面行list, 答案值)}。块头行＝行首（可带 **）`【标｜`；§4 定稿块＝`**【定稿2.4-新N】（…）** 题面…`。"""
    lines = open(path, encoding='utf-8', newline='').read().splitlines()
    blocks, cur = {}, None
    for ln in lines:
        m9 = re.match(r'^\*{0,2}(【(?:10|11|12|13)-[^｜]+｜[^】]*】)\*{0,2}\s*$', ln)
        m4 = re.match(r'^\*\*(【定稿2\.4-新\d】)（[^）]*）\*\*\s?(.*)$', ln)
        if m9:
            cur = (m9.group(1)[1:-1].split('｜', 1)[0], [])
            blocks[cur[0]] = cur[1]
        elif m4:
            cur = (m4.group(1)[1:-1], [])
            if m4.group(2).strip():
                cur[1].append(m4.group(2))
            blocks[cur[0]] = cur[1]
        elif cur is not None:
            if ln.startswith('【答案】'):
                blocks[cur[0]].append(('ANS', ln[len('【答案】'):].strip()))
                cur = None
            elif ln.startswith('【答案') or ln.startswith('【解'):
                cur = None
            else:
                cur[1].append(ln)
    out = {}
    for tag, body in blocks.items():
        ans = ''
        rows = []
        for it in body:
            if isinstance(it, tuple):
                ans = it[1]
            else:
                rows.append(it)
        out[tag] = (rows, ans)
    return out


def main():
    bad = []
    nq = 0
    for sl, src in SLICES.items():
        qp = os.path.join(TMUB, '%s-%s.md' % (sl, {'课时10': '2.4曲线与方程', '课时11': '2.5.1椭圆的标准方程',
                                                   '课时12': '2.5.2椭圆的几何性质', '课时13': '2.6.1双曲线的标准方程'}[sl]))
        ap = qp[:-len('.md')] + '-答案侧.md'
        blocks = ding_blocks(os.path.join(DING, src))
        vals = parse_answers(ap)
        for key, qtext in parse_questions(qp):
            nq += 1
            kk = key  # 形如 2章-导-课时10-G1
            short = kk.split('-', 2)[2]  # 课时10-G1
            tag, strip = MAP[short]
            if tag not in blocks:
                bad.append('%s %s：定稿块未找到：%s' % (sl, kk, tag))
                continue
            rows, ans = blocks[tag]
            exp_rows = list(rows)
            if strip:
                exp_rows = [(exp_rows[0][len(strip):] if exp_rows[0].startswith(strip) else exp_rows[0])] + exp_rows[1:]
            exp_text = '\n'.join(exp_rows)
            if qtext != exp_text:
                bad.append('%s %s：题面漂移\n  库文=%r\n  源文=%r' % (sl, kk, qtext[:120], exp_text[:120]))
            v = vals.get(kk, '')
            if v != ans:
                bad.append('%s %s：值漂移\n  库值=%r\n  源值=%r' % (sl, kk, v[:120], ans[:120]))
    print('核对题块：%d' % nq)
    if bad:
        print('漂移 %d 处：' % len(bad))
        for b in bad:
            print(' - ' + b)
        print('VERDICT: DRIFT')
        sys.exit(1)
    print('VERDICT: OK（题面保真＋值照录 全零漂）')


if __name__ == '__main__':
    main()
