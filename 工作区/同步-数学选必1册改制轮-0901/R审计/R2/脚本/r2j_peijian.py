# -*- coding: utf-8 -*-
"""R2——配页前检查①②证据：21件清点、文件名↔文内开头标题↔core title三处一致、
配页件无页眉页脚断言、册目录页目录树提取、docDefaults同构抽验。只读。"""
import sys, io, os, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
D = r'C:\提示词\高中数学\高中数学同步'
OUT = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\R2\输出'

CONTENT = [
 ('X1','人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',29),
 ('I1','人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',47),
 ('B','人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',61),
 ('C','人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',79),
 ('X2','人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',13),
 ('I2','人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',67),
 ('E','人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',92),
 ('F','人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',90),
 ('G','人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',68),
 ('H','人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',89),
]
PEI = [
 ('封面','人教B版选必1·封面.docx'),('使用说明','人教B版选必1·使用说明.docx'),
 ('册目录页','人教B版选必1·册目录页.docx'),
 ('部分封面1a','人教B版选必1·部分封面（第1章 空间向量与立体几何·衔接）.docx'),
 ('部分封面1b','人教B版选必1·部分封面（第1章 空间向量与立体几何·清单）.docx'),
 ('部分封面1c','人教B版选必1·部分封面（第1章 空间向量与立体几何·讲练）.docx'),
 ('部分封面2a','人教B版选必1·部分封面（第2章 平面解析几何·衔接）.docx'),
 ('部分封面2b','人教B版选必1·部分封面（第2章 平面解析几何·清单）.docx'),
 ('部分封面2c','人教B版选必1·部分封面（第2章 平面解析几何·讲练）.docx'),
 ('错题1','人教B版选必1·错题记录（第1章 空间向量与立体几何）.docx'),
 ('错题2','人教B版选必1·错题记录（第2章 平面解析几何）.docx'),
]

out = open(os.path.join(OUT, 'r2j_配页件核验.txt'), 'w', encoding='utf-8')
def P(*a): print(*a); print(*a, file=out)

# ① 21件清点
files_on_disk = set(f for f in os.listdir(D) if f.endswith('.docx'))
expect = [fn for _, fn, _ in CONTENT] + [fn for _, fn in PEI]
missing = [fn for fn in expect if fn not in files_on_disk]
P('①清点: 期望docx=%d（10内容+11配页），盘上缺失=%s；装订单md存在=%s' % (
    len(expect), missing or '无', os.path.exists(os.path.join(D, '人教B版选必1·装订单.md'))))

# ② 三处一致（内容件：文件名↔文内开头标题↔core title）
for code, fn, _ in CONTENT:
    zf = zipfile.ZipFile(os.path.join(D, fn))
    doc = etree.fromstring(zf.read('word/document.xml'))
    body = doc.find(q('body'))
    first = ''
    for p in body.iter(q('p')):
        t = ''.join(x.text or '' for x in p.iter(q('t'))).strip()
        if t: first = t; break
    core = ''
    try:
        c = etree.fromstring(zf.read('docProps/core.xml'))
        for el in c.iter():
            if etree.QName(el).localname == 'title' and el.text: core = el.text.strip(); break
    except KeyError: core = '(无core title)'
    ok1 = (first == fn[:-5]); ok2 = (core == fn[:-5]) if core != '(无core title)' else None
    P('%s: 文内开头标题%s文件名 %s｜core title%s文件名 %s' % (code, '==' if ok1 else '!=', '一致' if ok1 else '[%s]vs[%s]' % (first, fn[:-5]),
      ('==' if ok2 else '!=') if ok2 is not None else '（无）', '一致' if ok2 else ('[%s]' % core if ok2 is not None else '')))
    zf.close()

# ③ 配页件：无页眉页脚断言＋首段文本（封面类标题豁免一致性——记录即可）
for code, fn in PEI:
    zf = zipfile.ZipFile(os.path.join(D, fn))
    names = zf.namelist()
    hf = [n for n in names if re.match(r'word/(header|footer)\d*\.xml$', n)]
    doc = etree.fromstring(zf.read('word/document.xml'))
    refs = re.findall(r'(headerReference|footerReference)', zf.read('word/document.xml').decode('utf-8', 'ignore'))
    body = doc.find(q('body'))
    first = ''
    for p in body.iter(q('p')):
        t = ''.join(x.text or '' for x in p.iter(q('t'))).strip()
        if t: first = t; break
    P('%s(%s): header/footer部件=%s 引用=%s 首段=[%s]' % (code, '配页件', hf or '无', refs or '无', first[:60]))
    zf.close()

# ④ 册目录页目录树提取
zf = zipfile.ZipFile(os.path.join(D, '人教B版选必1·册目录页.docx'))
doc = etree.fromstring(zf.read('word/document.xml'))
P('--- 册目录页全部非空段（含制表符页码） ---')
n = 0
for p in doc.find(q('body')).iter(q('p')):
    t = ''.join(x.text or '' for x in p.iter(q('t'))).strip()
    if t:
        n += 1
        P('%3d| %s' % (n, t[:110]))
P('册目录页非空行数=%d' % n)
zf.close()

# ⑤ docDefaults同构抽验（封面/使用说明/部分封面1c/错题1）
for code, fn in [('封面','人教B版选必1·封面.docx'),('使用说明','人教B版选必1·使用说明.docx'),
                 ('部分封面1c','人教B版选必1·部分封面（第1章 空间向量与立体几何·讲练）.docx'),
                 ('错题1','人教B版选必1·错题记录（第1章 空间向量与立体几何）.docx')]:
    zf = zipfile.ZipFile(os.path.join(D, fn))
    root = etree.fromstring(zf.read('word/styles.xml'))
    dd = root.find(q('docDefaults'))
    sz = None
    if dd is not None:
        rpd = dd.find(q('rPrDefault'))
        if rpd is not None and rpd.find(q('rPr')) is not None:
            e = rpd.find(q('rPr')).find(q('sz'))
            sz = e.get(q('val')) if e is not None else None
    doc = etree.fromstring(zf.read('word/document.xml'))
    sect = doc.find(q('body')).find(q('sectPr'))
    pg = sect.find(q('pgSz')); mar = sect.find(q('pgMar'))
    P('%s: docDefaults rPrDefault sz=%s pgSz=%s pgMar=%s' % (code, sz,
      {k.split('}')[1]: v for k, v in pg.attrib.items()} if pg is not None else None,
      {k.split('}')[1]: v for k, v in mar.attrib.items()} if mar is not None else None))
    zf.close()
out.close(); print('DONE')
