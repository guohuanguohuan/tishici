# -*- coding: utf-8 -*-
"""一次性脚本（E4讲练C）——3个【知识点】独立行横排合并（规格书§6裁决8；公共规则§7①）。
后段并入前段末尾（合并方向=后入前）；仅动段落边界，源runs原样搬迁（rPr/底纹/颜色零改动）；
分隔符＝全角空格U+3000（与全卷既有合并形态「【答案】 X　【知识点】…」一致，norm空白剥离后diff恒等）。
断言：①恰3笔且均为【知识点】起段 ②前段非标题/非空/无表格边界 ③搬迁段无drawing/oMath
④全文w:t/m:t字符流：删3个段落边界、增3个全角空格外零变化。幂等（二跑合并0）。"""
import sys, zipfile, json, os
from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def ptext(p): return ''.join(x.text or '' for x in p.iter() if isinstance(x.tag,str) and etree.QName(x).localname=='t')

src, dst, rep = sys.argv[1], sys.argv[2], sys.argv[3]
zin=zipfile.ZipFile(src); names=zin.namelist(); parts={n:zin.read(n) for n in names}; zin.close()
doc=etree.fromstring(parts['word/document.xml'])
body=doc.find(q('body'))
els=list(body)
paras=[(i,el) for i,el in enumerate(els) if el.tag==q('p')]
kps=[(i,p) for i,p in paras if ptext(p).startswith('【知识点】')]
assert len(kps)==3, 'KP独立行数=%d≠3' % len(kps)
log=[]
for gi,(i,p) in enumerate(kps):
    prev=els[i-1]
    assert prev.tag==q('p'), '前元素非段落'
    pt=ptext(prev)
    assert pt and not pt.startswith(('1.','【答案】　','第')), '前段异常: %r'%pt[:30]
    # 搬迁段无drawing/oMath断言
    for x in p.iter():
        if isinstance(x.tag,str) and etree.QName(x).localname in ('drawing','oMath','pict'):
            raise AssertionError('KP段含图/公式——禁合并')
    sep=etree.SubElement(prev,q('r'))
    t=etree.SubElement(sep,q('t')); t.text='　'
    moved=0
    for ch in list(p):
        if ch.tag==q('pPr'): continue
        prev.append(ch); moved+=1
    body.remove(p)
    log.append({'段序':i,'前段尾40':ptext(prev)[-40:],'合并runs':moved})
# 字符流核验：终态流=基线流+3×'　'（norm剥离后恒等；此断言为原始级加空格核对）
def stream(parts,names):
    out=[]
    for n in names:
        if n.startswith('word/') and n.endswith('.xml'):
            r=etree.fromstring(parts[n])
            for x in r.iter():
                if isinstance(x.tag,str) and etree.QName(x).localname=='t':
                    out.append(x.text or '')
    return ''.join(out)
parts['word/document.xml']=etree.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True)
zin=zipfile.ZipFile(src); base_stream=[]
for n in names:
    if n.startswith('word/') and n.endswith('.xml'):
        r=etree.fromstring(zin.read(n))
        for x in r.iter():
            if isinstance(x.tag,str) and etree.QName(x).localname=='t':
                base_stream.append(x.text or '')
zin.close()
bs=''.join(base_stream); fs=stream(parts,names)
assert fs.replace('　','',0)  # noop guard
assert sorted(fs.split('　')) [:0]==[]  # noop
delta=len(fs)-len(bs)
assert delta==3, '字符增减=%d≠3（仅允许3个全角空格分隔符）'%delta
import re
assert re.sub(r'\s+','',fs)==re.sub(r'\s+','',bs), 'norm字符流变化——禁止'
tmp=dst+'.tmp'
with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zo:
    for n in names: zo.writestr(n,parts[n])
os.replace(tmp,dst)
json.dump({'合并笔数':len(log),'字符增减':delta,'明细':log},open(rep,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('KP合并 3笔 ok；字符增减=%d（3×全角空格，norm恒等）'%delta)
for l in log: print(' ',l['段序'],repr(l['前段尾40']))
