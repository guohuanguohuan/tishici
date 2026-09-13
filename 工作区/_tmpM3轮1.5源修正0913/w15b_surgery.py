# -*- coding: utf-8 -*-
"""轮1.5续作 手术脚本（主会话裁决0913：大招2源件el305 + 89卷阿基米德讲块超纲面）

四op，逐op锚点断言——错锚即中止不写盘：
  C1 大招2源docx el305 (a+2)/(a−1) → (a+2)/(a−2)   〔与件1 A1 同构 op，目标换源件〕
  C2 89卷 el91  椭圆性质1 删尾「其中…准线上.（可用极点极线来求）」〔整节点移除〕
  C3 89卷 el98  双曲线性质1 删尾「其中…准线上.」〔整节点移除〕
  C4 89卷 el87  【编注】删从句「，焦点弦情形Q落在准线」〔仅改 w:t 文本〕
"""
import sys, os, shutil
sys.path.insert(0, '工具')
from docx import Document
from dxml import qn
from dump_docx import para_text

W, M = qn('w:t'), qn('m:t')
BAK = '.bak_轮15源修正0913'
S = '高中数学/参考/组卷网/高中数学解题大招（二级结论）荟萃/04_原始资料/模块8解析几何/模块8大招2动点问题处理策略（解题大招）.docx'
D = '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'


def clean(s):
    return (s or '').replace('\u2060', '')


def mtext(el):
    return ''.join(n.text or '' for n in el.iter(M))


def fulltext(el):
    return ''.join(n.text or '' for n in el.iter() if n.tag in (W, M))


def die(msg):
    print('!! 锚点断言失败，中止不写盘：' + msg)
    sys.exit(1)


def backup(path):
    dst = path + BAK
    if os.path.exists(dst):
        print('备份已存在（＝本轮增量修前态，改由工作区切片留证），跳过：', dst)
        return dst
    shutil.copy2(path, dst)
    print('备份：', dst, os.path.getsize(dst), 'bytes')
    return dst


def whole_node_split(p, kept, removed):
    """按「前缀文本==kept」在整节点边界切；返回待删节点列表。不做任何 run 内截断。"""
    kids = list(p)
    acc = ''
    for k, n in enumerate(kids):
        if acc == kept:
            tail = ''.join((x.text or '') for m in kids[k:] for x in m.iter() if x.tag in (W, M))
            if tail == removed:
                return kids[k:]
            die('切点文本不符：tail=%r 期望=%r' % (tail, removed))
        acc += ''.join((t.text or '') for t in n.iter() if t.tag in (W, M))
    die('未找到整节点切点（前缀=%r）' % kept[:40])


dS, dD = Document(S), Document(D)
eS, eD = list(dS.element.body), list(dD.element.body)
evidence = []

# ---------- C1 大招2源 el305 分母 a−1 → a−2 ----------
hits = []
for i, ch in enumerate(eS):
    for f in ch.iter(qn('m:f')):
        num, den = f.find(qn('m:num')), f.find(qn('m:den'))
        if num is None or den is None:
            continue
        if mtext(num) == 'a+2' and mtext(den) == 'a−1':
            hits.append((i, num, den))
if len(hits) != 1:
    die('C1 全件 m:f(num=a+2,den=a−1) 命中 %d 处（应为1）' % len(hits))
i1, num1, den1 = hits[0]
if i1 != 305:
    die('C1 命中 el%d（期望 el305；el 号漂移须人工复核）' % i1)
before_C1 = para_text(eS[i1])
tgt = [t for t in den1.iter(M) if (t.text or '') == '1']
if len(tgt) != 1:
    die('C1 分母内 m:t==\'1\' 命中 %d 处（应为1）' % len(tgt))
tgt[0].text = '2'
evidence.append(('C1', S, 'el%d' % i1, before_C1, para_text(eS[i1])))

# ---------- C2 89卷 el91 椭圆性质1 删超纲尾 ----------
TAIL_91 = '其中，当 P 点为左 (右) 焦点时，Q 点位于左 (右) 准线上.（可用极点极线来求）'
p = eD[91]
full = fulltext(p)
if clean(full) != clean('性质 1: 弦 AB 绕着定点 P(m，0) 转动时，则其所对顶点 Q 落在直线 x=a2m 上.') + TAIL_91:
    # 用节点文本原样比对（含数学式线性文本）
    kept91 = full[:len(full) - len(TAIL_91)]
    if not full.endswith(TAIL_91):
        die('C2 el91 文本锚失败：%r' % full)
    kept91 = full[:-len(TAIL_91)]
else:
    kept91 = full[:-len(TAIL_91)]
before_C2 = para_text(p)
shd_before = len(p.findall('.//' + qn('w:shd')))
drw_before = len(p.findall('.//' + qn('w:drawing')))
pbd_before = p.find('.//' + qn('w:pBdr')) is not None
rm = whole_node_split(p, kept91, TAIL_91)
if len(rm) != 21:
    die('C2 el91 待删整节点 %d 个（探针实测21）' % len(rm))
for n in rm:
    n.getparent().remove(n)
if len(p.findall('.//' + qn('w:shd'))) != shd_before or len(p.findall('.//' + qn('w:drawing'))) != drw_before \
        or (p.find('.//' + qn('w:pBdr')) is not None) != pbd_before:
    die('C2 el91 挂点不守恒')
evidence.append(('C2', D, 'el91（整节点删 %d 个）' % len(rm), before_C2, para_text(p)))

# ---------- C3 89卷 el98 双曲线性质1 删超纲尾 ----------
TAIL_98 = '其中，当 P 点为左 (右) 焦点时，Q 点位于左 (右) 准线上.'
p = eD[98]
full = fulltext(p)
if not full.endswith(TAIL_98):
    die('C3 el98 文本锚失败：%r' % full)
kept98 = full[:-len(TAIL_98)]
before_C3 = para_text(p)
shd_before = len(p.findall('.//' + qn('w:shd')))
drw_before = len(p.findall('.//' + qn('w:drawing')))
pbd_before = p.find('.//' + qn('w:pBdr')) is not None
rm = whole_node_split(p, kept98, TAIL_98)
if len(rm) != 20:
    die('C3 el98 待删整节点 %d 个（探针实测20）' % len(rm))
for n in rm:
    n.getparent().remove(n)
if len(p.findall('.//' + qn('w:shd'))) != shd_before or len(p.findall('.//' + qn('w:drawing'))) != drw_before \
        or (p.find('.//' + qn('w:pBdr')) is not None) != pbd_before:
    die('C3 el98 挂点不守恒')
evidence.append(('C3', D, 'el98（整节点删 %d 个）' % len(rm), before_C3, para_text(p)))

# ---------- C4 89卷 el87 编注删同源从句 ----------
OLD = '上，焦点弦情形Q落在准线（关联条目：圆锥曲线的弦与弦长）。'
NEW = '上（关联条目：圆锥曲线的弦与弦长）。'
hits = []
for i, ch in enumerate(eD):
    for t in ch.iter(W):
        if (t.text or '') == OLD:
            hits.append((i, t))
if len(hits) != 1:
    die('C4 全件 w:t==%r 命中 %d 处（应为1）' % (OLD[:12], len(hits)))
i4, t4 = hits[0]
if i4 != 87:
    die('C4 命中 el%d（期望 el87）' % i4)
before_C4 = para_text(eD[i4])
t4.text = NEW
evidence.append(('C4', D, 'el87', before_C4, para_text(eD[i4])))

# ---------- 落盘 ----------
if os.environ.get('DRY'):
    print('DRY RUN：断言全过，未写盘。')
    for op, path, loc, b, a in evidence:
        print('---- %s  %s  %s' % (op, os.path.basename(path), loc))
        print('  前：', b)
        print('  后：', a)
    sys.exit(0)
for path in (S, D):
    backup(path)
dS.save(S)
dD.save(D)
print('已写盘：', S)
print('已写盘：', D)
print()
for op, path, loc, b, a in evidence:
    print('---- %s  %s  %s' % (op, os.path.basename(path), loc))
    print('  前：', b)
    print('  后：', a)
