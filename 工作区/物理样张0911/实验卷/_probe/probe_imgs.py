# -*- coding: utf-8 -*-
"""按 body 元素顺序列出 docx 内嵌图片：元素序号 -> media 文件名 + 显示尺寸(EMU换算mm)/像素尺寸"""
import sys, zipfile, io
from lxml import etree
from PIL import Image

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'

docx = sys.argv[1]
z = zipfile.ZipFile(docx)
rels = etree.fromstring(z.read('word/_rels/document.xml.rels'))
relmap = {rel.get('Id'): rel.get('Target') for rel in rels}
doc = etree.fromstring(z.read('word/document.xml'))
body = doc.find('{%s}body' % W)
for idx, el in enumerate(list(body)):
    tag = etree.QName(el).localname
    for blip in el.iter('{%s}blip' % A):
        rid = blip.get('{%s}embed' % R) or blip.get('{%s}link' % R)
        tgt = relmap.get(rid, '?')
        ext = ''
        for kind in ('inline', 'anchor'):
            for drawing in el.iter('{%s}%s' % (WP, kind)):
                e = drawing.find('{%s}extent' % A)
                if e is not None:
                    cx, cy = int(e.get('cx')), int(e.get('cy'))
                    ext = '%s %.2fx%.2fmm' % (kind, cx / 360000.0, cy / 360000.0)
                    break
            if ext:
                break
        px = '?'
        try:
            path = 'word/' + tgt.replace('../', '').lstrip('/')
            im = Image.open(io.BytesIO(z.read(path)))
            px = '%dx%d' % im.size
        except Exception as ex:
            px = 'ERR:' + str(ex)[:40]
        # text hint of paragraph
        txt = ''.join(t.text or '' for t in el.iter('{%s}t' % W))[:24]
        print('[%d]<%s> %s  %s  %s  | %s' % (idx, tag, tgt, ext, px, txt))
