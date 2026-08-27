# -*- coding: utf-8 -*-
#
# 收编：2026-08-27 选必1整册任务·F2收尾（来源轮次：A4样张首创五杠杆 → C5参数化定稿；此为工具文件夹唯一常驻版，A4/C5桌面scripts副本不再维护）
#
# 用法: python 工具/紧凑化五杠杆改版.py <src.docx> <out.docx> --qstart 起始题号 --qcount 题量 --imgdec <imgdec.json> [--merge decisions.json] [--nogrid]
# 功能: 紧凑化五杠杆①行距300→288＋关行网格 ②纯空段清零(图/公式感知) ③题号底纹A6A6A6(区间门控) ④大图三重保险缩放(imgdec逐张决策) ⑤短行合并(决策文件驱动)；不碰页脚/页码（先内容后页码，两级页码由 册级连续页码.py 统一重盖）

"""transform.py — C5紧凑化铺开五杠杆改版（F8/F9参数化版，样张transform.py改造）
用法: python transform.py <src_docx> <out_docx> --qstart N --qcount M --imgdec <json> [--merge decisions.json] [--nogrid]
杠杆: ①行距300→288＋关行网格 ②纯空段清零(图/公式感知) ③题号底纹M处(区间qstart..qstart+M-1)
      ④大图缩放(按imgdec逐张决策) ⑤短行合并(决策文件驱动)
不碰页脚/页码/pgNumType（D阶段统一重盖）。
"""
import sys, io, os, re, json, zipfile, shutil, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from 紧凑化公共库 import *
from lxml import etree

SRC = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])

def argval(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None

QSTART = int(argval('--qstart'))
QCOUNT = int(argval('--qcount'))
IMGDEC_FILE = argval('--imgdec')
MERGE_FILE = argval('--merge')
NOGRID = '--nogrid' in sys.argv
assert QSTART and QCOUNT and IMGDEC_FILE

TMP = os.path.join(os.path.dirname(OUT), '_tmp_unpacked')
if os.path.isdir(TMP):
    shutil.rmtree(TMP)
with zipfile.ZipFile(SRC) as z:
    z.extractall(TMP)

doc_path = os.path.join(TMP, 'word', 'document.xml')
sty_path = os.path.join(TMP, 'word', 'styles.xml')
tree, root, body = load(doc_path)
log = {}

# ---------- 杠杆① 行距 300→288 ----------
n_sp = 0
for sp in root.iter(qn('w:spacing')):
    if sp.get(qn('w:line')) == '300':
        sp.set(qn('w:line'), '288')
        n_sp += 1
log['行距288改处数(document.xml)'] = n_sp
stree = etree.parse(sty_path)
sroot = stree.getroot()
n_sp2 = 0
for sp in sroot.iter(qn('w:spacing')):
    if sp.get(qn('w:line')) == '300':
        sp.set(qn('w:line'), '288')
        n_sp2 += 1
log['行距288改处数(styles.xml pPrDefault)'] = n_sp2
stree.write(sty_path, xml_declaration=True, encoding='UTF-8', standalone=True)

# ---------- 杠杆③ 题号底纹（递进门控：起点QSTART，共QCOUNT处） ----------
QRE = re.compile(r'^(\d{1,3})．')
exp = [QSTART]
shade_cnt = 0
shaded_runs = []
for p in body.findall(qn('w:p')):
    raw = para_text(p)
    m = QRE.match(raw)
    if not m or int(m.group(1)) != exp[0]:
        continue
    exp[0] += 1
    prefix = m.group(0)          # 'N．'
    runs = [r for r in p.findall(qn('w:r')) if r.find(qn('w:t')) is not None]
    remaining = prefix
    contributors = []
    for r in runs:
        if not remaining:
            break
        t_el = r.find(qn('w:t'))
        txt = t_el.text or ''
        k = 0
        while k < len(txt) and k < len(remaining) and txt[k] == remaining[k]:
            k += 1
        if k == 0:
            continue
        contributors.append((r, t_el, k))
        remaining = remaining[k:]
    assert not remaining, '题号前缀跨run消费失败: %s / %r' % (prefix, raw[:30])
    first_r = contributors[0][0]
    new_r = copy.deepcopy(first_r)
    for ch in new_r.findall(qn('w:t')):
        new_r.remove(ch)
    t_new = etree.SubElement(new_r, qn('w:t'))
    t_new.text = prefix
    t_new.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    rpr = new_r.find(qn('w:rPr'))
    if rpr is None:
        rpr = etree.Element(qn('w:rPr'))
        new_r.insert(0, rpr)
    if rpr.find(qn('w:b')) is None:
        etree.SubElement(rpr, qn('w:b'))
    if rpr.find(qn('w:bCs')) is None:
        etree.SubElement(rpr, qn('w:bCs'))
    for old_shd in rpr.findall(qn('w:shd')):
        rpr.remove(old_shd)
    shd = etree.SubElement(rpr, qn('w:shd'))
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), 'A6A6A6')
    first_r.addprevious(new_r)
    for r, t_el, k in contributors:
        txt = t_el.text or ''
        t_el.text = txt[k:]
        t_el.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        if not t_el.text:
            r.getparent().remove(r)
    shaded_runs.append(new_r)
    shade_cnt += 1
log['题号底纹run数'] = shade_cnt
log['题号门控终值'] = exp[0]
assert shade_cnt == QCOUNT, '题号底纹数≠%d（实得%d）' % (QCOUNT, shade_cnt)

# ---------- 杠杆④ 大图三重保险缩放（按imgdec逐张决策；只>10cm者适用） ----------
WDEC = json.load(open(IMGDEC_FILE, encoding='utf-8'))   # {media名: {'factor':f,'判断依据':...}}
rels_root = etree.parse(os.path.join(TMP, 'word', '_rels', 'document.xml.rels')).getroot()
relmap = {r.get('Id'): r.get('Target') for r in rels_root}
scale_log = []
media_seen = {}
for ext_el in list(root.iter(qn('wp:extent'))):
    cx, cy = int(ext_el.get('cx')), int(ext_el.get('cy'))
    w_cm = cx / 360000.0
    if w_cm <= 10:
        continue          # 仅显示宽>10cm图适用
    drawing = ext_el
    while drawing is not None and drawing.tag != qn('w:drawing'):
        drawing = drawing.getparent()
    rid = None
    for blip in drawing.iter(qn('a:blip')):
        rid = blip.get(qn('r:embed'))
    media = os.path.basename(relmap.get(rid, '?'))
    dec = WDEC.get(media, {'factor': 1.0, '判断依据': '无登记决策——按铁律不缩'})
    factor = float(dec['factor'])
    ncx, ncy = int(cx * factor), int(cy * factor)
    ext_el.set('cx', str(ncx)); ext_el.set('cy', str(ncy))
    for xext in drawing.iter(qn('a:ext')):
        if xext.get('cx') == str(cx) and xext.get('cy') == str(cy):
            xext.set('cx', str(ncx)); xext.set('cy', str(ncy))
    scale_log.append({'media': media, '原cm': [round(w_cm, 2), round(cy / 360000.0, 2)],
                      '新cm': [round(ncx / 360000.0, 2), round(ncy / 360000.0, 2)],
                      'factor': factor, '判断依据': dec['判断依据']})
log['大图缩放登记'] = scale_log
log['大图缩放张数'] = sum(1 for s in scale_log if s['factor'] < 1.0)
log['大图不缩张数'] = sum(1 for s in scale_log if s['factor'] == 1.0)
used = set(s['media'] for s in scale_log)
unused = set(WDEC) - used
assert not unused, 'imgdec中存在未命中的media: %s' % unused

# ---------- 杠杆⑤ 短行合并（顺序安全共合；并入紧邻前一存活段） ----------
if MERGE_FILE:
    decisions = json.load(open(MERGE_FILE, encoding='utf-8'))
    dmap = {d['段索引']: d for d in decisions['items']}
    kids = list(body)
    SECT_RE = re.compile(r'^\d+\.\d+(\.\d+)?(\s|$|（)')
    QRE2 = re.compile(r'^(\d{1,3})．')
    seg_head = None
    zone = 'LECT'
    implicit_armed = False
    exp2 = [QSTART]
    merged_n = auto_keep_n = 0
    for idx, el in enumerate(kids):
        tag = etree.QName(el).localname
        if tag == 'sectPr':
            continue
        if tag == 'tbl':
            seg_head = None; implicit_armed = False
            continue
        t = para_text(el)
        st = t.strip()
        if not st:
            if has_object(el):
                seg_head = None
                implicit_armed = (zone == 'ANS')
            continue
        m = QRE2.match(st)
        if m and int(m.group(1)) == exp2[0]:
            exp2[0] += 1
            seg_head = None; implicit_armed = False; zone = 'STEM'
            continue
        if SECT_RE.match(st) or st.startswith('题型通式') or st.startswith('本节') or st.startswith('本卷') or st.startswith('全件') or idx == 0:
            seg_head = None; implicit_armed = False
            if SECT_RE.match(st) or st.startswith('题型通式'):
                zone = 'LECT'
            continue
        drow = dmap.get(idx)
        is_label = is_label_start(st)
        is_mark = is_marker_start(st)
        is_entry = re.match(r'^\d{1,3}[\.．]', st) is not None and not is_label
        if is_entry:
            seg_head = None; implicit_armed = False
            continue
        if is_label or is_mark:
            if zone == 'STEM' and is_mark:
                seg_head = el
                continue
            if is_label and zone == 'STEM':
                zone = 'ANS'
            seg_head = el; implicit_armed = False
            continue
        # CONT
        dec = drow['决策'] if drow else '保留'
        if zone == 'STEM':
            seg_head = el
            continue
        if dec == '合并':
            if seg_head is None:
                auto_keep_n += 1
                seg_head = el
                continue
            for ch in list(el):
                if ch.tag == qn('w:pPr'):
                    continue
                seg_head.append(ch)
            body.remove(el)
            merged_n += 1
            continue
        seg_head = el
    log['短行合并执行条数'] = merged_n
    log['合并改保留(无接收头)条数'] = auto_keep_n
    if 'items_br' in decisions:
        br_n = 0
        kids2 = list(body)
        for b in decisions['items_br']:
            if b['决策'] != '合并':
                continue
            raise AssertionError('br决策不应出现在本件（源无手动换行）；如有需逐条人工审')
        log['段内br合并条数'] = 0

# ---------- 禁排属性清零 ----------
n_kn = n_kl = n_pb = 0
for tag, cnt in ((qn('w:keepNext'), 'keepNext'), (qn('w:keepLines'), 'keepLines'), (qn('w:pageBreakBefore'), 'pageBreakBefore')):
    for el in list(root.iter(tag)):
        el.getparent().remove(el)
        if cnt == 'keepNext': n_kn += 1
        elif cnt == 'keepLines': n_kl += 1
        else: n_pb += 1
log['keepNext移除'] = n_kn; log['keepLines移除'] = n_kl; log['pageBreakBefore移除'] = n_pb

# ---------- §7⑥残留剥除：删除线/双删除线样式（只剥rPr子元素，不动任何文字） ----------
n_strike = 0
for tag in (qn('w:strike'), qn('w:dstrike')):
    for el in list(root.iter(tag)):
        el.getparent().remove(el)
        n_strike += 1
log['strike/dstrike剥除'] = n_strike

# ---------- §5零内容垃圾图清理候选扫描（<3磅；命中只登记并断言为空——两件勘测均为0） ----------
tiny_log = []
for ext_el in list(root.iter(qn('wp:extent'))):
    cx, cy = int(ext_el.get('cx')), int(ext_el.get('cy'))
    if cx < 38100 or cy < 38100:
        d_el = ext_el
        while d_el is not None and d_el.tag != qn('w:drawing'):
            d_el = d_el.getparent()
        if d_el is None:
            continue
        rels_root2 = etree.parse(os.path.join(TMP, 'word', '_rels', 'document.xml.rels')).getroot()
        rmap2 = {r.get('Id'): r.get('Target') for r in rels_root2}
        blip = d_el.find('.//' + qn('a:blip'))
        media2 = rmap2.get(blip.get(qn('r:embed')), '?') if blip is not None else '?'
        par = ext_el.getparent()
        while par is not None and par.tag != qn('w:p'):
            par = par.getparent()
        tiny_log.append({'media': media2, '显示pt': [round(cx / 12700, 2), round(cy / 12700, 2)],
                         '上下文段': para_text(par)[:30] if par is not None else '?'})
if tiny_log:
    raise AssertionError('发现垃圾图候选%d张——须人工逐张识别后再授权删除，禁止静默批量删: %r' % (len(tiny_log), tiny_log))
log['垃圾图清理张数'] = 0

# ---------- 杠杆② 纯空段清零（图/公式感知；B5回填纯公式段绝不删） ----------
n_empty = 0
protected = 0
for p in list(body.findall(qn('w:p'))):
    if para_text(p).strip():
        continue
    if has_object(p):
        protected += 1
        continue
    body.remove(p)
    n_empty += 1
log['纯空段删除数'] = n_empty
log['图形/公式段保留数(含B5回填公式段)'] = protected

# ---------- docGrid 关行网格 ----------
if NOGRID:
    for dg in root.iter(qn('w:docGrid')):
        dg.set(qn('w:type'), 'default')
    log['docGrid'] = '→type=default(关行网格)'

tree.write(doc_path, xml_declaration=True, encoding='UTF-8', standalone=True)

# ---------- 重打包（不碰页脚/页码/pgNumType） ----------
if os.path.isfile(OUT):
    os.remove(OUT)
zf = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
for base, _, files in os.walk(TMP):
    for f in files:
        full = os.path.join(base, f)
        arc = os.path.relpath(full, TMP).replace('\\', '/')
        zf.write(full, arc)
zf.close()
shutil.rmtree(TMP)
print(json.dumps(log, ensure_ascii=False, indent=1))
