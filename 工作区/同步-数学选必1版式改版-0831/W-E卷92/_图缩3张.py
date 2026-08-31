# -*- coding: utf-8 -*-
"""W-E卷92 图定尺寸3张缩小：image8/image247/image271 显示高→9.0cm（宽等比）；只改wp:extent与a:xfrm/a:ext"""
import zipfile, os, time
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PR = 'http://schemas.openxmlformats.org/package/2006/relationships'
def qns(u, t): return '{%s}%s' % (u, t)

path = 'E卷92-工作副本.docx'
TARGET_CM = 9.0
TARGET_EMU = int(TARGET_CM * 360000)

with zipfile.ZipFile(path) as z:
    parts = {n: z.read(n) for n in z.namelist()}

# rels: rId -> media名
rels = etree.fromstring(parts['word/_rels/document.xml.rels'])
rid2img = {}
for rel in rels:
    tgt = rel.get('Target') or ''
    if 'media/' in tgt:
        rid2img[rel.get('Id')] = tgt.split('/')[-1]

doc = etree.fromstring(parts['word/document.xml'])
changed = []
for drawing in doc.iter(qns(W, 'drawing')):
    blip = drawing.find('.//' + qns(A, 'blip'))
    if blip is None:
        continue
    rid = blip.get(qns(R, 'embed'))
    img = rid2img.get(rid)
    if img not in ('image8.png', 'image247.png', 'image271.png'):
        continue
    ext = drawing.find(qns(WP, 'inline') + '/' + qns(WP, 'extent'))
    if ext is None:
        ext = drawing.find('.//' + qns(WP, 'extent'))
    cx, cy = int(ext.get('cx')), int(ext.get('cy'))
    ncx = int(cx * TARGET_EMU / cy)
    old = (cx / 360000.0, cy / 360000.0)
    ext.set('cx', str(ncx)); ext.set('cy', str(TARGET_EMU))
    # a:xfrm/a:ext 同步
    for ax in drawing.iter(qns(A, 'ext')):
        if int(ax.get('cy')) == cy and int(ax.get('cx')) == cx:
            ax.set('cx', str(ncx)); ax.set('cy', str(TARGET_EMU))
    changed.append((img, old, (ncx / 360000.0, TARGET_EMU / 360000.0)))

assert len(changed) == 3, '期望3张，实际%d: %r' % (len(changed), changed)
parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
tmp = path + '.imgtmp'
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
    for n, b in parts.items():
        zo.writestr(n, b)
for i in range(12):
    try:
        os.replace(tmp, path); break
    except PermissionError:
        time.sleep(5)
for img, old, new in changed:
    print('%s: %.2fx%.2fcm -> %.2fx%.2fcm' % (img, old[0], old[1], new[0], new[1]))
