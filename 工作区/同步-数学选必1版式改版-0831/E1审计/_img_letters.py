# -*- coding: utf-8 -*-
"""E1复审计：改动图字母视觉高实测（每章≥3张，对W登记表期望值）。只读。"""
import os, io, re, zipfile, json
from lxml import etree
from PIL import Image
import numpy as np

NSW = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WPA = 'http://schemas.openxmlformats.org/drawingml/2006/main'
WPR = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
RNS = 'http://schemas.openxmlformats.org/package/2006/relationships'
def q(t): return '{%s}%s' % (NSW, t)
BASE = r'C:\Users\28120\Desktop\提示词\高中数学\高中数学同步'

# (code, docx名, media名, 期望显示cm(w,h), 期望最小字母pt口径说明)
PICKS = [
    ('X1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', 'image48.png', (1.71, 2.34), '登记:12px→5.76pt(150dpi硬限优先)'),
    ('X1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', 'image55.png', (12.00, 12.25), '裁决:19px→6.68pt'),
    ('X1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', 'image25.png', (None, None), '登记:5.76pt下限例外'),
    ('I1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', 'image18.jpg', (None, None), 'extent纵横比修正'),
    ('F',  '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', 'image87.png', (7.65, 9.00), '登记:缩后9.5pt(23px@151dpi)'),
    ('F',  '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', 'image286.png', (7.58, 9.00), '登记:缩后≈8.5pt'),
    ('G',  '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', 'image31.png', (4.42, 9.00), '登记:标签中位11.7pt@9cm'),
    ('G',  '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', 'image34.png', (9.45, 9.00), '登记:标签中位17.1pt'),
    ('E',  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', 'image8.png', (9.09, 9.00), '登记:缩后8.6-10.7pt'),
    ('I2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', 'image12.png', (14.48, 7.52), '登记:9pt命中'),
]

def cc_letter_heights(img):
    """连通域字母高度px列表（近似）。"""
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGBA')
        bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(bg, img)
    arr = np.asarray(img.convert('L'))
    binv = arr < 160
    H, W = binv.shape
    lab = np.zeros((H, W), dtype=np.int32)
    cur = 0
    hs = []
    for y in range(H):
        for x in range(W):
            if not binv[y, x] or lab[y, x]: continue
            cur += 1
            stack = [(y, x)]; lab[y, x] = cur
            ys = [y]; xs = [x]
            while stack:
                cy, cx = stack.pop()
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < H and 0 <= nx < W and binv[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = cur
                            stack.append((ny, nx))
                            ys.append(ny); xs.append(nx)
            h = max(ys) - min(ys) + 1
            w = max(xs) - min(xs) + 1
            n = len(ys)
            # 字母形过滤：尺寸、长宽比、实心度（排除长线与噪点）
            if 4 <= h <= 80 and 1 <= w <= 4 * h and 0.08 <= h / max(w, 1) <= 8 and n >= 8 and n >= 0.15 * h * w:
                hs.append(h)
    return hs

def extent_of_media(z, doc, rels, media_name):
    relmap = {r.get('Id'): r.get('Target') for r in rels}
    hits = []
    for inline in doc.iter('{%s}inline' % WPR):
        blip = inline.find('.//{%s}blip' % WPA)
        ext = inline.find('.//{%s}extent' % WPR)
        if blip is None or ext is None: continue
        rid = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
        tgt = relmap.get(rid, '')
        if tgt.split('/')[-1] == media_name:
            hits.append((int(ext.get('cx')) / 360000.0, int(ext.get('cy')) / 360000.0))
    return hits

for code, fn, media, expw, note in PICKS:
    z = zipfile.ZipFile(os.path.join(BASE, fn))
    doc = etree.fromstring(z.read('word/document.xml'))
    rels = etree.fromstring(z.read('word/_rels/document.xml.rels'))
    exts = extent_of_media(z, doc, rels, media)
    img = Image.open(io.BytesIO(z.read('word/media/' + media)))
    W, H = img.size
    hs = cc_letter_heights(img)
    out = {'file': code, 'media': media, 'px': (W, H), 'extents_cm': [(round(a,2),round(b,2)) for a,b in exts],
           'n_letters': len(hs), 'note': note}
    if hs and exts:
        dispw, disph = exts[0]
        # 以竖向比例换算：pt = px * disph_cm / H * 28.3465
        pt = sorted(h * disph / H * 28.3465 for h in hs)
        out['min_pt'] = round(pt[0], 2)
        out['p10_pt'] = round(pt[max(0, len(pt)//10)], 2)
        out['median_pt'] = round(pt[len(pt)//2], 2)
        out['max_pt'] = round(pt[-1], 2)
    print(json.dumps(out, ensure_ascii=False))
