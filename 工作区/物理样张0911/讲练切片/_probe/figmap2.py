# -*- coding: utf-8 -*-
"""兼容 drawing/pict/object 三态的图映射（含 VML v:imagedata）"""
import sys, zipfile, io
from lxml import etree
from PIL import Image

R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

src, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
z = zipfile.ZipFile(src)
rels = etree.fromstring(z.read('word/_rels/document.xml.rels'))
rid2t = {r.get('Id'): r.get('Target') for r in rels}
doc = etree.fromstring(z.read('word/document.xml'))
body = doc.find('{%s}body' % W)

def rid_of(el):
    return el.get('{%s}embed' % R) or el.get('{%s}link' % R) or el.get('{%s}id' % R)

for i, child in enumerate(body):
    if not (lo <= i <= hi) or child.tag != '{%s}p' % W:
        continue
    kinds = []
    for run in child.iter():
        t = etree.QName(run).localname
        if t == 'blip':
            kinds.append(('drawing', rid_of(run)))
        elif t == 'imagedata':
            kinds.append(('vml', rid_of(run)))
    seen = set()
    for kind, rid in kinds:
        if not rid or rid in seen:
            continue
        seen.add(rid)
        tgt = rid2t.get(rid, '?')
        px = (0, 0)
        if tgt.startswith('media/'):
            px = Image.open(io.BytesIO(z.read('word/' + tgt))).size
        ext = child.find('.//{%s}extent' % WP)
        disp = ''
        if ext is not None:
            disp = ' disp=%.1fx%.1fmm' % (int(ext.get('cx'))/360000.0, int(ext.get('cy'))/360000.0)
        print('[%d] %s %s px=%dx%d%s' % (i, kind, tgt, px[0], px[1], disp))
