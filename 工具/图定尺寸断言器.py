# -*- coding: utf-8 -*-
r"""图定尺寸断言器.py — 工具债案11（公共规则§7图片内容感知定尺寸＋附则《表格规范》图尺寸工具门；
2026-09-04 选必1复合修复轮子步5建）。

断言面（规格书v2第17条＋任务书子步5）：
  ①含文本主体且显示高≥1.5cm的图过 [9,12]pt 带域断言（主体字符＝数量占比最大字号档的字母数字视觉高；
    目标≈9pt、上限12超即缩；下限6.5pt仅可辨底线不驱动放大，跌破→差图重绘候选登记）；
  ②登记类豁免族（符号/公式碎片/纯几何无字符图＋断言域外图）逐张登记实际字高与最大边，
    无字符图双参判定（最大边≤栏宽＋相对题干字号比例≤2:1，逐张登记判定值）；
  ③显示宽≤栏宽 全图无例外（超即缩）；④单图显示高≤9cm（超限逐张判定落盘理由）；
  ⑤150dpi自然尺寸禁令（显示宽cm≤像素宽÷59.06；像素<200×200不放大不缩放）；
  ⑥表格单元格内图：显示宽≤所在列分配宽−cellMar（随子步4列宽现算）；
  ⑦全件图宽离散度台账（最大/最小/中位＋豁免族清单）；⑧页尾空白断言（--page-tail，PDF侧）。
边界：只改 wp:extent（含 a:ext 同步）＋登记；不重绘不转写；图像守恒按计数/哈希恒等复跑；
      wp:anchor=0 与嵌入型独立段制复跑随断言。

模式：
  --scan    只读测量＋处置预案（dry-run）
  --apply   按预案改 extent（文字流零字符核验＋守恒复跑）
  --assert  施工后全参数断言＋台账落盘
  --page-tail 页尾空白断言（输入＝PDF：python 图定尺寸断言器.py --page-tail --out 前缀 代号=pdf路径 ...）
用法:
  python 图定尺寸断言器.py --scan|--apply|--assert --out 前缀 代号=docx路径 ...
"""
import sys, io, os, re, json, zipfile, shutil, hashlib, statistics
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
def q(t): return '{%s}%s' % (W, t)

EMU_PER_CM = 360000.0
CM_PER_TW = 1.0 / 566.93
PT_PER_CM = 28.3465
PX_PER_CM_150 = 59.06
COL_W_CM_DEFAULT = 8.62      # 兜底；实际栏宽逐件现算
BAND_LO, BAND_HI, BAND_TGT, BAND_FLOOR = 9.0, 12.0, 9.5, 6.5
ICON_CM = 1.5                # 显示高<1.5cm＝断言域外（图标级）
MAX_H_CM = 9.0

RE_FIGREF = re.compile(r'(如图|图甲|图乙|图丙|图丁|图所示|下图|上图|右图|左图|见图|图\d)')


def pixel_size(data):
    try:
        from PIL import Image
        with Image.open(io.BytesIO(data)) as im:
            return im.size
    except Exception:
        return None


def measure_char_height(data):
    """cv2连通域测主体字号档字符高（px，原图像素坐标）。返回 (h_px, n_dom, n_all, conf) 或 None。"""
    try:
        import numpy as np
        import cv2
    except Exception:
        return None
    arr = np.frombuffer(data, dtype='uint8') if isinstance(data, (bytes, bytearray)) else None
    if arr is None:
        return None
    img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
    if img is None:
        return None
    if img.ndim == 3 and img.shape[2] == 4:
        bgr = img[:, :, :3].astype('float32')
        alpha = img[:, :, 3:4].astype('float32') / 255.0
        img = (bgr * alpha + 255.0 * (1 - alpha)).astype('uint8')
    if img.ndim == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    H0, W0 = gray.shape[:2]
    if H0 < 20 or W0 < 20:
        return None
    scale = min(1.0, 1200.0 / max(H0, W0))
    if scale < 1.0:
        gray_s = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    else:
        gray_s = gray
    H, W = gray_s.shape[:2]
    bw = cv2.threshold(gray_s, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    border = list(bw[0, :]) + list(bw[-1, :]) + list(bw[:, 0]) + list(bw[:, -1])
    if sum(border) / len(border) < 128:
        bw = 255 - bw
    fg = 255 - bw
    n, labels, stats, cents = cv2.connectedComponentsWithStats(fg, connectivity=8)
    comps = []
    for i in range(1, n):
        x, y, wc, hc, area = stats[i]
        if hc < 4 or wc < 2 or area < 10:
            continue
        if hc > 0.6 * H or wc > 0.6 * W:
            continue
        asp = wc / float(hc)
        if asp < 0.05 or asp > 3.0:
            continue
        fill = area / float(wc * hc)
        if fill < 0.04 or fill > 0.95:
            continue
        # 虚线碎片过滤：细长且实心（字母「1」ratio≤3.5 不受影响）
        ratio = max(wc, hc) / float(min(wc, hc))
        if ratio > 3.5 and fill > 0.70:
            continue
        comps.append((int(hc), int(area)))
    if len(comps) < 4:
        return None
    heights = [c[0] for c in comps]
    med = statistics.median(heights)
    binw = max(2.0, med * 0.15)
    bins = {}
    for h, a in comps:
        b = bins.setdefault(int(h / binw), [0, 0, []])
        b[0] += a          # 面积权重（防虚线碎片以数量霸榜）
        b[1] += 1          # 计数
        b[2].append(h)
    dom = max(bins.values(), key=lambda v: v[0])     # 面积占比最大字号档
    tot_area = sum(v[0] for v in bins.values())
    if dom[1] < 3 or dom[0] < 0.18 * tot_area:
        return None
    h_px = statistics.median(dom[2]) / scale
    return h_px, dom[1], len(comps), round(dom[0] / tot_area, 3)


def parse_rels(z):
    try:
        root = etree.fromstring(z.read('word/_rels/document.xml.rels'))
    except KeyError:
        return {}
    out = {}
    for rel in root.iter('{%s}Relationship' % REL):
        if (rel.get('Type') or '').endswith('/image'):
            out[rel.get('Id')] = rel.get('Target')
    return out


def zone_params(root):
    body = root.find(q('body'))
    sect = body.find(q('sectPr'))
    pgSz, pgMar = sect.find(q('pgSz')), sect.find(q('pgMar'))
    cols = sect.find(q('cols'))
    num = int(cols.get(q('num')) or 1) if cols is not None else 1
    space = int(cols.get(q('space')) or 425) if cols is not None else 425
    content_tw = int(pgSz.get(q('w'))) - int(pgMar.get(q('left'))) - int(pgMar.get(q('right')))
    col_tw = (content_tw - space * (num - 1)) / num
    return col_tw * CM_PER_TW


def cell_margins_of(tbl):
    l = r = 108
    tblpr = tbl.find(q('tblPr'))
    if tblpr is not None:
        cm = tblpr.find(q('tblCellMar'))
        if cm is not None:
            e = cm.find(q('left'))
            if e is not None and e.get(q('w')) is not None:
                l = int(e.get(q('w')))
            e = cm.find(q('right'))
            if e is not None and e.get(q('w')) is not None:
                r = int(e.get(q('w')))
    return l, r


def tc_cap_tw(tc):
    """单元格内容可用宽（缇）＝tcW − 表cellMar左右。"""
    tcpr = tc.find(q('tcPr'))
    if tcpr is None:
        return None
    tcw = tcpr.find(q('tcW'))
    if tcw is None or not tcw.get(q('w')):
        return None
    anc = tc
    marL = marR = 108
    while anc is not None:
        if etree.QName(anc).localname == 'tbl':
            marL, marR = cell_margins_of(anc)
            break
        anc = anc.getparent()
    return int(tcw.get(q('w'))) - marL - marR


def scan_docx(path, measure=True):
    """全图清单＋处置预案。"""
    z = zipfile.ZipFile(path)
    root = etree.fromstring(z.read('word/document.xml'))
    rid2t = parse_rels(z)
    col_w_cm = zone_params(root)
    body = root.find(q('body'))
    media_hash = {}
    rows = []
    # 直接遍历全部含 drawing 的段落（含表格单元格内段落）；ki＝含图段落序号（施工按键匹配）
    all_paras = list(body.iter(q('p')))
    ki = -1
    for pi, p in enumerate(all_paras):
        draws = list(p.iter(q('drawing')))
        if not draws:
            continue
        ki += 1
        para_txt = ''.join(t.text or '' for t in p.iter(q('t'))).strip()
        p_txt = para_txt
        # 所在表格单元格（若有）
        anc = p.getparent()
        in_tc = None
        while anc is not None:
            ln = etree.QName(anc).localname
            if ln == 'tc':
                in_tc = anc
                break
            if ln == 'body':
                break
            anc = anc.getparent()
        cap_tw = tc_cap_tw(in_tc) if in_tc is not None else None
        for d in draws:
            ext = d.find('.//{%s}extent' % WP)
            cx = int(ext.get('cx')) if ext is not None and ext.get('cx') else 0
            cy = int(ext.get('cy')) if ext is not None and ext.get('cy') else 0
            disp_w, disp_h = cx / EMU_PER_CM, cy / EMU_PER_CM
            is_anchor = d.find('{%s}anchor' % WP) is not None
            blip = d.find('.//{%s}blip' % A)
            rid = blip.get('{%s}embed' % R) if blip is not None else None
            tgt = rid2t.get(rid)
            pw = ph = None
            m = None
            if tgt:
                zp = 'word/' + tgt if not tgt.startswith('/') else tgt[1:]
                try:
                    data = z.read(zp)
                    media_hash.setdefault(zp, hashlib.sha256(data).hexdigest()[:16])
                    sz = pixel_size(data)
                    if sz:
                        pw, ph = sz
                    if measure:
                        m = measure_char_height(data)
                        if m:
                            m = (float(m[0]), int(m[1]), int(m[2]), float(m[3]))
                except KeyError:
                    pass
            nat_w = (pw / PX_PER_CM_150) if pw else None
            # 带域测量
            band = None
            if m and disp_h >= ICON_CM:
                h_pt = m[0] * (disp_h * PT_PER_CM) / ph if ph else None
                if h_pt:
                    band = {'h_pt': round(h_pt, 2), 'n_dom': m[1], 'n_all': m[2], 'conf': m[3]}
            rows.append({'ki': ki, 'rid': rid, 'media': tgt, 'cx': cx, 'cy': cy,
                         'disp_w': round(disp_w, 3), 'disp_h': round(disp_h, 3),
                         'pw': pw, 'ph': ph, 'nat_w': round(nat_w, 3) if nat_w else None,
                         'anchor': is_anchor, 'in_table': in_tc is not None,
                         'cap_tw': cap_tw, 'band': band,
                         'para_txt': p_txt[:30], 'n_in_para': len(draws)})
    # 图引邻接核验（正文区纯图段：前后最近非空段有无图引）
    z.close()
    return {'col_w_cm': round(col_w_cm, 3), 'rows': rows, 'media_hash': media_hash}


def plan_images(scan):
    """逐图处置预案。"""
    col_w = scan['col_w_cm']
    for r in scan['rows']:
        acts = []
        factor = 1.0
        # ③栏宽硬钳
        if r['disp_w'] > col_w:
            f = col_w / r['disp_w']
            factor = min(factor, f)
            acts.append('栏宽钳制→%.2fcm' % col_w)
        # ⑥表格单元格适配
        if r['in_table'] and r['cap_tw']:
            cap_cm = (r['cap_tw'] - 20) * CM_PER_TW
            cur_w = r['disp_w'] * factor
            if cap_cm > 0.2 and cur_w > cap_cm:
                factor *= cap_cm / cur_w
                acts.append('单元格适配→%.2fcm' % cap_cm)
        # ⑤150dpi自然尺寸禁令
        small_px = (r['pw'] or 0) < 200 and (r['ph'] or 0) < 200
        if r['nat_w'] and r['disp_w'] * factor > r['nat_w'] + 1e-6:
            if small_px:
                acts.append('像素<200×200不缩（登记）')
            else:
                f = r['nat_w'] / (r['disp_w'] * factor)
                factor *= f
                acts.append('150dpi自然宽钳制→%.2fcm' % r['nat_w'])
        # ①带域
        r['band_verdict'] = None
        if r['band']:
            h_pt = r['band']['h_pt']
            if h_pt > BAND_HI:
                f = BAND_TGT / h_pt
                factor *= f
                r['band_verdict'] = '超上限缩→%.1fpt' % BAND_TGT
                acts.append('主体字高%.1fpt>12缩→%.1fpt' % (h_pt, BAND_TGT))
            elif h_pt < BAND_FLOOR:
                r['band_verdict'] = '跌破6.5pt→差图重绘候选（不放大）'
            elif h_pt < BAND_LO:
                r['band_verdict'] = '低于9pt不驱动放大（合规）'
            else:
                r['band_verdict'] = '带域内[9,12]pt合规'
        # 分类
        if r['disp_h'] < ICON_CM:
            r['cls'] = '豁免族-断言域外(高<1.5cm)'
        elif r['band'] is None:
            r['cls'] = '豁免族-无字符/测不出'
        else:
            r['cls'] = '带域断言族'
        r['factor'] = round(factor, 4)
        r['acts'] = acts
        r['new_w'] = round(r['disp_w'] * factor, 3)
        r['new_h'] = round(r['disp_h'] * factor, 3)
        # ④9cm上限（施工后仍超限→判定登记）
        r['over9cm'] = r['new_h'] > MAX_H_CM
        # ②双参判定值
        r['p1_maxedge'] = round(max(r['new_w'], r['new_h']), 3)
        r['p2_ratio'] = round((r['new_h'] * PT_PER_CM) / 12.0, 2)
        # 缩后跌破6.5pt预测（带域族按新尺寸换算）
        if r['band'] and factor < 1.0:
            new_hpt = r['band']['h_pt'] * factor
            r['post_h_pt'] = round(new_hpt, 2)
            if new_hpt < BAND_FLOOR:
                r['band_verdict'] = (r['band_verdict'] or '') + '；缩后预测%.1fpt<6.5→差图重绘候选' % new_hpt
    return scan


def dispersion(rows):
    ws = [r['new_w'] for r in rows]
    return {'n': len(rows), 'max': max(ws) if ws else 0, 'min': min(ws) if ws else 0,
            'median': round(statistics.median(ws), 3) if ws else 0}


def apply_extents(path, scan):
    """只改 wp:extent＋a:ext。返回改动数与守恒核验。"""
    z = zipfile.ZipFile(path)
    raw = z.read('word/document.xml')
    media_before = {}
    for name in z.namelist():
        if name.startswith('word/media/') and not name.endswith('/'):
            media_before[name] = hashlib.sha256(z.read(name)).hexdigest()
    z.close()
    root = etree.fromstring(raw)
    body = root.find(q('body'))
    # 文字流（w:t＋m:t）改前
    def tstream(rt):
        out = []
        for el in rt.find(q('body')).iter():
            ns, ln = etree.QName(el).namespace, etree.QName(el).localname
            if (ns == W and ln == 't') or (ns == M and ln == 't'):
                out.append(el.text or '')
        return out
    ts0 = tstream(root)
    changed = 0
    drawing_count = 0
    plan_by_key = {}
    for r in scan['rows']:
        plan_by_key.setdefault(r['ki'], []).append(r)
    all_paras = list(body.iter(q('p')))
    ki = -1
    for p in all_paras:
        draws = list(p.iter(q('drawing')))
        if not draws:
            continue
        ki += 1
        plans = plan_by_key.get(ki, [])
        for d, r in zip(draws, plans):
            drawing_count += 1
            if r['factor'] >= 0.995:
                continue
            new_cx = int(round(r['cx'] * r['factor']))
            new_cy = int(round(r['cy'] * r['factor']))
            ext = d.find('.//{%s}extent' % WP)
            if ext is not None:
                ext.set('cx', str(new_cx))
                ext.set('cy', str(new_cy))
            for aext in d.iter('{%s}ext' % A):
                if aext.get('cx'):
                    aext.set('cx', str(new_cx))
                    aext.set('cy', str(new_cy))
            changed += 1
    ts1 = tstream(root)
    new_raw = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    sha_before = hashlib.sha256(open(path, 'rb').read()).hexdigest()[:12]
    tmp = path + '.tmp_rewrite'
    zin = zipfile.ZipFile(path, 'r')
    zout = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == 'word/document.xml':
            data = new_raw
        zout.writestr(item, data)
    zin.close()
    zout.close()
    shutil.move(tmp, path)
    # 守恒复跑：media 计数/哈希不变
    z2 = zipfile.ZipFile(path)
    media_after = {}
    for name in z2.namelist():
        if name.startswith('word/media/') and not name.endswith('/'):
            media_after[name] = hashlib.sha256(z2.read(name)).hexdigest()
    d2 = len(etree.fromstring(z2.read('word/document.xml')).find(q('body')).findall('.//' + q('drawing')))
    z2.close()
    return {'changed': changed, 'text_equal': ts0 == ts1,
            'media_count_equal': len(media_before) == len(media_after),
            'media_hash_equal': media_before == media_after,
            'drawing_before': drawing_count, 'drawing_after': d2,
            'sha_before': sha_before, 'sha_after': hashlib.sha256(open(path, 'rb').read()).hexdigest()[:12]}


def figref_check(rows, path):
    """图段紧随引用文字段复跑：纯图段（段内仅图）其前后最近非空段须含图引（登记存疑项，非硬失败）。"""
    z = zipfile.ZipFile(path)
    root = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = root.find(q('body'))
    kids = list(body)
    suspects = []
    for i, el in enumerate(kids):
        if etree.QName(el).localname != 'p':
            continue
        draws = list(el.iter(q('drawing')))
        if not draws:
            continue
        txt = ''.join(t.text or '' for t in el.iter(q('t'))).strip()
        if txt:
            continue                       # 非纯图段（图随文内）不属本检
        # 纯图段：查前后
        prev_t = next_t = ''
        for j in range(i - 1, -1, -1):
            if etree.QName(kids[j]).localname == 'p':
                t = ''.join(x.text or '' for x in kids[j].iter(q('t'))).strip()
                if t:
                    prev_t = t
                    break
        for j in range(i + 1, len(kids)):
            if etree.QName(kids[j]).localname == 'p':
                t = ''.join(x.text or '' for x in kids[j].iter(q('t'))).strip()
                if t:
                    next_t = t
                    break
        if RE_FIGREF.search(prev_t or '') or RE_FIGREF.search(next_t or ''):
            continue
        suspects.append({'kid': i, 'n_img': len(draws), 'prev': (prev_t or '')[:24], 'next': (next_t or '')[:24]})
    return suspects


def page_tail(pdf_path, code):
    """页尾空白断言：逐页正文区页尾连续空白＞版心高35%登记归因。"""
    import pymupdf
    doc = pymupdf.open(pdf_path)
    out = []
    for pno in range(doc.page_count):
        pg = doc[pno]
        W_, H_ = pg.rect.width, pg.rect.height
        mt = mb = 42.5
        body_top, body_bot = mt, H_ - mb
        body_h = body_bot - body_top
        max_y = body_top
        for b in pg.get_text('blocks'):
            x0, y0, x1, y1, text = b[0], b[1], b[2], b[3], b[4]
            yc = (y0 + y1) / 2
            if yc <= mt or yc >= H_ - mb:
                continue
            if '羿郭工作室' in text or re.search(r'本\d+/共\d+本|第\d+页', re.sub(r'\s+', '', text)) and yc > H_ - mb - 20:
                continue
            max_y = max(max_y, y1)
        for d in pg.get_drawings():
            r = d['rect']
            if r.y0 > mt and r.y1 < H_ - mb:
                max_y = max(max_y, r.y1)
        for img in pg.get_images(full=True):
            try:
                for rc in pg.get_image_rects(img[0]):
                    if rc.y0 > mt and rc.y1 < H_ - mb:
                        max_y = max(max_y, rc.y1)
            except Exception:
                pass
        blank = body_bot - max_y
        if blank > 0.35 * body_h:
            out.append({'page': pno + 1, 'blank_pt': round(blank, 1), 'body_h': round(body_h, 1),
                        'ratio': round(blank / body_h, 3)})
    doc.close()
    return out


def to_md(results, mode):
    md = ['# 图定尺寸%s报告（案11）' % {'scan': '测量/dry-run', 'apply': '施工', 'assert': '断言'}[mode], '']
    for code, r in results.items():
        md.append('## %s（栏宽现算=%scm）' % (code, r['col_w_cm']))
        rows = r['rows']
        disp = dispersion(rows)
        n_act = sum(1 for x in rows if x['factor'] < 0.995)
        n_band = sum(1 for x in rows if x['cls'] == '带域断言族')
        n_ex = len(rows) - n_band
        n_cand = sum(1 for x in rows if x.get('band_verdict') and '差图重绘候选' in x['band_verdict'])
        n_o9 = sum(1 for x in rows if x['over9cm'])
        n_anchor = sum(1 for x in rows if x['anchor'])
        md.append('- 图 %d 张（带域断言族 %d／豁免族 %d）；处置改动 %d 张；差图重绘候选 %d；9cm超限 %d；wp:anchor=%d' % (
            len(rows), n_band, n_ex, n_act, n_cand, n_o9, n_anchor))
        md.append('- 图宽离散度：max=%.2f min=%.2f median=%.2f cm' % (disp['max'], disp['min'], disp['median']))
        md.append('| # | 类 | 显示cm(旧→新) | 像素 | 主体字高pt | 判定/处置 | 归属 |')
        md.append('|---|---|---|---|---|---|---|')
        for i, x in enumerate(rows, 1):
            bh = x['band']['h_pt'] if x['band'] else '—'
            md.append('| %d | %s | %.2f×%.2f→%.2f×%.2f | %s×%s | %s | %s | %s |' % (
                i, x['cls'], x['disp_w'], x['disp_h'], x['new_w'], x['new_h'],
                x['pw'] or '?', x['ph'] or '?', bh,
                (x.get('band_verdict') or '；'.join(x['acts']) or '不动').replace('|', '｜'),
                x['para_txt'].replace('|', '｜')))
        md.append('')
    return '\n'.join(md)


def main():
    args, opts, i = [], {}, 1
    while i < len(sys.argv):
        a = sys.argv[i]
        if a.startswith('--'):
            if '=' in a:
                k, v = a.split('=', 1)
                opts[k] = v
            elif a == '--out' and i + 1 < len(sys.argv):
                opts[a] = sys.argv[i + 1]
                i += 1
            else:
                opts[a] = True
        else:
            args.append(a)
        i += 1
    out = str(opts.get('--out', '图定尺寸_out'))
    pairs = [tuple(a.split('=', 1)) for a in args if '=' in a]
    odir = os.path.dirname(os.path.abspath(out))
    if odir:
        os.makedirs(odir, exist_ok=True)
    if '--page-tail' in opts:
        res = {}
        for code, path in pairs:
            res[code] = page_tail(path, code)
            print('[%s] 页尾空白>35%% 页数=%d' % (code, len(res[code])))
        with open(out + '.json', 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
        md = ['# 页尾空白断言（>版心高35%登记）', '']
        for code, rows in res.items():
            md.append('## %s：命中 %d 页' % (code, len(rows)))
            for r in rows:
                md.append('- p%d 空白%.1fpt/版心%.1fpt（%.1f%%）' % (r['page'], r['blank_pt'], r['body_h'], r['ratio'] * 100))
        with open(out + '.md', 'w', encoding='utf-8') as f:
            f.write('\n'.join(md) + '\n')
        return
    mode = 'scan'
    for m in ('scan', 'apply', 'assert'):
        if '--' + m in opts:
            mode = m
    results = {}
    for code, path in pairs:
        if not os.path.exists(path):
            print('[%s] 缺失' % code)
            continue
        scan = plan_images(scan_docx(path, measure=True))
        rec = {'col_w_cm': scan['col_w_cm'], 'rows': scan['rows']}
        if mode == 'apply':
            rec['apply'] = apply_extents(path, scan)
            print('[%s] 图%d 改动%d 文字流等=%s 守恒media=%s/%s drawing %d→%d' % (
                code, len(scan['rows']), rec['apply']['changed'], rec['apply']['text_equal'],
                rec['apply']['media_count_equal'], rec['apply']['media_hash_equal'],
                rec['apply']['drawing_before'], rec['apply']['drawing_after']))
        else:
            n_act = sum(1 for x in scan['rows'] if x['factor'] < 0.995)
            print('[%s] 图%d（带域%d）处置预案%d wp:anchor=%d' % (
                code, len(scan['rows']), sum(1 for x in scan['rows'] if x['cls'] == '带域断言族'),
                n_act, sum(1 for x in scan['rows'] if x['anchor'])))
        if mode == 'assert':
            rec['figref_suspects'] = figref_check(scan['rows'], path)
        results[code] = rec
    with open(out + '.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    with open(out + '.md', 'w', encoding='utf-8') as f:
        f.write(to_md(results, mode if mode != 'assert' else 'assert'))
    print('落盘: %s.json / .md' % out)


if __name__ == '__main__':
    main()
