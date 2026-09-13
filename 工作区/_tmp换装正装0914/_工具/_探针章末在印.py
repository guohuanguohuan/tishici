# -*- coding: utf-8 -*-
"""探针：章末 true/pure PDF 文字层值在印验证（对付 [D] 答案区口径不适用）。
从值快照取章末样值，剥空白归一后在 PDF 归一文字层查找；true 应在、pure 应不在。"""
import io, json, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pymupdf

snap = json.load(io.open(r'C:/提示词/工作区/M2-第1章量产0911/成卷/答案册/值快照.json', encoding='utf-8'))
vals = snap.get('vals', snap)
norm = lambda s: re.sub(r'\s+', '', s)


def pdf_text(f):
    doc = pymupdf.open(f)
    return norm(''.join(p.get_text() for p in doc))


t = pdf_text('M2导学本/章末-本章总结提升/main-true.pdf')
p = pdf_text('M2导学本/章末-本章总结提升/main-pure.pdf')
sample_keys = ['导-章末-例1', '导-章末-变式1', '导-章末-例12', '导-章末-变式12',
               '导-章末-高考1', '导-章末-高考2', '导-章末-高考3', '导-章末-高考4']
miss_t = miss_p = 0
for k in sample_keys:
    v = norm(vals[k])
    hit_t, hit_p = v in t, v in p
    miss_t += 0 if hit_t else 1
    miss_p += 0 if hit_p else 1
    print('%s true=%s pure=%s  %s' % (k, hit_t, hit_p, v[:42]))
# 全 28 键扫
allk = [k for k in vals if k.startswith('导-章末-')]
mt = sum(0 if norm(vals[k]) in t else 1 for k in allk)
mp = sum(0 if norm(vals[k]) in p else 1 for k in allk)
print('全 %d 键：true 缺 %d｜pure 缺 %d（pure 答案不印为正）' % (len(allk), mt, mp))
