# -*- coding: utf-8 -*-
"""答案册 ⑬ 差1 定位探针2：逐行数学剥离→分段骨架，在 pdf 全文（去空白）中查存在性。"""
import re
import pymupdf

body = open(r'C:\提示词\工作区\M2-第1章量产0911\成卷\答案册\body.tex', encoding='utf-8').read()
lines = [ln for ln in body.split('\n') if not ln.lstrip().startswith('%')]

doc = pymupdf.open(r'C:\提示词\工作区\M2-第1章量产0911\成卷\答案册\main.pdf')
full_ns = re.sub(r'\s+', '', ''.join(p.get_text() for p in doc))
doc.close()

math = re.compile(r'\\\((?:[^\\]|\\.)*?\\\)')
SENT = 'ZMATHZ'

def skeletons(ln):
    """非数学段 → 骨架串（保非 ASCII＋ASCII 字母数字）。"""
    s = math.sub(SENT, ln)
    s = re.sub(r'\\[A-Za-z@]+\*?(\[[^\]]*\])?', ' ', s)
    s = re.sub(r'[{}$&~^_]', ' ', s)
    out = []
    for seg in s.split(SENT):
        sk = re.sub(r'\s+', '', seg)
        sk = ''.join(ch for ch in sk if not ch.isascii() or ch.isalnum())
        if len(sk) >= 2:
            out.append(sk)
    return out

miss = 0
for idx, ln in enumerate(lines):
    if '（' not in ln:
        continue
    for sk in skeletons(ln):
        if sk not in full_ns:
            miss += 1
            print(f'L{idx} 缺段「{sk[:40]}」 源行: {ln.strip()[:88]}')
print('缺失段合计:', miss)
