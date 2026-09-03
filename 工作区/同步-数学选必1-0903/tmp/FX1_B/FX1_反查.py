# -*- coding: utf-8 -*-
"""FX1-B 反查（只读）：九件内容件检索题1.2.1.2-2同源副本
签名1=题干首句（已知点A(0,1,0)…若PA⊥平面ABC）
签名2=详解线性化（x-1+z=0-2x-z=0 ／ x=1z=-2 旧错值形态）
另：B件C9C9C9 run全量扫描标点越界"""
import zipfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
BASE = r'C:\提示词\高中数学\高中数学同步'
NINE = [
    '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
    '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
]

def para_streams(path):
    """yield 每段 (全文流含公式线性化, 纯w:t流)"""
    with zipfile.ZipFile(path) as z:
        root = etree.fromstring(z.read('word/document.xml'))
    for p in root.findall(f'.//{{{W}}}body//{{{W}}}p'):
        full = []
        wt = []
        for el in p.iter():
            ln = etree.QName(el).localname
            if ln == 't' and el.text:
                full.append(el.text)
                if etree.QName(el).namespace == W:
                    wt.append(el.text)
        yield ''.join(full), ''.join(wt)

def norm(s):
    return ''.join(s.split())  # 去所有空白后比对

SIG1 = '若PA⊥平面ABC'          # 题干首句特征段（w:t纯文字段）
SIG1B = '已知点A(0,1,0)'        # 题干首句开头（含m:t坐标流）
SIG2A = 'x-1+z=0-2x-z=0'        # 详解方程组线性化
SIG2B = 'x=1z=-2'               # 详解旧错值形态（未纠错副本命中特征）

print('=' * 20, '反查九件（只读）', '=' * 20)
total_hits = 0
for fn in NINE:
    path = BASE + '\\' + fn
    hits = []
    for i, (full, wt) in enumerate(para_streams(path)):
        nf, nw = norm(full), norm(wt)
        for sig, tag in ((SIG1, '题干特征'), (SIG1B, '题干首句'), (SIG2A, '详解方程'), (SIG2B, '详解旧错值')):
            if norm(sig) in nf or norm(sig) in nw:
                hits.append((i, tag))
    total_hits += len(hits)
    print(f'{fn}: 命中={len(hits)}' + (f' {hits}' if hits else ''))
print(f'反查合计命中={total_hits}')

print('=' * 20, 'B件C9C9C9标点越界扫描', '=' * 20)
import re
with zipfile.ZipFile(r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx') as z:
    root = etree.fromstring(z.read('word/document.xml'))
paras = root.findall(f'.//{{{W}}}body//{{{W}}}p')
punct_only = re.compile(r'^[，．。、；：,.;:()\[\]（）　 ]+$')
hits = []
cnt = 0
for i, p in enumerate(paras):
    for r in p.findall(f'.//{{{W}}}r'):
        shd = r.find(f'{{{W}}}rPr/{{{W}}}shd')
        if shd is None or shd.get(f'{{{W}}}fill') != 'C9C9C9':
            continue
        cnt += 1
        t = r.find(f'{{{W}}}t')
        txt = t.text if t is not None and t.text else ''
        if txt and punct_only.match(txt):
            hits.append((i, txt))
print(f'C9C9C9 run总数={cnt}，纯标点越界run={len(hits)} {hits if hits else ""}')
