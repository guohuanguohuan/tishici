# -*- coding: utf-8 -*-
"""RF修复轮 定点迭代主循环。
每轮：restore原始副本→按累计shift手术→COM导出→PyMuPDF全页扫描→
锚匹配（XML序 vs PDF渲染序对齐）→仍失败锚（底>785）加量。
最多3轮；I2 idx12单独下移+65（正文被盖专项）。
产物：输出\loop_log.json、PDF\<code>_fix<r>.pdf。"""
import sys, os, json, shutil, zipfile
sys.stdout.reconfigure(encoding='utf-8')
from lxml import etree
import fitz
import win32com.client as wc

R = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复'
BASE = os.path.join(R, '基线'); PRIS = os.path.join(BASE, '原始')
PDFDIR = os.path.join(R, 'PDF'); OUT = os.path.join(R, '输出')
CODES = ['X1','B','C','I2','E','F','G','H']
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
EMU = 12700.0
TARGET = 784.0      # 目标图底
FAIL = 785.0        # 判失败阈值（>785须处置）
PAGE_BOTTOM = 841.9

def xml_items(code):
    """[[kind, anchor_idx|None, w_pt, h_pt]] 文档序（anchor与inline混序）"""
    z = zipfile.ZipFile(os.path.join(PRIS, code + '.docx'))
    root = etree.fromstring(z.read('word/document.xml')); z.close()
    items = []; ai = 0
    for p in root.iter('{%s}p' % W):
        for node in p.iter():
            if node.tag == '{%s}anchor' % WP:
                ai += 1
                ext = node.find('{%s}extent' % WP)
                items.append(['anchor', ai, round(int(ext.get('cx'))/EMU,1), round(int(ext.get('cy'))/EMU,1)])
            elif node.tag == '{%s}inline' % WP:
                ext = node.find('{%s}extent' % WP)
                items.append(['inline', None, round(int(ext.get('cx'))/EMU,1), round(int(ext.get('cy'))/EMU,1)])
    return items

def align(code, tag):
    """返回 (match: anchor_idx→placement, fails, n_pages)"""
    doc = fitz.open(os.path.join(PDFDIR, '%s_%s.pdf' % (code, tag)))
    n_pages = doc.page_count
    pl = []
    for pi in range(n_pages):
        page = doc[pi]
        rects = []
        for img in page.get_images(full=True):
            for Rr in page.get_image_rects(img[0]):
                rects.append(Rr)
        seen = set()
        for Rr in rects:
            key = tuple(round(v, 1) for v in Rr)
            if key in seen: continue
            seen.add(key)
            pl.append({'p': pi+1, 'rect': key, 'bottom': round(Rr.y1,1), 'top': round(Rr.y0,1),
                       'w': round(Rr.width,1), 'h': round(Rr.height,1)})
    doc.close()
    pl.sort(key=lambda x: (x['p'], x['rect'][1], x['rect'][0]))
    its = xml_items(code)
    match = {}
    j = 0
    for it in its:
        for k in range(j, len(pl)):
            if abs(pl[k]['w'] - it[2]) < 0.75 and abs(pl[k]['h'] - it[3]) < 0.75:
                if it[0] == 'anchor':
                    match[it[1]] = pl[k]
                j = k + 1
                break
    fails = {ai: m for ai, m in match.items() if m['bottom'] > FAIL}
    return match, fails, n_pages, len(pl), len(its)

def surgery(code, cum):
    src = os.path.join(PRIS, code + '.docx')
    dst = os.path.join(BASE, code + '.docx')
    shutil.copy2(src, dst)
    if not cum: return
    z = zipfile.ZipFile(dst)
    names = z.namelist(); data = {n: z.read(n) for n in names}; infos = {n: z.getinfo(n) for n in names}
    z.close()
    root = etree.fromstring(data['word/document.xml'])
    idx = 0; done = []
    for p in root.iter('{%s}p' % W):
        for an in p.findall('.//{%s}anchor' % WP):
            idx += 1
            if idx not in cum: continue
            shift = cum[idx]
            pv = an.find('{%s}positionV' % WP)
            off = pv.find('{%s}posOffset' % WP)
            if off is None:
                off = etree.SubElement(pv, '{%s}posOffset' % WP); pv.insert(0, off); old = 0
            else:
                old = int(off.text)
            off.text = str(old - round(shift * EMU))
            done.append((idx, old, off.text))
    data['word/document.xml'] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zo:
        for n in names: zo.writestr(infos[n], data[n])
    return done

def export(tag, codes):
    word = wc.DispatchEx('Word.Application'); word.Visible = False; word.DisplayAlerts = 0
    try:
        for code in codes:
            local = os.path.join(PDFDIR, code + '_local.docx')
            shutil.copy2(os.path.join(BASE, code + '.docx'), local)
            doc = word.Documents.Open(local, ReadOnly=True, AddToRecentFiles=False)
            try:
                doc.ExportAsFixedFormat(os.path.join(PDFDIR, '%s_%s.pdf' % (code, tag)), 17, False, 0, 0)
            finally:
                doc.Close(False)
            os.remove(local)
    finally:
        word.Quit()

log = {'rounds': [], 'cum': {c: {} for c in CODES}, 'final': {}}
# I2 p24专项：idx12下移65（负shift=下移）
log['cum']['I2'][12] = -65.0
# 第0轮播种：基线扫描（tag=base）失败锚直接加量
seed = {}
for code in CODES:
    match, fails, n_pages, n_pl, n_it = align(code, 'base')
    seed[code] = {'matched': len(match), 'fails': {str(k): v['bottom'] for k, v in fails.items()},
                  'pages': n_pages, 'placements': n_pl, 'items': n_it}
    for ai, m in fails.items():
        log['cum'][code][ai] = log['cum'][code].get(ai, 0.0) + (m['bottom'] - TARGET + 0.5)
log['rounds'].append({'base': seed})
print('== 基线播种:')
for code in CODES:
    s = seed[code]
    print('  %s 锚匹配%d/条目%d安置图%d 失败锚%d：%s' % (
        code, s['matched'], s['items'], s['placements'], len(s['fails']),
        sorted(int(k) for k in s['fails'])))

for r in range(1, 4):
    tag = 'fix%d' % r
    for code in CODES:
        surgery(code, log['cum'][code])
    export(tag, CODES)
    rlog = {}
    for code in CODES:
        match, fails, n_pages, n_pl, n_it = align(code, tag)
        rlog[code] = {'pages': n_pages, 'placements': n_pl, 'xml_items': n_it,
                      'matched_anchors': len(match), 'fails': {str(k): v['bottom'] for k, v in fails.items()},
                      'fail_pages': sorted(set(v['p'] for v in fails.values()))}
    log['rounds'].append({tag: rlog})
    print('==== round %d (%s)' % (r, tag))
    for code in CODES:
        rl = rlog[code]
        print('  %s 页=%d 锚匹配%d/%d安置图%d 失败%d %s' % (
            code, rl['pages'], rl['matched_anchors'], rl['xml_items'], rl['placements'],
            len(rl['fails']), rl['fail_pages'] or ''))
    # 加量
    any_fail = False
    prev_fails = log['rounds'][r-1][('fix%d' % (r-1))] if r >= 2 else (seed if r == 1 else None)
    for code in CODES:
        match, fails, n_pages, _, _ = align(code, tag)
        for ai, m in fails.items():
            any_fail = True
            extra = m['bottom'] - TARGET + 0.5
            stuck = False
            if prev_fails is not None:
                pb = prev_fails[code]['fails'].get(str(ai))
                if pb is not None and abs(pb - PAGE_BOTTOM) < 0.3 and abs(m['bottom'] - PAGE_BOTTOM) < 0.3:
                    stuck = True
            if stuck:
                extra += 60 * r + (80 if r == 3 else 0)
            new_cum = log['cum'][code].get(ai, 0.0) + extra
            if new_cum > 400: new_cum = 400
            log['cum'][code][ai] = new_cum
    if not any_fail:
        print('ALL CLEAN at round', r)
        break
else:
    print('3轮未全清——停（按派发：仍不达标停下报告）')

json.dump(log, open(os.path.join(OUT, 'loop_log.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('LOOP DONE')
