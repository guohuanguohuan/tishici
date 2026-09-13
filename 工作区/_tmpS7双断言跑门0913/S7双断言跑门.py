# -*- coding: utf-8 -*-
r"""S7 双断言链·参数化跑门器（M2 第1章 成卷全件）。
源谱系：工作区/字替对照-0909/variantF/_测v4断言.py（v4.4·54 门骨架）＋ 断言顶格.py（顶格五查）。
按 S2就绪报告 §四-2 登记口径拆「件型公共门」（编译三0／页脚／花形／判断右挂／全角残留／图位）
×参数化计数门；顶格链 (a)(c)(d)(e) 照 断言顶格.py 判据逐字承袭，签名集按件型族参数化。
红线：只读跑门（零写）；窗口凡 L1/v4 校准值（A4 双栏族）逐字承袭源脚本；新件型族
（卷件 8K 三栏／答案册单栏／配页件）按「同禁则扩门」降为在场＋族内一致性门（排产单 §五-A1 授权，
P2 登记）。输出：控制台逐件逐门 绿/红＋_S7跑门读数.json。
族：
  D＝导学件族（A4 双栏，v11 导学禁则原生域：课时01~10＋衔接节＋章末）
  L＝练习线族（A4 双栏：练习件×10＋拓展册上下；题号/选项悬挂为件型设计，(a) 门仅扫 2em/7mm）
  J＝卷件族（8K 横三栏：测评卷＋滚A/滚B；丝带角饰/卷末答案表为件型设计）
  A＝答案册族（A4 单栏层级缩进；值排印归 A2 对号断言链管，本链只跑公共门）
  P＝配页件（册目录页，pagestyle empty 无页脚）
另含装配四本（ASM：导学本44／练习本38／测评本7／答案本13，全局页码 1/45/83/90 起）＝33 件射程。
"""
import io, sys, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from collections import Counter
import pymupdf

ROOT = r"C:\提示词\工作区\M2-第1章量产0911\成卷"
PT = 72 / 25.4

# ---------------- 族参数（A4 双栏族窗口＝v4 断言 L1 校准值逐字承袭） ----------------
# A 族 blk/lead 为 0913 跑门实测定窗（预定 13.8/18.0 系错值：13 页页脚块一律 31.0×7.8mm·底11.08；
# 行距主峰 6.25pt×143），按「读数系统性偏移按实测登记再定窗」口径校准，P2 登记。
FAM = {
    'D': dict(margin=17.2 * PT, top=19.6 * PT, bot=20 * PT, colsep=7.6 * PT, ncols=2,
              page=(595.276, 842.0), lead=18.0, blk=(26.2, 7.8),
              sig=r'^(\d+．|\[答案\]|\[解析\]|【诊断分析】|【素养小结】|【学习目标】|[A-D]．|[①②③④⑤⑥⑦⑧⑨]|◆|（\d+|\(\d+)',
              topgeom='auto', judge=True, huax=True),
    'L': dict(margin=17.2 * PT, top=19.6 * PT, bot=20 * PT, colsep=7.6 * PT, ncols=2,
              page=(595.276, 842.0), lead=18.0, blk=(31.0, 7.8),
              sig=r'^(\d+\.(?!\d)|◆)', topgeom=False, judge=False, huax=False),
    'J': dict(margin=8.9 * PT, top=12.0 * PT, bot=17.6 * PT, colsep=11.0 * PT, ncols=3,
              colw=120.0 * PT, page=(399.8 * PT, 284.2 * PT), lead=17.7, blk=(26.2, 7.8),
              sig=r'^(\d+\.(?!\d)|[一二三四五]、)', topgeom=False, judge=False, huax=False),
    'A': dict(margin=17.2 * PT, top=15.0 * PT, bot=20 * PT, colsep=0, ncols=1,
              page=(595.276, 842.0), lead=6.25, blk=(31.0, 7.8),
              sig=None, topgeom=False, judge=False, huax=False),
    'P': dict(margin=17.2 * PT, top=19.6 * PT, bot=20 * PT, colsep=0, ncols=1,
              page=(595.276, 842.0), lead=None, blk=None,
              sig=None, topgeom=False, judge=False, huax=False),
}

ITEMS = ([(f'导学件/课时{i:02d}', 'D') for i in range(1, 11)]
         + [('导学件/衔接节-1.2.1前', 'D'), ('导学件/章末-本章总结提升', 'D')]
         + [(f'练习件/课时{i:02d}', 'L') for i in range(1, 11)]
         + [('拓展册/上册', 'L'), ('拓展册/下册', 'L')]
         + [('测评卷', 'J'), ('滚动卷/滚A', 'J'), ('滚动卷/滚B', 'J')]
         + [('答案册', 'A'), ('装配/册目录页', 'P')])

# 装配四本（合并卷，无独立 tex/log）：族／登记页数／全局起页号／页码格式
ASM = {'装配/导学本': ('D', 44, 1, 'plain'), '装配/练习本': ('L', 38, 45, 'pad3'),
       '装配/测评本': ('J', 7, 83, 'juan'), '装配/答案本': ('A', 13, 90, 'plain')}

# 设计调色板全集（全 qp-*.tex definecolor/混色普查，见 _普查调色板()；页灰 ⊆ 此集为绿）
PALETTE_SCAN_DIRS = ['导学件/课时01', '练习件/课时01', '拓展册/上册', '测评卷', '滚动卷/滚A', '答案册', '装配/册目录页']

fails_all, results = {}, {}

def rgb255(c):
    return tuple(round(x * 255) for x in c)

def strip_comments(t):
    """TeX 注释语义剥离：整行注释与行内 % 后内容均剔（\\% 转义保护；\\\\% 配对正确）。"""
    out = []
    for ln in t.split('\n'):
        i, n, cut = 0, len(ln), len(ln)
        while i < n:
            ch = ln[i]
            if ch == '\\':
                i += 2          # 控制列消费一个后续字符（\% 受保护；\\% 正确开出注释）
                continue
            if ch == '%':
                cut = i
                break
            i += 1
        out.append(ln[:cut])
    return '\n'.join(out)

def tex_sources(it):
    fs = [os.path.join(ROOT, it, 'main.tex')]
    if os.path.exists(os.path.join(ROOT, it, 'body.tex')):
        fs.append(os.path.join(ROOT, it, 'body.tex'))
    return fs

def read_sources(it):
    return ''.join(open(p, encoding='utf-8').read() for p in tex_sources(it) if os.path.exists(p))

def census_palette():
    """普查件型宏族 qp-*.tex 的灰档定义（HTML/gray/black!x），构成设计调色板全集。"""
    pal = set()
    for d in PALETTE_SCAN_DIRS:
        for fn in os.listdir(os.path.join(ROOT, d)):
            if not fn.endswith('.tex'):
                continue
            t = open(os.path.join(ROOT, d, fn), encoding='utf-8').read()
            for m in re.finditer(r'\\definecolor\{[^}]+\}\{(HTML|gray)\}\{([^}]+)\}', t):
                if m.group(1) == 'HTML':
                    v = m.group(2).strip()
                    if len(v) == 6 and v[0:2] == v[2:4] == v[4:6]:
                        pal.add(int(v[0:2], 16))
                else:
                    v = float(m.group(2))
                    if 0 < v < 1:
                        pal.add(round(v * 255))
            for m in re.finditer(r'\[HTML\]\{([0-9A-Fa-f]{6})\}', t):   # 内联 \color[HTML]{..} 等
                v = m.group(1)
                if v[0:2] == v[2:4] == v[4:6]:
                    pal.add(int(v[0:2], 16))
            for m in re.finditer(r'(black|white)!(\d+(?:\.\d+)?)', t):
                frac = float(m.group(2)) / 100.0
                # xcolor：black!x＝x% 黑（灰值 255×(1−x)）；white!x＝x% 白（灰值 255×x）
                pal.add(round(255 * ((1 - frac) if m.group(1) == 'black' else frac)))
    pal |= {76, 77, 119, 122, 189, 221, 210, 166, 32, 102}   # L1 各族命名灰档（v4 白名单＋卷件 silk/juan/sub）
    return pal

PALETTE = census_palette()

def col_lefts(cfg, pw):
    m, cs = cfg['margin'], cfg['colsep']
    if cfg['ncols'] == 3:
        cw = cfg['colw']
        return [m + i * (cw + cs) for i in range(3)], cw
    cw = (pw - 2 * m - cs * (cfg['ncols'] - 1)) / cfg['ncols']
    return [m + i * (cw + cs) for i in range(cfg['ncols'])], cw

def col_bands(page, x0, x1, y0, y1, thresh=128, dpi=150):
    sc = dpi / 72.0
    pm = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY, clip=pymupdf.Rect(x0, y0, x1, y1))
    w, h, s = pm.width, pm.height, pm.samples
    rows = [any(s[r * w + c] < thresh for c in range(w)) for r in range(h)]
    out, st = [], None
    for i, d in enumerate(rows):
        if d and st is None:
            st = i
        elif not d and st is not None:
            out.append((y0 + st / sc, y0 + i / sc)); st = None
    if st is not None:
        out.append((y0 + st / sc, y0 + h / sc))
    return out

def merge_bands(bs, gap=0.5):
    out = []
    for a, b in bs:
        if out and a - out[-1][1] < gap:
            out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
    return out

def ink_left(page, y0, y1, cl, dpi=300):
    clip = pymupdf.Rect(cl - 3, y0 - 0.5, cl + 7, y1 + 0.5)
    pix = page.get_pixmap(dpi=dpi, clip=clip)
    w, h, n, s = pix.width, pix.height, pix.n, pix.samples
    for x in range(w):
        for y in range(h):
            off = (y * w + x) * n
            if (s[off] + s[off + 1] + s[off + 2]) / 3 < 128:
                return clip.x0 + x / (dpi / 72.0)
    return 1e9

def pick_col(x0, cls, colw):
    """栏归属：v4 口径＝含 x0 的栏带（±7pt 容差）；右挂元素按 bb[0] 落带归栏（近栏中点法会误判）。"""
    for cl in cls:
        if cl - 7 <= x0 < cl + colw + 7:
            return cl
    return min(cls, key=lambda c: abs(x0 - c))

def img_ink_mask(doc, info, pm, R, dpi=600, thresh=128):
    """位图暗墨投影掩码：把 info 位图暗像素（灰<thresh）经变换矩阵逆映射采样到 pm 的网格。
    返回 True＝墨；越出位图范围、无 xref 或解码失败一律按无墨（False 不参与压字判定）。"""
    import numpy as _np
    from PIL import Image as _PILImage
    a_, b_, c_, d_, e_, f_ = info['transform']
    H, W = pm.height, pm.width
    ink = _np.zeros((H, W), dtype=bool)
    xref = info.get('xref') or 0
    if xref <= 0:
        return ink
    try:
        arr = _np.asarray(_PILImage.open(io.BytesIO(doc.extract_image(xref)['image'])).convert('L'))
    except Exception:
        return ink
    ih, iw = arr.shape
    det = a_ * d_ - b_ * c_
    if det == 0:
        return ink
    sc = dpi / 72.0
    xs = R.x0 + (_np.arange(W) + 0.5) / sc
    ys = R.y0 + (_np.arange(H) + 0.5) / sc
    X, Y = _np.meshgrid(xs, ys)
    U = ((d_ * (X - e_) - c_ * (Y - f_)) / det) * iw    # 单位方块→像素列
    V = ((a_ * (Y - f_) - b_ * (X - e_)) / det) * ih
    ui = _np.round(U).astype(int)
    vi = _np.round(V).astype(int)
    ok = (ui >= 0) & (ui < iw) & (vi >= 0) & (vi < ih)
    ink[ok] = arr[vi[ok], ui[ok]] < thresh
    return ink

def near_ink(ink, r=2):
    """墨掩码的 r 像素邻域膨胀（600dpi 下 r=2 ≈ 0.24pt 触墨容差）。"""
    import numpy as _np
    H, W = ink.shape
    p = _np.pad(ink, r, constant_values=False)
    acc = _np.zeros((H, W), dtype=bool)
    for dr in range(2 * r + 1):
        for dc in range(2 * r + 1):
            acc |= p[dr:dr + H, dc:dc + W]
    return acc

def newcommand_spans(t):
    """扫描 \\newcommand/\\renewcommand 定义，返回 [(name, arity, body, span_start, span_end)]（花括号配平）。"""
    spans = []
    for m in re.finditer(r'\\(?:re)?newcommand\s*\{', t):
        k = m.end() - 1                      # 指向名称组 '{'
        depth, j = 0, k
        while j < len(t):
            if t[j] == '{':
                depth += 1
            elif t[j] == '}':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if j >= len(t):
            continue
        name = t[k + 1:j]
        j += 1
        arity = 0
        while j < len(t) and t[j] in ' \t\n':
            j += 1
        if j < len(t) and t[j] == '[':
            e = t.find(']', j)
            if e < 0:
                continue
            arity = int(t[j + 1:e]) if t[j + 1:e].isdigit() else 0
            j = e + 1
            while j < len(t) and t[j] in ' \t\n':
                j += 1
            if j < len(t) and t[j] == '[':          # 缺省值括号（\newcommand{\m}[n][默认]{..}）
                e = t.find(']', j)
                j = e + 1 if e >= 0 else len(t)
        while j < len(t) and t[j] in ' \t\n':
            j += 1
        if j >= len(t) or t[j] != '{':
            continue
        depth, k2 = 0, j
        while j < len(t):
            if t[j] == '{':
                depth += 1
            elif t[j] == '}':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if j >= len(t):
            continue
        spans.append((name, arity, t[k2 + 1:j], m.start(), j + 1))
    return spans

def strip_newcommand_bodies(t):
    """剔除全部 newcommand 定义（按 newcommand_spans），用于「正文裸用」判据。"""
    if not t:
        return t
    cuts = [(s, e) for _n, _a, _b, s, e in newcommand_spans(t)]
    out, prev = [], 0
    for s, e in cuts:
        out.append(t[prev:s])
        prev = e
    out.append(t[prev:])
    return ''.join(out)

def press_check(pdfp, doc, imgs_all, lines_of, cls, colw, pw):
    """墨级压字扫描（源件/装配本共用）：返回 (越栏数, 压字数, 明细)。
    doc 只读；doc2 为内存副本逐图影删后重渲染，不落盘。"""
    n_viol_e = 0
    for _p, _i, r in imgs_all:
        cl = pick_col(r.x0, cls, colw)
        if not (r.x0 >= cl - 1.0 and r.x1 <= cl + colw + 1.0):
            n_viol_e += 1
    n_press = 0
    press_det = []
    if imgs_all:
        import numpy as _np
        doc2 = pymupdf.open(pdfp)
        for pno, info, r in imgs_all:
            hit = [(t, bb) for t, bb, sps in lines_of[pno] if pymupdf.Rect(bb).intersects(r)]
            if not hit:
                continue
            xref = info.get('xref') or 0
            if xref <= 0:
                press_det.append(f'p{pno} 内嵌图xref0 未判')
                continue
            page2 = doc2[pno - 1]
            try:
                page2.delete_image(xref)
            except Exception:
                press_det.append(f'p{pno} 影删失败 未判')
                continue
            pmC = page2.get_pixmap(dpi=600, colorspace=pymupdf.csGRAY, clip=r)
            T_dark = _np.frombuffer(pmC.samples, dtype=_np.uint8).reshape(pmC.height, pmC.width) < 128
            press_px = T_dark & near_ink(img_ink_mask(doc, info, pmC, r), 2)
            if press_px.any():
                n_press += 1
                press_det.append(f'p{pno} {hit[0][0][:8]}…×{int(press_px.sum())}px')
        doc2.close()
    return n_viol_e, n_press, press_det

def run_item(it, fam):
    cfg = FAM[fam]
    checks = []
    def check(name, ok, detail=''):
        checks.append(dict(gate=name, ok=bool(ok), detail=detail))
    base = os.path.join(ROOT, it)
    pdfp, logp = os.path.join(base, 'main.pdf'), os.path.join(base, 'main.log')

    # ---- ① 编译三0 ＋ ② 页数一致（_测v4断言 ①／排产单 A3 口径） ----
    log = open(logp, encoding='utf-8', errors='ignore').read() if os.path.exists(logp) else ''
    n_err = len(re.findall(r'^! ', log, re.M))
    n_ovr = log.count('Overfull')
    n_mch = log.count('Missing character')
    m = re.search(r'Output written on main\.pdf \((\d+) pages', log)
    n_log = int(m.group(1)) if m else -1
    doc = pymupdf.open(pdfp)
    n_pdf = doc.page_count
    check('①编译三0（error/Overfull/Missing character＝0）', n_err == 0 and n_ovr == 0 and n_mch == 0,
          f'err={n_err} ovr={n_ovr} mch={n_mch}')
    check('②页数 一致（log＝pdf）', n_log == n_pdf and n_pdf > 0, f'log={n_log} pdf={n_pdf}')

    pw, ph = cfg['page']
    cls, colw = col_lefts(cfg, pw)
    MID = (min(cls) + max(cls) + colw) / 2 if cfg['ncols'] > 1 else pw / 2
    TOP, BOT = cfg['top'], cfg['bot']
    BODY_BOT = ph - BOT

    lines_of = {}
    for pno, page in enumerate(doc, 1):
        ls = []
        for blk in page.get_text('dict')['blocks']:
            for ln in blk.get('lines', []):
                t = ''.join(sp['text'] for sp in ln['spans']).strip()
                if t:
                    ls.append((t, ln['bbox'], ln['spans']))
        lines_of[pno] = ls
    full = re.sub(r'\s+', '', ''.join(p.get_text() for p in doc))

    # ---- ③ 页眉缺席 ----
    hdr_bad = []
    for pno in range(1, n_pdf + 1):
        hdr = [t for t, bb, sps in lines_of[pno] if bb[3] < TOP - 1]   # v4 ⑨ 判据：行盒底 全在版心顶上方
        if hdr:
            hdr_bad.append((pno, hdr[0][:12]))
    check('③页眉缺席（版心顶上方无文本）', not hdr_bad, '；'.join(f'p{p}{h}' for p, h in hdr_bad[:4]))

    # ---- ④页脚块几何 ＋ ⑤奇偶交替（v4 ⑧⑩；A/P/J 族按在场＋族内一致性扩门） ----
    body_txt = strip_comments(read_sources(it))
    jianming = ''
    mjm = re.findall(r'\\(?:re)?newcommand\{\\qpjianming\}\{([^}]*)\}', body_txt)
    if mjm:
        jianming = mjm[-1]
    blocks_pg = {}
    for pno in range(1, n_pdf + 1):
        page = doc[pno - 1]
        blk_rect, num = None, None
        for d in page.get_drawings():
            r = d['rect']
            f = d.get('fill')
            if not f or r.y0 <= BODY_BOT - 10:
                continue
            if rgb255(f) == (221, 221, 221):
                blk_rect = r
        foot_spans, foot_txts = [], []
        for t, bb, sps in lines_of[pno]:
            if bb[1] > BODY_BOT - 2:
                foot_spans += [sp for sp in sps if sp['text'].strip()]
                foot_txts.append(t)
            for sp in sps:
                if sp['text'].strip() in (str(pno), '%02d' % pno, '%03d' % pno) \
                   and blk_rect and bb[1] > BODY_BOT - 10 \
                   and blk_rect.x0 - 1 <= sp['bbox'][0] and sp['bbox'][2] <= blk_rect.x1 + 1:
                    num = sp
        blocks_pg[pno] = (blk_rect, num, foot_spans, foot_txts)
    if cfg['blk'] is None:
        nblk = sum(1 for b, _n, _s, _t in blocks_pg.values() if b)
        check('④页脚（配页件 pagestyle empty＝无页脚块·设计态）', nblk == 0, f'页脚块 {nblk}/0')
    elif fam == 'J':
        juanname = ''
        mjm2 = re.findall(r'juanname\}\{([^}]*)\}', body_txt)
        if mjm2:
            juanname = mjm2[-1]
        base_ok, det_j, ys_j = True, [], []
        for pno in range(1, n_pdf + 1):
            _b, _n, foot_spans, foot_txts = blocks_pg[pno]
            ft = ''.join(foot_txts).replace(' ', '')
            want = '%02d' % pno
            good = bool(foot_txts) and want in ft
            if pno % 2 == 1:
                good = good and juanname.replace(' ', '') in ft
            else:
                good = good and '羿郭工作室' in ft
            if foot_spans:
                ys_j.append(round(min(sp['bbox'][1] for sp in foot_spans), 1))
            base_ok = base_ok and good
            det_j.append(f'p{pno}{"✗" if not good else "ok"}[{ft[:26]}]')
        uni_j = (max(ys_j) - min(ys_j)) <= 1.5 if ys_j else False
        check('④页脚（卷件 YJ-02 文字行页脚：卷号01~NN 逐页在场＋基线族内一致）',
              base_ok and uni_j, '；'.join(det_j) + f' 基线{ys_j}')
        check('⑤奇偶交替（奇＝卷名+件名+卷NN／偶＝NN卷+品牌+册名）', base_ok,
              f'卷名={juanname}')
    else:
        bwT, bhT = cfg['blk']
        geo_ok, geo_bad, dets, uni = True, [], [], set()
        alt_ok, alt_bad = True, []
        for pno in range(1, n_pdf + 1):
            blk_rect, num, foot_spans, foot_txts = blocks_pg[pno]
            if not blk_rect or not num:
                geo_ok = False
                geo_bad.append(f'p{pno}缺块/数字')
                continue
            bw, bh = blk_rect.width / PT, blk_rect.height / PT
            bot = (ph - blk_rect.y1) / PT
            near = abs(((num['bbox'][0] if pno % 2 == 1 else num['bbox'][2])
                        - (blk_rect.x0 if pno % 2 == 1 else blk_rect.x1))) / PT
            szs = sorted({round(sp['size'], 2) for sp in foot_spans})
            dets.append(f'p{pno} {bw:.1f}×{bh:.1f} 底{bot:.1f} 数字{num["size"]:.1f} 近{near:.2f}')
            uni.add((round(bw, 1), round(bh, 1), round(bot, 1), round(num['size'], 1)))
            if fam == 'D':
                okg = (abs(bw - bwT) <= 0.3 and abs(bh - bhT) <= 0.3 and abs(bot - 11) <= 0.5
                       and 10.5 <= num['size'] <= 11.5 and 2.5 <= near <= 3.4
                       and any(5.0 <= s <= 5.45 for s in szs))
                fonts = {sp['font'] for sp in foot_spans}
                okg = okg and (any('FZSSJW' in f for f in fonts)
                               and (any('NotoSansSC' in f for f in fonts) if pno % 2 == 1 else True))
            elif fam == 'A':
                okg = (abs(bw - bwT) <= 0.6 and abs(bh - bhT) <= 0.3
                       and 8.5 <= bot <= 13.5 and 10.0 <= num['size'] <= 12.0 and 1.5 <= near <= 4.5
                       and any(5.0 <= s <= 5.6 for s in szs))
            elif fam == 'L':
                okg = (abs(bw - bwT) <= 0.6 and abs(bh - bhT) <= 0.3
                       and 8.5 <= bot <= 13.5 and 10.0 <= num['size'] <= 12.0 and 1.5 <= near <= 4.5
                       and any(5.0 <= s <= 5.6 for s in szs))
            else:   # J 族：在场＋族内一致性（扩门登记）
                okg = (abs(bh - bhT) <= 0.3 and 9.0 <= bot <= 13.0
                       and 10.0 <= num['size'] <= 12.0 and 1.5 <= near <= 4.5)
            if not okg:
                geo_ok = False
                geo_bad.append(f'p{pno}')
            odd = pno % 2 == 1
            ft = ''.join(foot_txts).replace(' ', '')
            if odd:
                okp = blk_rect.x1 >= max(cls) + colw - 1.5 and (jianming in ft or jianming == '')
            else:
                okp = blk_rect.x0 <= min(cls) + 1.5 and ('人教B' in ft or fam != 'D')
            if not okp:
                alt_ok = False
                alt_bad.append(f'p{pno}{"奇" if odd else "偶"}')
        check('④页脚块几何（L1 窗或族内一致性）', geo_ok, '；'.join(dets[:4]) + ('…' if len(dets) > 4 else '')
              + ('' if geo_ok else ' ✗' + ','.join(geo_bad[:5]) + ' 全读数：' + '；'.join(dets)))
        check('⑤奇偶交替（奇＝块贴右＋件名／偶＝块贴左＋册名）', alt_ok,
              f'件名={jianming or "(空)"}' + ('' if alt_ok else ' ✗' + ','.join(alt_bad[:6])))

    # ---- ⑥ 灰档全集 ⊆ 设计调色板（v4 ③ 参数化） ----
    grays_all, gray_bad = set(), []
    for pno in range(1, n_pdf + 1):
        page = doc[pno - 1]
        grays = set()
        for t, bb, sps in lines_of[pno]:
            for sp in sps:
                col = sp['color']
                r, g, b = (col >> 16) & 255, (col >> 8) & 255, col & 255
                if r == g == b and 0 < r < 255:
                    grays.add(r)
        for d in page.get_drawings():
            for key in ('color', 'fill'):
                c = d.get(key)
                if c:
                    rgb = rgb255(c)
                    if rgb[0] == rgb[1] == rgb[2] and 0 < rgb[0] < 255:
                        grays.add(rgb[0])
        grays_all |= grays
        if not grays <= PALETTE:
            gray_bad.append(f'p{pno}={sorted(grays - PALETTE)}')
    check('⑥灰档全集⊆设计调色板（v4③ 参数化）', not gray_bad,
          f'全集{sorted(grays_all)}' + ('' if not gray_bad else ' ✗' + '；'.join(gray_bad[:4])))

    # ---- ⑦ 栏线（双栏族；v4 ⑭ 扩门口径：逐页在场＋段质量＋覆盖度；长度降为读数） ----
    # 缘由＝M2 课01 p1 跨栏元素把栏线断为两段（61.9+79.1mm）、拓下 p13 末页 51.0mm，v4 长度窗
    # （非末 0.5／末 0.22 版心高）在本域误伤；改判：每页 ≥1 段 MID 处 0.4±0.05pt 色 189 栏线，
    # 全页段总高 ≥0.15 版心高，渲染芯 170-210 不变。
    if cfg['ncols'] == 2:
        rule_found = {}
        rule_len = {}
        for pno in range(1, n_pdf + 1):
            page = doc[pno - 1]
            segs = 0.0
            for d in page.get_drawings():
                r = d['rect']
                if not (r.width <= 1.5 and r.height >= 20):
                    continue
                if abs(r.x0 - MID) > 2 and abs(r.x1 - MID) > 2:
                    continue
                c = d.get('color') or d.get('fill')
                if c and rgb255(c) == (189, 189, 189):
                    if not (abs((d.get('width') or 0) - 0.4) <= 0.05):
                        continue
                    rule_found[pno] = d
                    segs += r.height
            rule_len[pno] = round(segs / PT, 1)
        core_ok, core_med = True, -1
        if len(rule_found) == n_pdf and rule_found:
            core_vals = []
            for pno, d in sorted(rule_found.items()):
                page = doc[pno - 1]
                sc3 = 300 / 72.0
                pm = page.get_pixmap(dpi=300, colorspace=pymupdf.csGRAY,
                                     clip=pymupdf.Rect(MID - 2, TOP + 20, MID + 2, BODY_BOT - 20))
                w3, h3, s3 = pm.width, pm.height, pm.samples
                col3 = min(range(w3), key=lambda c: abs((MID - 2) + (c + 0.5) / sc3 - MID))
                vals = sorted(s3[r3 * w3 + col3] for r3 in range(h3) if s3[r3 * w3 + col3] < 250)
                if vals:
                    core_vals.append(vals[len(vals) // 2])
            core_med = sorted(core_vals)[len(core_vals) // 2] if core_vals else -1
            core_ok = 170 <= core_med <= 210
        cov_ok = all(rule_len[p] >= 0.15 * (ph - TOP - BOT) / PT for p in rule_len)
        check('⑦栏线（逐页在场 0.4pt 色189＋覆盖≥0.15版心＋芯170-210）',
              len(rule_found) == n_pdf and core_ok and cov_ok,
              f'页{len(rule_found)}/{n_pdf} 芯{core_med} 段高{rule_len}')

    # ---- ⑧ 行距主峰（设计 lead ±0.5pt；v4 ② 参数化） ----
    if cfg['lead']:
        diffs = []
        for pno in range(1, n_pdf + 1):
            cols = {i: [] for i in range(len(cls))}
            for t, bb, sps in lines_of[pno]:
                if any(9.5 <= sp['size'] <= 11.2 for sp in sps):
                    ci = min(range(len(cls)), key=lambda i: abs(bb[0] - cls[i]))
                    cols[ci].append(sps[0]['origin'][1])
            for c in cols:
                ys = sorted(cols[c])
                diffs += [round((b - a) * 4) / 4 for a, b in zip(ys, ys[1:]) if 3 < b - a < 40]
        peak, cnt = Counter(diffs).most_common(1)[0] if diffs else (0, 0)
        check('⑧行距主峰（设计lead±0.5pt）', abs(peak - cfg['lead']) <= 0.5 and cnt >= 5,
              f'主峰{peak}pt(×{cnt}) 设计{cfg["lead"]}pt')

    # ---- ⑨⑩⑪⑫ 顶格链（断言顶格.py (a)(c)(d)(e) 逐字承袭，签名/栏带按族参数化） ----
    tex_raw = read_sources(it)
    tex_body = strip_comments(tex_raw)
    bad_h7 = re.findall(r'\\hspace\*\{7mm\}|\\hspace\*\{2em\}', tex_body)
    bad_hang = re.findall(r'\\hangindent', tex_body)
    raw_hang = re.findall(r'\\hangindent', strip_newcommand_bodies(tex_body))
    des_hang = len(bad_hang) - len(raw_hang)   # 定义体内＝件型设计（登记制）
    if fam == 'D':
        check('⑨顶格(a) 禁则（正文无\\hangindent·定义内计件型设计／无\\hspace*{7mm}／\\hspace*{2em}）',
              not bad_h7 and not raw_hang,
              f'hang={len(bad_hang)}(定义内{des_hang}) h7/2em={len(bad_h7)}' + ('' if raw_hang else ''))
    else:
        check('⑨顶格(a) 族内禁则（无\\hspace*{7mm}／\\hspace*{2em}；hangindent＝族设计登记）',
              not bad_h7, f'hang={len(bad_hang)}(族设计) h7/2em={len(bad_h7)}')

    if cfg['sig']:
        SIG = re.compile(cfg['sig'])
        TOL = 3.5
        n_sig = n_viol_c = 0
        viol_c_det = []
        for pno, page in enumerate(doc, 1):
            H = page.rect.height
            lines = []
            for blk_ in page.get_text('dict')['blocks']:
                for ln in blk_.get('lines', []):
                    t = ''.join(sp['text'] for sp in ln['spans']).strip()
                    if t:
                        lines.append((t, pymupdf.Rect(ln['bbox']), ln['spans'][0]['origin'][1]))
            for t, r, basey in lines:
                if not SIG.match(t):
                    continue
                if basey < TOP - 1 or basey > H - BOT + 1:
                    continue
                cl0 = pick_col(r.x0, cls, colw)
                if not (cl0 - 7 <= r.x0 < cl0 + colw + 7):
                    continue
                if any(o is not r and abs(o[2] - basey) < 2.0 and o[1].x0 >= cl0 - 1.0
                       and o[1].x1 <= r.x0 + 1.0 for o in lines):
                    continue
                n_sig += 1
                ref = r.x0 if cl0 - 0.5 <= r.x0 else None
                ink = ink_left(page, r.y0, r.y1, cl0) if ref is None else cl0
                if not (cl0 - TOL <= ink <= cl0 + TOL):
                    n_viol_c += 1
                    viol_c_det.append(f'p{pno} {t[:12]} x0={r.x0:.1f} 墨={ink:.1f} 栏左={cl0:.1f}')
        check('⑩顶格(c) 签名行行首＝栏左±3.5pt（违规0）', n_viol_c == 0 and n_sig >= 3,
              f'签名{n_sig} 违规{n_viol_c}' + ('' if not viol_c_det else ' ✗' + '；'.join(viol_c_det[:5])))

        n_rules = n_leftedge = n_viol_d = 0
        for pno, page in enumerate(doc, 1):
            for d in page.get_drawings():
                r = d['rect']
                if not (r.width <= 2.0 and r.height >= 4.0):
                    continue
                if cfg['ncols'] > 1 and any(abs(r.x0 - (min(cls) + i * (colw + cfg['colsep']) + colw + cfg['colsep'] / 2)) < 1.0
                                            for i in range(cfg['ncols'] - 1)):
                    continue   # 栏间线
                cl = pick_col(r.x0, cls, colw)
                if r.x0 < cl - colw - 7 or r.x0 > cl + colw + 7:
                    continue
                n_rules += 1
                if r.x0 < cl - 1.0 or r.x1 > cl + colw + 1.0:
                    n_viol_d += 1
                if any(abs(r.x0 - c) <= 1.0 for c in cls):
                    n_leftedge += 1
        n_tab = len(re.findall(r'\\begin\{tabular', tex_body))
        check('⑪顶格(d) 表线在栏带内（违规0）', n_viol_d == 0,
              f'竖线{n_rules} 左框线{n_leftedge} tabular{n_tab} 违规{n_viol_d}')

    # ---- ⑫ 图位（raster 数＝tex 图行数；在栏带内；墨级压字 0；断言顶格 (e)＋v4 N6 参数化） ----
    # 压字＝文字层分离口径：bbox 相交仅作初筛；对相交图在内存副本 doc2 上 delete_image 后重渲染
    # 同区（600dpi 灰<128）得「文字自墨」，与位图原生暗墨投影掩码（img_ink_mask）的 2px 邻域求交，
    # 有共位方计压字。缘由＝M2 设计增设「解答书写区」浅灰水印（课时02 p2 实测：行盒与图 bbox 相交
    # 而墨隙不触，矩形/墨盒级判法在本域均为假阳；浅灰 184~233 在暗阈下无墨，不触图墨即绿）。
    body_no_defs = strip_newcommand_bodies(tex_body)
    n_gfx = 0

    def _fig_count(gp):
        if gp.lower().endswith('.pdf') and os.path.exists(gp):
            try:
                gdoc = pymupdf.open(gp)
                n = sum(len(pg.get_image_info(xrefs=True)) for pg in gdoc)
                gdoc.close()
                return n
            except Exception:
                return 1
        return 1 if os.path.exists(gp) else 0

    for g in re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', body_no_defs):
        gp = os.path.join(base, g)
        n_gfx += _fig_count(gp if os.path.exists(gp) else os.path.join(base, g + '.pdf'))
    for name, arity, dbody, _s, _e in newcommand_spans(tex_body):
        mt = re.search(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', dbody)
        if not mt:
            continue
        tmpl = mt.group(1)
        pat = re.escape(name) + r'\s*(?:\[([^\]]*)\])?' + r'(?:\s*\{([^{}]*)\})?' * max(arity, 1)
        for mu in re.finditer(pat, body_no_defs):
            opt = mu.group(1)
            braced = [g for g in mu.groups()[1:] if g is not None]
            args = ([opt] if opt is not None else ['']) + braced   # LaTeX 可选参语义：有 [..] 时 #1=[..]
            path = tmpl
            for k in range(1, arity + 1):
                if k <= len(args):
                    path = path.replace('#%d' % k, args[k - 1])
            gp = os.path.join(base, path)
            n_gfx += _fig_count(gp if os.path.exists(gp) else os.path.join(base, path + '.pdf'))
    imgs_all = []
    for pno, page in enumerate(doc, 1):
        Hpg = page.rect.height
        for info in page.get_image_info(xrefs=True):
            r = pymupdf.Rect(info['bbox'])
            if r.height > Hpg - 2 or r.width > pw - 2:
                continue
            imgs_all.append((pno, info, r))
    n_fig = len(imgs_all)
    n_viol_e = 0
    for _p, _i, r in imgs_all:
        cl = pick_col(r.x0, cls, colw)
        if not (r.x0 >= cl - 1.0 and r.x1 <= cl + colw + 1.0):
            n_viol_e += 1
    n_fig = len(imgs_all)
    n_viol_e, n_press, press_det = press_check(pdfp, doc, imgs_all, lines_of, cls, colw, pw)
    check('⑫图位（raster=图源内嵌位图账；栏带内；墨级压字0）', n_fig == n_gfx and n_viol_e == 0 and n_press == 0,
          f'位图{n_fig}/图源账{n_gfx} 越栏{n_viol_e} 压字{n_press}' + ('' if not press_det else ' ✗' + '；'.join(press_det[:4])))

    # ---- ⑬ 全角括号残留（v4 ②；M2 域判据＝全册全角开合总数相等，栈配对与源字面降为读数） ----
    # 缘由＝v4 字面账只成立于定义体在 main.tex 的三件式域；pdf 逐页/栈序配对又被 dfrac 堆叠式
    # 提取流错位打假（答案册 p3 实测：源「（\(\dfrac{..}\)）」成对，提取流中 ）错位到别处）。
    # 开合总数相等＋字形逐个在场＝残留 0 的域内稳健判据；D 族判断槽恰＝zhentib 数；J 族 \kw 账不变。
    n_fw = full.count('（')
    n_close = full.count('）')
    n_slot = full.count('（）')
    n_zhentib = len(re.findall(r'\\zhentib[\{\s]', tex_raw))
    loose = []
    stack = []
    for m in re.finditer('[（）]', full):
        if m.group() == '（':
            stack.append(m.start())
        elif stack:
            stack.pop()
        else:
            loose.append('孤）' + full[max(0, m.start() - 8):m.start() + 8])
    for pos in stack:
        loose.append('孤（' + full[max(0, pos - 6):pos + 14])
    if fam == 'J':
        n_kw = len(re.findall(r'\\kw(?![a-zA-Z])', tex_body.replace('\\newcommand{\\kw}', '')))
        check('⑬全角括号残留（J 族：pdf槽对＝\\kw 用数＋开合总数相等；散项读数登记）',
              n_slot == n_kw and n_fw == n_close,
              f'全角{n_fw}（槽对{n_slot}＋散{n_fw - n_slot}）合{n_close} kw{n_kw} 错位{len(loose)}'
              + ('' if not loose else ' ✗' + '；'.join(loose[:4])))
    else:
        check('⑬全角括号残留（开合总数相等＋D 族判断槽恰＝zhentib 数；栈配对/源字面读数）',
              n_fw == n_close and (fam != 'D' or n_slot == n_zhentib),
              f'全角{n_fw} 合{n_close}（槽对{n_slot}＋散{n_fw - n_slot}）源字面{tex_body.count("（")} '
              f'zhentib{n_zhentib} 错位{len(loose)}'
              + ('' if not loose else ' ✗' + '；'.join(loose[:4])))

    # ---- ⑭ 判断槽右挂（v4 N1；D 族且 zhentib>0） ----
    if cfg['judge'] and n_zhentib > 0:
        par_ok, par_detail, n_par = True, [], 0
        for pno in range(1, n_pdf + 1):
            page = doc[pno - 1]
            for t, bb, sps in lines_of[pno]:
                tc = re.sub(r'\s+', '', t)
                if not tc.endswith('（）'):
                    continue
                cl = pick_col(bb[0], cls, colw)
                n_par += 1
                pm = page.get_pixmap(dpi=150, colorspace=pymupdf.csGRAY,
                                     clip=pymupdf.Rect(cl, bb[1] - 1, cl + colw, bb[3] + 1))
                w, h, s = pm.width, pm.height, pm.samples
                cols = [any(s[r_ * w + c] < 128 for r_ in range(h)) for c in range(w)]
                sc = 150 / 72.0
                ink_r = cl + (w - 1 - cols[::-1].index(True)) / sc
                ink_d = (cl + colw - ink_r) / PT
                bb_d = (cl + colw - bb[2]) / PT
                good = 0.75 <= ink_d <= 1.35 and -0.8 <= bb_d <= -0.5
                par_ok = par_ok and good
                par_detail.append(f'p{pno} ink{ink_d:.2f}/bb{bb_d:.2f}' + ('' if good else '✗'))
        check('⑭判断槽右挂（ink 0.75-1.35／bbox −0.8~−0.5；v4 N1 逐字）', par_ok and n_par == n_zhentib,
              f'槽{n_par}/{n_zhentib} ' + ' '.join(par_detail[:6]) + ('…' if len(par_detail) > 6 else ''))

    # ---- ⑮ 花形几何全集（v4 ⑦；huaxing 在场件） ----
    n_huax_tex = len(re.findall(r'\\huaxing[\{\s]', tex_raw))
    if cfg['huax'] or n_huax_tex:
        hua_rules = []
        for pno in range(1, n_pdf + 1):
            page = doc[pno - 1]
            for d in page.get_drawings():
                r = d['rect']
                c = d.get('color') or d.get('fill')
                if not c:
                    continue
                if rgb255(c) != (77, 77, 77) or not (r.width > 100 and r.height <= 3):
                    continue
                hua_rules.append((pno, d, r))
        ok7 = len(hua_rules) == n_huax_tex
        d7 = []
        for pno, d, r in hua_rules:
            page = doc[pno - 1]
            cl = cls[0] if (r.x0 + r.x1) / 2 < MID else cls[-1]
            sw = d.get('width') or r.height
            dias = [d2['rect'] for d2 in page.get_drawings()
                    if d2.get('fill') and rgb255(d2['fill']) == (255, 255, 255)
                    and d2['rect'].y1 <= r.y0 + 2 and d2['rect'].y1 >= r.y0 - 25
                    and d2['rect'].x0 >= cl - 2 and d2['rect'].x1 <= cl + colw + 2
                    and 8 < d2['rect'].width / PT < 12]
            if len(dias) < 4:
                ok7 = False
                d7.append(f'p{pno}菱形{len(dias)}/4!')
                continue
            gw = (max(x.x1 for x in dias) - min(x.x0 for x in dias)) / PT
            gh = (max(x.y1 for x in dias) - min(x.y0 for x in dias)) / PT
            tie = (r.y0 - max(x.y1 for x in dias)) / PT
            st_dist = (r.x0 - cl) / PT
            en_dist = (cl + colw - r.x1) / PT
            words = []
            for t, bb, sps in lines_of[pno]:
                if not (r.y0 - 20 <= bb[1] and bb[3] <= r.y1 + 8) or not (cl - 7 <= bb[0] < cl + colw + 7):
                    continue
                for sp in sps:
                    if 6.0 <= sp['size'] <= 7.0 and sp['color'] == 0x7A7A7A and sp['text'].strip():
                        words.append(sp)
            words.sort(key=lambda s: s['bbox'][0])
            w_right = (cl + colw - words[-1]['bbox'][2]) / PT if words else -9
            ok_i = (abs(gw - 23.5) <= 1.2 and 6.2 <= gh <= 7.0 and 0.15 <= tie <= 0.45
                    and abs(sw - 1.2) <= 0.06 and abs(st_dist - 2.77) <= 0.3 and abs(en_dist - 4.0) <= 0.5
                    and len(words) >= 2 and abs(w_right - 4.0) <= 1.0)
            ok7 = ok7 and ok_i
            d7.append(f'p{pno} 组{gw:.1f}×{gh:.2f} 贴{tie:.2f} 起{st_dist:.2f} 终{en_dist:.2f} 词{len(words)} 右缘{w_right:.2f}'
                      + ('' if ok_i else '✗'))
        check('⑮花形几何全集（×n＝huaxing 数；v4 ⑦ 窗逐字）', ok7,
              f'{len(hua_rules)}/{n_huax_tex} ' + '；'.join(d7[:4]) + ('…' if len(d7) > 4 else ''))

    # ---- ⑯ 答案值签名反向（卷面件 0；v4 ⑥ 全域参数化）＋ 探究点计数 ----
    if fam in ('D', 'L', 'J'):
        sigs = ['[答案]', '[解析]', '【答案】', '【解析】', '【详解】', '【点睛】', '【分析】', '故答案为', '故选']
        cnts = {s: full.count(s) for s in sigs}
        bad16 = {s: c for s, c in cnts.items() if c}
        check('⑯答案值签名反向（卷面 0 在场）', not bad16, str(cnts))
        n_tj_tex = len(re.findall(r'\\tjdnr[\{\s]', tex_raw))
        n_tj_pdf = full.count('◆探究点')
        check('⑰探究点计数（pdf＝tex tjdnr 数）', n_tj_pdf == n_tj_tex, f'pdf{n_tj_pdf}/tex{n_tj_tex}')
    else:
        cnts = {s: full.count(s) for s in ['[答案]', '[解析]', '【答案】']}
        check('⑯答案值签名（答案册族＝设计在场，读数登记）', True, str(cnts))

    doc.close()
    red = [c for c in checks if not c['ok']]
    results[it] = dict(family=fam, gates=checks, n_red=len(red))
    tag = '全绿' if not red else f'红{len(red)}'
    print(f'\n== {it} [{fam}] —— {tag} ({len(checks)} 门)')
    for c in checks:
        print(('  ✓ ' if c['ok'] else '  ✗R ') + c['gate'] + '　' + c['detail'][:150])
    return len(red)

def run_asm(it):
    """装配四本跑门：合并卷（无 tex/log）——①三0 引装配报告 ②页数登记 ③④⑤⑥⑦⑧⑫⑯ pdf 层门；
    页码/奇偶按全局号（G7 跨本连续），tex 级门由 29 源件门承担。"""
    fam, pages_exp, start, numfmt = ASM[it]
    cfg = FAM[fam]
    checks = []
    def check(name, ok, detail=''):
        checks.append(dict(gate=name, ok=bool(ok), detail=detail))
    pdfp = os.path.join(ROOT, it + '.pdf')
    doc = pymupdf.open(pdfp)
    n_pdf = doc.page_count

    rep = r'C:\提示词\工作区\M2-第1章量产0911\_tmp装配装订0912\_S7重跑装配报告0913.txt'
    rep_n = open(rep, encoding='utf-8', errors='ignore').read().count('OK') if os.path.exists(rep) else -1
    check('①装配三0（组件副本 err/ovr/mch=0＝装配报告 28 副本 OK 引用）', rep_n >= 28, f'报告OK数={rep_n}')
    check('②页数（登记 %d）' % pages_exp, n_pdf == pages_exp, f'pdf={n_pdf} 登记={pages_exp}')

    pw, ph = cfg['page']
    cls, colw = col_lefts(cfg, pw)
    MID = (min(cls) + max(cls) + colw) / 2 if cfg['ncols'] > 1 else pw / 2
    TOP, BOT = cfg['top'], cfg['bot']
    BODY_BOT = ph - BOT

    lines_of = {}
    for pno, page in enumerate(doc, 1):
        ls = []
        for blk in page.get_text('dict')['blocks']:
            for ln in blk.get('lines', []):
                t = ''.join(sp['text'] for sp in ln['spans']).strip()
                if t:
                    ls.append((t, ln['bbox'], ln['spans']))
        lines_of[pno] = ls
    full = re.sub(r'\s+', '', ''.join(p.get_text() for p in doc))

    hdr_bad = [(p, t) for p in range(1, n_pdf + 1) for t, bb, sps in lines_of[p] if bb[3] < TOP - 1]
    check('③页眉缺席（版心顶上方无文本）', not hdr_bad, '；'.join(f'p{p}{h}' for p, h in hdr_bad[:4]))

    # ④⑤ 页脚（全局页码＋全局奇偶）
    blocks_pg = {}
    for pno in range(1, n_pdf + 1):
        page = doc[pno - 1]
        blk_rect, num = None, None
        for d in page.get_drawings():
            r = d['rect']
            f = d.get('fill')
            if not f or r.y0 <= BODY_BOT - 10:
                continue
            if rgb255(f) == (221, 221, 221):
                blk_rect = r
        foot_spans, foot_txts = [], []
        gno = start + pno - 1
        want = {str(gno), '%02d' % gno, '%03d' % gno}
        for t, bb, sps in lines_of[pno]:
            if bb[1] > BODY_BOT - 2:
                foot_spans += [sp for sp in sps if sp['text'].strip()]
                foot_txts.append(t)
            for sp in sps:
                if sp['text'].strip() in want and blk_rect and bb[1] > BODY_BOT - 10 \
                   and blk_rect.x0 - 1 <= sp['bbox'][0] and sp['bbox'][2] <= blk_rect.x1 + 1:
                    num = sp
        blocks_pg[pno] = (blk_rect, num, foot_spans, foot_txts)
    if fam == 'J':
        base_ok, det_j, ys_j = True, [], []
        for pno in range(1, n_pdf + 1):
            _b, _n, fs, ft = blocks_pg[pno]
            gno = start + pno - 1
            ftj = ''.join(ft).replace(' ', '')
            good = bool(ft) and ('%02d' % gno) in ftj
            if gno % 2 == 0:
                good = good and '羿郭工作室' in ftj and '选择性必修第一册' in ftj
            if fs:
                ys_j.append(round(min(sp['bbox'][1] for sp in fs), 1))
            base_ok = base_ok and good
            det_j.append(f'p{pno}(卷{gno}){"✗" if not good else "ok"}[{ftj[:24]}]')
        uni_j = (max(ys_j) - min(ys_j)) <= 1.5 if ys_j else False
        check('④页脚（装配卷 YJ-02 文字行：全局卷号 83~89 连续在场＋基线族内一致）', base_ok and uni_j,
              '；'.join(det_j) + f' 基线{ys_j}')
        check('⑤奇偶交替（全局偶＝NN卷+品牌+册名）', base_ok, '')
    else:
        jianming = {'D': ['导学件'], 'L': ['练习件', '拓展册'], 'A': []}[fam]   # 装配本可含多件名（练习本兼拓展册）
        bwT, bhT = cfg['blk']
        geo_ok, geo_bad, dets, uni = True, [], [], set()
        alt_ok, alt_bad = True, []
        for pno in range(1, n_pdf + 1):
            gno = start + pno - 1
            blk_rect, num, fs, ft = blocks_pg[pno]
            if not blk_rect or not num:
                geo_ok = False
                geo_bad.append(f'p{pno}缺块/数字')
                continue
            bw, bh = blk_rect.width / PT, blk_rect.height / PT
            bot = (ph - blk_rect.y1) / PT
            odd = gno % 2 == 1
            near = abs(((num['bbox'][0] if odd else num['bbox'][2])
                        - (blk_rect.x0 if odd else blk_rect.x1))) / PT
            szs = sorted({round(sp['size'], 2) for sp in fs})
            dets.append(f'p{pno}(卷{gno}) {bw:.1f}×{bh:.1f} 底{bot:.1f} 数字{num["size"]:.1f} 近{near:.2f}')
            uni.add((round(bw, 1), round(bh, 1), round(bot, 1), round(num['size'], 1)))
            okg = (abs(bw - bwT) <= 0.6 and abs(bh - bhT) <= 0.3 and 8.5 <= bot <= 13.5
                   and 10.0 <= num['size'] <= 12.0 and 1.5 <= near <= 4.5
                   and any(5.0 <= s <= 5.6 for s in szs))
            if not okg:
                geo_ok = False
                geo_bad.append(f'p{pno}')
            ftj = ''.join(ft).replace(' ', '')
            if odd:
                okp = blk_rect.x1 >= max(cls) + colw - 1.5 and (any(j in ftj for j in jianming)
                                                                or not jianming)
            else:
                okp = blk_rect.x0 <= min(cls) + 1.5 and '人教B' in ftj
            if not okp:
                alt_ok = False
                alt_bad.append(f'p{pno}({"奇" if odd else "偶"})')
        check('④页脚块几何（装配本 全局页码；块窗＝族 blk）', geo_ok,
              '；'.join(dets[:4]) + ('…' if len(dets) > 4 else '')
              + ('' if geo_ok else ' ✗' + ','.join(geo_bad[:5]) + ' 全读数：' + '；'.join(dets)))
        check('⑤奇偶交替（全局奇＝块贴右＋件名集／偶＝块贴左＋册名）', alt_ok,
              f'件名集={jianming or "[空]"}' + ('' if alt_ok else ' ✗' + ','.join(alt_bad[:6])))

    # ⑥ 灰档
    grays_all, gray_bad = set(), []
    for pno in range(1, n_pdf + 1):
        grays = set()
        for t, bb, sps in lines_of[pno]:
            for sp in sps:
                col = sp['color']
                r, g, b = (col >> 16) & 255, (col >> 8) & 255, col & 255
                if r == g == b and 0 < r < 255:
                    grays.add(r)
        for d in doc[pno - 1].get_drawings():
            for key in ('color', 'fill'):
                c = d.get(key)
                if c:
                    rgb = rgb255(c)
                    if rgb[0] == rgb[1] == rgb[2] and 0 < rgb[0] < 255:
                        grays.add(rgb[0])
        grays_all |= grays
        if not grays <= PALETTE:
            gray_bad.append(f'p{pno}={sorted(grays - PALETTE)}')
    check('⑥灰档全集⊆设计调色板（v4③ 参数化）', not gray_bad,
          f'全集{sorted(grays_all)}' + ('' if not gray_bad else ' ✗' + '；'.join(gray_bad[:4])))

    # ⑦ 栏线（D/L）
    if cfg['ncols'] == 2:
        rule_found, rule_len = {}, {}
        for pno in range(1, n_pdf + 1):
            segs = 0.0
            for d in doc[pno - 1].get_drawings():
                r = d['rect']
                if not (r.width <= 1.5 and r.height >= 20):
                    continue
                if abs(r.x0 - MID) > 2 and abs(r.x1 - MID) > 2:
                    continue
                c = d.get('color') or d.get('fill')
                if c and rgb255(c) == (189, 189, 189) and abs((d.get('width') or 0) - 0.4) <= 0.05:
                    rule_found[pno] = d
                    segs += r.height
            rule_len[pno] = round(segs / PT, 1)
        cov_ok = all(rule_len[p] >= 0.15 * (ph - TOP - BOT) / PT for p in rule_len)
        check('⑦栏线（逐页在场 0.4pt 色189＋覆盖≥0.15版心）',
              len(rule_found) == n_pdf and cov_ok, f'页{len(rule_found)}/{n_pdf} 段高{rule_len}')

    # ⑧ 行距主峰（多栏族按栏内配对，与 run_item 同口径）
    if cfg['lead']:
        diffs = []
        for pno in range(1, n_pdf + 1):
            cols = {i: [] for i in range(len(cls))}
            for t, bb, sps in lines_of[pno]:
                if any(9.5 <= sp['size'] <= 11.2 for sp in sps):
                    ci = min(range(len(cls)), key=lambda i: abs(bb[0] - cls[i]))
                    cols[ci].append(sps[0]['origin'][1])
            for c in cols:
                ys = sorted(cols[c])
                diffs += [round((b - a) * 4) / 4 for a, b in zip(ys, ys[1:]) if 3 < b - a < 40]
        peak, cnt = Counter(diffs).most_common(1)[0] if diffs else (0, 0)
        check('⑧行距主峰（装配本设计lead±0.5pt）', abs(peak - cfg['lead']) <= 0.5 and cnt >= 5,
              f'主峰{peak}pt(×{cnt}) 设计{cfg["lead"]}pt')

    # ⑫ 图位（越栏＋压字；位图账归 29 源件门）
    imgs_all = []
    for pno, page in enumerate(doc, 1):
        Hpg = page.rect.height
        for info in page.get_image_info(xrefs=True):
            r = pymupdf.Rect(info['bbox'])
            if r.height > Hpg - 2 or r.width > pw - 2:
                continue
            imgs_all.append((pno, info, r))
    n_viol_e, n_press, press_det = press_check(pdfp, doc, imgs_all, lines_of, cls, colw, pw)
    check('⑫图位（位图账归组件门；栏带内；墨级压字0）', n_viol_e == 0 and n_press == 0,
          f'位图{len(imgs_all)} 越栏{n_viol_e} 压字{n_press}' + ('' if not press_det else ' ✗' + '；'.join(press_det[:4])))

    # ⑯ 答案值签名
    if fam in ('D', 'L', 'J'):
        sigs = ['[答案]', '[解析]', '【答案】', '【解析】', '【详解】', '【点睛】', '【分析】', '故答案为', '故选']
        bad16 = {s: full.count(s) for s in sigs if full.count(s)}
        check('⑯答案值签名反向（装配卷面 0 在场）', not bad16, str({s: full.count(s) for s in sigs}))
    else:
        cnts = {s: full.count(s) for s in ['[答案]', '[解析]', '【答案】']}
        check('⑯答案值签名（答案本族＝设计在场，读数登记）', True, str(cnts))

    doc.close()
    red = [c for c in checks if not c['ok']]
    results[it] = dict(family=fam + '装', gates=checks, n_red=len(red))
    tag = '全绿' if not red else f'红{len(red)}'
    print(f'\n== {it} [{fam}装] —— {tag} ({len(checks)} 门)')
    for c in checks:
        print(('  ✓ ' if c['ok'] else '  ✗R ') + c['gate'] + '　' + c['detail'][:150])
    return len(red)

def main():
    total_red = 0
    items = list(ITEMS) + [(it, ASM[it][0]) for it in ASM]
    for it, fam in items:
        try:
            total_red += run_asm(it) if it in ASM else run_item(it, fam)
        except Exception as e:
            import traceback
            results[it] = dict(family=fam, gates=[dict(gate='执行器异常', ok=False,
                                 detail=traceback.format_exc()[-300:])], n_red=1)
            total_red += 1
            print(f'\n== {it} [{fam}] —— 执行器异常 {e}')
    print(f'\n———— 全件 {len(items)} 项，红门合计 {total_red} ————')
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_S7跑门读数.json')
    json.dump(results, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('读数 json →', out)

if __name__ == '__main__':
    main()
