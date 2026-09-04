# -*- coding: utf-8 -*-
"""P2回归门·勘误复核（只读）：题1.2.1.2-2 详解末值符号纠错是否在位
对象：B件讲练上卷。方法：解包XML只读，oMath线性化=拼接全部m:t文本。
零写入：不修改任何文件。"""
import zipfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
DOCX = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'

with zipfile.ZipFile(DOCX) as z:
    root = etree.fromstring(z.read('word/document.xml'))
paras = root.findall(f'.//{{{W}}}body//{{{W}}}p')

def streams(p):
    full, wt = [], []
    for el in p.iter():
        ln = etree.QName(el).localname
        if ln == 't' and el.text:
            full.append(el.text)
            if etree.QName(el).namespace == W:
                wt.append(el.text)
    return ''.join(full), ''.join(wt)

def norm(s):
    return ''.join(s.split())

# 1) 定位题号块 1.2.1.2-2．
anchor = None
for i, p in enumerate(paras):
    full, wt = streams(p)
    if '1.2.1.2-2' in wt.replace(' ', ''):
        anchor = i
        print(f'[定位] 题号块命中 p#{i}: {wt[:60]!r}')
if anchor is None:
    print('[定位] 未命中题号文本！')
    raise SystemExit(1)

# 2) 输出题块：题号段起，直到下一题号块或题块结束（打印后续30段内的 题干/详解/答案 相关段）
print('\n===== 题块全文（题号段起35段，含oMath线性化） =====')
for i in range(anchor, min(anchor + 35, len(paras))):
    full, wt = streams(paras[i])
    if not full.strip() and not wt.strip():
        continue
    tag = ''
    for k in ('1.2.1.2-', '【分析】', '【详解】', '【答案】', '【知识点】'):
        if k in wt:
            tag = f'  <<{k}'
    print(f'p#{i}{tag}\n  WT纯文字: {wt!r}\n  FULL线性化: {full!r}')

# 3) 签名断言：改正态 vs 旧错态
print('\n===== 签名断言 =====')
block_full = ''
for i in range(anchor, min(anchor + 35, len(paras))):
    f, _ = streams(paras[i])
    block_full += f
nb = norm(block_full)
print('改正态签名 x=-1z=2  命中:', norm('x=-1z=2') in nb)
print('旧错态签名 x=1z=-2  命中:', norm('x=1z=-2') in nb)
print('方程组签名 x-1+z=0-2x-z=0 命中:', norm('x-1+z=0-2x-z=0') in nb)
print('结论签名 P(－1,0,2) 命中:', ('P(－1,0,2)' in nb) or ('P(-1,0,2)' in nb))
print('答案C签名 故选C 命中:', '故选C' in nb)

# 4) 「解得」逐字上下文
idx = nb.find('解得')
if idx >= 0:
    print(f'\n「解得」后40字(去空白): {nb[idx:idx+40]!r}')
# 原始未去空白上下文（FULL流）
for i in range(anchor, min(anchor + 35, len(paras))):
    f, _ = streams(paras[i])
    if '解得' in f:
        j = f.find('解得')
        print(f'p#{i}「解得」原始上下文: {f[max(0,j-30):j+50]!r}')
