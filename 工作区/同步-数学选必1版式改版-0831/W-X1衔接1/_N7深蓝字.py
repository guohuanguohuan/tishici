# -*- coding: utf-8 -*-
# N7深蓝字：内容标记run（答案值/需背/挖空答案，w:r与oMath内）文字色→#1F4E79
# 黑字不变：块标签【×】、题号块N．、条目号N．、条目第一子层（N）（全角括号）
import zipfile, tempfile, os, re, time, sys
from lxml import etree
WNS='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
MNS='http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s'%(WNS,t)
def m(t): return '{%s}%s'%(MNS,t)
p = sys.argv[1]
BLUE='1F4E79'
z = zipfile.ZipFile(p); doc = etree.fromstring(z.read('word/document.xml')); z.close()
body = doc.find(q('body'))

def keep_black(rt):
    rt2 = rt.strip()
    if not rt2: return True  # 空run不动
    if rt2.startswith('【') : return True          # 块标签芯片
    if re.fullmatch(r'\d+[．.、]?', rt2): return True  # 题号块/条目号 N．
    if re.fullmatch(r'[（(]\d+[）)]', rt2) and rt2.startswith('（'): return True  # 全角（N）第一子层
    return False

def set_blue(rpr):
    col = rpr.find(q('color'))
    if col is None:
        col = etree.SubElement(rpr, q('color'))
    col.set(q('val'), BLUE)
    for a in (q('themeColor'), q('themeTint'), q('themeShade')):
        if col.get(a) is not None: del col.attrib[a]

c_w = c_m = c_ctrl = c_skip = 0
pi = 0
for para in body.iter(q('p')):
    pi += 1
    for r in para.iter(q('r')):
        rpr = r.find(q('rPr'))
        if rpr is None: continue
        shd = rpr.find(q('shd'))
        if shd is None or shd.get(q('fill'))!='C9C9C9': continue
        rt = ''.join(t.text or '' for t in r.iter(q('t')))
        if keep_black(rt):
            c_skip += 1; continue
        set_blue(rpr)
        c_w += 1

for om in body.iter(m('oMath')):
    for rpr in om.iter(q('rPr')):
        shd = rpr.find(q('shd'))
        if shd is None or shd.get(q('fill'))!='C9C9C9': continue
        parent = rpr.getparent()
        is_ctrl = parent.tag == m('ctrlPr')
        set_blue(rpr)
        if is_ctrl: c_ctrl += 1
        else: c_m += 1

new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
fd,tmp = tempfile.mkstemp(suffix='.docx', dir=os.path.dirname(os.path.abspath(p))); os.close(fd)
with zipfile.ZipFile(p) as zin, zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zout:
    for it in zin.infolist():
        zout.writestr(it, new_xml if it.filename=='word/document.xml' else zin.read(it.filename))
for k in range(10):
    try: os.replace(tmp,p); break
    except PermissionError: time.sleep(5)
print('N7完成：w:r文字run染色 %d｜oMath m:r染色 %d｜ctrlPr染色 %d｜黑字保留 %d' % (c_w,c_m,c_ctrl,c_skip))
