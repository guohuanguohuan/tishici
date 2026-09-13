# -*- coding: utf-8 -*-
"""轮1.5源修正0913 手术脚本（M3轮1.5·素材层成品带病五件，docx侧四件）

四op，逐op锚点断言——错锚即中止不写盘：
  A1 成品卷②(90题) 2.4.2.6-10【详解】中间步 m:f 分母 a−1 → a−2（q26）
  A2 成品卷②(90题) 2.4.2.4-6【温馨提醒】悬空引导句整段删（同源W2出清残留）
  B1 大招2源docx   举一反三2【详解】el66 b²=√(a²−c²)=√3 → b²=a²−c²=3（两个m:rad脱壳，q10）
  B2 大招2源docx   题13【详解】el285 |AB|=4√2 → |AB|=2√2（m:t '4'→'2'，q25）
"""
import sys, shutil, os
sys.path.insert(0, '工具')
from docx import Document
from dxml import qn
from dump_docx import para_text
from lxml import etree

W, M = qn('w:t'), qn('m:t')
BAK = '.bak_轮15源修正0913'
A = '高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'
S = '高中数学/参考/组卷网/高中数学解题大招（二级结论）荟萃/04_原始资料/模块8解析几何/模块8大招2动点问题处理策略（解题大招）.docx'


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
        print('备份已存在，跳过：', dst)
        return dst
    shutil.copy2(path, dst)
    print('备份：', dst, os.path.getsize(dst), 'bytes')
    return dst


def body(doc):
    return list(doc.element.body)


# ---------- 读入 ----------
dA, dS = Document(A), Document(S)
eA, eS = body(dA), body(dS)
evidence = []

# ---------- A1 成品卷② q26 分母 a−1 → a−2 ----------
hits = []
for i, ch in enumerate(eA):
    for f in ch.iter(qn('m:f')):
        num = f.find(qn('m:num'))
        den = f.find(qn('m:den'))
        if num is None or den is None:
            continue
        if mtext(num) == 'a+2' and mtext(den) == 'a−1':
            hits.append((i, num, den))
if len(hits) != 1:
    die('A1 全件 m:f(num=a+2,den=a−1) 命中 %d 处（应为1）' % len(hits))
i1, num1, den1 = hits[0]
before_A1 = para_text(eA[i1])
tgt = [t for t in den1.iter(M) if (t.text or '') == '1']
if len(tgt) != 1:
    die('A1 分母内 m:t==\'1\' 命中 %d 处（应为1）' % len(tgt))
tgt[0].text = '2'
evidence.append(('A1', A, 'el%d' % i1, before_A1, para_text(eA[i1])))

# ---------- A2 成品卷② 悬空【温馨提醒】引导句整段删 ----------
want = '【温馨提醒】利用定义法求动点轨迹的常见情形有：'
hits = [(i, ch) for i, ch in enumerate(eA) if clean(fulltext(ch)) == want]
if len(hits) != 1:
    die('A2 悬空引导句段命中 %d 处（应为1）' % len(hits))
i2, p2 = hits[0]
prev_txt = clean(fulltext(eA[i2 - 1]))[:36]
next_txt = clean(fulltext(eA[i2 + 1]))[:36]
if not prev_txt.startswith('【题后反思】') or not next_txt.startswith('2.4.2.4-7'):
    die('A2 邻段核验失败：prev=%r next=%r' % (prev_txt, next_txt))
p2.getparent().remove(p2)
evidence.append(('A2', A, 'el%d' % i2, want + '（段；前后邻段＝%s …/%s …）' % (prev_txt, next_txt),
                 '（段落已删除，元素数 %d→%d）' % (len(eA), len(body(dA)))))

# ---------- B1 大招2源 q10 脱根号 ----------
i3 = 66
p3 = eS[i3]
if '，可得' not in clean(fulltext(p3)) or not clean(fulltext(p3)).startswith('且a=2,c=1'):
    die('B1 el66 文本锚失败：%r' % clean(fulltext(p3))[:60])
rads = list(p3.iter(qn('m:rad')))
btxt = mtext(rads[0]) if rads else ''
if len(rads) != 2 or mtext(rads[0]) != 'a2−c2' or mtext(rads[1]) != '3':
    die('B1 el66 m:rad 命中 %d 个或内容不符（期望 a2−c2 / 3）' % len(rads))
before_B1 = para_text(p3)
for r in rads:
    e = r.find(qn('m:e'))
    parent = r.getparent()
    pos = parent.index(r)
    for child in list(e):
        e.remove(child)
        parent.insert(pos, child)
        pos += 1
    parent.remove(r)
evidence.append(('B1', S, 'el66', before_B1, para_text(p3)))

# ---------- B2 大招2源 q25 |AB|=4√2 → 2√2 ----------
i4 = 285
p4 = eS[i4]
if not clean(fulltext(p4)).startswith('则由AB=42得'):
    die('B2 el285 文本锚失败：%r' % clean(fulltext(p4))[:60])
cand = []
for om in p4.iter(qn('m:oMath')):
    kids = list(om)
    for k, node in enumerate(kids):
        if node.tag != qn('m:r'):
            continue
        if mtext(node) != '4':
            continue
        if k + 1 < len(kids) and kids[k + 1].tag == qn('m:rad') and mtext(kids[k + 1]) == '2':
            cand.append((om, node.find(M)))
if len(cand) != 1:
    die('B2 el285「m:r(4)＋紧随m:rad(2)」命中 %d 处（应为1）' % len(cand))
before_B2 = para_text(p4)
cand[0][1].text = '2'
evidence.append(('B2', S, 'el285', before_B2, para_text(p4)))

# ---------- 落盘 ----------
if os.environ.get('DRY'):
    print('DRY RUN：断言全过，未写盘。')
    for op, path, loc, before, after in evidence:
        print('---- %s  %s  %s' % (op, os.path.basename(path), loc))
        print('  前：', before)
        print('  后：', after)
    sys.exit(0)
for path in (A, S):
    backup(path)
dA.save(A)
dS.save(S)
print('已写盘：', A)
print('已写盘：', S)
print()
for op, path, loc, before, after in evidence:
    print('---- %s  %s  %s' % (op, os.path.basename(path), loc))
    print('  前：', before)
    print('  后：', after)
