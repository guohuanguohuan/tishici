# -*- coding: utf-8 -*-
"""⑧轮债1探针2：括注token全谱／I1-I2-TOC标签在场性／A5回归件改前基线快照（只读）。"""
import sys, io, os, re, zipfile, json, collections
sys.path.insert(0, r'C:/提示词/工具')
from extract_structure import structure   # 先导入——该模块导入时会自重包 stdout（utf-8），此后不得再包
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
WJ = '\u2060'

def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def paras(path):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    return [(i, el, ptext(el)) for i, el in enumerate(list(body)) if el.tag == q('p')]

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
KUO = re.compile(r'^(\d+(?:\.\d+)+-\d+|\d+)．（([^）]{1,20})）')

print('==== 括注token全谱（每件） ====')
for code, fn in FILES.items():
    cnt = collections.Counter()
    for _, _, t in paras(os.path.join(BASE, fn)):
        tn = t.replace(WJ, '')
        m = KUO.match(tn)
        if m:
            cnt[m.group(2)] += 1
    print('%-3s %s' % (code, dict(cnt) if cnt else '{}'))

print()
print('==== I1/I2/TOC 标签在场性（【答案】【难度】归一后计数） ====')
for code in ('I1', 'I2', 'TOC'):
    ps = paras(os.path.join(BASE, FILES[code]))
    n_ans = sum(1 for _, _, t in ps if '【答案】' in t.replace(WJ, ''))
    n_diff = sum(1 for _, _, t in ps if re.search(r'【难度】', t.replace(WJ, '')))
    n_kuo = sum(1 for _, _, t in ps if KUO.match(t.replace(WJ, '')))
    print('%-3s 【答案】%d 【难度】%d 括注形%d' % (code, n_ans, n_diff, n_kuo))

print()
print('==== A5 回归件改前基线（structure() 现状输出快照） ====')
REG = r'C:/提示词/高中物理/高中物理同步/人教版必修3 第10章 静电场中的能量·简单卷（14题）.docx'
print('存在:', os.path.exists(REG))
s = structure(REG)
qs = s['questions']
kinds = collections.Counter(x['kind'] for x in s['items'])
print('questions=%d 题号=%s..%s 连续=%s' % (
    len(qs), qs[0]['no'] if qs else '-', qs[-1]['no'] if qs else '-',
    all(int(qs[k]['no']) == int(qs[k-1]['no']) + 1 for k in range(1, len(qs))) if len(qs) > 1 else '单题'))
print('items kind 计数: %s' % dict(sorted(kinds.items())))
print('diff 计数: %s' % dict(collections.Counter(x['diff'] for x in qs)))
# 回归件题号头形态样本
ps = paras(REG)
for i, el, t in ps[:40]:
    tn = t.replace(WJ, '')
    if re.match(r'^(?:\d+(?:\.\d+)+-\d+|\d+)．', tn):
        print('  题号头样本 [%d] %s' % (i, t.replace(WJ, '')[:50]))
        break
snap = {'questions': [{'no': x['no'], 'diff': x['diff'], 'sec': x['sec'],
                       'start': x['start'], 'end': x['end']} for x in qs],
        'items_kind': dict(sorted(kinds.items())),
        'items_text': [x['text'] for x in s['items']]}
out = r'C:/提示词/工作区/选必1成书修复-0905/②工具/⑧_05_A5回归件_改前基线.json'
json.dump(snap, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('快照落盘:', out)
