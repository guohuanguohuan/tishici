# -*- coding: utf-8 -*-
r"""_复核-三判据0910.py —— 缩档轮·改件后三判据复核（只读探针，临时产物落 缩档测量/）。

三判据（用户 0910 令·规格＝靠齐样张-0910/缩档轮-规格.md）：
 ①字母标签字号 ≈7.5pt（±0.3；下限 7.0pt）〔TW-05〕
 ②含标外廓宽 落 单图 27.7–36.0mm〔TW-02〕／并排子图每张 18.0–24.0mm〔TW-03〕（g6 子图口径＝含标宽÷3，
   与权威依据表 缩档测量.txt【二】同一折算）
 ③有效线宽 ≈0.21mm（±0.03）〔TW-05 参照〕——有效线宽＝片段声明值 × 该图缩档后有效系数；
   实测侧只统计描边件（color 非空），填充件（顶点圆点/箭头头/圈号盘）的 width 兜底 1.0pt 不入读数。

只读：open 读 main.pdf／body.tex／figs/*.tikz；口径函数 importlib 原样载入
     工作区/_tmp取证0909c/片G/权威实测.py（未改一字、未复制近似实现）。
置宽档＝本轮后端档（＝body.tex 实写），素材/件内仍走同一函数。

用法：python -X utf8 _复核-三判据0910.py > 缩档后-三判据复核.txt
"""
import importlib.util
import io
import re
import statistics
import sys
from collections import Counter

import pymupdf

AUTH = 'C:/提示词/工作区/_tmp取证0909c/片G/权威实测.py'
MAIN = 'C:/提示词/工作区/字替对照-0909/variantF/main.pdf'
BODY = 'C:/提示词/工作区/字替对照-0909/variantF/body.tex'
FIGDIR = 'C:/提示词/工作区/字替对照-0909/variantF/figs/'

BOX_MM = {'g6-triple': 80.8, 'g1-prism': 41.1, 'g2-cubeE': 42.0,
          'g3-cube6': 36.3, 'g4-dihedral': 30.5, 'g5-fold': 28.2}
FONT_T, FONT_D, FONT_FLOOR = 7.5, 0.3, 7.0
WIN_SINGLE, WIN_PANEL = (27.7, 36.0), (18.0, 24.0)
LINE_T, LINE_D = 0.21, 0.03
NPANEL = {'g6-triple': 3}
GAP_W = (1.99, 4.44)        # ⑱-2 缩档后重标窗（实测极值 2.24/4.19 ±0.25）
GAP_D = (2.04, 3.85)        # 同上（实测极值 2.29/3.60 ±0.25）
ARROWS = '\u20d7\u20d1\u20db\u20c1'


def load_auth():
    spec = importlib.util.spec_from_file_location('_auth_qw_chk', AUTH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def is_letter(t):
    return not re.fullmatch(r'[0-9①②③④⑤⑥⑦⑧⑨⑩]+', re.sub('[' + ARROWS + ']', '', t).strip())


def frag_decls(name):
    s = io.open(FIGDIR + name + '.tikz', encoding='utf-8').read()
    lw = sorted(set((float(v), u) for v, u in re.findall(r'line width=\s*([\d.]+)\s*(pt|mm)', s)))
    fs = sorted(set(float(v) for v in re.findall(r'\\fontsize\{\s*([\d.]+)\s*(?:pt)?\s*\}', s)))
    return lw, fs


def band(x, lo, hi):
    return '档内' if lo <= x <= hi else ('超档' if x > hi else '低于档')


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    m = load_auth()
    PT = m.PT
    body = io.open(BODY, encoding='utf-8').read()
    decl = {n: w for w, n in re.findall(
        r'\\resizebox\{([^{}]+)\}\{!\}\{\\input\{figs/([\w-]+)\.tikz\}\}', body)}
    doc = pymupdf.open(MAIN)
    print('=' * 124)
    print('缩档轮·改件后三判据复核｜件内 %s｜%d 页' % (MAIN, doc.page_count))
    print('判据①字母字号 %.1f±%.1fpt（下限 %.1f）｜判据②含标宽 单图 %.1f–%.1f／子图每张 %.1f–%.1f｜'
          '判据③有效线宽 %.2f±%.2fmm' % (FONT_T, FONT_D, FONT_FLOOR, WIN_SINGLE[0], WIN_SINGLE[1],
                                        WIN_PANEL[0], WIN_PANEL[1], LINE_T, LINE_D))
    print('=' * 124)
    stks, lns, cand = {}, {}, []
    for pno in range(1, doc.page_count + 1):
        stks[pno] = m.strokes(doc[pno - 1])
        lns[pno] = m.text_lines(doc[pno - 1])
        for c in m.clusters(stks[pno]):
            cand.append((pno, c))
    cand.sort(key=lambda z: (z[0], z[1][0].y0))
    assert len(cand) == 6, '簇数 %d ≠ 6' % len(cand)
    nbad = 0
    for (pno, clus), (tag, sn, _old, frag, at) in zip(cand, m.MAP):
        boxmm = BOX_MM[frag]
        d = m.measure_fig(doc[pno - 1], stks[pno], clus, lns[pno], box_mm=boxmm)
        near = pymupdf.Rect(clus[0].x0 - 0.3 * PT, clus[0].y0 - 0.3 * PT,
                            clus[0].x1 + 0.3 * PT, clus[0].y1 + 0.3 * PT)
        inidx = [i for i, s in enumerate(stks[pno])
                 if near.intersects(s['rect']) and d['band'].contains(s['rect'])]
        sw = [stks[pno][i]['w'] for i in inidx if stks[pno][i]['col'] is not None]
        nfill = len(inidx) - len(sw)
        msz = [L['sz'] for L in d['labs'] if is_letter(L['t'])]
        nsz = [L['sz'] for L in d['labs'] if not is_letter(L['t'])]
        med = statistics.median(msz)
        lwmed = statistics.median(sw) / PT
        ww, wh = d['W'].width / PT, d['W'].height / PT
        fw, fh = d['F'].width / PT, d['F'].height / PT
        lock = m.frag_lock(frag)
        f = boxmm / lock[0] if lock else float('nan')
        gap_u = (d['F'].y0 - d['up']['ink'].y1) / PT if d.get('up') else float('nan')
        gap_d = (d['dn']['ink'].y0 - d['F'].y1) / PT if d.get('dn') else float('nan')
        dclw, dfs = frag_decls(frag)
        dev = ((d['W'].x0 + d['W'].x1) / 2 - d['cc']) / PT
        over = max(0.0, d['box'][0] - d['F'].x0, d['F'].x1 - d['box'][1]) / PT if d.get('box') else 0.0
        win = WIN_PANEL if NPANEL.get(frag) else WIN_SINGLE
        pw = fw / NPANEL[frag] if NPANEL.get(frag) else fw
        bad = []
        if abs(med - FONT_T) > FONT_D:
            bad.append('字号中位 %+.2f 出 ±%.1f' % (med - FONT_T, FONT_D))
        if min(msz) < FONT_FLOOR:
            bad.append('字号最低 %.2f 破下限 %.1f' % (min(msz), FONT_FLOOR))
        if band(pw, *win) != '档内':
            bad.append('外廓 %s%.2f 出档' % ('子图宽 ' if NPANEL.get(frag) else '含标宽 ', pw))
        if abs(lwmed - LINE_T) > LINE_D:
            bad.append('有效线宽 %.3f 出档' % lwmed)
        nbad += len(bad)
        print('\n── %s  %s  p%dc%d｜tex 实写置宽 %s｜折 mm %.1f｜画布锁定 %s｜有效系数 f %s' % (
            frag, tag, pno, at[1], decl.get(frag, '?'), boxmm,
            ('%.2f×%.2f' % lock) if lock else '无锁定',
            ('%.6f' % f) if lock else '反推 %.6f' % (lwmed / dclw[0][0])))
        print('   ①字母标签 %d（圈号/序号另档 %d）min/中位/max ＝ %.2f / %.2f / %.2f pt｜'
              '偏差 %+.2f（中位 vs 7.5）｜逐个：%s' % (
                  len(msz), len(nsz), min(msz), med, max(msz), med - FONT_T,
                  ' '.join('%s=%.2f' % (L['t'].replace(' ', ''), L['sz']) for L in d['labs'])))
        if nsz:
            print('     圈号/序号档 %.2f–%.2fpt（不入主判据）' % (min(nsz), max(nsz)))
        print('   ②线框 W %.2f×%.2f｜含标 F %.2f×%.2f｜判据口径宽 %s %.2f → %s（档 %.1f–%.1f）｜'
              '片段 \\fontsize 声明 %s' % (
                  ww, wh, fw, fh, '子图（F÷3）' if NPANEL.get(frag) else '含标',
                  pw, band(pw, *win), win[0], win[1],
                  '/'.join('%.2fpt' % v for v in dfs) or '（继承宿主）'))
        det = Counter(round(v / PT, 4) for v in sw)
        print('   ③描边 %d 根＋填充 %d 件｜分档（有效 mm×根数）：%s｜中位 %.4fmm → %s（%.2f±%.2f）｜'
              '片段声明 %s' % (
                  len(sw), nfill,
                  '  '.join('%.4f×%d' % (mmv, cnt) for mmv, cnt in sorted(det.items())),
                  lwmed, band(lwmed, LINE_T - LINE_D, LINE_T + LINE_D), LINE_T, LINE_D,
                  ' '.join('%g%s' % (v, u) for v, u in dclw) or '—'))
        print('   旁证｜前距 %.2f（窗 %.2f–%.2f %s）下距 %.2f（窗 %.2f–%.2f %s）栏心偏 %+.2f｜'
              '越盒 %.2f｜标签 %d/素材同法 %d｜正文相交 %d' % (
                  gap_u, GAP_W[0], GAP_W[1], band(gap_u, *GAP_W),
                  gap_d, GAP_D[0], GAP_D[1], band(gap_d, *GAP_D),
                  dev, over, d['nlab'], len(d['labs']), len(d['hits'])))
        if bad:
            print('   ✗ 出档项：' + '；'.join(bad))
        else:
            print('   ✓ 三判据全合')
    print('\n合计出档项 %d（逐图三判据 %d 条检验＝18 条）' % (nbad, 6 * 3))


if __name__ == '__main__':
    main()
