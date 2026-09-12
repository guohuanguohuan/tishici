# -*- coding: utf-8 -*-
"""S4 拓展册·源位图提取器——从源 docx 按「题块元素区间」提取题面图（【答案】前），落 figs 暂存区。
口径：元素序号＝body 直接子元素 0 基序号（同 工具/dump_docx.py）；题面图＝题块内【答案】段之前的图；
源 extent（EMU）随图登记，排版侧按 TW-01/02 档放大或收窄。零改绘、位图原样复制（三维禁绘口径）。
"""
import os, re, json, shutil, zipfile
from lxml import etree

R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
WC = '{' + W + '}'

DOCX = {
    '讲上': r'C:/提示词/高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    '讲下': r'C:/提示词/高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    '单元2': r'C:/提示词/高中数学/参考/组卷网/【新课标 新探索】大单元作业设计/人教A版选择性必修1/第1章 空间向量与立体几何/2空间向量及其运算.docx',
    '单元3': r'C:/提示词/高中数学/参考/组卷网/【新课标 新探索】大单元作业设计/人教A版选择性必修1/第1章 空间向量与立体几何/3空间向量基本定理.docx',
    '单元4': r'C:/提示词/高中数学/参考/组卷网/【新课标 新探索】大单元作业设计/人教A版选择性必修1/第1章 空间向量与立体几何/4空间向量及其运算的坐标表示.docx',
    '单元5': r'C:/提示词/高中数学/参考/组卷网/【新课标 新探索】大单元作业设计/人教A版选择性必修1/第1章 空间向量与立体几何/5空间向量的应用.docx',
    '单元6': r'C:/提示词/高中数学/参考/组卷网/【新课标 新探索】大单元作业设计/人教A版选择性必修1/第1章 空间向量与立体几何/6空间向量与立体几何中的高考新题型.docx',
    '单元7': r'C:/提示词/高中数学/参考/组卷网/【新课标 新探索】大单元作业设计/人教A版选择性必修1/第1章 空间向量与立体几何/7单元综合测试-空间向量与立体几何.docx',
}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figs_pool')

def tagof(el): return el.tag.split('}')[-1]

def para_images(p_el, rels):
    """段落内图（文档序）：[(media文件名, cx_emu, cy_emu)]"""
    out = []
    for blip in p_el.iter('{%s}blip' % A):
        rid = blip.get('{%s}embed' % R)
        tgt = rels.get(rid)
        if not tgt: continue
        cx = cy = None
        # 向上找 extent（drawing 容器）
        node = blip
        while node is not None:
            node = node.getparent()
            if node is None: break
            if tagof(node) == 'drawing' or tagof(node) == 'pict':
                ext = node.find('.//{%s}extent' % WP)
                if ext is None:
                    ext = node.find('.//{%s}ext' % A)
                if ext is not None:
                    cx = int(ext.get('cx') or 0); cy = int(ext.get('cy') or 0)
                break
        out.append((tgt, cx, cy))
    return out

def para_text(p_el):
    parts = []
    def walk(el):
        for c in el:
            ct = tagof(c)
            if ct == 't': parts.append(c.text or '')
            elif ct in ('drawing', 'pict', 'object'): parts.append('【图】')
            elif ct == 'br': parts.append('\n')
            else: walk(c)
    walk(p_el)
    return ''.join(parts)

def load(doc):
    path = DOCX[doc]
    z = zipfile.ZipFile(path)
    xml = z.read('word/document.xml')
    root = etree.fromstring(xml)
    rels = {}
    try:
        rx = etree.fromstring(z.read('word/_rels/document.xml.rels'))
        for rel in rx:
            rels[rel.get('Id')] = rel.get('Target').split('/')[-1]
    except KeyError:
        pass
    body = root.find(WC + 'body')
    els = []
    for i, child in enumerate(body.iterchildren()):
        ct = tagof(child)
        if ct == 'p':
            els.append((i, 'p', para_text(child), para_images(child, rels)))
        else:
            els.append((i, ct, None, []))
    media = {}
    for n in z.namelist():
        if '/media/' in n:
            media[n.split('/')[-1]] = z.read(n)
    return els, media

QNUM = re.compile(r'^\d{1,3}．')          # 大单元题块起始
POOL = re.compile(r'^\d+\.\d+(\.\d+)*[-．]')  # 讲练件池题起始（1.2.5.4.1-4．）
HEAD = re.compile(r'^\d+(\.\d+)+\s*\S')   # 讲块节头

import struct

def is_real_fig(tgt, cx, cy, media):
    """真图判定：cy≥50万 EMU，或 PNG 像素≥120×60。行内公式碎片两条均不满足。"""
    if (cy or 0) >= 500000:
        return True
    data = media.get(tgt, b'')
    if data[:8] == b'\x89PNG\r\n\x1a\n' and len(data) >= 24:
        w, h = struct.unpack('>II', data[16:24])
        if w >= 120 and h >= 60:
            return True
    return False

def is_blockstart(text):
    if not text: return False
    t = text.strip()
    if len(t) < 8: return False
    if QNUM.match(t) or POOL.match(t): return True
    if HEAD.match(t) and len(t) < 40: return True
    return False

INVIS = dict.fromkeys(map(ord, '\u2060\u200b\u200c\u200d\ufeff'), None)

def extract(doc, start, end=None, locator=None, ans_split=True, qnum=None):
    """返回题块题面图列表 [(media名, cx, cy)]。start=元素号 / locator 文本 / qnum=大单元题号（^N．起始段）。"""
    els, media = load(doc)
    idx = {e[0]: e for e in els}
    if qnum is not None:
        pat = re.compile(r'^%d\s*．' % qnum)
        start = None
        for i, tag, text, imgs in els:
            if text and pat.match(text.strip()):
                start = i; break
        if start is None:
            return None
    if locator is not None:
        start = None
        for i, tag, text, imgs in els:
            if text and locator in text:
                start = i; break
        if start is None:
            return None
    if end is None:
        end = els[-1][0]
        for i, tag, text, imgs in els:
            if i > start and is_blockstart(text or ''):
                end = i - 1; break
    figs = []
    for i in range(start, end + 1):
        e = idx.get(i)
        if not e: continue
        _, tag, text, imgs = e
        if ans_split and text:
            t = text.translate(INVIS)
            if '【答案' in t or '【解析' in t or '【详解' in t or '【分析' in t:
                break
        figs.extend(img for img in imgs if is_real_fig(img[0], img[1], img[2], media))
    return figs, media

if __name__ == '__main__':
    import sys
    jobs = json.load(open(sys.argv[1], encoding='utf-8'))
    os.makedirs(OUT, exist_ok=True)
    cache = {}
    manifest = {}
    for job in jobs:
        tid, doc = job['id'], job['doc']
        key = job.get('range')  # [start, end] or None
        figs, media = extract(doc, key[0] if key else None, key[1] if key else None,
                              job.get('locator'), job.get('ans_split', True), job.get('qnum'))
        if figs is None:
            manifest[tid] = {'doc': doc, 'err': '未命中',
                             'locator': job.get('locator'), 'qnum': job.get('qnum')}
            continue
        files = []
        for k, (tgt, cx, cy) in enumerate(figs):
            if tgt not in media:
                continue
            ext = os.path.splitext(tgt)[1] or '.png'
            name = '%s_%d%s' % (tid, k, ext)
            with open(os.path.join(OUT, name), 'wb') as f:
                f.write(media[tgt])
            files.append({'file': name, 'src': tgt, 'cx': cx, 'cy': cy})
        manifest[tid] = {'doc': doc, 'n': len(files), 'figs': files,
                         'start': key[0] if key else job.get('locator')}
    json.dump(manifest, open(os.path.join(OUT, 'manifest.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    ok = sum(1 for v in manifest.values() if v.get('n'))
    print('jobs:', len(jobs), '有图:', ok, '->', OUT)
