# -*- coding: utf-8 -*-
"""按 body 元素序号列 docx 内嵌图：元素→rId→media 文件→显示尺寸→像素尺寸"""
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
for i, child in enumerate(body):
    if not (lo <= i <= hi) or child.tag != '{%s}p' % W:
        continue
    for blip in child.iter('{%s}blip' % R):
        rid = blip.get('{%s}embed' % R) or blip.get('{%s}link' % R)
        tgt = rid2t.get(rid, '?')
        ext = child.find('.//{%s}extent' % WP)
        cx = int(ext.get('cx')) / 360000.0 if ext is not None else 0
        cy = int(ext.get('cy')) / 360000.0 if ext is not None else 0
        px = (0, 0)
        if tgt.startswith('media/'):
            px = Image.open(io.BytesIO(z.read('word/' + tgt))).size
        print('[%d] %s disp=%.1fx%.1fmm px=%dx%d' % (i, tgt, cx, cy, px[0], px[1]))
