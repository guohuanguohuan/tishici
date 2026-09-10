# -*- coding: utf-8 -*-
r"""缩档测量.py —— 六图缩档轮·只读测量＋逐图反解（0910）。

只读：本脚本只 open 读取 main.pdf／figs/*.tikz／素材 standalone，唯一写出＝本目录 缩档测量.txt。
variantF/ 与 附则/ 一字不改。

【口径源】工作区/_tmp取证0909c/片G/权威实测.py（0910 定档·权威线框口径）。
  以 importlib 原样载入并调用其 strokes / clusters / text_lines / measure_fig / frag_lock，
  不改其一字、不复制近似实现（复制＝造第二套口径，正是 0910【甲】C 已证伪的老病）。

【两级判据】（用户 0910 定·规格＝靠齐样张-0910/缩档轮-规格.md）
  主判据＝图内顶点字母标签字号（文本层 span size·与权威口径同一取数路径）
          目标 7.5pt（正文 10.5pt 的 70–75%），下限 7.0pt —— 〔零件库〕TW-05
          ①②③ 圈号/序号＝另档，单列备注，不入主判据（也不与字母取中位数）。
  校验判据＝含标外廓落全品档：单图 27.7–36mm〔TW-02〕／并排子图每张 18–24mm〔TW-03〕
  线宽参照＝0.21mm〔TW-05〕｜硬闸＝不超栏宽 84.0mm。

【为什么以 r＝含标长边 ÷ 标签字号中位（mm/pt）作决策量】
  \resizebox{X}{!}＝单一 CTM 各向同性缩放：外廓、标签字号、线宽、虚线节距同乘一个系数，
  故比值 r 与置宽无关（缩放只沿 r 的"刻度"平移，改不动 r）。
  → 两判据能否一次同时满足，完全由 r 决定：r 落在 [档下沿/7.5, 档上沿/7.5] ＝ A（只改置宽）；
    否则＝B（须让标签与几何"脱钩"——改片段 \\fontsize 或收紧顶点间距）；B 也不成立＝C（例外）。
  r 的恒等性前提「严格同比、无拉伸畸变」由权威口径不变量 |rx−ry|≤0.005 背书（run4 实测 max 0.00265）。

用法：python -X utf8 缩档测量.py      （stdout 与 缩档测量.txt 同源同码）
"""
import hashlib
import importlib.util
import io
import os
import re
import statistics
import sys

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
AUTH = 'C:/提示词/工作区/_tmp取证0909c/片G/权威实测.py'
MAIN = 'C:/提示词/工作区/字替对照-0909/variantF/main.pdf'
BODY = 'C:/提示词/工作区/字替对照-0909/variantF/body.tex'
FIGDIR = 'C:/提示词/工作区/字替对照-0909/variantF/figs/'
OUT = os.path.join(HERE, '缩档测量.txt')

FONT_TARGET, FONT_FLOOR = 7.5, 7.0            # pt  〔TW-05〕
WIN_SINGLE = (27.7, 36.0)                     # mm  〔TW-02〕题下居中
WIN_PARA = (18.0, 24.0)                       # mm  〔TW-03〕并排每张
LINE_TARGET_MM, LINE_TOL = 0.21, 0.05         # mm  〔TW-05〕
NPANEL = {'g6-triple': 3}                     # 并排子图（三联）
GAP_PANEL = 0.5                               # mm 墨 x 向空档 ≥ 此值即断带
COLW_MM = 84.0                                # 硬闸
ARROWS = '\u20d7\u20d1\u20db\u20c1'


def load_auth():
    spec = importlib.util.spec_from_file_location('_auth_qw', AUTH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)               # 口径源带 __main__ 门控 → 导入不触发自跑
    return mod


def frag_decl(mod, name):
    """片段自声明（只读）：\\fontsize 档／line width 档／画布锁定（锁定用口径源原函数）。"""
    s = io.open(FIGDIR + name + '.tikz', encoding='utf-8').read()
    fs = sorted(set(float(v) for v in re.findall(r'\\fontsize\{\s*([\d.]+)\s*(?:pt)?\s*\}', s)))
    lw = sorted(set(float(v) for v in re.findall(r'line width=\s*([\d.]+)\s*mm', s)))
    return dict(fonts=fs, lws=lw, lock=mod.frag_lock(name))


def is_letter(t):
    """顶点字母标签＝True；①②③圈号/纯序号＝False（剥掉向量头上划线后再判）。"""
    x = re.sub('[' + ARROWS + ']', '', t).strip()
    return not re.fullmatch(r'[0-9①②③④⑤⑥⑦⑧⑨⑩]+', x)


def panel_bands(stk, inidx, PT, gap_mm=GAP_PANEL):
    """簇内笔画按 x 向墨空档断带 → 逐子图**线框**外接（实测算出，不按总宽均分）。"""
    iv = sorted((stk[i]['rect'].x0, stk[i]['rect'].x1, i) for i in inidx)
    grp, cur = [], [iv[0]]
    for t in iv[1:]:
        if t[0] - max(z[1] for z in cur) > gap_mm * PT:
            grp.append(cur)
            cur = [t]
        else:
            cur.append(t)
    grp.append(cur)
    out = []
    for g in grp:
        r = pymupdf.Rect(stk[g[0][2]]['rect'])
        for _, _, i in g[1:]:
            r |= stk[i]['rect']
        out.append(r)
    return out


def band_of(win, x):
    return '档内' if win[0] <= x <= win[1] else ('超档' if x > win[1] else '破下沿')


def side(x, lo, hi):
    return '偏小' if x < lo else ('偏大' if x > hi else '合')


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    m = load_auth()
    PT = m.PT
    out = []
    W = out.append

    md5 = hashlib.md5(io.open(MAIN, 'rb').read()).hexdigest()
    body = io.open(BODY, encoding='utf-8').read()
    decl = {n: w for w, n in re.findall(
        r'\\resizebox\{([^{}]+)\}\{!\}\{\\input\{figs/([\w-]+)\.tikz\}\}', body)}
    lines = {n: i for i, n in enumerate(body.split('\n'), 1) if 'resizebox' in n and 'figs/' in n}

    W('=' * 124)
    W('六图缩档轮·只读实测＋反解（口径源＝_tmp取证0909c/片G/权威实测.py，importlib 原样载入，未改一字）')
    W('件内 %s｜7 页｜md5 %s' % (MAIN, md5))
    W('主判据＝图内顶点字母标签字号 → 目标 %.1fpt／下限 %.1fpt（正文 10.5pt×70–75%%）〔TW-05〕；①②③圈号另档单列、不入主判据'
      % (FONT_TARGET, FONT_FLOOR))
    W('校验判据＝含标外廓长边落档：单图 %.1f–%.1fmm〔TW-02〕／并排子图每张 %.1f–%.1fmm〔TW-03〕；线宽参照 %.2fmm；硬闸 不超栏宽 %.1fmm'
      % (WIN_SINGLE[0], WIN_SINGLE[1], WIN_PARA[0], WIN_PARA[1], LINE_TARGET_MM, COLW_MM))
    W('决策量 r＝含标长边÷字母字号中位（mm/pt）：\\resizebox 各向同性 → r 与置宽无关，故 r 决定"能否一次落双档"')
    W('  ⇒ 单图可解窗 r ∈ [%.3f, %.3f]；并排子图窗 r ∈ [%.3f, %.3f]'
      % (WIN_SINGLE[0] / FONT_TARGET, WIN_SINGLE[1] / FONT_TARGET,
         WIN_PARA[0] / FONT_TARGET, WIN_PARA[1] / FONT_TARGET))
    W('=' * 124)

    doc = pymupdf.open(MAIN)
    stks, lns, cand = {}, {}, []
    for pno in range(1, doc.page_count + 1):
        stks[pno] = m.strokes(doc[pno - 1])
        lns[pno] = m.text_lines(doc[pno - 1])
        for c in m.clusters(stks[pno]):
            cand.append((pno, c))
    cand.sort(key=lambda z: (z[0], z[1][0].y0))
    W('矢量图簇命中 %d（须 6）' % len(cand))
    if len(cand) != 6:
        W('!! 簇数≠6 → 并簇/门槛参数失效，整表判废')
        return _flush(out)

    rows = []
    for (pno, clus), (tag, sn, wbox, frag, at) in zip(cand, m.MAP):
        d = m.measure_fig(doc[pno - 1], stks[pno], clus, lns[pno], box_mm=wbox)
        assert d is not None, frag
        # 簇内笔画索引：复用 measure_fig 同一选择式（near∩band），并核对根数与其一致
        r = clus[0]
        near = pymupdf.Rect(r.x0 - 0.3 * PT, r.y0 - 0.3 * PT, r.x1 + 0.3 * PT, r.y1 + 0.3 * PT)
        band = d['band']
        inidx = [i for i, s in enumerate(stks[pno])
                 if near.intersects(s['rect']) and band.contains(s['rect'])]
        assert len(inidx) == d['nstroke'], (frag, len(inidx), d['nstroke'])
        # 线宽只取描边对象（col 非空）；填充件（顶点圆点/箭头头/圈号盘）strokes() 把 width
        # 兜底成 1.0pt，混入即假读数 → 单列根数，不参与线宽统计
        sw = [stks[pno][i]['w'] for i in inidx if stks[pno][i]['col'] is not None]
        pn = panel_bands(stks[pno], inidx, PT) if NPANEL.get(frag) else None
        pnf = [pymupdf.Rect(x) for x in pn] if pn else None
        if pnf:                                 # 逐子图含标框＝该带线框 ∪ 落带标签墨（按带心就近归属）
            for L in d['labs']:
                j = min(range(len(pnf)), key=lambda t: abs(
                    (L['ink'].x0 + L['ink'].x1) / 2 - (pnf[t].x0 + pnf[t].x1) / 2))
                pnf[j] |= L['ink']
        spw = pymupdf.open(m.SRC + sn)[0].rect.width / PT
        d.update(tag=tag, frag=frag, page=pno, boxmm=wbox, at=at, srcname=sn, sw=sw,
                 nfill=len(inidx) - len(sw), k_src=wbox / spw, lock=m.frag_lock(frag),
                 over=max(0.0, d['box'][0] - d['F'].x0, d['F'].x1 - d['box'][1]) / PT,
                 pnw=pn, pnf=pnf,
                 upF=(d['F'].y0 - d['up']['ink'].y1) / PT if d.get('up') else float('nan'),
                 dnF=(d['dn']['ink'].y0 - d['F'].y1) / PT if d.get('dn') else float('nan'),
                 devW=((d['W'].x0 + d['W'].x1) / 2 - d['cc']) / PT)
        rows.append(d)
    assert [(d['page'], d['col']) for d in rows] == [x[4] for x in m.MAP], '落位与台账不符'

    # ------------------------------------------------------------ 派生量
    for d in rows:
        msz = [L['sz'] for L in d['labs'] if is_letter(L['t'])]
        nsz = [L['sz'] for L in d['labs'] if not is_letter(L['t'])]
        med = statistics.median(msz)
        k, k70 = FONT_TARGET / med, FONT_FLOOR / med
        ww, wh = d['W'].width / PT, d['W'].height / PT
        fw, fh = d['F'].width / PT, d['F'].height / PT
        pl = [max(p.width, p.height) / PT for p in d['pnf']] if d['pnf'] else [max(fw, fh)]
        pw = [max(p.width, p.height) / PT for p in d['pnw']] if d['pnw'] else [max(ww, wh)]
        win = WIN_PARA if d['pnf'] else WIN_SINGLE
        cur = max(pl)
        r_ratio = cur / med                                  # mm/pt·与置宽无关
        r_lo, r_hi = win[0] / FONT_TARGET, win[1] / FONT_TARGET
        k_geo = min(1.0, r_hi / r_ratio) if r_ratio > r_hi else (
            min(k, r_lo / r_ratio) if r_ratio < r_lo else k)  # 落档所需总缩放（含 k_font）
        d.update(msz=msz, nsz=nsz, med=med, k=k, k70=k70, win=win,
                 ww=ww, wh=wh, fw=fw, fh=fh, cur=cur, pw_all=pw, ov=[a - b for a, b in zip(pl, pw)],
                 r=r_ratio, r_lo=r_lo, r_hi=r_hi,
                 new=cur * k, box_new=d['boxmm'] * k, box_new70=d['boxmm'] * k70,
                 Wn=(ww * k, wh * k), Fn=(fw * k, fh * k),
                 lw=statistics.median(d['sw']), lwn=statistics.median(d['sw']) / PT * k,
                 k_geo=k_geo, box_geo=d['boxmm'] * k_geo, new_geo=cur * k_geo)
        d['j_new'] = band_of(win, d['new'])
        d['j_cur'] = band_of(win, cur)
        d['j70'] = band_of(win, cur * k70)
        d['cls'] = 'A' if d['j_new'] == '档内' else ('B' if _feasible(d) else 'C')

    # ------------------------------------------------------------ 【一】逐图
    W('\n【一】逐图读数（标签字号逐个列全·线宽只统计描边件）')
    for d in rows:
        fd = frag_decl(m, d['frag'])
        W(' ── %s｜%s｜p%dc%d（body.tex L%d）｜置宽 %s（tex 实写 %s）｜素材自然幅 %.2fmm→声明同比 k %.4f｜画布锁定 %s'
         % (d['frag'], d['tag'], d['page'], d['col'], lines.get(d['frag'], 0),
            ('84.0mm(\\linewidth)' if d['boxmm'] == 84.0 else '%.1fmm' % d['boxmm']),
            decl.get(d['frag'], '?'), d['boxmm'] / d['k_src'], d['k_src'],
            ('%.2f×%.2fmm' % d['lock']) if d['lock'] else '无锁定'))
        W('    外廓｜线框 W %6.2f × %6.2f｜含标 F %6.2f × %6.2f｜长宽比 W %.2f F %.2f｜描边 %d 根＋填充 %d 件｜标签 %d（字母 %d＋圈号 %d）'
         % (d['ww'], d['wh'], d['fw'], d['fh'],
            max(d['ww'], d['wh']) / min(d['ww'], d['wh']), max(d['fw'], d['fh']) / min(d['fw'], d['fh']),
            len(d['sw']), d['nfill'], len(d['labs']), len(d['msz']), len(d['nsz'])))
        W('    字号｜字母标签 min/中位/max ＝ %.2f / %.2f / %.2f（档差 %.2f）｜片段 \\fontsize 声明 %s'
         % (min(d['msz']), d['med'], max(d['msz']), max(d['msz']) - min(d['msz']),
            '/'.join('%.2fpt' % v for v in fd['fonts']) or '（继承宿主）'))
        W('          逐个：' + '  '.join('%s=%.2f' % (L['t'].replace(' ', ''), L['sz']) for L in d['labs']))
        W('    圈号备注（不入主判据）：%s'
         % ('无' if not d['nsz'] else '另档 %.2f–%.2fpt ×%d（"%s"）→ 缩档时按同系数缩，落 %s；其档差与字母档不同，单列不混入中位数'
            % (min(d['nsz']), max(d['nsz']), len(d['nsz']),
               ' '.join(L['t'] for L in d['labs'] if not is_letter(L['t'])),
               ' / '.join('%.2fpt' % (v * d['k']) for v in (min(d['nsz']), max(d['nsz'])))))
        W('    线宽｜描边 pt min/中位/max ＝ %.3f/%.3f/%.3f｜mm ＝ %.3f/%.3f/%.3f｜片段 line width 声明 %s｜现 %.2fmm → %s（TW-05 %.2f±%.2f）'
         % (min(d['sw']), d['lw'], max(d['sw']), min(d['sw']) / PT, d['lw'] / PT, max(d['sw']) / PT,
            '/'.join('%.3fmm' % v for v in fd['lws']) or '—',
            d['lw'] / PT, side(d['lw'] / PT, LINE_TARGET_MM - LINE_TOL, LINE_TARGET_MM + LINE_TOL),
            LINE_TARGET_MM, LINE_TOL))
        if d['pnf']:
            W('    子图｜断带 %d（墨空档≥%.1fmm）逐带含标长边 %s mm｜逐带线框长边 %s｜标签外扩 %s'
             % (len(d['pnf']), GAP_PANEL,
                ' '.join('%.2f' % (max(p.width, p.height) / PT) for p in d['pnf']),
                ' '.join('%.2f' % v for v in d['pw_all']),
                ' '.join('%.2f' % v for v in d['ov'])))
            W('      带间空档 %s mm（合计 %.2f）'
             % (' '.join('%.2f' % ((d['pnf'][i + 1].x0 - d['pnf'][i].x1) / PT) for i in range(len(d['pnf']) - 1)),
                sum((d['pnf'][i + 1].x0 - d['pnf'][i].x1) / PT for i in range(len(d['pnf']) - 1))))
        W('    反解｜k_font(7.5) ＝ %.4f｜k_font(7.0) ＝ %.4f → 新置宽 %.1fmm（7.0 档 %.1fmm）｜新线框 %.2f×%.2f｜新含标 %.2f×%.2f'
         % (d['k'], d['k70'], d['box_new'], d['box_new70'], d['Wn'][0], d['Wn'][1], d['Fn'][0], d['Fn'][1]))
        W('    落档｜判据量（含标长边%s）现 %.2f %s → 缩后 %.2f %s（7.0 下限档 %.2f %s）｜副读：新含标宽基 %.2f｜新线框长边 %.2f'
         % ('/每子图max' if d['pnf'] else '', d['cur'], d['j_cur'], d['new'], d['j_new'],
            d['cur'] * d['k70'], d['j70'], d['fw'] * d['k'], max(d['ww'], d['wh']) * d['k']))
        W('    决策量 r %.3f mm/pt（窗 [%.3f, %.3f] → %s）｜新线宽 %.3fmm %s｜现缝 前%.2f/下%.2f｜栏心偏 %+.2f｜越盒 %.2f｜正文相交 %d'
         % (d['r'], d['r_lo'], d['r_hi'], side(d['r'], d['r_lo'], d['r_hi']), d['lwn'],
            side(d['lwn'], LINE_TARGET_MM - LINE_TOL, LINE_TARGET_MM + LINE_TOL),
            d['upF'], d['dnF'], d['devW'], d['over'], len(d.get('hits') or [])))
        W('    处置＝%s｜%s' % (d['cls'], _why(d)))

    # ------------------------------------------------------------ 【二】总表
    W('\n【二】缩档总表（逐图一行一列全；k＝7.5÷字母字号中位；判据量＝含标外廓长边，三联取逐子图 max）')
    W('片段|置宽mm|线框W宽×高|含标F宽×高|字母字号min/中位/max|圈号档|线宽中位pt|线宽中位mm|k7.5|k7.0|'
      '新置宽mm|新线框宽×高|新含标宽×高|判据量现→新|落档现→新|r(mm/pt)|处置')
    W('-' * 124)
    for d in rows:
        W('|'.join('%s' % x for x in [
            d['frag'], '%.1f' % d['boxmm'], '%.2f×%.2f' % (d['ww'], d['wh']),
            '%.2f×%.2f' % (d['fw'], d['fh']), '%.2f/%.2f/%.2f' % (min(d['msz']), d['med'], max(d['msz'])),
            ('%.2f–%.2f' % (min(d['nsz']), max(d['nsz']))) if d['nsz'] else '—',
            '%.3f' % d['lw'], '%.3f' % (d['lw'] / PT), '%.4f' % d['k'], '%.4f' % d['k70'],
            '%.1f' % d['box_new'], '%.2f×%.2f' % d['Wn'], '%.2f×%.2f' % d['Fn'],
            '%.2f→%.2f' % (d['cur'], d['new']), '%s→%s' % (d['j_cur'], d['j_new']),
            '%.3f %s' % (d['r'], side(d['r'], d['r_lo'], d['r_hi'])), d['cls']]))

    # ------------------------------------------------------------ 【三】处置反解
    W('\n【三】处置反解（A＝只改 \\resizebox 即双档同落；B＝缩放后仍不档，须让标签与几何脱钩；C＝B 亦无解→登记例外）')
    for d in rows:
        win = d['win']
        W('  %s〔%s〕' % (d['frag'], d['cls']))
        W('    A 只改置宽：k_font %.4f → 判据量 %.2f（窗 %.1f–%.1f）%s；新置宽 %.1fmm；新线宽 %.3fmm %s'
         % (d['k'], d['new'], win[0], win[1], d['j_new'], d['box_new'], d['lwn'],
            side(d['lwn'], LINE_TARGET_MM - LINE_TOL, LINE_TARGET_MM + LINE_TOL)))
        # B 的两条实现路：(b1) 守 7.5pt 字号、把"线框几何"单独收紧（标签不动）；(b2) 守外廓、把标签单独缩小
        c_need = 1.0 - (win[1] - max(d['ov']) * d['k']) / (max(d['pw_all']) * d['k'])
        b2_font = FONT_TARGET / (d['med'] * _kgeo(d))
        W('    B 脱钩路：(b1) 守字号 7.5pt、只压顶点间距 → 子图/整图**线框长边**需再收紧 %s（标签外扩 %.2fmm 不随缩，'
          '故所需收紧率略大于"判据量超档 %.1f%%"）'
         % ('%.1f%%' % (100 * c_need) if c_need > 0 else '0%（无需）', max(d['ov']) * d['k'],
            100 * max(0.0, 1 - win[1] / d['new'])))
        W('              (b2) 守外廓落档、只缩标签 → 置宽取 %.1fmm（档%s），片段 \\fontsize 需再 ×%.4f（件内有效字号 %.2fpt→7.50pt）；'
          '此时件内线宽 %.3fmm，片段 line width 需再 ×%.4f 方回 TW-05'
         % (d['box_geo'], '上沿' if d['r'] > d['r_hi'] else ('下沿' if d['r'] < d['r_lo'] else '（等比即可）'),
            b2_font, d['med'] * _kgeo(d), d['lw'] / PT * _kgeo(d),
            LINE_TARGET_MM / (d['lw'] / PT * _kgeo(d))))
        W('    C 例外检验：%s' % _why(d))

    # ------------------------------------------------------------ 【四】影响面
    W('\n【四】改件影响面（本轮不动手，仅供改件轮照单执行）')
    W('  ① body.tex \\resizebox 置宽（六处·唯一必动项）：')
    for d in rows:
        W('     %-11s L%-4d  %s → %.1fmm（A 等比解）%s'
         % (d['frag'], lines.get(d['frag'], 0),
            '%.1fmm' % d['boxmm'] if d['boxmm'] != 84.0 else '\\linewidth(84.0mm)', d['box_new'],
            '' if d['cls'] == 'A' else '｜若走 B(b2) 档内解 → %.1fmm＋片段字号 ×%.3f' % (d['box_geo'], b2f(d))))
    W('  ② 门值必改（_测v4断言.py）：')
    W('     ⑱ tex 形制门 FIG_W（L294–295）六档逐图钉死 → 必改，否则 ⑱ 直接红；')
    W('     ⑱-2 K_MAP boxmm（L744–751）六值 → 必改（声明盒/越盒门/置宽复算三处挂钩）；')
    W('     ⑱-2 前距窗 [1.99,4.14]／下距窗 [2.04,4.36]（含标基·实测极值±0.25 垫）→ 必重标：图缩矮则上下缝只增不减；')
    W('        现读 前距 %s' % ' '.join('%s=%.2f' % (x['frag'][:2], x['upF']) for x in rows))
    W('        现读 下距 %s' % ' '.join('%s=%.2f' % (x['frag'][:2], x['dnF']) for x in rows))
    W('        等比缩后 F 高变化量（近似＝原高×(k−1)·缝另受分页影响，须实测重标）：%s'
     % ' '.join('%s=%+.2f' % (x['frag'][:2], x['fh'] * (x['k'] - 1)) for x in rows))
    W('     ⑱-2 Δ线框≤0.50mm（素材×k 同比）：k 变→素材侧标签认领半径按 1/k 放大，线框基与 k/字体均无关 → 预期仍绿；')
    W('        但素材 standalone 页宽是 k 的分母，若同步改片段 \\fontsize 使自然外框变化 → k 变 → Δ 须重跑；')
    W('     ⑱-2 越声明盒≤0.30mm：现 %s（等比缩放按比例同缩，预期仍绿；g1/g5 贴 0.23/0.25 须重跑确认）；'
     % ' '.join('%s=%.2f' % (x['frag'][:2], x['over']) for x in rows))
    W('     ⑱-2 栏心偏±1.45（线框基 %s）：同比保心 → 不变；' % ' '.join('%s=%+.2f' % (x['frag'][:2], x['devW']) for x in rows))
    W('     ⑱-2 g5 无锁定不变量第三项 |含标宽−声明置宽|≤0.30mm：与置宽直接挂钩 → 必重跑（现 %.2fmm）；'
     % abs(rows[5]['fw'] - rows[5]['boxmm']))
    W('     ⑱-2 硬门 标签数件内==素材／虚线保真率≥0.99（现 min 1.000）／正文相交=0：与缩放无关或同向变好；')
    W('     ⑱-3 图旁零文字＋上下邻行在场：下置形态不变；')
    W('     N6 六图落位（页,栏）＋⑮ 探究点归属＋断言顶格.py：图高变化＝竖向腾量 %s，合计 %+.2fmm → 分页可能移动，'
      '三套断言全量须重跑（尤其跨页题组）；'
     % (' '.join('%s=%+.2f' % (x['frag'][:2], -x['wh'] * (1 - x['k'])) for x in rows),
        sum(-x['wh'] * (1 - x['k']) for x in rows)))
    W('  ③ 走 B（改片段）附加面：figs/%s 的 \\fontsize／顶点坐标 → 素材 standalone（_tmp片G素材/%s）须同步重导，'
      '否则同比含标列失效（线框列不受影响）；' % ('/*.tikz', '*.pdf'))
    W('  ④ 留痕：改前按规格第四节备份 .bak_缩档0910；禁 git；本轮不新建测试文件。')
    W('  ⑤ 关联账（附则/全品基准总表.md L47）「全品图内标签 31–33px／我方 23–24px 差 ~35%」＝位图时代 px 口径；'
      '本片已纯 TikZ 矢量，改件后应以本表 pt 直读（目标 7.5pt±0.3）替换该 px 账——登记动作归主脑，本轮不改附则。')
    return _flush(out)


def _kgeo(d):
    """落档所需总缩放系数（含 k_font 方向）：r 超上沿→压到上沿；r 破下沿→不得使判据量低于下沿。"""
    if d['r'] > d['r_hi']:
        return d['r_hi'] / d['r']
    if d['r'] < d['r_lo']:
        return min(d['k'], d['r_lo'] / d['r'])
    return d['k']


def b2f(d):
    return FONT_TARGET / (d['med'] * _kgeo(d))


def _feasible(d):
    """B 可行性：r 在「守 7.5pt 时外廓仍可达档」的区间内——即存在缩放 s 使 s·cur∈窗 且 s·med≥7.0。"""
    s_lo = max(WIN_FLOOR_K(d), d['win'][0] / d['cur'])
    s_hi = d['win'][1] / d['cur']
    return s_lo <= s_hi


def WIN_FLOOR_K(d):
    return FONT_FLOOR / d['med']


def _why(d):
    win = d['win']
    if d['cls'] == 'A':
        return ('双档一次同落（r %.3f ∈ 窗）' % d['r'] if d['j_new'] == '档内' else '')
    if d['r'] > d['r_hi']:
        return ('r %.3f 超窗上沿 %.3f → 单靠 \\resizebox 会把字号拖破 %.1fpt 下限；须收紧几何 '
                '（在 k_font %.4f 解之上，判据量仍 %.2f 超档 %.1f%%）'
         % (d['r'], d['r_hi'], FONT_FLOOR, d['k'], d['new'], 100 * (1 - win[1] / d['new'])))
    if d['r'] < d['r_lo']:
        return ('r %.3f 破窗下沿 %.3f → 守 7.5pt 时外廓只能缩到 %.2f（<%.1f）；等比解＝缩过头，'
                '取档下沿解须让标签与几何脱钩（片段 \\fontsize ×%.3f）'
         % (d['r'], d['r_lo'], d['new'], win[0], b2f(d)))
    return 'r 在窗内但判据量未落档（数值边界）→ 复核 r 窗常数'


def _flush(out):
    txt = '\n'.join(out)
    io.open(OUT, 'w', encoding='utf-8', newline='\n').write(txt + '\n')
    print(txt)
    return 0


if __name__ == '__main__':
    sys.exit(main())
