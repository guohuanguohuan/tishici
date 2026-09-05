# -*- coding: utf-8 -*-
"""④轮步骤5：纠错轮遗留 3 项处置（附则《元素守恒断言》口径）。
【项1】B件 段idx534（题1.2.1.6-8 详解块首段）残句「试题分析：」删除——run1 文本
  '试题分析：连接'→'连接'（删 5 字符；纠错轮台账#3b 同型残句、F件整块型系台账明示维持不复涉）。
【项2】B件 孤儿媒资 word/media/image87.jpg（115216B，rels rId94 悬挂、document 零引用）删除：
  媒资＋rels 条目同步清（守恒对账：document.xml 三族不动、media -1、rels -1 全登记）。
【项3】I1 image21.png ／ C sub3_C_3.png（同字节对 24×27px、295B）：渲染定性＝内容承载公式碎片
  （84 不透明像素、根号形笔画可辨），非零内容垃圾图——保留登记（L107 豁免族·公式碎片；
  删除台账拍板名单外）。
落盘 ④_遗留3项_处置登记.json。"""
import io, sys, os, re, json, zipfile
from lxml import etree
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'C:\提示词\工作区\选必1成书修复-0905\②工具'
DST = BASE + r'\副本_④轮'
REP = BASE + r'\报告'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
FAM_PATS = {'w:t': re.compile(rb'<w:t(?:\s[^>]*)?>'), 'm:oMath': re.compile(rb'<m:oMath(?:\s[^>]*)?>'),
            'm:t': re.compile(rb'<m:t(?:\s[^>]*)?>'), 'm:oMathPara': re.compile(rb'<m:oMathPara(?:\s[^>]*)?>'),
            'wp:inline': re.compile(rb'<wp:inline(?:\s[^>]*)?>'), 'wp:anchor': re.compile(rb'<wp:anchor(?:\s[^>]*)?>')}
def fam_counts(b):
    return {k: len(p.findall(b)) for k, p in FAM_PATS.items()}

ok_all = True
reg = {}
B = '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
p = os.path.join(DST, B)
zin = zipfile.ZipFile(p)
members = {n: zin.read(n) for n in zin.namelist()}
zin.close()
doc_old = members['word/document.xml']
fam_pre = fam_counts(doc_old)
n_analy = len(re.findall('试题分析', doc_old.decode('utf-8')))
n_jiexi = len(re.findall('试题解析', doc_old.decode('utf-8')))
assert (n_analy, n_jiexi) == (1, 0), 'B 试题分析计数 %d/%d ≠ 1/0' % (n_analy, n_jiexi)
old_t = '>试题分析：连接<'
new_t = '>连接<'
assert doc_old.count(old_t.encode()) == 1, 'B 残句定位失准'
doc_new = doc_old.replace(old_t.encode(), new_t.encode())
etree.fromstring(doc_new)
fam_post = fam_counts(doc_new)
assert fam_pre == fam_post, 'B 三族计数变动'
members['word/document.xml'] = doc_new
# 项2：rels 删 rId94
rels = members['word/_rels/document.xml.rels'].decode('utf-8')
m = re.search(r'<Relationship Id="rId94" [^>]*Target="media/image87\.jpg"[^>]*/>', rels)
assert m, 'B rId94 条目未命中'
rels_new = rels[:m.start()] + rels[m.end():]
etree.fromstring(rels_new.encode('utf-8'))
members['word/_rels/document.xml.rels'] = rels_new.encode('utf-8')
assert 'word/media/image87.jpg' in members
del members['word/media/image87.jpg']
tmp = p + '.fix'
zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
for n, b in members.items():
    zo.writestr(n, b)
zo.close()
os.replace(tmp, p)
# 复核：B 现态零试题分析、image87 与 rId94 全清、media=128
z2 = zipfile.ZipFile(p)
d2 = z2.read('word/document.xml').decode('utf-8')
r2 = z2.read('word/_rels/document.xml.rels').decode('utf-8')
check = ('试题分析' not in d2 and 'rId94' not in r2
         and 'word/media/image87.jpg' not in z2.namelist()
         and len([n for n in z2.namelist() if n.startswith('word/media/')]) == 128)
ok_all = ok_all and check
reg['项1_B残句'] = {'file': B, '位置': 'body 段 idx534（题1.2.1.6-8 【详解】块首段）',
                    '原文': '【详解】试题分析：连接，因为底面…',
                    '处置': '删「试题分析：」5字符（run1 文本 试题分析：连接→连接）',
                    '依据': '纠错轮台账#3b 同型残句清零（源材料标签残留）；F件整块型系台账#6b明示维持、不复涉',
                    '改动前试题分析计数': n_analy, '改动后': 0, 'PASS': check}
reg['项2_B孤儿图'] = {'file': B, '对象': 'word/media/image87.jpg（115216B）＋rels rId94（悬挂）',
                      '处置': '媒资＋rels 条目一并删除；document.xml 零改动',
                      '依据': '纠错轮核对报告注记（bak 同为孤儿、先于纠错轮存在）；media 129→128',
                      '三族守恒': fam_pre == fam_post, 'PASS': check}
# 项3 保留登记（含 C sub3_C_5 同字节核对）
zc = zipfile.ZipFile(os.path.join(DST, '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'))
s3 = zc.read('word/media/sub3_C_3.png')
s5 = zc.read('word/media/sub3_C_5.png') if 'word/media/sub3_C_5.png' in zc.namelist() else None
zi = zipfile.ZipFile(os.path.join(DST, '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx'))
i21 = zi.read('word/media/image21.png')
reg['项3_疑似空图'] = {'对象': ['I1 media/image21.png（rIdW1_7 实引）', 'C media/sub3_C_3.png（rId359 实引）'],
                       '渲染定性': '24×27px、295B、同字节三对（image21=sub3_C_3=%s）；84 不透明像素、'
                                   '根号形公式碎片笔画可辨＝内容承载，非零内容垃圾图' % (i21 == s3),
                       '处置': '保留（L107 登记类豁免族·公式碎片；同步盘删除台账拍板名单未列入）',
                       'sub3_C_5 同字节': (s5 == s3) if s5 is not None else '件内无sub3_C_5',
                       'PASS': True}
with open(os.path.join(REP, '④_遗留3项_处置登记.json'), 'w', encoding='utf-8') as f:
    json.dump(reg, f, ensure_ascii=False, indent=1)
for k, v in reg.items():
    print(k, 'PASS' if v['PASS'] else '←FAIL')
print('合计 PASS＝%s' % ok_all)
sys.exit(0 if ok_all else 1)
