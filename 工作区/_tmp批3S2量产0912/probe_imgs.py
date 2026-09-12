# -*- coding: utf-8 -*-
"""探针：docx 正文元素序 → 内嵌图片 rId/media 文件/extent(mm)，供图位取证。
用法：python probe_imgs.py <docx> <起元> <止元>
"""
import sys, zipfile, re
from docx import Document
from docx.oxml.ns import qn

EMU = 360000.0  # per cm

def probe(path, lo, hi):
    doc = Document(path)
    body = doc.element.body
    rels = doc.part.rels
    z = zipfile.ZipFile(path)
    idx = -1
    for child in body.iterchildren():
        idx += 1
        if not (lo <= idx <= hi):
            continue
        tag = child.tag.split('}')[1]
        if tag != 'p':
            print('[%d] <%s>' % (idx, tag))
            continue
        texts = ''.join(n.text or '' for n in child.iter(qn('w:t')))
        blips = child.findall('.//' + qn('a:blip'))
        exts = child.findall('.//' + qn('wp:extent'))
        imgs = []
        for i, b in enumerate(blips):
            rid = b.get(qn('r:embed'))
            fn = rels[rid].target_ref if rid in rels else '?'
            ext = exts[i] if i < len(exts) else None
            if ext is not None:
                w = int(ext.get('cx')) / EMU
                h = int(ext.get('cy')) / EMU
                sz = '%.1fx%.1fmm' % (w, h)
            else:
                sz = '?'
            try:
                nbytes = len(z.read('word/' + fn)) if not fn.startswith('/') else len(z.read('word' + fn))
            except KeyError:
                nbytes = -1
            imgs.append('%s(%s,%dB)' % (fn, sz, nbytes))
        mark = 'IMG: ' + ' | '.join(imgs) if imgs else ''
        t = texts.strip().replace('\n', ' ')[:44]
        if mark or t:
            print('[%d] %s %s' % (idx, t, mark))

if __name__ == '__main__':
    probe(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
