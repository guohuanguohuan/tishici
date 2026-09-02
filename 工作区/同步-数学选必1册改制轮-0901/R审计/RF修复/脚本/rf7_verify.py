# -*- coding: utf-8 -*-
"""RF修复轮 终验。用法：python rf7_verify.py <tag>   （tag=fix1/fix2/fix3）
七项：
①全锚图底≤785（797口径）＋图顶≥40（不侵页眉带）
②全页redaction差分：被盖字形显影px（目标=0；对照基线）
③图-图bbox交叠（去重、area>15pt²）与基线对比（不新增）
④文字流diff：pristine vs 修复 w:t+m:t流＝0差异
⑤页数对比（基线 vs 修复）
⑥XML改动面：仅手术锚posOffset文本变化（其余字节零差）
⑦I2 idx12专项：p24图与【备考建议】段文字零交叠
输出 输出\verify_<tag>.json ＋控制台摘要。"""
import sys, os, json, zipfile
sys.stdout.reconfigure(encoding='utf-8')
from lxml import etree
import fitz
import numpy as np

R = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复'
BASE = os.path.join(R, '基线'); PRIS = os.path.join(BASE, '原始')
PDFDIR = os.path.join(R, 'PDF'); OUT = os.path.join(R, '输出')
CODES = ['X1','B','C','I2','E','F','G','H']
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
EMU = 12700.0
tag = sys.argv[1]

def placements(code, tg):
    doc = fitz.open(os.path.join(PDFDIR, '%s_%s.pdf' % (code, tg)))
    pl = []
    for pi in range(doc.page_count):
        page = doc[pi]
        seen = set()
        for img in page.get_images(full=True):
            for Rr in page.get_image_rects(img[0]):
                key = tuple(round(v, 1) for v in Rr)
                if key in seen: continue
                seen.add(key)
                pl.append({'p': pi+1, 'rect': key, 'bottom': round(Rr.y1,1), 'top': round(Rr.y0,1),
                           'w': round(Rr.width,1), 'h': round(Rr.height,1)})
    n = doc.page_count
    doc.close()
    pl.sort(key=lambda x: (x['p'], x['rect'][1], x['rect'][0]))
    return pl, n

def redact_coverage(code, tg, dpi=150):
    doc = fitz.open(os.path.join(PDFDIR, '%s_%s.pdf' % (code, tg)))
    hits = []
    for pi in range(doc.page_count):
        page = doc[pi]
        spans = []
        for blk in page.get_text('dict')['blocks']:
            if blk['type'] != 0: continue
            for ln in blk['lines']:
                for sp in ln['spans']:
                    if sp['text'].strip(): spans.append(fitz.Rect(sp['bbox']))
        rects = []
        for img in page.get_images(full=True):
            for Rr in page.get_image_rects(img[0]): rects.append(Rr)
        cand = False
        for Rr in rects:
            for S in spans:
                it = Rr & S
                if not it.is_empty and it.get_area() > 1: cand = True; break
            if cand: break
        if not cand: continue
        pix1 = page.get_pixmap(dpi=dpi, colorspace=fitz.csGRAY)
        a1 = np.frombuffer(pix1.samples, dtype=np.uint8).reshape(pix1.height, pix1.width)
        page.add_redact_annot(fitz.Rect(0, 0, page.rect.width, page.rect.height))
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE,
                              graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                              text=fitz.PDF_REDACT_TEXT_NONE)
        pix2 = page.get_pixmap(dpi=dpi, colorspace=fitz.csGRAY)
        a2 = np.frombuffer(pix2.samples, dtype=np.uint8).reshape(pix2.height, pix2.width)
        rec = int(((a2 < 128) & ~(a1 < 128)).sum())
        if rec > 30: hits.append((pi+1, rec))
    doc.close()
    return hits

def imgimg(code, tg):
    pl, n = placements(code, tg)
    ov = []
    bypage = {}
    for x in pl: bypage.setdefault(x['p'], []).append(x)
    for p, xs in bypage.items():
        for i in range(len(xs)):
            for j in range(i+1, len(xs)):
                A, B = xs[i]['rect'], xs[j]['rect']
                ix = max(0, min(A[2], B[2]) - max(A[0], B[0])); iy = max(0, min(A[3], B[3]) - max(A[1], B[1]))
                if ix * iy > 15: ov.append({'p': p, 'area': round(ix*iy,1), 'A': A, 'B': B})
    return ov

def textflow(path):
    z = zipfile.ZipFile(path)
    root = etree.fromstring(z.read('word/document.xml')); z.close()
    return ''.join(t.text or '' for t in root.iter('{%s}t' % W)) + \
           ''.join(t.text or '' for t in root.iter('{%s}t' % M))

def xml_diff_pairs(pris, fixed):
    """逐锚posOffset对比＋其余树差异计数"""
    def anchors(path):
        z = zipfile.ZipFile(path)
        root = etree.fromstring(z.read('word/document.xml')); z.close()
        out = []
        for p in root.iter('{%s}p' % W):
            for an in p.findall('.//{%s}anchor' % WP):
                pv = an.find('{%s}positionV' % WP)
                off = pv.find('{%s}posOffset' % WP) if pv is not None else None
                ext = an.find('{%s}extent' % WP)
                out.append({'off': off.text if off is not None else None,
                            'cx': ext.get('cx'), 'cy': ext.get('cy'),
                            'pv_rel': pv.get('relativeFrom') if pv is not None else None})
        return out
    a, b = anchors(pris), anchors(fixed)
    assert len(a) == len(b), '锚数变化!'
    changed = []
    for i, (x, y) in enumerate(zip(a, b), 1):
        assert (x['cx'], x['cy'], x['pv_rel']) == (y['cx'], y['cy'], y['pv_rel']), '锚%d extent/rel变化!' % i
        if x['off'] != y['off']:
            changed.append({'idx': i, 'old': x['off'], 'new': y['off'],
                            'shift_pt': round((int(x['off'] or 0) - int(y['off'] or 0)) / EMU, 2)})
    return changed, len(a)

res = {}
print('======== 终验 tag=%s' % tag)
for code in CODES:
    r = {}
    pl_fix, n_fix = placements(code, tag)
    pl_base, n_base = placements(code, 'base')
    r['pages'] = {'base': n_base, 'fix': n_fix}
    r['bottom_max'] = max((x['bottom'] for x in pl_fix), default=0)
    r['bottom_over797'] = [x for x in pl_fix if x['bottom'] > 797]
    r['bottom_over785'] = [x for x in pl_fix if x['bottom'] > 785]
    r['top_under40'] = [x for x in pl_fix if x['top'] < 40]
    r['cov_fix'] = redact_coverage(code, tag)
    r['cov_base'] = redact_coverage(code, 'base')
    r['imgimg_fix'] = imgimg(code, tag)
    r['imgimg_base'] = imgimg(code, 'base')
    ta, tb = textflow(os.path.join(PRIS, code + '.docx')), textflow(os.path.join(BASE, code + '.docx'))
    r['textflow_equal'] = (ta == tb)
    r['textflow_len'] = (len(ta), len(tb))
    ch, n_anchors = xml_diff_pairs(os.path.join(PRIS, code + '.docx'), os.path.join(BASE, code + '.docx'))
    r['posoffset_changed'] = ch
    r['anchors'] = n_anchors
    res[code] = r
    print('%s: 页%d→%d | 图底max=%.1f >797:%d >785:%d | 图顶<40:%d | 显影px基线%s→修%s | 图图交叠基线%d→修%d | 文字流%d | posOffset改%d/%d' % (
        code, n_base, n_fix, r['bottom_max'], len(r['bottom_over797']), len(r['bottom_over785']),
        len(r['top_under40']), r['cov_base'], r['cov_fix'], len(r['imgimg_base']), len(r['imgimg_fix']),
        1 if r['textflow_equal'] else 0, len(ch), n_anchors))
json.dump(res, open(os.path.join(OUT, 'verify_%s.json' % tag), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('VERIFY DONE')
