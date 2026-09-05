# -*- coding: utf-8 -*-
"""②D_R2_06_诊断清单2.py — FX-2 根因定位：T7 清单2 exec 复核断言失败（节2.2.1 dy=66.6 page=1）。
①XML 侧：数插后空段（column br＋1pt 签名）数量与位置（前后邻居文本）。
②COM 侧：枚举全部「标题 3」段 (text[:24], dy, page)——找空文本段／异常 dy 段；同时抽 3 个插后空段的 Style.NameLocal。
只读诊断，不改文件。
"""
import sys, io, os, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
N = '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'
FP = os.path.join(HERE, '副本', N)
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

print('== ① XML 侧 ==', flush=True)
z = zipfile.ZipFile(FP)
doc = etree.fromstring(z.read('word/document.xml'))
styles = etree.fromstring(z.read('word/styles.xml'))
z.close()
body = doc.find(q('body'))
els = list(body)
# 默认段落样式
dt = None
for st in styles.iter(q('style')):
    if st.get(q('type')) == 'paragraph' and st.get(q('default')) == '1':
        nm = st.find(q('name'))
        dt = nm.get(q('val')) if nm is not None else '?'
print('docDefaults 默认段落样式 = %r' % dt)
n_ins = 0
for i, e in enumerate(els):
    if e.tag != q('p'):
        continue
    brs = [b for b in e.iter(q('br')) if b.get(q('type')) == 'column']
    if not brs:
        continue
    ppr = e.find(q('pPr'))
    spc = ppr.find(q('spacing')) if ppr is not None else None
    if spc is not None and spc.get(q('line')) == '20':
        n_ins += 1
        if n_ins <= 3:
            ctx = []
            for j in (i - 1, i, i + 1):
                if 0 <= j < len(els):
                    pj = ppr.find(q('pStyle')) if (j == i and ppr is not None) else None
                    stj = pj.get(q('val')) if pj is not None else ''
                    ctx.append('[%s|%r]' % (els[j].tag.split('}')[1] + (':' + stj if stj else ''), ptext(els[j])[:24]))
            print('  插段#%d idx%d %s' % (n_ins, i, ' '.join(ctx)))
print('插后空段总数 = %d' % n_ins)
# XML 标题清单（前 6 个）
print('XML 标题（前 6）：')
cnt = 0
for e in els:
    if e.tag != q('p'):
        continue
    ppr = e.find(q('pPr'))
    sh = ppr.find(q('shd')) if ppr is not None else None
    t = ptext(e)
    if sh is not None and sh.get(q('fill')) == 'ADC2DA' and t[:1].isdigit():
        cnt += 1
        if cnt <= 6:
            print('  %d %r' % (cnt, t[:30]))
print('XML 标题总数 = %d' % cnt)

print('== ② COM 侧 ==', flush=True)
import win32com.client, pythoncom
pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    d = word.Documents.Open(os.path.abspath(FP), ReadOnly=True, AddToRecentFiles=False)
    try:
        d.Repaginate()
        print('pages = %d' % d.ComputeStatistics(2))
        rows = []
        empty3 = []
        k = 0
        for para in d.Paragraphs:
            k += 1
            try:
                st = para.Range.Style.NameLocal
            except Exception:
                continue
            if st != '标题 3':
                continue
            t = para.Range.Text.strip('\r\x07\x0c').strip()
            y = para.Range.Information(6)
            tm = para.Range.Sections(1).PageSetup.TopMargin
            pg = para.Range.Information(3)
            rows.append((t, round(y - tm, 1), pg))
            if len(rows) <= 26:
                pass
        print('「标题 3」段总数 = %d' % len(rows))
        for t, dy, pg in rows[:26]:
            print('  %r dy=%s page=%s' % (t[:24], dy, pg))
        n_empty = sum(1 for t, dy, pg in rows if not t)
        print('其中空文本段 = %d' % n_empty)
        if n_empty:
            print('  空段 dy/page 前 5：%s' % [(dy, pg) for t, dy, pg in rows if not t][:5])
    finally:
        d.Close(False)
finally:
    word.Quit()
    pythoncom.CoUninitialize()
print('DONE', flush=True)
