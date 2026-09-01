# -*- coding: utf-8 -*-
"""取B/I1实物run级参数（同构基准）：题号块/括注/【答案】芯片/文字型值/公式型值/解析块浅底段/条目号/第一子层。"""
import io, re, sys, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def qn(t): return '{%s}%s' % (W, t)
def mn(t): return '{%s}%s' % (M, t)

def load(p):
    with zipfile.ZipFile(p) as z:
        return etree.fromstring(z.read('word/document.xml'))

def rpr_sig(r):
    rPr = r.find(qn('rPr'))
    if rPr is None:
        return 'NO_rPr'
    parts = []
    for el in rPr:
        tag = el.tag.split('}')[1]
        attrs = {k.split('}')[1]: v for k, v in el.attrib.items()}
        parts.append(f'{tag}{attrs if attrs else ""}')
    return ' '.join(parts)

def ppr_sig(p):
    pPr = p.find(qn('pPr'))
    if pPr is None:
        return 'NO_pPr'
    parts = []
    for el in pPr:
        tag = el.tag.split('}')[1]
        attrs = {k.split('}')[1]: v for k, v in el.attrib.items()}
        parts.append(f'{tag}{attrs if attrs else ""}')
    return ' '.join(parts)

def ptext(p):
    return ''.join(t.text or '' for t in p.iter(qn('t')))

B = r'C:/提示词/高中数学/高中数学同步/人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'
I1 = r'C:/提示词/高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx'

broot = load(B)
bbody = broot.find(qn('body'))
shown = {'qnum': 0, 'ans': 0, 'ftype': 0, 'shallow': 0}
for p in bbody.findall(qn('p')):
    t = ptext(p)
    if shown['qnum'] < 2 and re.match(r'^\d+\.\d+-\d+．（', t):
        print('== B 题号块段:', t[:44])
        print('   pPr:', ppr_sig(p)[:160])
        for r in p.findall(qn('r'))[:3]:
            txt = ''.join(x.text or '' for x in r.iter(qn('t')))
            if txt:
                print(f'   run«{txt[:14]}»:', rpr_sig(r)[:200])
        shown['qnum'] += 1
    if shown['ans'] < 2 and t.startswith('【答案】'):
        print('== B 【答案】段:', t[:60])
        print('   pPr:', ppr_sig(p)[:160])
        for r in p.findall(qn('r'))[:6]:
            txt = ''.join(x.text or '' for x in r.iter(qn('t')))
            om = 'OMML!' if r.find(mn('oMath')) is not None or r.getparent().find(mn('oMath')) is not None else ''
            if txt or om:
                print(f'   run«{txt[:14]}»{om}:', rpr_sig(r)[:220])
        # 段内oMath检查
        oms = p.findall(mn('oMath')) + [o for o in p.iter(mn('oMath'))]
        print('   oMath数:', len(list(p.iter(mn('oMath')))))
        shown['ans'] += 1
    pPr = p.find(qn('pPr'))
    if shown['shallow'] < 1 and pPr is not None:
        shd = pPr.find(qn('shd'))
        if shd is not None and shd.get(qn('fill')) == 'F2F2F2':
            print('== B 解析浅底段:', t[:50])
            print('   pPr:', ppr_sig(p)[:200])
            shown['shallow'] += 1
    if all(v >= 1 for v in [shown['qnum'] and 1, shown['ans'], shown['shallow']]) and shown['qnum'] >= 2:
        break

# 公式型答案值：段内oMath且【答案】起头，看oMath内m:r的rPr
found = 0
for p in bbody.findall(qn('p')):
    t = ptext(p)
    if t.startswith('【答案】') and len(list(p.iter(mn('oMath')))) > 0 and found < 2:
        print('== B 公式型答案段:', t[:40])
        for om in p.iter(mn('oMath')):
            mrs = om.findall('.//' + mn('r'))
            for r in mrs[:1]:
                rPr = r.find(mn('rPr'))
                wPr = r.find(qn('rPr'))
                print('   m:r rPr(math):', etree.tostring(rPr, encoding='unicode') if rPr is not None else None)
                print('   m:r rPr(word):', etree.tostring(wPr, encoding='unicode') if wPr is not None else None)
            break
        found += 1

iroot = load(I1)
ibody = iroot.find(qn('body'))
c = 0
for p in ibody.findall(qn('p')):
    t = ptext(p)
    if re.match(r'^\d+\.\d+-\d+．', t) and c < 1:
        print('== I1 条目段:', t[:44])
        print('   pPr:', ppr_sig(p)[:160])
        for r in p.findall(qn('r'))[:5]:
            txt = ''.join(x.text or '' for x in r.iter(qn('t')))
            if txt:
                print(f'   run«{txt[:14]}»:', rpr_sig(r)[:200])
        c += 1
    if '（1）' in t and c < 2 and re.search(r'（\d+）', t[:12]):
        pass
# 第一子层段
c2 = 0
for p in ibody.findall(qn('p')):
    t = ptext(p)
    if re.match(r'^（\d+）', t) and c2 < 1:
        print('== I1 第一子层段:', t[:40])
        for r in p.findall(qn('r'))[:4]:
            txt = ''.join(x.text or '' for x in r.iter(qn('t')))
            if txt:
                print(f'   run«{txt[:14]}»:', rpr_sig(r)[:200])
        c2 += 1
