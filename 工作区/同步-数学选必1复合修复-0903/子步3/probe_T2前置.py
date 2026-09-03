# -*- coding: utf-8 -*-
"""子步3 T2前置探测：条目块样式/编号/图引用/rels 细节（只读）"""
import sys, io, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
def q(t): return '{%s}%s' % (W, t)
def qr(t): return '{%s}%s' % (R, t)
def qa(t): return '{%s}%s' % (A, t)
def tag(e): return etree.QName(e).localname
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))

BASE = r'C:\提示词\高中数学\高中数学同步'
F = {
    'I1': BASE + r'\人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    'I2': BASE + r'\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    'B': BASE + r'\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
}
ENT_RE = re.compile(r'^(\d+(?:\.\d+)*)-(\d+)．')

for code in ('I1', 'I2'):
    z = zipfile.ZipFile(F[code])
    root = etree.fromstring(z.read('word/document.xml'))
    body = root.find(q('body'))
    pstyles, numprs, embeds, links, docprs = set(), set(), [], [], []
    in_entry = False
    for el in body:
        if tag(el) == 'p':
            t = ptext(el)
            if t.strip():
                if ENT_RE.match(t):
                    in_entry = True
                else:
                    ppr = el.find(q('pPr'))
                    st = ppr.find(q('pStyle')) if ppr is not None else None
                    shd = ppr.find(q('shd')) if ppr is not None else None
                    fill = shd.get(q('fill')) if shd is not None else None
                    sv = st.get(q('val')) if st is not None else None
                    if sv == 'JieMingMao' or fill == 'ADC2DA':
                        in_entry = False
            if not in_entry:
                continue
            ppr = el.find(q('pPr'))
            if ppr is not None:
                st = ppr.find(q('pStyle'))
                if st is not None: pstyles.add(st.get(q('val')))
                np = ppr.find(q('numPr'))
                if np is not None:
                    ilvl = np.find(q('ilvl')); nid = np.find(q('numId'))
                    numprs.add((ilvl.get(q('val')) if ilvl is not None else None,
                                nid.get(q('val')) if nid is not None else None))
        elif tag(el) == 'tbl' and in_entry:
            pass
        if in_entry:
            for b in el.iter(qa('blip')):
                e = b.get(qr('embed')); l = b.get(qr('link'))
                if e: embeds.append(e)
                if l: links.append(l)
            for d in el.iter('{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr'):
                docprs.append(d.get('id'))
    print(f'== {code} == 条目区 pStyle={sorted(pstyles)} numPr={sorted(numprs)}')
    print(f'   图 embed rIds={len(embeds)} link={len(links)} docPr数={len(docprs)} 样本id={docprs[:5]}')
    rels = etree.fromstring(z.read('word/_rels/document.xml.rels'))
    rmap = {}
    for rel in rels:
        rmap[rel.get('Id')] = (rel.get('Type').rsplit('/', 1)[-1], rel.get('Target'))
    imgtypes = {}
    for rid in embeds:
        if rid in rmap:
            t, tg = rmap[rid]
            imgtypes[(t, tg.rsplit('.', 1)[-1])] = imgtypes.get((t, tg.rsplit('.', 1)[-1]), 0) + 1
    print(f'   引用图类型: {imgtypes}')
    # styles.xml 中条目区引用样式是否定义
    sz = etree.fromstring(z.read('word/styles.xml'))
    defined = {s.get(q('styleId')) for s in sz.findall(q('style'))}
    print(f'   缺失样式: {[s for s in pstyles if s not in defined]}')
    # 媒体清单
    media = [n for n in z.namelist() if n.startswith('word/media/')]
    print(f'   media文件数={len(media)} 扩展名={sorted(set(n.rsplit(".",1)[-1].lower() for n in media))}')

# B 讲练件：题型标题段 XML 样本（克隆模板用）
z = zipfile.ZipFile(F['B'])
root = etree.fromstring(z.read('word/document.xml'))
body = root.find(q('body'))
for el in body:
    if tag(el) == 'p' and ptext(el).startswith('1.1.1.1 空间向量及其运算：'):
        print('== B 题型标题段 XML ==')
        print(etree.tostring(el, pretty_print=True, encoding='unicode')[:2200])
        break
# B 的 rels 与 media 基线
rels = etree.fromstring(z.read('word/_rels/document.xml.rels'))
rids = [rel.get('Id') for rel in rels]
nums = sorted(int(r[3:]) for r in rids if r.startswith('rId') and r[3:].isdigit())
print(f'== B == rels数={len(rids)} 最大rId号={nums[-1] if nums else None}')
media = [n for n in z.namelist() if n.startswith('word/media/')]
print(f'   media文件数={len(media)} 扩展名={sorted(set(n.rsplit(".",1)[-1].lower() for n in media))}')
docprs = [d.get('id') for d in root.iter('{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr')]
print(f'   docPr最大id={max(int(i) for i in docprs if i and i.isdigit())}')
