# -*- coding: utf-8 -*-
"""轮1.5续作二 手术脚本（主会话同旨裁决：89卷同类超纲面2处 照删）

两op，逐op锚点断言——错锚即中止不写盘（文件：89题卷④ docx，单件）：
  E1 el480 题2.8.5.2-17【编注】＝C1 极线断言句（13字）＋C2 易错点「极线方程…」〔尾4整节点切除＋首w:t尾部修剪、补句号〕
  E2 el767 题型通式【编注】超纲括注「（或端点到相应准线的距离）」〔仅改 w:t 文本〕
"""
import sys, os, shutil
sys.path.insert(0, '工具')
from docx import Document
from dxml import qn
from dump_docx import para_text
from lxml import etree

W, M, WR, PR = qn('w:t'), qn('m:t'), qn('w:r'), qn('w:pPr')
MATH = qn('m:oMath')
BAK = '.bak_轮15源修正0913'
D = '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'


def die(msg):
    print('!! 锚点断言失败，中止不写盘：' + msg)
    sys.exit(1)


def text_of(n):
    return ''.join((t.text or '') for t in n.iter() if t.tag in (W, M))


def ln(n):
    return etree.QName(n).localname


doc = Document(D)
els = list(doc.element.body)
evidence = []

# ---------- 全件唯一性前置 ----------
blob = ''.join(text_of(ch) for ch in els)
for needle, exp in (('极线', 2), ('（或端点到相应准线的距离）', 1)):
    if blob.count(needle) != exp:
        die('全件 %r 命中 %d（期望 %d）' % (needle, blob.count(needle), exp))

# ================= E1 el480 =================
p = els[480]
if not (p.find(PR) is not None and len(list(p)) == 4 and ln(list(p)[1]) == 'r' and ln(list(p)[2]) == 'r'):
    die('E1 el480 顶层结构漂移：%s' % [ln(x) for x in p])
if '【' not in text_of(list(p)[1]) or '分' not in text_of(list(p)[2]):
    die('E1 el480 标签段不符：%r / %r' % (text_of(list(p)[1]), text_of(list(p)[2])))
run = list(p)[3]
kids = [k for k in run if k.tag != qn('w:rPr')]
T1 = ('过椭圆内一点M的两弦端点切线分别交于P、Q求PQ：切线交点落在过M弦的极线上，'
      '由切点弦方程知P、Q都满足3x/25＋2y/9＝1，此即PQ；易错点：极线方程xMx/')
T1N = ('过椭圆内一点M的两弦端点切线分别交于P、Q求PQ：'
       '由切点弦方程知P、Q都满足3x/25＋2y/9＝1，此即PQ。')
if len(kids) != 5 or kids[0].tag != W or (kids[0].text or '') != T1:
    die('E1 el480 正文 run 子节点形态漂移：%s / 文本=%r' % ([ln(x) for x in kids], (kids[0].text or '')[:40]))
TAILTXT = ''.join(text_of(k) for k in kids[1:])
if TAILTXT != 'a²＋yMy/b²＝1系数勿代错。':
    die('E1 el480 尾4整节点文本=%r（期望 %r）' % (TAILTXT, 'a²＋yMy/b²＝1系数勿代错。'))
if blob.count(T1) != 1:
    die('E1 首 w:t 全文串全件命中 %d（应为1）' % blob.count(T1))
before_E1 = para_text(p)
shd0 = len(p.findall('.//' + qn('w:shd'))); drw0 = len(p.findall('.//' + qn('w:drawing')))
mat0 = len(p.findall('.//' + MATH)); pbd0 = p.find('.//' + qn('w:pBdr')) is not None
kids[0].text = T1N  # 原 w:t 已带 xml:space="preserve"，改文本不碰属性
for k in kids[1:]:
    k.getparent().remove(k)
if (len(p.findall('.//' + qn('w:shd'))), len(p.findall('.//' + qn('w:drawing'))),
        len(p.findall('.//' + MATH)), p.find('.//' + qn('w:pBdr')) is not None) != (shd0, drw0, 0, pbd0):
    die('E1 el480 挂点复核不符（期望 oMath %d→0，其余守恒）' % mat0)
evidence.append(('E1', 'el480 题2.8.5.2-17【编注】（修剪1个w:t＋切除4整节点：2 m:oMath＋2 w:r）',
                 before_E1, para_text(p)))

# ================= E2 el767 =================
p = els[767]
kids = list(p)
if not (len(kids) == 3 and ln(kids[2]) == 'r'):
    die('E2 el767 顶层结构漂移：%s' % [ln(x) for x in kids])
ts = [t for t in kids[2].iter(W)]
if len(ts) != 1:
    die('E2 el767 正文 run 内 w:t 数=%d（应为1）' % len(ts))
T2 = ('题型通式：识别信号——题干给出分别过椭圆（或双曲线）两焦点的两条平行弦，求两三角形（四边形）面积的比，'
      '判归本题型。通法步骤——第一步用焦半径公式（或端点到相应准线的距离）表示两弦长，'
      '第二步由同高（或同底）关系写出面积的比并求值。')
T2N = T2.replace('（或端点到相应准线的距离）', '')
if (ts[0].text or '') != T2:
    die('E2 el767 w:t 文本不符：%r' % (ts[0].text or '')[:60])
if blob.count(T2) != 1 or blob.count('（或端点到相应准线的距离）') != 1:
    die('E2 锚点不唯一')
before_E2 = para_text(p)
shd0 = len(p.findall('.//' + qn('w:shd'))); drw0 = len(p.findall('.//' + qn('w:drawing')))
pbd0 = p.find('.//' + qn('w:pBdr')) is not None
ts[0].text = T2N
if (len(p.findall('.//' + qn('w:shd'))), len(p.findall('.//' + qn('w:drawing'))),
        p.find('.//' + qn('w:pBdr')) is not None) != (shd0, drw0, pbd0):
    die('E2 el767 挂点不守恒')
evidence.append(('E2', 'el767 题型通式【编注】（仅改1个w:t文本）', before_E2, para_text(p)))

# ---------- 落盘 ----------
for op, loc, b, a in evidence:
    print('---- %s %s\n  前：%s\n  后：%s' % (op, loc, b, a))
if os.environ.get('DRY'):
    print('\nDRY RUN：断言全过，未写盘。')
    sys.exit(0)
dst = D + BAK
if os.path.exists(dst):
    print('备份已存在（＝轮1.5首次修前态，不覆盖；本轮增量修前态见 _dump-D2-old.txt／_六类-D2-old.txt），跳过：')
else:
    shutil.copy2(D, dst)
    print('备份：', dst, os.path.getsize(dst), 'bytes')
doc.save(D)
print('已写盘：', D)
