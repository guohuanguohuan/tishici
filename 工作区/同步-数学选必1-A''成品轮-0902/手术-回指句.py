# -*- coding: utf-8 -*-
"""回指句删除（A''拍板39处：「（详见知识清单N.N.N条目M）」形态段——结构性衔接语废止）"""
import zipfile, os, sys
from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s%(W,t)'.replace('%s%','%s}'%'{')  # placeholder
def q(t): return '{%s}%s' % (W, t)
p = sys.argv[1]
z=zipfile.ZipFile(p); parts={n:z.read(n) for n in z.namelist()}; z.close()
doc=etree.fromstring(parts['word/document.xml']); body=doc.find(q('body'))
def ptext(e): return ''.join(t.text or '' for t in e.iter(q('t')))
removed=[]
for e in list(body):
    if e.tag!=q('p'): continue
    t=ptext(e).strip()
    if t.startswith('（详见知识清单') and t.endswith('）'):
        removed.append(t[:44]); body.remove(e)
print('回指句删除:', len(removed))
for r in removed[:6]: print('  ', r)
parts['word/document.xml']=etree.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True)
tmp=p+'.s3'; zo=zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED)
for nm,b in parts.items(): zo.writestr(nm,b)
zo.close(); os.replace(tmp,p)
