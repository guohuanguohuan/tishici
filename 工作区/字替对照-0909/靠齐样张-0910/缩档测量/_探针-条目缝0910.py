# -*- coding: utf-8 -*-
r"""_探针-条目缝0910.py —— 诊断 ⑦ 条目缝第 5 对读数 2.71→2.54（缩档轮 collateral）。

做法：exec 载入 variantF/_测v4断言.py（其 ⑦ 收集段在模块级，helper 全在 globals），
     再把「条目缝配对＋带隙计算」那一小段按原式重跑一遍，逐对打印两端行的文本与 y、
     所属页栏、带号——只为定位读数来自哪两行，不设新判据、不改任何门值。
只读。用法：python -X utf8 _探针-条目缝0910.py
"""
import contextlib
import importlib.util
import io
import re
import sys

P = 'C:/提示词/工作区/字替对照-0909/variantF/_测v4断言.py'
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

spec = importlib.util.spec_from_file_location('_v4_for_probe', P)
mod = importlib.util.module_from_spec(spec)
_rc = None
with contextlib.redirect_stdout(io.StringIO()):
    try:
        spec.loader.exec_module(mod)          # 跑全套断言（只读），取其模块级 helper 与常数
    except SystemExit as e:                   # 件尾 raise SystemExit(结算码) → 捕获后门值照常可读
        _rc = e.code
print('（载入 _测v4断言.py 完成，其自身结算码＝%s，本探针不复述其输出）' % _rc)

g = mod.__dict__
PT, COLL, doc, n_pages = g['PT'], g['COLL'], g['doc'], g['n_pages']
col_rows, col_bands, band_at = g['col_rows'], g['col_bands'], g['band_at']
_sig_t = None
print('⑦ 条目缝逐对明细（原式重跑·只诊断）')
print('对序｜页栏｜上带末行（文本/y1/带号）→ 下带首行（文本/y0/带号）｜缝 mm｜g_tm 现值')
vals = []
for pno in range(1, n_pages + 1):
    for cl in COLL:
        bs = col_bands(pno, cl)
        rows = col_rows(pno, cl)
        if not bs or not rows:
            continue
        sig = lambda t: bool(re.match(r'^(◆|例1|变式1|\[(?!注意)|【)', t))
        kn0 = next((k for k, (_y0, _y1, t, _s) in enumerate(rows) if t.startswith('◆知识点')), -1)
        num_rows = [k for k, (y0_, y1_, t, _sps) in enumerate(rows) if re.match(r'^\d+\.(?!\d)', t)]
        for k1, k2 in zip(num_rows, num_rows[1:]):
            if k1 <= kn0:
                continue
            if any(sig(rows[m][2]) for m in range(k1 + 1, k2)):
                continue

            def _same_line(m, k):
                a0, a1, b0, b1 = rows[m][0], rows[m][1], rows[k][0], rows[k][1]
                return min(a1, b1) - max(a0, b0) > 0.5 * min(a1 - a0, b1 - b0)

            prev = [m for m in range(k1, k2) if not _same_line(m, k2)]
            last = max(prev, key=lambda m: rows[m][1]) if prev else k1
            b_j = band_at(bs, rows[k2][0], rows[k2][1])
            b_i = band_at(bs, rows[last][0], rows[last][1])
            if b_j > b_i:
                v = (bs[b_j][0] - bs[b_i][1]) / PT
                vals.append(v)
                if v < 2.7:            # 出界对：把上下两带的成员行与带边全打出来（诊断用）
                    for bi, nm in ((b_i, '上带'), (b_j, '下带')):
                        mem = [(rr[2][:30], rr[0] / PT, rr[1] / PT) for rr in rows
                               if band_at(bs, rr[0], rr[1]) == bi]
                        print('   %s 带%d 边[%.2f,%.2f]mm 成员行 %d：%s' % (
                            nm, bi, bs[bi][0] / PT, bs[bi][1] / PT, len(mem),
                            ' ‖ '.join('「%s」bbox %.2f–%.2f' % mmr for mmr in mem)))
                print('%d｜p%dc%d｜上末行「%s」y底 %.2f 带%d → 下首行「%s」y顶 %.2f 带%d｜%.2f' % (
                    len(vals), pno, 1 if cl == COLL[0] else 2, rows[last][2][:26],
                    rows[last][1] / PT, b_i, rows[k2][2][:26], rows[k2][0] / PT, b_j, v))
print('\ng_tm ＝', ' '.join('%.2f' % v for v in vals), '｜n＝', len(vals),
      '｜窗 2.7–3.6｜出界', ['%.2f' % v for v in vals if not 2.7 <= v <= 3.6])
