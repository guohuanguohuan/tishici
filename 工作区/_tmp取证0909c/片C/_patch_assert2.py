# -*- coding: utf-8 -*-
"""片C 断言适配补丁 v2（仅 ④ 块）：× 答案槽识别改稳健版——
'(' 侧允许尾随形（'…．(' 与孤 '(' 皆可），')' 侧允许孤 ')' 或首字 ')'；× 墨盒去重（双 \fill 同 rect）。"""
P = r'C:\提示词\工作区\字替对照-0909\variantF\_测v4断言.py'
s = open(P, encoding='utf-8').read()

a = """# F 片C 0909 适配（旧→新）：#34 × 走 TikZ 后答案槽文本层为孤 '(' / ')' 片段——按 × 墨盒位置
#   将「( ＋ ×墨盒 ＋ )」三件合成伪片段 '(×)'、原件剔除，后续归并/右挂判定逻辑不变。
_x_boxes_16 = {}
for _pno in range(1, n_pages + 1):
    for _d in doc[_pno - 1].get_drawings():
        if _d['fill'] is None:
            continue
        _r = pymupdf.Rect(_d['rect'])
        if 2.2 < _r.width / PT < 2.6 and 2.2 < _r.height / PT < 2.6:
            _x_boxes_16.setdefault(_pno, []).append(_r)
_skip_frag = set()
_grp16 = {}
for pno in range(1, n_pages + 1):
    frags = lines_of[pno]
    pseudo = []
    for r in _x_boxes_16.get(pno, []):
        yc = (r.y0 + r.y1) / 2
        lps = [f for f in frags if f[0].strip() == '(' and abs((f[1][1] + f[1][3]) / 2 - yc) < 6
               and f[1][2] <= r.x0 + 2]
        rps = [f for f in frags if f[0].strip() == ')' and abs((f[1][1] + f[1][3]) / 2 - yc) < 6
               and f[1][0] >= r.x1 - 2]
        if lps and rps:
            lp = max(lps, key=lambda f: f[1][2])
            rp = min(rps, key=lambda f: f[1][0])
            _skip_frag.add((pno, round(lp[1][0], 1), round(lp[1][1], 1)))
            _skip_frag.add((pno, round(rp[1][0], 1), round(rp[1][1], 1)))
            pseudo.append((lp[1][0], '(×)', rp[2]))
    for t, bb, sps in frags:
        if (pno, round(bb[0], 1), round(bb[1], 1)) in _skip_frag:
            continue
        base = sps[0]['origin'][1]
        cl = COLL[0] if bb[0] < MID else COLL[1]
        _grp16.setdefault((pno, cl, round(base * 2)), []).append((bb[0], t))
    for x0, t, sps in pseudo:
        cl = COLL[0] if x0 < MID else COLL[1]
        base = sps[0]['origin'][1] if sps else 0
        _grp16.setdefault((pno, cl, round(base * 2)), []).append((x0, t))"""

b = """# F 片C 0909 适配（旧→新）：#34 × 走 TikZ 后答案槽文本层为孤 '(' / ')' 片段（或「…．(」尾随形）——
#   按 × 墨盒位置把「( ＋ ×墨盒 ＋ )」合成伪片段 '(×)'：'(' 侧片段剥尾 '('（剥空则剔）、')' 侧剔除，
#   后续归并/右挂判定逻辑不变。× 墨盒按 rect 去重（TikZ 双 \\fill 同 rect）。
def _uniq_x(boxes):
    seen, out = set(), []
    for r in boxes:
        k = (round(r.x0, 1), round(r.y0, 1), round(r.width, 1))
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out

_x_boxes_16 = {}
for _pno in range(1, n_pages + 1):
    for _d in doc[_pno - 1].get_drawings():
        if _d['fill'] is None:
            continue
        _r = pymupdf.Rect(_d['rect'])
        if 2.2 < _r.width / PT < 2.6 and 2.2 < _r.height / PT < 2.6:
            _x_boxes_16.setdefault(_pno, []).append(_r)
_skip_frag = set()
_strip_frag = {}
_grp16 = {}
for pno in range(1, n_pages + 1):
    frags = lines_of[pno]
    pseudo = []
    for r in _uniq_x(_x_boxes_16.get(pno, [])):
        yc = (r.y0 + r.y1) / 2
        lps = [f for f in frags if f[0].rstrip().endswith('(')
               and abs((f[1][1] + f[1][3]) / 2 - yc) < 6
               and 0 <= r.x0 - f[1][2] <= 9]
        rps = [f for f in frags if f[0].lstrip().startswith(')')
               and abs((f[1][1] + f[1][3]) / 2 - yc) < 6
               and 0 <= f[1][0] - r.x1 <= 9]
        if lps and rps:
            lp = max(lps, key=lambda f: f[1][2])
            rp = min(rps, key=lambda f: f[1][0])
            kl = (pno, round(lp[1][0], 1), round(lp[1][1], 1))
            kr = (pno, round(rp[1][0], 1), round(rp[1][1], 1))
            stripped = lp[0].rstrip()[:-1]
            if stripped.strip():
                _strip_frag[kl] = stripped
            else:
                _skip_frag.add(kl)
            if rp[0].lstrip() == ')':
                _skip_frag.add(kr)
            else:
                _strip_frag[kr] = rp[0].lstrip()[1:]
            pseudo.append((lp[1][0], '(×)', rp[2]))
    for t, bb, sps in frags:
        key = (pno, round(bb[0], 1), round(bb[1], 1))
        if key in _skip_frag:
            continue
        t2 = _strip_frag.get(key, t)
        base = sps[0]['origin'][1]
        cl = COLL[0] if bb[0] < MID else COLL[1]
        _grp16.setdefault((pno, cl, round(base * 2)), []).append((bb[0], t2))
    for x0, t, sps in pseudo:
        cl = COLL[0] if x0 < MID else COLL[1]
        base = sps[0]['origin'][1] if sps else 0
        _grp16.setdefault((pno, cl, round(base * 2)), []).append((x0, t))"""

assert s.count(a) == 1, '④v2 锚点未命中'
s = s.replace(a, b)
open(P, 'w', encoding='utf-8').write(s)
print('④ v2 落地')
