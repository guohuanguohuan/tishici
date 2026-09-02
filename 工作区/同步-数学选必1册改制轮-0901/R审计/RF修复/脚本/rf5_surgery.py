# -*- coding: utf-8 -*-
"""RF修复轮 posOffset手术：对手术清单中的锚施加positionV负移。
手术清单＝输出\plan_<tag>.json：[{code, anchor_idx, shift_pt}]（anchor_idx＝文档序1..N，与anchors_<code>.json对齐）。
规则：只改wp:positionV/wp:posOffset（无节点则插入，置于positionV首子）；不动extent/锚段/其余锚。
对基线副本直接手术（基线另有单独备份副本）。
用法：python rf5_surgery.py <tag>"""
import sys, os, json, shutil, zipfile
sys.stdout.reconfigure(encoding='utf-8')
from lxml import etree

BASE = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复\基线'
OUT = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复\输出'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
EMU = 12700
tag = sys.argv[1]

plan = json.load(open(os.path.join(OUT, 'plan_%s.json' % tag), encoding='utf-8'))
by_code = {}
for it in plan:
    by_code.setdefault(it['code'], []).append(it)

for code, items in by_code.items():
    src = os.path.join(BASE, code + '.docx')
    z = zipfile.ZipFile(src)
    names = z.namelist()
    data = {n: z.read(n) for n in names}
    infos = {n: z.getinfo(n) for n in names}
    z.close()
    root = etree.fromstring(data['word/document.xml'])
    idx = 0
    done = {}
    for p in root.iter('{%s}p' % W):
        for an in p.findall('.//{%s}anchor' % WP):
            idx += 1
            m = [it for it in items if it['anchor_idx'] == idx]
            if not m: continue
            assert len(m) == 1
            shift = m[0]['shift_pt']
            pv = an.find('{%s}positionV' % WP)
            assert pv is not None, 'anchor %d 无positionV' % idx
            off = pv.find('{%s}posOffset' % WP)
            if off is None:
                off = etree.SubElement(pv, '{%s}posOffset' % WP)
                pv.insert(0, off)
                old = 0
            else:
                old = int(off.text)
            new = old - round(shift * EMU)
            off.text = str(new)
            done[idx] = (old, new, round(shift, 1))
    # 回写zip（仅document.xml变）
    data['word/document.xml'] = etree.tostring(root, xml_declaration=True,
                                               encoding='UTF-8', standalone=True)
    with zipfile.ZipFile(src, 'w', zipfile.ZIP_DEFLATED) as zo:
        for n in names:
            zo.writestr(infos[n], data[n])
    print('%s: 手术%d锚 %s' % (code, len(done),
          '; '.join('idx%d %d→%d(−%.1fpt)' % (k, v[0], v[1], v[2]) for k, v in sorted(done.items()))))
print('DONE')
