# -*- coding: utf-8 -*-
"""⑧轮债1探针3：QSTART_RE 原文 vs 归一 失配普查（kind 层是否须归一）＋回归件 WJ 普查。"""
import sys, re, zipfile, os
sys.path.insert(0, r'C:/提示词/工具')
from extract_structure import structure   # 先导入（自重包 stdout）
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
WJ = '\u2060'
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
QSTART = re.compile(r'^(?:\d+(?:\.\d+)+-\d+|\d+)．')

BASE = r'C:/提示词/高中数学/高中数学同步'
FILES = {
    'B':  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'C':  '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    'E':  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    'F':  '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    'G':  '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    'H':  '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
    'I1': '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    'I2': '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    'X1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    'X2': '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
    'SM': '人教B版选必1·使用说明.docx',
    'TOC': '人教B版选必1·册目录页.docx',
}
print('件  原文QSTART命中  归一QSTART命中  失配(归中失原)  全文WJ数')
for code, fn in FILES.items():
    z = zipfile.ZipFile(os.path.join(BASE, fn))
    doc = etree.fromstring(z.read('word/document.xml'))
    xml_bytes = z.read('word/document.xml')
    z.close()
    ps = [ptext(el) for el in doc.find(q('body')) if el.tag == q('p')]
    raw = sum(1 for t in ps if QSTART.match(t))
    nor = sum(1 for t in ps if QSTART.match(t.replace(WJ, '')))
    wj = xml_bytes.count(WJ.encode('utf-8'))
    print('%-3s %-6d %-6d %-6d %d' % (code, raw, nor, nor - raw, wj))
REG = r'C:/提示词/高中物理/高中物理同步/人教版必修3 第10章 静电场中的能量·简单卷（14题）.docx'
z = zipfile.ZipFile(REG)
doc = etree.fromstring(z.read('word/document.xml'))
xml_bytes = z.read('word/document.xml')
z.close()
ps = [ptext(el) for el in doc.find(q('body')) if el.tag == q('p')]
raw = sum(1 for t in ps if QSTART.match(t))
nor = sum(1 for t in ps if QSTART.match(t.replace(WJ, '')))
print('REG %-6d %-6d %-6d %d' % (raw, nor, nor - raw, xml_bytes.count(WJ.encode('utf-8'))))
