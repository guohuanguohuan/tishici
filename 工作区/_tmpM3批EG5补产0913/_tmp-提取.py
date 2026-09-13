# -*- coding: utf-8 -*-
"""G5补产候选题富矿docx对象层提取（只读源docx；产出候选题全文切片）"""
import re, sys, os
from docx import Document
from docx.oxml.ns import qn

ROOT = r"C:/提示词/高中数学/参考/组卷网/【新课标 新探索】大单元作业设计/人教A版选择性必修1/第3章 圆锥曲线的方程"
OUT = r"C:/提示词/工作区/_tmpM3批EG5补产0913/_tmp-候选切片.txt"

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'

def para_text(p):
    """段落全文：w:t 顺序拼接 + OMML m:t 以 〔…〕包裹（保序遍历）"""
    parts = []
    for node in p._p.iter():
        tag = node.tag
        if tag == W + 't':
            parts.append(node.text or '')
        elif tag == M + 't':
            parts.append('⟦' + (node.text or '') + '⟧')
    return ''.join(parts)

def file_paras(path):
    doc = Document(path)
    return [para_text(p) for p in doc.paragraphs]

def grab(fn, wanted, label):
    """wanted: 题号集合（如 {'3','4'}）；按题号行切题块"""
    path = os.path.join(ROOT, fn)
    paras = file_paras(path)
    # 找题号起始行（形如 N．或 N.）
    items_all = []
    for i, t in enumerate(paras):
        m = re.match(r'^\s*(\d{1,2})\s*[．.、]\s*\S', t)
        if m:
            items_all.append((i, int(m.group(1))))
    starts = [x for x in items_all if x[1] in wanted]
    # 相邻重复题号（如「题号标记」变体）去重：保留首个
    seen = set(); starts2 = []
    for i, n in starts:
        if n in seen:
            continue
        seen.add(n); starts2.append((i, n))
    starts2.sort()
    print(f'== {label} ({fn}) 题号命中: {[n for _,n in starts2]}', file=sys.stderr)
    out = []
    for k, (i, n) in enumerate(starts2):
        end = starts2[k+1][0] if k+1 < len(starts2) else len(paras)
        block = [t for t in paras[i:end]]
        # 去掉块尾的下一题无关尾部空行
        while block and not block[-1].strip():
            block.pop()
        out.append(f'\n########## {label} #{n}（段{i}起） ##########\n' + '\n'.join(block))
    return out

items = [
    ('5 直线与椭圆的位置关系（共13题）.docx', {11,13}, '3章件5'),
    ('6 椭圆中的弦（共24题）.docx', {1,3,4,5,6,9,10,11,16,21}, '3章件6'),
    ('11 直线与双曲线的位置关系（共13题）.docx', {4,5,6,8}, '3章件11'),
    ('12 双曲线中的弦（共23题）.docx', {5,8,12,14,18}, '3章件12'),
    ('16 直线与抛物线的位置关系（共15题）.docx', {5,13}, '3章件16'),
    ('17 抛物线中的弦（共23题）.docx', {1,8,14,15,16,19,21,22,23}, '3章件17'),
    ('19 圆锥曲线之间的综合问题（共15题）.docx', {6}, '3章件19'),
    ('20 高考新题型-圆锥曲线（共48题）.docx', {41,43}, '3章件20'),
    ('21 章节综合测试-圆锥曲线的方程（共22题）.docx', {1,4,5}, '3章件21'),
]

all_out = []
for fn, wanted, label in items:
    try:
        all_out.extend(grab(fn, wanted, label))
    except Exception as e:
        print(f'!! {label}: {e}', file=sys.stderr)

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(all_out))
print('written', OUT, len(all_out), file=sys.stderr)
