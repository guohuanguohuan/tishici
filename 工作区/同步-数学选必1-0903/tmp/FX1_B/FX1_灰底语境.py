# -*- coding: utf-8 -*-
"""FX1-B：35个纯标点C9C9C9 run逐处语境核查（含run序列展示灰底边界）"""
import zipfile, re
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
with zipfile.ZipFile(r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx') as z:
    root = etree.fromstring(z.read('word/document.xml'))
paras = root.findall(f'.//{{{W}}}body//{{{W}}}p')
punct_only = re.compile(r'^[，．。、；：,.;:()\[\]（）　 ]+$')

for i, p in enumerate(paras):
    # 段内run序列（含oMath线性化），标出灰底run
    seq = []
    has_punct_shd = False
    for child in p.iter():
        ln = etree.QName(child).localname
        if ln == 'r':
            shd = child.find(f'{{{W}}}rPr/{{{W}}}shd')
            fill = shd.get(f'{{{W}}}fill') if shd is not None else None
            t = child.find(f'{{{W}}}t')
            txt = t.text if t is not None and t.text else ''
            if txt:
                if fill == 'C9C9C9':
                    seq.append(f'[灰:{txt}]')
                    if punct_only.match(txt):
                        has_punct_shd = True
                else:
                    seq.append(txt)
        elif ln == 'oMath':
            lin = ''.join(e.text or '' for e in child.iter() if etree.QName(e).localname == 't')
            seq.append(f'⟨{lin}⟩')
    if has_punct_shd:
        print(f'--- p#{i} ---')
        print(''.join(seq)[:400])
        print()
