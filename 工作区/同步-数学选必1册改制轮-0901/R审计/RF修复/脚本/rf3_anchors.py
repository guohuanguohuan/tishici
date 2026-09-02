# -*- coding: utf-8 -*-
"""RF修复轮 XML锚清单：从基线docx抽 wp:anchor 全量（doc序、docPr id/name、extent、positionV/H、
wrap类型、锚段文本快照），输出 输出\anchors_<code>.json。"""
import sys, os, json, zipfile
sys.stdout.reconfigure(encoding='utf-8')
from lxml import etree

BASE = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复\基线'
OUT = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复\输出'
CODES = ['X1','B','C','I2','E','F','G','H']
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
NS = {'w': W, 'wp': WP, 'a': A}
EMU = 12700.0

def para_text(p):
    parts = []
    for t in p.iter('{%s}t' % W):
        parts.append(t.text or '')
    for t in p.iter('{http://schemas.openxmlformats.org/officeDocument/2006/math}t'):
        parts.append(t.text or '')
    return ''.join(parts)

for code in CODES:
    z = zipfile.ZipFile(os.path.join(BASE, code + '.docx'))
    root = etree.fromstring(z.read('word/document.xml'))
    z.close()
    anchors = []
    idx = 0
    for p in root.iter('{%s}p' % W):
        pt = para_text(p)
        for an in p.findall('.//{%s}anchor' % WP):
            idx += 1
            ext = an.find('{%s}extent' % WP)
            dp = an.find('{%s}docPr' % WP)
            pv = an.find('{%s}positionV' % WP)
            ph = an.find('{%s}positionH' % WP)
            wrap = None
            for tag in ('wrapSquare', 'wrapTopAndBottom', 'wrapTight', 'wrapThrough', 'wrapNone'):
                if an.find('{%s}%s' % (WP, tag)) is not None:
                    wrap = tag; break
            ao = an.get('allowOverlap')
            def posinfo(el):
                if el is None: return None
                off = el.find('{%s}posOffset' % WP)
                align = el.find('{%s}align' % WP)
                return {'rel': el.get('relativeFrom'),
                        'offset': int(off.text) if off is not None else None,
                        'align': align.text if align is not None else None}
            anchors.append({
                'idx': idx, 'docPr_id': dp.get('id') if dp is not None else None,
                'docPr_name': dp.get('name') if dp is not None else None,
                'cx': int(ext.get('cx')), 'cy': int(ext.get('cy')),
                'w_pt': round(int(ext.get('cx')) / EMU, 1), 'h_pt': round(int(ext.get('cy')) / EMU, 1),
                'positionV': posinfo(pv), 'positionH': posinfo(ph),
                'wrap': wrap, 'allowOverlap': ao,
                'para_txt': pt[:60], 'para_txt_full': pt[:160],
            })
    with open(os.path.join(OUT, 'anchors_%s.json' % code), 'w', encoding='utf-8') as f:
        json.dump(anchors, f, ensure_ascii=False, indent=1)
    print('%s: anchors=%d' % (code, len(anchors)))
print('DONE')
