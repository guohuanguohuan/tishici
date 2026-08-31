# -*- coding: utf-8 -*-
"""W-G 图9pt复扫处置：image31（题227）与image34（题242）显示高缩至9.00cm
只改 wp:extent 与 a:ext（授权§2.6 无文字变化）；其余42-2张维持（判定见登记md）"""
import zipfile, os, time, json
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
def w(t): return '{%s}%s' % (W, t)

PATH = r"C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-G卷68\G工作副本.docx"
TARGET_MEDIA = {'image31.png', 'image34.png'}
NEW_H_EMU = 3240000  # 9.00cm

with zipfile.ZipFile(PATH) as z:
    parts = {n: z.read(n) for n in z.namelist()}
doc = etree.fromstring(parts['word/document.xml'])
rels = etree.fromstring(parts['word/_rels/document.xml.rels'])
rid2img = {}
for rel in rels:
    t = rel.get('Target', '')
    if t.startswith('media/'):
        rid2img[rel.get('Id')] = t.split('/')[-1]

changed = []
for drawing in doc.iter(w('drawing')):
    blip = drawing.find('.//{%s}blip' % A)
    if blip is None: continue
    rid = blip.get('{%s}embed' % R)
    if rid not in rid2img or rid2img[rid] not in TARGET_MEDIA: continue
    ext = drawing.find('.//{%s}extent' % WP)
    aext = drawing.find('.//{%s}ext' % A)
    oldw, oldh = int(ext.get('cx')), int(ext.get('cy'))
    neww = round(oldw * NEW_H_EMU / oldh)
    ext.set('cx', str(neww)); ext.set('cy', str(NEW_H_EMU))
    aext.set('cx', str(neww)); aext.set('cy', str(NEW_H_EMU))
    changed.append({'media': rid2img[rid], '旧cm': '%.2fx%.2f' % (oldw/360000, oldh/360000),
                    '新cm': '%.2fx%.2f' % (neww/360000, NEW_H_EMU/360000)})

parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
tmp = PATH + '.imgtmp'
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
    for n, b in parts.items():
        zo.writestr(n, b)
for i in range(12):
    try:
        os.replace(tmp, PATH); break
    except PermissionError:
        time.sleep(5)
print(json.dumps(changed, ensure_ascii=False, indent=1))
