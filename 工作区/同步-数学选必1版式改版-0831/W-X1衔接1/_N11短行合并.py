# -*- coding: utf-8 -*-
# N11短行合并扩面（X1衔接件）：零字符段落合并——后段子元素并入前段，删除空段
# 决策清单见同目录 决策清单-N11短行合并.md
import zipfile, tempfile, os, time, sys
from lxml import etree
WNS='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
MNS='http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s'%(WNS,t)
def m(t): return '{%s}%s'%(MNS,t)
p = sys.argv[1]
z = zipfile.ZipFile(p); doc = etree.fromstring(z.read('word/document.xml')); z.close()
body = doc.find(q('body'))
paras = list(body.iter(q('p')))

# 合并组（1-based段落序号，当前态）：[起点, 终点]
GROUPS = [
    (18,20,'条目1.2.1相似判定①②③枚举短行必并'),
    (22,25,'条目1.2.1相似比①②③④枚举短行必并'),
    (29,31,'条目3射影定理条件行＋①②枚举必并'),
    (53,54,'点拨①②（①为13字短行）'),
    (61,62,'点拨①②枚举短行必并'),
    (111,112,'题10小问(1)(2)短行必并'),
    (203,205,'题18【答案】三段折行合一（短字段并行）'),
    (206,208,'题18【分析】(1)(2)(3)全短行枚举必并'),
    (231,233,'题22小问(1)(2)(3)短行必并'),
    (282,283,'题29小问(1)(2)短行必并'),
    (285,286,'题29【答案】两段折行合一'),
    (287,288,'题29【分析】(2)并入(1)（零字符、与115同类形态）'),
    (291,292,'题29【详解】(2)并入(1)尾（零字符）'),
]

assert all(paras[a-1] is not None for a,b,_ in GROUPS)
# 身份法：先取元素引用再改树
merged = 0
for a,b,why in GROUPS:
    first = paras[a-1]
    for k in range(a+1, b+1):
        src = paras[k-1]
        # 移动除pPr外全部子元素到first末尾
        for child in list(src):
            if child.tag == q('pPr'):
                continue
            first.append(child)
        src.getparent().remove(src)
        merged += 1

new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
fd,tmp = tempfile.mkstemp(suffix='.docx', dir=os.path.dirname(os.path.abspath(p))); os.close(fd)
with zipfile.ZipFile(p) as zin, zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zout:
    for it in zin.infolist():
        zout.writestr(it, new_xml if it.filename=='word/document.xml' else zin.read(it.filename))
for k in range(10):
    try: os.replace(tmp,p); break
    except PermissionError: time.sleep(5)
print('N11合并完成：合并入前段 %d 个段落（13组），文件段落 -%d' % (merged, merged))
