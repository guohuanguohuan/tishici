# -*- coding: utf-8 -*-
r"""_p1_probe.py — 定向取证：①对账「高度重复5对」逐对分数 ②B段召回带（0.40–0.55）全列 ③C段召回带全列
命中≠判重、漏报≠不重——低分对按 M2 先例人工补判。"""
import os, json
from difflib import SequenceMatcher

WS = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(WS, '_p1池.json'), encoding='utf-8'))
POOL = {q['id']: q for q in D['pool41']}
SRC = {q['no']: q for q in D['src66']}
LOST = [1, 4, 5, 6, 7, 8, 13, 15, 21, 28, 31, 33, 38, 40, 41, 42, 45, 52, 55, 58, 59, 61, 63, 65, 66]
BACK = [SRC[n] for n in LOST]


def ratio(a, b):
    if not a or not b:
        return 0.0
    if len(a) > len(b) * 2 or len(b) > len(a) * 2:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def conf(a, b):
    if not a or not b:
        return 0.0
    sm = SequenceMatcher(None, a, b)
    m = sum(bl.size for bl in sm.get_matching_blocks())
    return m / min(len(a), len(b))


def score(a, b):
    return max(ratio(a['norm'], b['norm']), ratio(a['cjk'], b['cjk'])), \
        max(conf(a['norm'], b['norm']), conf(a['cjk'], b['cjk']))


out = []
out.append('## ① 对账「高度重复5对」定向分数\n')
for xn, pn in [(8, '简1'), (15, '中5'), (38, '简7'), (52, '中22'), (65, '简9')]:
    r, c = score(SRC[xn], POOL[pn]) if pn in ('简1', '简7', '简9') else score(SRC[xn], POOL[pn])
    out.append('Q%d ↔ %s：判%.3f conf%.3f' % (xn, pn, r, c))
r, c = score(SRC[8], SRC[7])
out.append('Q8 ↔ Q7（双双落选，C段内）：判%.3f conf%.3f' % (r, c))
# Q65 与池内另有大面积重合对象；一并看 Q65↔中25(Q60)/中27(Q64)
for p in ('中25', '中27', '中26'):
    r, c = score(SRC[65], POOL[p])
    out.append('Q65 ↔ %s：判%.3f conf%.3f' % (p, r, c))

out.append('\n## ② B段召回带 0.40≤判<0.55（Q落选 × 池41）\n')
for b in BACK:
    for pid, p in POOL.items():
        r, c = score(b, p)
        if 0.40 <= r < 0.55 or (0.40 <= c < 0.95 and r >= 0.30):
            out.append('%.3f/%.2f  %s(%s) ↔ %s(%s)｜%s ↔ %s' % (
                r, c, b['id'], b['kp'][:14], pid, p['kp'][:14], b['head'][:24], p['head'][:24]))

out.append('\n## ③ C段召回带 0.40≤判<0.55（落选内部）\n')
n = len(BACK)
for i in range(n):
    for j in range(i + 1, n):
        a, b = BACK[i], BACK[j]
        r, c = score(a, b)
        if 0.40 <= r < 0.55 or (r >= 0.30 and c >= 0.85):
            out.append('%.3f/%.2f  %s(%s) ↔ %s(%s)｜%s ↔ %s' % (
                r, c, a['id'], a['kp'][:14], b['id'], b['kp'][:14], a['head'][:24], b['head'][:24]))

with open(os.path.join(WS, '_p1取证.md'), 'w', encoding='utf-8') as f:
    f.write('# P1 定向取证（漏报回扫＋召回带）\n\n')
    f.write('\n'.join(out))
print('\n'.join(out))
