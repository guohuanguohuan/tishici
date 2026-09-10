# -*- coding: utf-8 -*-
r"""_探针-描边线宽0910.py —— 缩档轮·只读探针（临时产物，落 缩档测量/）。

为什么需要：权威依据表 缩档测量.txt 的「笔画线宽」列把填充件（顶点圆点/箭头头/圈号盘）
的 width 兜底值 1.0pt 一并计入中位数（g1 0.353／g6 0.353 皆此来路），故不能直接当「有效线宽」
核 0.21mm 档。本探针只统计描边件（color 非空＝真有 stroke 的对象），填充件单列根数，
用于：改件前取现状、改件后核「有效线宽＝片段声明 × 缩档后系数」是否落 0.21±0.03mm。

只读：open 读 main.pdf／figs/*.tikz，不写任何件；口径函数 importlib 原样载入
     （工作区/_tmp取证0909c/片G/权威实测.py），未改一字。

用法：python -X utf8 _探针-描边线宽0910.py [置宽档名]
      置宽档名＝old（默认，用口径源 MAP 内置档）或 new（用本轮缩档后端档）
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

# 缩档轮后端置宽档（＝body.tex 实写；tex 侧若仍写 \linewidth 则折 84.0mm）
NEW_BOX = {'g6-triple': 80.8, 'g1-prism': 41.1, 'g2-cubeE': 42.0,
           'g3-cube6': 36.3, 'g4-dihedral': 30.5, 'g5-fold': 28.2}
LINE_TARGET_MM, LINE_TOL = 0.21, 0.03


def load_auth():
    spec = importlib.util.spec_from_file_location('_auth_qw_probe', AUTH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def frag_decls(name):
    s = io.open(FIGDIR + name + '.tikz', encoding='utf-8').read()
    lw = sorted(set((float(v), u) for v, u in re.findall(r'line width=\s*([\d.]+)\s*(pt|mm)', s)))
    fs = sorted(set(float(v) for v in re.findall(r'\\fontsize\{\s*([\d.]+)\s*(?:pt)?\s*\}', s)))
    return lw, fs


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    arm = (sys.argv[1] if len(sys.argv) > 1 else 'old').lower()
    m = load_auth()
    PT = m.PT
    body = io.open(BODY, encoding='utf-8').read()
    decl = {n: w for w, n in re.findall(
        r'\\resizebox\{([^{}]+)\}\{!\}\{\\input\{figs/([\w-]+)\.tikz\}\}', body)}
    doc = pymupdf.open(MAIN)
    print('探针臂＝%s｜main.pdf %d 页' % (arm, doc.page_count))
    print('tex 实写置宽：' + '  '.join('%s=%s' % (n, decl.get(n, '?')) for _, _, _, n, _ in m.MAP))
    print('')
    hdr = ('片段|置宽mm|画布锁定mm|系数f=置宽/画布|描边根/填充件|描边宽 pt min/中/max|'
           '描边宽 mm min/中/max|片段声明 line width|中位÷主声明（应≈f）')
    print(hdr)
    print('-' * 156)
    stks, cand = {}, []
    for pno in range(1, doc.page_count + 1):
        stks[pno] = m.strokes(doc[pno - 1])
        for c in m.clusters(stks[pno]):
            cand.append((pno, c))
    cand.sort(key=lambda z: (z[0], z[1][0].y0))
    assert len(cand) == 6, '簇数 %d ≠ 6' % len(cand)
    for (pno, clus), (tag, sn, wbox, frag, at) in zip(cand, m.MAP):
        r, inidx = clus[0], clus[2]
        sw = [stks[pno][i]['w'] for i in inidx if stks[pno][i]['col'] is not None]
        nf = sum(1 for i in inidx if stks[pno][i]['col'] is None)
        lock = m.frag_lock(frag)
        boxmm = wbox if arm == 'old' else NEW_BOX[frag]
        f = (boxmm / lock[0]) if lock else float('nan')
        dclw, dfs = frag_decls(frag)
        # 片段声明折算 pt（1mm＝PT/72.27*... 用 mm→pt＝72/25.4）
        dpt = sorted(set(v * (PT / 25.4) if u == 'mm' else v for v, u in dclw))
        main_d = dpt[0] if dpt else float('nan')
        print('%s|%s|%.4g|%.6g|%d/%d|%.3f/%.3f/%.3f|%.3f/%.3f/%.3f|%s|%.5f' % (
            frag, boxmm, lock[0] if lock else float('nan'), f, len(sw), nf,
            min(sw), statistics.median(sw), max(sw),
            min(sw) / PT, statistics.median(sw) / PT, max(sw) / PT,
            ' '.join('%g%s' % (v, u) for v, u in dclw) or '—',
            statistics.median(sw) / main_d if dpt else float('nan')))
        tgt = statistics.median(sw) / PT
        ok = '档内' if abs(tgt - LINE_TARGET_MM) <= LINE_TOL else ('偏细' if tgt < LINE_TARGET_MM else '偏粗')
        det = Counter(round(v / PT, 4) for v in sw)
        print('   ↳ 片段 \\fontsize 声明档：' + ('/'.join('%.2fpt' % v for v in dfs) or '（继承宿主）'))
        print('   ↳ 描边分档（mm×根数，反推声明＝mm÷f）：' + '  '.join(
            '%.4fmm×%d（声明%.4f）' % (mmv, cnt, (mmv / f) if lock else float('nan'))
            for mmv, cnt in sorted(det.items())))
        print('   ↳ 有效线宽（描边中位）%.3fmm → %s（TW-05 %.2f±%.2f）｜目标声明新值＝0.21/f＝%s' % (
            tgt, ok, LINE_TARGET_MM, LINE_TOL,
            'n/a（无锁定，按现中位×新/老置宽比折算）' if not lock else '%.4fmm' % (LINE_TARGET_MM / f)))
    # 无锁定片段（g5）：系数以「实测描边中位 ÷ 片段声明」反取
    print('\n注：g5 无画布锁定 → f 用反证法：现 f＝现实测描边中位÷现声明，'
          '新 f＝现 f×（新置宽/老置宽），声明新值＝0.21÷新 f。')


if __name__ == '__main__':
    main()
