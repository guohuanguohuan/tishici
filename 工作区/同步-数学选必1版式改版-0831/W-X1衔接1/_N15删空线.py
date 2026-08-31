# -*- coding: utf-8 -*-
# N15挖空双标记清理：删「＿＿」空线（其后紧邻灰底答案＝答案嵌原位合法形态）
# 仅删「＿＿」字符本身；run若仅剩空白则删run；文字零其他增删。
import zipfile, tempfile, os, time, sys
from lxml import etree
WNS='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s'%(WNS,t)
p = sys.argv[1]
z = zipfile.ZipFile(p); doc = etree.fromstring(z.read('word/document.xml')); z.close()
body = doc.find(q('body'))

removed = 0
runs_dropped = 0
reg = []
pi=0
for para in body.iter(q('p')):
    pi+=1
    for r in list(para.iter(q('r'))):
        for t in r.findall(q('t')):
            txt = t.text or ''
            if '＿＿' not in txt: continue
            n = txt.count('＿＿')
            new = txt.replace('＿＿','')
            t.text = new
            removed += n
            reg.append((pi, txt[:20]))
            # 若run文本变空且无其他内容（无drawing等），删除该run
            if not new.strip() and r.find(q('drawing')) is None and r.find(q('br')) is None:
                r.getparent().remove(r); runs_dropped+=1
            elif not new:
                t.text=''
            # xml:space preserve
            t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')

new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
fd,tmp = tempfile.mkstemp(suffix='.docx', dir=os.path.dirname(os.path.abspath(p))); os.close(fd)
with zipfile.ZipFile(p) as zin, zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zout:
    for it in zin.infolist():
        zout.writestr(it, new_xml if it.filename=='word/document.xml' else zin.read(it.filename))
for k in range(10):
    try: os.replace(tmp,p); break
    except PermissionError: time.sleep(5)
print('N15完成：删＿＿空线 %d 处（涉及run删除 %d 个）' % (removed, runs_dropped))
for x in reg: print('  para',x[0],repr(x[1]))
