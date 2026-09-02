# -*- coding: utf-8 -*-
"""A''成品轮开工盘点：十内容件结构现状（只读）"""
import glob, os, re, zipfile
from lxml import etree
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
WP = '{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
BASE = r'C:\提示词\高中数学\高中数学同步'
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
def qn(t): return t
for tag, fn in FILES:
    p = os.path.join(BASE, fn)
    if not os.path.exists(p): print(f'{tag}: MISSING {fn}'); continue
    with zipfile.ZipFile(p) as z:
        xml = z.read('word/document.xml')
        names = z.namelist()
    root = etree.fromstring(xml)
    body = root.find(W+'body')
    sects = body.findall('.//'+W+'sectPr')
    cols_attrs = [(s.find(W+'cols') is not None, (s.find(W+'cols').get(W+'num'), s.find(W+'cols').get(W+'space'), s.find(W+'cols').get(W+'sep')) if s.find(W+'cols') is not None else None) for s in sects]
    anchors = body.findall('.//'+WP+'anchor')
    inlines = body.findall('.//'+WP+'inline')
    # 题号形态采样：正则扫描全部w:t文本找「\d+\.\d+-\d+．」与「\d+．」
    texts = ''.join(t.text or '' for t in body.iter(W+'t'))
    m_new = re.findall(r'\d+(?:\.\d+)+-\d+．', texts)
    m_old = re.findall(r'(?<![\d.])(\d+\.\d+-\d+)．', texts)
    # C9C9C9 / F2F2F2 / E0E0E0 / 1F4E79 计数
    xmls = xml.decode('utf-8')
    c_shd = {v: xmls.count(f'w:fill="{v}"') for v in ['C9C9C9','F2F2F2','E0E0E0']}
    c_blue = xmls.count('1F4E79')
    hdrs = len([n for n in names if re.match(r'word/header\d+\.xml', n)])
    ftrs = len([n for n in names if re.match(r'word/footer\d+\.xml', n)])
    sz21 = xmls.count('w:sz w:val="21"'); sz24=xmls.count('w:sz w:val="24"'); sz18=xmls.count('w:sz w:val="18"')
    print(f"{tag}: sectPr={len(sects)} cols={cols_attrs} anchor={len(anchors)} inline={len(inlines)} "
          f"题号新形={len(m_new)} shd={c_shd} 深蓝={c_blue} hdr/ftr={hdrs}/{ftrs} sz21/24/18={sz21}/{sz24}/{sz18} size={os.path.getsize(p)//1024}KB")
