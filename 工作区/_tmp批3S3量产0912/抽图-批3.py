# -*- coding: utf-8 -*-
"""S3 练习件·批3（课时09/10）源位图提取器——口径同 批2 抽图-批2F.py：
从源 docx 按「题块元素区间/qnum」提取题面图（【答案】前），落 figs 暂存区；
零改绘、位图原样复制（三维禁绘口径）；元素号＝body 直接子元素 0 基（同 工具/dump_docx.py）。
区间依据：亲算-1.2.4-a.md（池-1＝[988]–[1003]、池-6＝[1218]–[1302]，讲练上）；
亲算-1.2.5-a.md（1.2.5.2-2＝[80]–[94]、1.2.5.3-3＝[98]–[109]，讲练下）；
F6·14＝单元6 q14；F7·5＝单元7 q5（亲算-1.2.5-e.md 行区间旁证）。
"""
import os, re, json, zipfile
from lxml import etree

R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
WC = '{' + W + '}'

DOCX = {
    '讲上': r'C:/提示词/高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    '讲下': r'C:/提示词/高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    '单元6': r'C:/提示词/高中数学/参考/组卷网/【新课标 新探索】大单元作业设计/人教A版选择性必修1/第1章 空间向量与立体几何/6空间向量与立体几何中的高考新题型.docx',
    '单元7': r'C:/提示词/高中数学/参考/组卷网/【新课标 新探索】大单元作业设计/人教A版选择性必修1/第1章 空间向量与立体几何/7单元综合测试-空间向量与立体几何.docx',
}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figs_批3')

JOBS = [
    {"id": "ks09_q03", "doc": "讲上", "range": [988, 1003], "note": "池-1 1.2.4.2.1-1"},
    {"id": "ks09_q05", "doc": "讲上", "range": [1218, 1302], "note": "池-6 1.2.4.2.4-6"},
    {"id": "ks09_q06", "doc": "单元6", "qnum": 14, "note": "F6·14"},
    {"id": "ks10_q02", "doc": "单元7", "qnum": 5, "note": "F7·5"},
    {"id": "ks10_q09", "doc": "讲下", "range": [80, 94], "note": "池-2 1.2.5.2-2"},
    {"id": "ks10_q10", "doc": "讲下", "range": [98, 109], "note": "池-3 1.2.5.3-3"},
]

def tagof(el): return el.tag.split('}')[-1]

def para_images(p_el, rels):
    out = []
    for blip in p_el.iter('{%s}blip' % A):
        rid = blip.get('{%s}embed' % R)
        tgt = rels.get(rid)
        if not tgt: continue
        cx = cy = None
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

import struct

def is_real_fig(tgt, cx, cy, media):
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
    if re.match(r'^\d{1,3}．', t) or re.match(r'^\d+\.\d+(\.\d+)*[-．]', t): return True
    if re.match(r'^\d+(\.\d+)+\s*\S', t) and len(t) < 40: return True
    return False

INVIS = dict.fromkeys(map(ord, '\u2060\u200b\u200c\u200d\ufeff'), None)

def extract(doc, start, end=None, qnum=None):
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
    if end is None:
        end = els[-1][0]
        for i, tag, text, imgs in els:
            if i > start and is_blockstart(text or ''):
                end = i - 1; break
    figs = []
    texts = []
    for i in range(start, end + 1):
        e = idx.get(i)
        if not e: continue
        _, tag, text, imgs = e
        if text:
            t = text.translate(INVIS)
            texts.append((i, t[:60]))
            if '【答案' in t or '【解析' in t or '【详解' in t or '【分析' in t:
                break
        figs.extend(img for img in imgs if is_real_fig(img[0], img[1], img[2], media))
    return figs, media, texts

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    manifest = {}
    for job in JOBS:
        tid, doc = job['id'], job['doc']
        key = job.get('range')
        res = extract(doc, key[0] if key else None, key[1] if key else None, job.get('qnum'))
        if res is None:
            manifest[tid] = {'doc': doc, 'err': '未命中', 'note': job['note']}
            continue
        figs, media, texts = res
        files = []
        for k, (tgt, cx, cy) in enumerate(figs):
            if tgt not in media:
                continue
            ext = os.path.splitext(tgt)[1] or '.png'
            name = '%s_%d%s' % (tid, k, ext)
            with open(os.path.join(OUT, name), 'wb') as f:
                f.write(media[tgt])
            files.append({'file': name, 'src': tgt, 'cx': cx, 'cy': cy})
        manifest[tid] = {'doc': doc, 'note': job['note'], 'n': len(files), 'figs': files,
                         'range': key, 'qnum': job.get('qnum')}
    json.dump(manifest, open(os.path.join(OUT, 'manifest.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    for tid, v in manifest.items():
        print(tid, v.get('doc'), 'n=', v.get('n', 'ERR'), [f['src'] for f in v.get('figs', [])])
