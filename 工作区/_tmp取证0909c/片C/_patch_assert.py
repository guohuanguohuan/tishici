# -*- coding: utf-8 -*-
"""片C 断言适配补丁（5 处，逐项对应报告登记）。
① ⑮ 行尾 ×) → )（× 走 TikZ，行文本无 ×）
② N1 答案槽识别加 × 墨盒支
③ ④ 答案槽 '(' + ×墨盒 + ')' 三件合成伪片段 '(×)'
④ ⑦ 条目缝窗 2.7–3.4 → 2.7–3.6（Task1 编注改短致墨深读数位移）
⑤ ⑭ 括号对剔除 × 答案槽（1.8em 空档非 \\kongwei）
"""
P = r'C:\提示词\工作区\字替对照-0909\variantF\_测v4断言.py'
s = open(P, encoding='utf-8').read()
orig = s

# ---- ① ⑮ ----
a1 = ("check('⑮【诊断分析】头单行×3（10.5pt 说明，紧缩文案 无引号版）', len(zhen_lines) == 3 and orphan_rpar == 0\n"
      "      and all('判断正误' in t and t.endswith('×)') and abs(sz - 10.5) <= 0.6 for _, t, sz in zhen_lines),")
b1 = ("# F 片C 0909 适配（旧→新）：#34 判断错号 × 改 TikZ 自绘后行文本无「×」字——行尾判定由\n"
      "#   endswith('×)') 放宽为「'判断正误' 起行且以 ')' 收尾」（× 矢量在场由 N1/④ 侧核）。\n"
      "check('⑮【诊断分析】头单行×3（10.5pt 说明，紧缩文案 无引号版）', len(zhen_lines) == 3 and orphan_rpar == 0\n"
      "      and all('判断正误' in t and t.rstrip().endswith(')') and abs(sz - 10.5) <= 0.6 for _, t, sz in zhen_lines),")
assert s.count(a1) == 1, '①锚点未命中'
s = s.replace(a1, b1)

# ---- ② N1 ----
a2 = """par_ok, par_detail = True, []
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    for t, bb, sps in lines_of[pno]:
        if not re.search(r'\\(\\s*[√×]\\s*\\)$', t):
            continue
        cl = COLL[0] if bb[0] < MID else COLL[1]
        pm = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY,
                             clip=pymupdf.Rect(cl, bb[1] - 1, cl + COLW, bb[3] + 1))
        w, h, s = pm.width, pm.height, pm.samples
        cols = [any(s[r_ * w + c] < 128 for r_ in range(h)) for c in range(w)]
        ink_r = cl + (w - 1 - cols[::-1].index(True)) / SC
        ink_d = (cl + COLW - ink_r) / PT
        bb_d = (cl + COLW - bb[2]) / PT
        par_ok = par_ok and -0.1 <= ink_d <= 0.45 and -0.4 <= bb_d <= 0.2
        par_detail.append(f'p{pno}{t[-3:]} ink{ink_d:.2f}/bbox{bb_d:.2f}')"""
b2 = """# F 片C 0909 适配（旧→新）：#34 × 走 TikZ 后答案槽文本层只剩孤 '(' / ')' 片段——
#   槽识别由「行尾 (√/×)」扩为「行尾 ')' 且其左同基线有 × 墨盒」；√ 槽照旧（文本形）。
par_ok, par_detail = True, []
_x_boxes_n1 = {}
for _pno in range(1, n_pages + 1):
    for _d in doc[_pno - 1].get_drawings():
        if _d['fill'] is None:
            continue
        _r = pymupdf.Rect(_d['rect'])
        if 2.2 < _r.width / PT < 2.6 and 2.2 < _r.height / PT < 2.6:
            _x_boxes_n1.setdefault(_pno, []).append(_r)
for pno in range(1, n_pages + 1):
    page = doc[pno - 1]
    for t, bb, sps in lines_of[pno]:
        if re.search(r'\\(\\s*[√×]\\s*\\)$', t):
            tag = t[-3:]
        elif t.strip() == ')':
            yc = (bb[1] + bb[3]) / 2
            if not any(abs((r.y0 + r.y1) / 2 - yc) < 6 and r.x1 <= bb[0] + 2
                       for r in _x_boxes_n1.get(pno, [])):
                continue
            tag = '×) '
        else:
            continue
        cl = COLL[0] if bb[0] < MID else COLL[1]
        pm = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY,
                             clip=pymupdf.Rect(cl, bb[1] - 1, cl + COLW, bb[3] + 1))
        w, h, s = pm.width, pm.height, pm.samples
        cols = [any(s[r_ * w + c] < 128 for r_ in range(h)) for c in range(w)]
        ink_r = cl + (w - 1 - cols[::-1].index(True)) / SC
        ink_d = (cl + COLW - ink_r) / PT
        bb_d = (cl + COLW - bb[2]) / PT
        par_ok = par_ok and -0.1 <= ink_d <= 0.45 and -0.4 <= bb_d <= 0.2
        par_detail.append(f'p{pno}{tag} ink{ink_d:.2f}/bbox{bb_d:.2f}')"""
assert s.count(a2) == 1, '②锚点未命中'
s = s.replace(a2, b2)

# ---- ③ ④ ----
a3 = """_grp16 = {}
for pno in range(1, n_pages + 1):
    for t, bb, sps in lines_of[pno]:
        base = sps[0]['origin'][1]
        cl = COLL[0] if bb[0] < MID else COLL[1]
        _grp16.setdefault((pno, cl, round(base * 2)), []).append((bb[0], t))"""
b3 = """# F 片C 0909 适配（旧→新）：#34 × 走 TikZ 后答案槽文本层为孤 '(' / ')' 片段——按 × 墨盒位置
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
assert s.count(a3) == 1, '③锚点未命中'
s = s.replace(a3, b3)

# ---- ④ ⑦ ----
a4 = "        and len(g_tm) == 6 and all(2.7 <= v <= 3.4 for v in g_tm))"
b4 = "        and len(g_tm) == 6 and all(2.7 <= v <= 3.6 for v in g_tm))"
assert s.count(a4) == 1, '④锚点未命中'
s = s.replace(a4, b4)
a4b = "'表底→下块 3.91±0.5×3／条目→条目 \\\\tiaomu 缝 ×%d 窗2.7-3.4）' % len(g_tm), ok7b,"
b4b = "'表底→下块 3.91±0.5×3／条目→条目 \\\\tiaomu 缝 ×%d 窗2.7-3.6）' % len(g_tm), ok7b,"
assert s.count(a4b) == 1, '④b锚点未命中'
s = s.replace(a4b, b4b)

# ---- ⑤ ⑭ ----
a5 = """kw_gaps, kw_stray = [], []
for pno in range(1, n_pages + 1):
    cs = chars_of[pno]
    for i in range(len(cs) - 1):
        if cs[i][0] == '(' and cs[i + 1][0] == ')':
            v = (cs[i + 1][1][0] - cs[i][1][2]) / PT
            (kw_gaps if 6.2 <= v <= 7.4 else kw_stray).append((pno, cs[i][1][1], v))"""
b5 = """# F 片C 0909 适配（旧→新）：#34 × 走 TikZ 后判断答案槽 '(' ')' 成相邻字符（1.8em 空档 6.4mm），
#   旧式误计为 \\kongwei 对（+4）；按 × 墨盒夹在括号对之间者剔除。
_x_boxes14 = {}
for _pno in range(1, n_pages + 1):
    for _d in doc[_pno - 1].get_drawings():
        if _d['fill'] is None:
            continue
        _r = pymupdf.Rect(_d['rect'])
        if 2.2 < _r.width / PT < 2.6 and 2.2 < _r.height / PT < 2.6:
            _x_boxes14.setdefault(_pno, []).append(_r)
kw_gaps, kw_stray = [], []
for pno in range(1, n_pages + 1):
    cs = chars_of[pno]
    for i in range(len(cs) - 1):
        if cs[i][0] == '(' and cs[i + 1][0] == ')':
            lp, rp = cs[i][1], cs[i + 1][1]
            yc = (min(lp[1], rp[1]) + max(lp[3], rp[3])) / 2
            if any(abs((r.y0 + r.y1) / 2 - yc) < 6 and lp[2] - 1 <= r.x0 and r.x1 <= rp[0] + 1
                   for r in _x_boxes14.get(pno, [])):
                continue
            v = (rp[0] - lp[2]) / PT
            (kw_gaps if 6.2 <= v <= 7.4 else kw_stray).append((pno, lp[1], v))"""
assert s.count(a5) == 1, '⑤锚点未命中'
s = s.replace(a5, b5)

open(P, 'w', encoding='utf-8').write(s)
print('5 处适配全部落地；文件行数', s.count(chr(10)) + 1, '（原', orig.count(chr(10)) + 1, '）')
