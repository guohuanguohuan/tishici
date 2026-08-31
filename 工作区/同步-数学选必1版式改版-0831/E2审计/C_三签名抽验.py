# -*- coding: utf-8 -*-
"""E2任务C①抽验：三签名命中段落交错流dump（公式⟦m:⟧＋图片⟦IMG⟧显形），
逐命中定性弱判据，排查行内公式图片盲区。"""
import zipfile, re, sys, io, os
from lxml import etree
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
WT_P = '{%s}p' % W
ROOT = r'C:\Users\28120\Desktop\提示词\高中数学\高中数学同步'
F = {
 'X1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
 'I1': '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
 'B':  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
 'C':  '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
 'X2': '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
 'I2': '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
 'E':  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
 'F':  '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
 'G':  '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
 'H':  '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}
# (code, p#) 来自扫描输出（root.iter(w:p) 全序）
HITS = [
 ('B', 353, '③2处「所以,且，」疑真空位'),
 ('E', 172, '③「直线某过点」疑掉位'),
 ('H', 446, '①双逗主判据 题276'),
 ('X2', 58, '②段尾簇 题8'),
 ('I1', 32, '③平面'), ('I1', 46, '③向量'), ('I1', 115, '③基向量'), ('I1', 141, '③坐标向量'), ('I1', 236, '③直线'),
 ('B', 57, '③单位向量'), ('B', 104, '③平移向量'), ('B', 147, '③共面向量'),
 ('I2', 189, '③圆定义'), ('I2', 258, '③阿氏圆'), ('I2', 403, '③椭圆'), ('I2', 556, '③双曲线'),
 ('I2', 791, '③等差数列'), ('I2', 805, '③设点'),
 ('E', 124, '③中心点'), ('E', 350, '③对称点'), ('E', 607, '③太极函数'),
 ('F', 79, '③x2/36'), ('F', 83, '①遗留复核'), ('F', 700, '③圆锥曲线Γ'),
 ('G', 83, '③双曲线右支'), ('G', 432, '③抛物线方程'),
 ('H', 17, '③题型标题'), ('H', 152, '③垂直直线'), ('H', 381, '③渐近线'),
 ('C', 0, 'SKIP'),
]
HITS = [h for h in HITS if h[2] != 'SKIP']

def dump(code, pno, note):
    path = os.path.join(ROOT, F[code])
    with zipfile.ZipFile(path) as z:
        root = etree.fromstring(z.read('word/document.xml'))
    for pi, p in enumerate(root.iter(WT_P)):
        if pi != pno:
            continue
        parts = []
        for child in p.iter():
            qn = etree.QName(child)
            if qn.namespace == W and qn.localname == 't' and child.text:
                parts.append(child.text)
            elif qn.namespace == M and qn.localname == 'oMath':
                lin = ''.join(t.text or '' for t in child.iter(f'{{{M}}}t'))
                parts.append(f'⟦m:{lin[:80]}⟧')
            elif qn.localname == 'drawing':
                parts.append('⟦IMG⟧')
        full = ''.join(parts)
        n_img = full.count('⟦IMG⟧')
        n_math = len(re.findall(r'⟦m:', full))
        print(f'== {code} p#{pno} [{note}] IMG={n_img} oMath={n_math}')
        print('   ', full[:400])
        return n_img, n_math, full
    print(f'== {code} p#{pno} NOT FOUND')

for code, pno, note in HITS:
    dump(code, pno, note)
