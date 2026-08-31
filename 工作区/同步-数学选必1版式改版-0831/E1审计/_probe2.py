# -*- coding: utf-8 -*-
"""探针v2：全文档级（含表格内）补测 + footer jc + 21run性质 + oMathPara混合段核验。只读。"""
import json, os, zipfile
from lxml import etree

NSW = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WP = '{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'
def q(t): return '{%s}%s' % (NSW, t)

base = r'C:\Users\28120\Desktop\提示词\高中数学\高中数学同步'
outd = r'C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\E1审计'
files = [('X1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'),
         ('I1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx'),
         ('B', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'),
         ('C', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'),
         ('X2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx'),
         ('I2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'),
         ('E', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx'),
         ('F', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'),
         ('G', '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx'),
         ('H', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx')]
res = {}
for code, fn in files:
    z = zipfile.ZipFile(os.path.join(base, fn))
    doc = etree.fromstring(z.read('word/document.xml'))
    rs = {}
    for r in doc.iter(q('r')):
        rpr = r.find(q('rPr'))
        if rpr is None: continue
        shd = rpr.find(q('shd'))
        if shd is None: continue
        f = (shd.get(q('fill')) or '').upper()
        if f and f != 'AUTO': rs[f] = rs.get(f, 0) + 1
    pl = {'410': 0, '280': 0, 'other': 0}
    ind = 0
    for p in doc.iter(q('p')):
        ppr = p.find(q('pPr'))
        sp = ppr.find(q('spacing')) if ppr is not None else None
        if sp is None: pl['other'] += 1
        else:
            ln, lr = sp.get(q('line')), sp.get(q('lineRule'))
            if ln == '410' and lr == 'atLeast': pl['410'] += 1
            elif ln == '280' and lr == 'atLeast': pl['280'] += 1
            else: pl['other'] += 1
        if ppr is not None and ppr.find(q('ind')) is not None: ind += 1
    f = etree.fromstring(z.read('word/footer1.xml'))
    fjc = []
    for p in f.iter(q('p')):
        ppr = p.find(q('pPr'))
        jce = ppr.find(q('jc')) if ppr is not None else None
        fjc.append(jce.get(q('val')) if jce is not None else 'None')
    texts21 = []
    n21 = 0
    for r in doc.iter(q('r')):
        rpr = r.find(q('rPr'))
        if rpr is None: continue
        sz = rpr.find(q('sz'))
        if sz is None or sz.get(q('val')) != '21': continue
        n21 += 1
        t = ''.join(tt.text or '' for tt in r.iter(q('t')))
        has_img = r.find('.//' + WP + 'inline') is not None
        if t.strip() and len([x for x in texts21 if x[2]]) < 6:
            texts21.append((t[:30], has_img, True))
    standalone = 0; mixed = 0
    for omp in doc.iter('{%s}oMathPara' % M):
        p = omp.getparent()
        while p is not None and p.tag != q('p'): p = p.getparent()
        if p is None: continue
        txt = ''
        for child in p:
            if child.tag == q('pPr'): continue
            if child.tag in ('{%s}oMathPara' % M, '{%s}oMath' % M): continue
            txt += ''.join(t.text or '' for t in child.iter(q('t')))
        if txt.strip(): mixed += 1
        else: standalone += 1
    print(code, '| runSHD:', rs, '| paraLine全档:', pl, '| ind:', ind, '| footer jc:', fjc)
    print('   21run数:', n21, '有文本样本:', texts21[:6], '| oMathPara独占:', standalone, '混合:', mixed)
    res[code] = {'run_shd_all': rs, 'para_line_all': pl, 'ind_all': ind,
                 'oMathPara_standalone': standalone, 'footer_jc': fjc,
                 'n21': n21, 't21_texts': texts21}
json.dump(res, open(os.path.join(outd, 'probe2_全档.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
