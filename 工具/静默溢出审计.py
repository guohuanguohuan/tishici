# -*- coding: utf-8 -*-
r"""静默溢出审计.py — [D] 门脚本：「零高固定栏承件族」静默溢出审计（军师收口轮0913 §九钉①：
静默失效类必须有负测，脚本化入冒烟与正装门）。

背景：零高 \jpcol（\raisebox{0pt}[0pt][0pt]{\vtop…}）结构下内容出栏出纸 TeX 零报错——
P1 测评案A 实测丢 题6/12 答案块（印面无文本、log 无 Error、无 Overfull），属静默失效。
本脚本对该族 tex 件做三层读数并抓红旗：

  ①静态扫描（tex，含 \input/\include 链）：承件族判定（零高固定栏／手工固定栏／
    multicol 可回流／非承件）＋几何解析（paperheight／边距／\jpcolw／\jpgap→栏带）
    ＋键账（% ans: 注释锚 ↔ \begin{ansblock}[键] 编译锚，对集合）＋档向
    （\showanstrue/false、\def\mthreepure、[pure] 选项）。
  ②编译 log 解析（同名 .log 自动发现）：Error／Overfull hbox·vbox／Missing character／
    页数＋M3-ANSKEY 键集合（恒发两档；tex 有块而 log 无键＝编译层吞块红旗——
    块根本没被排版，比印面丢块更早一层）。
  ③印面提取（同名 .pdf 自动发现）：逐页逐栏内容底边（文本∪图∪矢量线，剔页脚签名带）
    vs 纸边（页高硬线）＝出纸读数；「常规取文」vs「无限裁剪取文」双读——键印面缺失
    且无限裁剪也缺失＝内容流丢失（实锤）；常规缺而无限在＝印在纸外（出纸）。
    [答案] 区计数/数号集合 vs 键账集合＝答案块静默丢失红旗（ansblock 在源、印面无文本
    而 TeX 零报错，必逮）。

档位：--grade zero-fp（默认，正装门/冒烟用）：出纸、印面丢块、log 吞块＝FAIL；
      触页脚带（纸高−redfoot）＝WARN 登记不判死（PL1/PL2 冻结卷式原印面固有触带，如
      P1 基线 p1 栏2 底 280.5mm，零误报口径）。
      --grade strict（印前严档）：触页脚带亦 FAIL。两档下出纸/丢块恒 FAIL。
负测自测：--selftest 在临时目录合成静默丢失样本（印面丢块／出纸／log 吞块三负例＋
      健康正例＋false 档正例），断言真拦真放行；系统临时目录内读写，不落项目树。
用法: python 工具/静默溢出审计.py <tex文件>… [--grade zero-fp|strict] [--out 报告.txt]
      [--pdf 覆盖] [--log 覆盖] [--no-pdf] [--redfoot-mm 7.2] [--tol-mm 0.05]
      [--footer-re 正则] [--selftest]
  默认逐件自动发现同目录同名 .log/.pdf；--pdf/--log 仅对单件生效。
退出码: 0＝全过（WARN 不算失败）；1＝有红旗；2＝用法/输入错；selftest 断言不过＝1。
红线: 全部输入只读；零 git；--out 报告与 selftest 临时件除外不写任何处。
"""
import argparse
import io
import os
import re
import sys
import tempfile

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import pymupdf
except ImportError:      # 旧版 PyMuPDF 兼容（视觉回归.py 同制）
    import fitz as pymupdf

MM2PT = 72 / 25.4
DEF_REDFOOT_MM = 7.2     # 页脚带高＝纸边上推 7.2mm（P1 实测 284.2−277.0 同源）
DEF_TOL_MM = 0.05        # 出纸判定容差（对勘-P1测评 BOT+0.05 同源）
# 页脚签名带文字（对勘 FOOT_SIG 并集泛化）：底部带内命中＝豁免条，仅出纸层仍全量检
DEF_FOOTER_RE = (r'卷0\d|卷\d{2}|羿郭|工作室|编制|审核|校对|印装|RJB'
                 r'|必修第?[一二三四]册|选择性必修|高中数学|高中物理')
RE_COMMENT = re.compile(r'(?<!\\)%.*$')
RE_INPUT = re.compile(r'\\(?:input|include)\{([^}]+)\}')
RE_ZHF = re.compile(r'\\raisebox\s*\{\s*0pt\s*\}\s*\[\s*0pt\s*\]\s*\[\s*0pt\s*\]\s*\{\s*\\vtop')
RE_DEFMAC = re.compile(r'\\(?:re|provide)?newcommand\{?\\([A-Za-z@]+)\}?')
RE_ENVKEY = re.compile(r'\\begin\{ansblock\}\[([^\]]+)\]')
RE_PCTKEY = re.compile(r'%\s*ans:(\S+)')
RE_ANSKEY = re.compile(r'M3-ANSKEY:\s*(\S+)')
RE_NUMZONE = re.compile(r'(\d{1,3})[.\uFF0E]\s*\[答案\]')
RE_MODE = re.compile(r'\\showans(true|false)|\\def\\mthreepure\{([01])\}|\\usepackage\s*\[([^\]]*pure[^\]]*)\]\{qp-m3p')
RE_GEOM = re.compile(r'\\geometry\{([^}]*)\}')
RE_DIMSET = re.compile(r'\\setlength\{\\(jpcolw|jpgap)\}\{([0-9.]+)mm\}')


def _read(path):
    with open(path, encoding='utf-8-sig', errors='replace') as fh:
        return fh.read()


def strip_comment(line):
    return RE_COMMENT.sub('', line.rstrip('\n')).rstrip()


# ---------------- ① 静态扫描 ----------------

def load_tex(path, seen=None, depth=0, lines=None):
    r"""展平 \input/\include 链；lines=[(file, lineno, raw, code)]。"""
    if seen is None:
        seen, lines = set(), []
    ap = os.path.abspath(path)
    if ap in seen or depth > 6:
        return lines, seen
    seen.add(ap)
    try:
        raws = _read(ap).splitlines()
    except OSError as e:
        print(f'[FAIL] 读 tex 失败 {path}: {e}')
        return lines, seen
    for i, raw in enumerate(raws, 1):
        code = strip_comment(raw)
        lines.append((ap, i, raw, code))
        if depth < 6:
            for m in RE_INPUT.finditer(code):
                sub = m.group(1)
                if not sub.endswith('.tex'):
                    sub += '.tex'
                cand = os.path.join(os.path.dirname(ap), sub)
                if os.path.isfile(cand):
                    load_tex(cand, seen, depth + 1, lines)
    return lines, seen


def judge_family(lines):
    """承件族判定。返回 (判定串, 是否固定栏承件, 证据列表)。"""
    zh = []           # 零高 \jpcol 定义行
    vtop_h = []       # 手工 \hbox to…\vtop（非零高但固定宽不可回流）
    mcols = []
    macnames = set()
    for f, n, raw, code in lines:
        if RE_ZHF.search(code):
            zh.append((f, n))
            m = RE_DEFMAC.search(code)
            if m:
                macnames.add(m.group(1))
        elif '\\vtop' in code and '\\hbox to' in code:
            vtop_h.append((f, n))
        if '\\begin{multicols}' in code or '\\end{multicols}' in code:
            mcols.append((f, n))
    base = os.path.basename(lines[0][0]) if lines else '?'
    ev = [f'{os.path.basename(f)}:{n}' for f, n in (zh or vtop_h)[:4]]
    calls = sum(1 for _, _, _, c in lines if '\\jpthree{' in c or '\\jptwo{' in c)
    if zh:
        return ('零高固定栏承件族（静默高危）', True,
                ev + [f'\\jpcol 宏名={sorted(macnames) or "inline"} 三栏排布行×{calls}'])
    if vtop_h:
        return ('手工固定栏承件（不可回流）', True, ev)
    if mcols:
        return ('multicol 可回流栏（非静默族：出栏 TeX 报 Overfull \\vbox）', False,
                [f'{os.path.basename(f)}:{n}' for f, n in mcols[:4]])
    return ('非固定栏承件', False, [f'判定基础={base}'])


def parse_geom(lines):
    """几何：paper w/h、左边距、栏宽、栏距、栏数。缺项回退 8 开横放三栏 house 默认。"""
    g = {'pw': 399.8, 'ph': 284.2, 'left': 8.9, 'colw': 120.0, 'gap': 11.0, 'ncols': 3}
    src = {'pw': '默认', 'ph': '默认', 'left': '默认', 'colw': '默认', 'gap': '默认', 'ncols': '默认'}
    for _, _, _, code in lines:
        m = RE_GEOM.search(code)
        if m:
            for key, pat in (('pw', r'paperwidth=([0-9.]+)mm'), ('ph', r'paperheight=([0-9.]+)mm'),
                             ('left', r'left=([0-9.]+)mm')):
                mm2 = re.search(pat, m.group(1))
                if mm2:
                    g[key] = float(mm2.group(1))
                    src[key] = '\\geometry'
        for mm2 in RE_DIMSET.finditer(code):
            k = {'jpcolw': 'colw', 'jpgap': 'gap'}[mm2.group(1)]
            g[k] = float(mm2.group(2))
            src[k] = 'setlength'
        m2 = re.search(r'\\newcommand\{?\\jpthree\}?.*\{\\jpcol\{#1\}.*', code)
        if m2:
            g['ncols'] = code.count('\\jpcol{#') or 3
            src['ncols'] = 'jpthree定义'
    bands = []
    x = g['left']
    for k in range(g['ncols']):
        bands.append((x, x + g['colw']))
        x += g['colw'] + g['gap']
    return g, bands, src


def scan_keys(lines):
    """键账与档向：% ans:（注释锚）↔ \\begin{ansblock}[键]（编译锚）对集合。"""
    env, pct, order = [], [], []
    mode = None
    for _, _, raw, code in lines:
        for m in RE_ENVKEY.finditer(code):
            k = m.group(1).strip()
            if k not in env:
                env.append(k)
                order.append(k)
        for m in RE_PCTKEY.finditer(raw):
            k = m.group(1).strip()
            if k not in pct:
                pct.append(k)
        m = RE_MODE.search(code)
        if m:
            if m.group(1):
                mode = 'true' if m.group(1) == 'true' else 'false'
            elif m.group(2) is not None:
                mode = 'false' if m.group(2) == '1' else 'true'
            elif m.group(3):
                mode = 'false'
    return env, pct, mode


def keynum(k):
    m = re.search(r'(\d+)\s*$', k)
    return int(m.group(1)) if m else None


# ---------------- ② log 解析 ----------------

def parse_log(path):
    txt = _read(path)
    r = {}
    r['error'] = len(re.findall(r'^! ', txt, re.M)) + len(re.findall(r'LaTeX Error:', txt))
    r['ohbox'] = len(re.findall(r'Overfull \\hbox', txt))
    r['ovbox'] = len(re.findall(r'Overfull \\vbox', txt))
    r['uvbox'] = len(re.findall(r'Underfull \\vbox', txt))
    r['misschar'] = len(re.findall(r'Missing [Cc]haracter', txt))
    r['anks'] = RE_ANSKEY.findall(txt)
    m = re.search(r'Output written on .*?\((\d+) page', txt)
    r['pages'] = int(m.group(1)) if m else None
    return r


# ---------------- ③ 印面提取 ----------------

def pdf_face(pdfpath, bands, g, foot_re, tol_pt, redfoot_pt):
    """返回读数 dict：colmax/footmax 逐页逐栏（含无限裁剪）、越纸条、答案区、越栏统计。"""
    d = pymupdf.open(pdfpath)
    pw, ph = (d[0].rect.width, d[0].rect.height) if d.page_count else (g['pw'] * MM2PT, g['ph'] * MM2PT)
    footre = re.compile(foot_re)
    red_pt = ph - redfoot_pt
    norm_txt, inf_txt = [], []
    colmax = {}       # (page, col) -> 常规底
    colmax_inf = {}   # (page, col) -> 含无限裁剪底
    footmax = {}      # (page, col) -> 页脚带内豁免条最大底
    offp = []         # 越纸条 (page, col|'越栏', y1mm, kind)
    noutband = 0
    def bandof(x0, x1):
        cx = (x0 + x1) / 2 / MM2PT
        for c, (a, b) in enumerate(bands, 1):
            if a - 2 <= cx <= b + 2:
                return c
        return None
    for i, pg in enumerate(d, 1):
        norm_txt.append(pg.get_text())
        try:
            inf_txt.append(pg.get_text(clip=pymupdf.INFINITE_RECT()))
        except Exception:
            inf_txt.append(pg.get_text())
        cm = {c: 0.0 for c in range(1, len(bands) + 1)}
        cmi = dict(cm)
        fm = dict(cm)
        items = []      # (x0,y0,x1,y1,kind,签名命中)
        for b in pg.get_text('blocks'):
            items.append((b[0], b[1], b[2], b[3], '文', bool(footre.search(b[4]))))
        for b in pg.get_text('blocks', clip=pymupdf.INFINITE_RECT()):
            items.append((b[0], b[1], b[2], b[3], '文(裁外)', bool(footre.search(b[4]))))
        for im in pg.get_image_info():
            items.append((*im['bbox'], '图', False))
        for dd in pg.get_drawings():
            r0 = dd['rect']
            items.append((r0.x0, r0.y0, r0.x1, r0.y1, '线', False))
        seen = set()
        for x0, y0, x1, y1, kind, sig in items:
            kkey = (round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1), kind)
            if kkey in seen:
                continue
            seen.add(kkey)
            c = bandof(x0, x1)
            over = y1 > ph + tol_pt
            if over:
                offp.append((i, c if c else '越栏', y1 / MM2PT, kind))
            if c is None:
                noutband += 1
                continue
            # 页脚签名带豁免（出纸条先入 offp，永不丢读数）：文字条＝命中签名正则且底在
            # 纸下缘 25mm 带内；图/线＝底部 20mm 带内且居纸两端缘（品牌框线，对勘同制）
            foot = ((not over) and sig and y1 > ph - 25 * MM2PT) or \
                   (kind in ('图', '线') and y0 > ph - 20 * MM2PT and
                    (x1 < 80 * MM2PT or x0 > pw - 70 * MM2PT))
            if foot:
                fm[c] = max(fm[c], y1)
                continue
            cm[c] = max(cm[c], y1)
            cmi[c] = max(cmi[c], y1)
        colmax[i] = {c: v / MM2PT for c, v in cm.items()}
        colmax_inf[i] = {c: v / MM2PT for c, v in cmi.items()}
        footmax[i] = {c: v / MM2PT for c, v in fm.items()}
    alln = '\n'.join(norm_txt)
    alli = '\n'.join(inf_txt)
    return {
        'doc': d, 'ph_mm': ph / MM2PT, 'pw_mm': pw / MM2PT,
        'norm': alln, 'infinite': alli,
        'ans_n': alln.count('[答案]'), 'ans_i': alli.count('[答案]'),
        'nums_n': sorted({int(x) for x in RE_NUMZONE.findall(alln)}),
        'nums_i': sorted({int(x) for x in RE_NUMZONE.findall(alli)}),
        'colmax': colmax, 'colmax_inf': colmax_inf, 'footmax': footmax,
        'offpaper': offp, 'outband': noutband, 'pages': d.page_count,
    }


# ---------------- 单件审计 ----------------

def audit_piece(tex, cfg, pdf=None, log=None):
    rep = []
    nfail = nwarn = 0
    def red(msg):
        nonlocal nfail
        nfail += 1
        rep.append(f'  [红旗] {msg}')
    def warn(msg):
        nonlocal nwarn
        nwarn += 1
        rep.append(f'  [警告] {msg}')
    def info(msg):
        rep.append(f'  {msg}')
    lines, seen = load_tex(tex)
    if not lines:
        return [f'[件] {tex}', '  [红旗] tex 读取失败'], 1, 0
    fam, fixed, ev = judge_family(lines)
    g, bands, gsrc = parse_geom(lines)
    env, pct, mode_src = scan_keys(lines)
    rep.append(f'[件] {tex}')
    info(f'承件族判定：{fam}｜证据 {"；".join(ev)}')
    keys = env or pct
    senv, spct = set(env), set(pct)
    if keys:
        miss_pct = senv - spct
        miss_env = spct - senv
        if miss_pct or miss_env:
            red(f'锚账不齐：% ans:缺 {sorted(miss_env) or "—"}｜ansblock缺 {sorted(miss_pct) or "—"}')
        else:
            info(f'锚账：键 {len(senv | spct)} 集合 % ans:↔ansblock 对平 ✓（档向源={"tex明记 " + mode_src if mode_src else "未记·印面推断"}）')
    # —— log ——
    lg = None
    logp = log or os.path.splitext(tex)[0] + '.log'
    if os.path.isfile(logp):
        lg = parse_log(logp)
        info(f'log：Error {lg["error"]}｜Overfull h/v {lg["ohbox"]}/{lg["ovbox"]}｜Underfull vbox {lg["uvbox"]}'
             f'｜Missing char {lg["misschar"]}｜页数 {lg["pages"]}｜M3-ANSKEY {len(set(lg["anks"]))} 键')
        if lg['error']:
            red(f'编译报错 Error×{lg["error"]}（非静默，正常红）')
        if lg['ovbox'] and fixed:
            warn(f'零高栏下仍现 Overfull \\vbox×{lg["ovbox"]}（疑非零高路径或 \\jpcol 外容器，登记目验）')
        if keys and lg['anks'] is not None:
            lset = set(lg['anks'])
            lost = set(keys) - lset
            extra = lset - set(keys)
            if lost:
                red(f'编译层吞块：tex 有 ansblock 而 log 无 M3-ANSKEY：键 {sorted(lost)}（块未进排版即丢，静默）')
            if extra:
                warn(f'log 有幻影键（tex 无对应块）：键 {sorted(extra)}')
    else:
        info('log：未找到（跳过编译层读数）')
    # —— pdf ——
    pdfp = None if cfg['no_pdf'] else (pdf or os.path.splitext(tex)[0] + '.pdf')
    if pdfp and os.path.isfile(pdfp):
        face = pdf_face(pdfp, bands, g, cfg['footer_re'], cfg['tol_pt'], cfg['redfoot_pt'])
        phh = face['ph_mm']
        red_line = phh - cfg['redfoot_pt'] / MM2PT
        info(f'印面：页数 {face["pages"]}｜纸面 {face["pw_mm"]:.1f}×{phh:.1f}mm（纸边硬线 {phh:.1f}｜脚带线 {red_line:.1f}）'
             f'｜[答案]×{face["ans_n"]}（无限裁剪层×{face["ans_i"]}）｜键档向={mode_src or "推断"}')
        silent = not lg or lg['error'] == 0
        # 越纸绝对红（豁免逻辑不可遮蔽）：栏内出纸条＝红；越栏出纸条＝警告（页框/品牌件）
        opp = {}
        obv = 0
        for i, c, y, k in face['offpaper']:
            if c == '越栏':
                obv += 1
            else:
                opp[(i, c)] = max(opp.get((i, c), 0.0), y)
        for (i, c), y in sorted(opp.items()):
            red(f'p{i} 栏{c} 内容出纸：越纸条峰值 {y - phh:.1f}mm（底 {y:.1f}mm＞纸边 {phh:.1f}，'
                f'页脚豁免不可遮）{"（TeX Error 0＝静默溢出）" if silent else ""}')
        if obv:
            warn(f'越栏出纸条×{obv}（栏外墨过纸边——疑 \\linewidth 未随栏宽类出栏坑，登记）')
        # 栏底边（出纸红已由越纸条绝对红兜底，此处只做读数与触脚带判旗）
        for i in sorted(face['colmax_inf']):
            row = face['colmax_inf'][i]
            marks = []
            for c, y in sorted(row.items()):
                if y > phh + cfg['tol_pt'] / MM2PT:
                    marks.append(f'栏{c}!!出纸{y - phh:.1f}(底{y:.1f})')
                elif y > red_line:
                    tag = '!!' if cfg['grade'] == 'strict' else '旗:'
                    if cfg['grade'] == 'strict':
                        red(f'p{i} 栏{c} 底 {y:.1f}mm 触页脚带（{red_line:.1f}~{phh:.1f}）·严档判死')
                    else:
                        warn(f'p{i} 栏{c} 底 {y:.1f}mm 触页脚带（{red_line:.1f}~{phh:.1f}）·零误报档登记')
                    marks.append(f'{tag}触脚带{c}({y:.1f})')
            rowtxt = ' '.join(f'栏{c}:{v:.1f}' for c, v in sorted(row.items()))
            if marks or cfg['verbose']:
                info(f'  p{i} 栏底 {rowtxt} {" ".join(marks)}')
        if face['footmax']:
            fz = max((v for pgm in face['footmax'].values() for v in pgm.values()), default=0.0)
            if fz > 0:
                info(f'  页脚签名带豁免条最大底 {fz:.1f}mm（不计栏底）')
        if face['offpaper']:
            kinds = {}
            for i, c, y, k in face['offpaper']:
                kinds[k] = max(kinds.get(k, 0.0), y)
            info(f'  越纸条峰值：' + '｜'.join(f'{k} {v:.1f}mm' for k, v in sorted(kinds.items()))
                 + f'｜越栏条 {face["outband"]}（含页框/品牌件）')
        # 答案区静默丢失
        knum = {}
        ambig = False
        for k in keys:
            n = keynum(k)
            if n is None:
                ambig = True
                continue
            if n in knum:
                ambig = True
            knum[n] = k
        printed_n = set(face['nums_n'])
        printed_i = set(face['nums_i'])
        if face['ans_i'] == 0 and face['ans_n'] == 0:
            if keys and mode_src == 'true':
                red(f'案卷标 true 档而印面 [答案]×0——整册答案静默蒸发（键 {len(set(keys))} 个全丢）')
            else:
                info('印面 [答案]×0 → 判纯题档（false）：答案区应零，PASS 口径')
        elif keys and not ambig:
            missing = sorted(set(knum) - printed_n)
            if missing:
                detail = []
                for n in missing:
                    where = '印在纸外(无限裁剪层可见)' if n in printed_i else '内容流整块丢失(无限裁剪层亦无)'
                    detail.append(f'{n}[{knum[n]}]·{where}')
                red(f'印面答案块静默丢失 {len(missing)}/{len(knum)}：{"；".join(detail)}'
                    f'（tex 有 ansblock 而 PDF 对应区无文本{"，且 TeX Error 0＝静默" if silent else ""}）')
            ghost = sorted(printed_n - set(knum))
            if ghost:
                warn(f'印面幻影答案区（键账无此号）：{ghost}')
        elif keys and face['ans_n'] < len(set(keys)):
            warn(f'答案区计数 {face["ans_n"]} < 键数 {len(set(keys))}（键含多区块等数号歧义，降级对数）')
    elif pdfp:
        info(f'印面：未找到 {os.path.basename(pdfp) or "pdf"}（跳过印面读数——静默丢失须有 pdf 方可实锤）')
    rep.append(f'  判定：{"FAIL 红旗" + str(nfail) + " 警告" + str(nwarn) if nfail else "PASS（警告 " + str(nwarn) + "）"}')
    return rep, nfail, nwarn


# ---------------- 负测/正测自测 ----------------

def _skeleton_tex(keys, body_extra=''):
    n = len(keys)
    colargs = []
    for chunk in range(min(n, 3)):
        seg = []
        for j, k in enumerate(keys):
            if j % 3 != chunk:
                continue
            num = keynum(k)
            seg.append(f'  题{num}．设问行若干。\n  % ans:{k}\n  \\begin{{ansblock}}[{k}]\n  \\end{{ansblock}}\n')
        colargs.append('\n'.join(seg))
    while len(colargs) < 3:
        colargs.append('  （空栏）\n')
    return ('\\documentclass[UTF8]{ctexart}\n'
            '\\usepackage{geometry}\n'
            '\\geometry{paperwidth=399.8mm,paperheight=284.2mm,left=8.9mm,right=8.9mm,top=6mm,bottom=6mm}\n'
            '\\newlength{\\jpcolw}\\setlength{\\jpcolw}{120.0mm}\n'
            '\\newlength{\\jpgap}\\setlength{\\jpgap}{11.0mm}\n'
            '\\newcommand{\\jpcol}[1]{\\raisebox{0pt}[0pt][0pt]{\\vtop{\\hsize\\jpcolw\\parskip0pt\\parindent0pt #1}}}\n'
            '\\newcommand{\\jpthree}[3]{\\nointerlineskip\\noindent\\jpcol{#1}\\hspace{\\jpgap}\\jpcol{#2}%\n'
            '  \\hspace{\\jpgap}\\jpcol{#3}\\par}\n'
            '\\begin{document}\n'
            '\\jpthree{\n' + colargs[0] + '}{\n' + colargs[1] + '}{\n' + colargs[2] + '}\n'
            + body_extra + '\\end{document}\n')


def _synth_pdf(pdfpath, nums, drop=(), offpaper=(), foot=True):
    d = pymupdf.open()
    pg = d.new_page(width=399.8 * MM2PT, height=284.2 * MM2PT)
    for n in nums:
        if n in drop:
            continue
        y = 340.0 if n in offpaper else 60.0 + 14 * n
        pg.insert_text((20 * MM2PT, y * MM2PT), f'{n}. [答案] 值{n}', fontname='china-s', fontsize=10.5)
    if 99 not in drop:
        pg.insert_text((340 * MM2PT, 274 * MM2PT), '单元测评卷（一）卷01', fontname='china-s', fontsize=8)
    for n in offpaper:
        pg.draw_rect(pymupdf.Rect(140 * MM2PT, 300 * MM2PT, 250 * MM2PT, 301 * MM2PT), color=(.48, .48, .48))
    d.save(pdfpath)
    d.close()


def _synth_log(logpath, keys, drop=()):
    with open(logpath, 'w', encoding='utf-8') as fh:
        fh.write('This is XeTeX... (synthetic)\n')
        for k in keys:
            if keynum(k) not in drop:
                fh.write(f'M3-ANSKEY: {k}\n')
        fh.write('Output written on synth.pdf (1 page).\n')


def selftest(cfg):
    """负测真拦＋正测真放行。返回 (n_ok, n_bad)。"""
    cases = []
    with tempfile.TemporaryDirectory(prefix='静默溢出审计-selftest-') as td:
        ks = [f'测-{i}' for i in range(1, 6)]
        # N1 印面丢块（内容流无）——必须拦
        t1 = os.path.join(td, 'n1.tex'); open(t1, 'w', encoding='utf-8').write(_skeleton_tex(ks))
        _synth_pdf(os.path.join(td, 'n1.pdf'), [1, 2, 3, 4, 5], drop={3})
        _synth_log(os.path.join(td, 'n1.log'), ks)
        cases.append(('N1 印面静默丢块', t1, True))
        # N2 出纸（印在纸外+线越纸）——必须拦
        t2 = os.path.join(td, 'n2.tex'); open(t2, 'w', encoding='utf-8').write(_skeleton_tex(ks))
        _synth_pdf(os.path.join(td, 'n2.pdf'), [1, 2, 3, 4, 5], offpaper={5})
        _synth_log(os.path.join(td, 'n2.log'), ks)
        cases.append(('N2 出纸越界', t2, True))
        # N3 编译层吞块（log 无键）——必须拦
        t3 = os.path.join(td, 'n3.tex'); open(t3, 'w', encoding='utf-8').write(_skeleton_tex(ks))
        _synth_pdf(os.path.join(td, 'n3.pdf'), [1, 2, 3, 4, 5])
        _synth_log(os.path.join(td, 'n3.log'), ks, drop={4})
        cases.append(('N3 log 吞块', t3, True))
        # P0 健康件——必须放行
        t0 = os.path.join(td, 'p0.tex'); open(t0, 'w', encoding='utf-8').write(_skeleton_tex(ks))
        _synth_pdf(os.path.join(td, 'p0.pdf'), [1, 2, 3, 4, 5])
        _synth_log(os.path.join(td, 'p0.log'), ks)
        cases.append(('P0 健康 true 档', t0, False))
        # P1 纯题档（印面零答案）——必须放行
        tp = os.path.join(td, 'p1.tex')
        open(tp, 'w', encoding='utf-8').write(_skeleton_tex(ks).replace('\\begin{document}',
            '\\showansfalse\n\\begin{document}'))
        _synth_pdf(os.path.join(td, 'p1.pdf'), [1, 2, 3, 4, 5], drop={1, 2, 3, 4, 5})
        _synth_log(os.path.join(td, 'p1.log'), ks)
        cases.append(('P1 纯题档零答案', tp, False))
        # P2 无键非承件健康——必须放行
        t2b = os.path.join(td, 'p2.tex')
        open(t2b, 'w', encoding='utf-8').write('\\documentclass{article}\n\\begin{document}plain\n\\end{document}\n')
        pymupdf.open(); d = pymupdf.open(); pg = d.new_page(); d.save(t2b.replace('.tex', '.pdf')); d.close()
        cases.append(('P2 非承件无键', t2b, False))
        nok = nbad = 0
        for name, tex, expect_fail in cases:
            rep, nf, nw = audit_piece(tex, cfg)
            caught = nf > 0
            ok = caught == expect_fail
            nok += ok
            nbad += (not ok)
            print(f'[selftest {"PASS" if ok else "FAIL"}] {name}：红旗{nf} 警告{nw}'
                  f'（期望{"拦" if expect_fail else "放"}）')
            if not ok:
                for ln in rep:
                    print('   ', ln)
    print(f'—— selftest 读数：负测真拦 {sum(1 for c in cases if c[2])} 例／正测真放 '
          f'{sum(1 for c in cases if not c[2])} 例——全 {nok} 过，挂 {nbad} ——')
    return nok, nbad


# ---------------- 主流程 ----------------

def main(argv):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument('tex', nargs='*')
    ap.add_argument('--pdf')
    ap.add_argument('--log')
    ap.add_argument('--grade', choices=('zero-fp', 'strict'), default='zero-fp')
    ap.add_argument('--redfoot-mm', type=float, default=DEF_REDFOOT_MM)
    ap.add_argument('--tol-mm', type=float, default=DEF_TOL_MM)
    ap.add_argument('--footer-re', default=DEF_FOOTER_RE)
    ap.add_argument('--no-pdf', action='store_true')
    ap.add_argument('--quiet-pass', action='store_true', help='只打挂旗件')
    ap.add_argument('--out')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('-h', '--help', action='store_true')
    a = ap.parse_args(argv[1:])
    if a.help or (not a.tex and not a.selftest):
        print(__doc__)
        return 2
    cfg = {'grade': a.grade, 'redfoot_pt': a.redfoot_mm * MM2PT, 'tol_pt': a.tol_mm * MM2PT,
           'footer_re': a.footer_re, 'no_pdf': a.no_pdf, 'verbose': not a.quiet_pass}
    if a.selftest:
        _, nbad = selftest(cfg)
        print('[selftest PASS 负测真拦·正测真放行]' if nbad == 0
              else f'[selftest FAIL] 断言挂 {nbad} 例')
        return 0 if nbad == 0 else 1
    if (a.pdf or a.log) and len(a.tex) != 1:
        print('[FAIL] --pdf/--log 仅单件可用')
        return 2
    for t in a.tex:
        if not (t.endswith('.tex') and os.path.isfile(t)):
            print('[FAIL] 输入须为 .tex 文件:', t)
            return 2
    lines_out = []
    tf = tw = 0
    for t in a.tex:
        rep, nf, nw = audit_piece(t, cfg, pdf=a.pdf, log=a.log)
        tf += nf
        tw += nw
        lines_out += rep
        if nf or not a.quiet_pass:
            print('\n'.join(rep))
    grade_name = '零误报档' if cfg['grade'] == 'zero-fp' else '严档'
    verdict = (f'[PASS] 静默溢出审计全过（{grade_name}｜件 {len(a.tex)}／红旗 0／警告 {tw}）'
               if tf == 0 else
               f'[FAIL] 红旗 {tf}（{grade_name}）：出纸/丢块/吞块须回炉（附卷制迁移或缩块），警告 {tw} 登记')
    print(verdict)
    lines_out.append(verdict)
    if a.out:
        with open(a.out, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(lines_out) + '\n')
    return 0 if tf == 0 else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
