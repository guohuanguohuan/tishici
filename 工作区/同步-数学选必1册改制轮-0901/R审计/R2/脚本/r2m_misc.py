# -*- coding: utf-8 -*-
"""R2——补充：①十件w:ind清零断言；②卷首要素（统计行/导航表只在章首卷：B/E有、C/F/G/H无）；
③X1/C/B页脚X渲染值抽验（X=start+页序）。"""
import sys, io, os, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree
import fitz

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
D = r'C:\提示词\高中数学\高中数学同步'
PDF = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\R2\PDF'

FILES = [
 ('X1','人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'),
 ('I1','人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx'),
 ('B','人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'),
 ('C','人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'),
 ('X2','人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx'),
 ('I2','人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'),
 ('E','人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx'),
 ('F','人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'),
 ('G','人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx'),
 ('H','人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'),
]
print('== ① w:ind清零（十件，正文+标题全部段落）==')
for code, fn in FILES:
    zf = zipfile.ZipFile(os.path.join(D, fn))
    doc = etree.fromstring(zf.read('word/document.xml'))
    bad = 0; ex = []
    for p in doc.find(q('body')).iter(q('p')):
        ppr = p.find(q('pPr'))
        if ppr is None: continue
        ind = ppr.find(q('ind'))
        if ind is not None:
            for v in ind.attrib.values():
                if v not in ('0',): bad += 1; ex.append(dict(ind.attrib)); break
    print('%s: w:ind非零段=%d %s' % (code, bad, ex[:2]))
    zf.close()

print('== ② 卷首要素（统计行「全件N题」/导航表只在章首卷）==')
for code, fn in FILES:
    zf = zipfile.ZipFile(os.path.join(D, fn))
    doc = etree.fromstring(zf.read('word/document.xml'))
    body = doc.find(q('body'))
    # 前三个非空段（文内标题之后）
    paras = []
    for p in body.iter(q('p')):
        t = ''.join(x.text or '' for x in p.iter(q('t'))).strip()
        if t: paras.append(t)
    head = paras[:3]
    stat = any(re.match(r'^全件\d+题', h) for h in head)
    tbl = body.find(q('tbl')) is not None
    print('%s: 首3段=%s  统计行在前3段=%s 有表格=%s' % (code, [h[:26] for h in head], stat, tbl))
    zf.close()

print('== ③ 页脚X渲染值抽验（X=start+页序）==')
for code, pages, start in (('X1', [1, 9, 17], 1), ('C', [1, 40, 77], 78), ('B', [1, 39, 77], 1)):
    pdf = fitz.open(os.path.join(PDF, code + '.pdf'))
    for pno1 in pages:
        txt = re.sub(r'\s+', '', pdf[pno1 - 1].get_text())
        ms = re.findall(r'第(\d+)页（', txt) or re.findall(r'页脚第(\d+)页', txt) or re.findall(r'第(\d+)页$', txt)
        # 直接抓页眉页脚两处「第X页」
        ms = re.findall(r'第(\d+)页', txt)
        exp = start + pno1 - 1
        ok = all(int(x) == exp for x in ms) and len(ms) >= 2
        print('%s p%d: 渲染X=%s 期望=%d %s' % (code, pno1, ms, exp, 'OK' if ok else 'MISMATCH'))
    pdf.close()
print('DONE')
