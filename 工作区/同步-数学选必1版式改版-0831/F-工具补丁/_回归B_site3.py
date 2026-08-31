# -*- coding: utf-8 -*-
"""任务B补充回归：标题行内统计段run切分分支（site3——持活补丁第3处add位点）功能验证。
E卷幂等复跑不触发该分支（json实测切分=0，run已在前次执行中拆分）；构造统计段跨界run合成件
首跑触发，验证：切分正确（豁免段无sz、统计段sz=18）＋持活后断言零假失败＋文字零增删。
"""
import os, sys, subprocess, zipfile, json

WS = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(WS))), '工具', '字号双档改版.py')

CT = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'''
RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'''
STYLES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:style w:type="paragraph" w:styleId="Normal"><w:name w:val="Normal"/></w:style></w:styles>'''

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

def p(runs):
    rs = ''.join('<w:r><w:t xml:space="preserve">%s</w:t></w:r>' % t for t in runs)
    return '<w:p>%s</w:p>' % rs

T1 = '2.1 直线的倾斜角与斜率（第1—20题）　本节2'   # 跨界run：统计段起点「本节」在本run内部
T2 = '0题：简单1｜中档12｜难6'
DOC = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
       '<w:document xmlns:w="' + W + '"><w:body>'
       + p(['第2章 平面解析几何'])
       + p([T1, T2])
       + p(['1．（中档·保80%·卡壳看答案）已知直线l过点P(0,1)且方向向量m=(1,1)，求倾斜角。'])
       + p(['【答案】π/4　【知识点】倾斜角与斜率'])
       + p(['【详解】由方向向量得tanα=1，取α∈[0,π)得α=π/4。'])
       + '</w:body></w:document>')

syn = os.path.join(WS, '回归B-site3合成.docx')
out = os.path.join(WS, '回归B-site3输出.docx')
jp = os.path.join(WS, '回归B-site3输出.json')
with zipfile.ZipFile(syn, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', CT)
    z.writestr('_rels/.rels', RELS)
    z.writestr('word/document.xml', DOC)
    z.writestr('word/styles.xml', STYLES)

r = subprocess.run([sys.executable, TOOL, syn, out, '--json', jp],
                   capture_output=True, text=True, encoding='utf-8',
                   env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
print('退出码=%d' % r.returncode)
print(r.stdout.strip())
if r.returncode != 0:
    print(r.stderr[-2000:]); raise SystemExit('site3合成件失败')

from lxml import etree
def q(t): return '{%s}%s' % (W, t)
with zipfile.ZipFile(out) as z:
    doc = etree.fromstring(z.read('word/document.xml'))
paras = doc.find(q('body')).findall(q('p'))
title = paras[1]
runs = [r_ for r_ in title.findall(q('r')) if (r_.find(q('t')) is not None and r_.find(q('t')).text)]
log = json.load(open(jp, encoding='utf-8'))
print('标题行内统计段run切分 =', log['分类计数']['标题行内统计段run切分'])
assert log['分类计数']['标题行内统计段run切分'] == 1, 'site3未触发'
txts = [r_.find(q('t')).text for r_ in runs]
print('切分后标题段run文本:', txts)
assert ''.join(txts) == T1 + T2, '文字流变化'
def sz_of(r_):
    rpr = r_.find(q('rPr'))
    if rpr is None: return None
    s = rpr.find(q('sz'))
    return s.get(q('val')) if s is not None else None
for t, r_ in zip(txts, runs):
    print('  run %r -> sz=%s' % (t[:18], sz_of(r_)))
assert txts[0].endswith('　') and sz_of(runs[0]) is None, '豁免段不应有sz'
assert txts[1] == '本节2' and sz_of(runs[1]) == '18', '统计段前半应置18'
assert txts[2] == T2 and sz_of(runs[2]) == '18', '统计段后半应置18'
print('site3补充回归PASS：切分正确＋豁免段留T4＋断言零假失败＋文字零增删')
