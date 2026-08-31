# -*- coding: utf-8 -*-
"""W-F卷90 图9pt复扫处置：4张显示高>9cm图等比缩至高≤9.00cm（只改wp:extent与a:ext，EMU）
判据（§7图片内容感知定尺寸）：
  image87  (#3  p51)  8.89x10.45→7.66x9.00  字母23px@151dpi=11.0pt→9.5pt（实测组件中位）
  image286 (#24 p546) 12.00x14.26→7.57x9.00  最小标注≈图高1/25~1/30→13.5pt→8.5pt（视觉估测）
  image116 (#26 p613) 18.00x9.54→17.00x9.00  最小标注≈1/35~1/40→7.3pt→6.9pt（视觉估测）
  image25  (#43 p867) 13.00x11.51→10.16x9.00 标注≈1/15~1/20→16~21pt→13~16pt（视觉估测）
全部：缩后字母≥6.5pt下限、宽≤18cm版心、显示宽≤150dpi自然宽（均为缩小）。"""
import zipfile, sys, os, time, json
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
def w(t): return '{%s}%s' % (W, t)

TARGETS = {  # 媒体文件 -> 目标高度cm（等比缩放，宽随之）
    'image87.png': 9.00, 'image286.png': 9.00, 'image116.png': 9.00, 'image25.png': 9.00,
}
NAMES = {'image87.png': 'image87(#3)', 'image286.png': 'image286(#24)', 'image116.png': 'image116(#26)', 'image25.png': 'image25(#43)'}

def lin(el):
    return ''.join(s.text or '' for s in el.iter() if isinstance(s.tag, str) and s.tag == w('t'))

def main(path):
    with zipfile.ZipFile(path) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    doc = etree.fromstring(parts['word/document.xml'])
    body = doc.find(w('body'))
    rels = etree.fromstring(parts['word/_rels/document.xml.rels'])
    rid2media = {}
    for rel in rels:
        tgt = rel.get('Target') or ''
        if 'media/' in tgt:
            rid2media[rel.get('Id')] = tgt.split('/')[-1]
    embed_attr = '{%s}embed' % R
    changed = 0
    log = []
    done = set()
    for p in body.iter(w('p')):
        for blip in p.iter('{%s}blip' % A):
            media = rid2media.get(blip.get(embed_attr))
            if media not in TARGETS or media in done:
                continue
            target_h = TARGETS[media]
            exts = [sub for sub in p.iter() if isinstance(sub.tag, str) and sub.tag == '{%s}extent' % WP]
            assert len(exts) == 1, '段extent数=%d (%s)' % (len(exts), media)
            ext = exts[0]
            cx, cy = int(ext.get('cx')), int(ext.get('cy'))
            cur_h = cy / 360000.0
            scale = target_h / cur_h
            ncx, ncy = round(cx * scale), round(cy * scale)
            ext.set('cx', str(ncx)); ext.set('cy', str(ncy))
            for sub in p.iter():
                if not isinstance(sub.tag, str): continue
                if sub.tag == '{%s}ext' % A:
                    sub.set('cx', str(ncx)); sub.set('cy', str(ncy))
            changed += 1
            done.add(media)
            log.append((NAMES[media], '%.2fx%.2f→%.2fx%.2fcm' % (cx/360000, cy/360000, ncx/360000, ncy/360000), 'scale=%.3f' % scale))
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
    for row in log:
        print(row)
    print('缩图数:', changed)

if __name__ == '__main__':
    main(sys.argv[1])
