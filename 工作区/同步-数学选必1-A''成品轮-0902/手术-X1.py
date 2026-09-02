# -*- coding: utf-8 -*-
"""X1内容手术：课标对照表×2删除（任务C元描述块回扫）＋图例行核对（X1无图例行——衔接件）"""
import zipfile, os
from lxml import etree
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
import sys as _s; p = _s.argv[1] if len(_s.argv)>1 else 'wip/X1.docx'
z = zipfile.ZipFile(p); parts = {n: z.read(n) for n in z.namelist()}; z.close()
doc = etree.fromstring(parts['word/document.xml'])
body = doc.find(q('body'))
removed = 0
for tbl in list(body.findall(q('tbl'))):
    txt = ''.join(t.text or '' for t in tbl.iter(q('t')))
    if '初中要求' in txt or '高中要求' in txt:
        # 相邻空段清一段
        nxt = tbl.getnext()
        body.remove(tbl)
        removed += 1
        if nxt is not None and nxt.tag == q('p') and not ''.join(t.text or '' for t in nxt.iter(q('t'))).strip():
            body.remove(nxt)
print('课标表删除:', removed)
assert removed >= 1, '课标表至少1张，实删%d' % removed
parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
tmp = p + '.s1'
zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
for nm, b in parts.items(): zo.writestr(nm, b)
zo.close(); os.replace(tmp, p)
print('X1 surgery OK')
