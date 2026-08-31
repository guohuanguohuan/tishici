# -*- coding: utf-8 -*-
# W-I2清单2 步骤4：N7深蓝字——内容标记族run（填空答案/公式标记/需背名词）→#1F4E79
# 条目号/条目第一子层/块标签芯片【×】黑字不变；公式结构（ctrlPr挂C9C9C9者）整结构深蓝
import zipfile, re, sys, time
from lxml import etree
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
M='{http://schemas.openxmlformats.org/officeDocument/2006/math}'
BLUE='1F4E79'
path='I2工作副本.docx'
zin=zipfile.ZipFile(path)
parts={n:zin.read(n) for n in zin.namelist()}
zin.close()
root=etree.fromstring(parts['word/document.xml'])
body=root.find(W+'body')

def set_color(rpr):
    c=rpr.find(W+'color')
    if c is None:
        c=etree.SubElement(rpr,W+'color')
    c.set(W+'val',BLUE); c.set(W+'themeColor','') if False else None
    # remove themeColor attrs to avoid theme override
    for a in (W+'themeColor',W+'themeShade',W+'themeTint'):
        if c.get(a) is not None: del c.attrib[a]

RE_ENTRY=re.compile(r'^\d{1,3}．'); RE_SUB=re.compile(r'^（\d{1,2}）'); RE_CHIP=re.compile(r'^【[^】]{1,12}】')
stats={'文本内容标记':0,'公式结构':0,'公式内m:r':0,'ctrlPr':0}
for p in root.iter(W+'p'):
    for r in p.findall(W+'r'):
        rpr=r.find(W+'rPr')
        if rpr is None: continue
        shd=rpr.find(W+'shd')
        if shd is None or shd.get(W+'fill')!='C9C9C9': continue
        t=''.join(x.text or '' for x in r.findall(W+'t'))
        if RE_ENTRY.match(t) or RE_SUB.match(t) or RE_CHIP.match(t):
            continue  # 黑字不变
        set_color(rpr); stats['文本内容标记']+=1
# 公式结构：ctrlPr 挂 C9C9C9 的结构元素（rad/f/sSup/sSub/d）
for c in list(root.iter(M+'ctrlPr')):
    wrpr=c.find(W+'rPr')
    if wrpr is None: continue
    shd=wrpr.find(W+'shd')
    if shd is None or shd.get(W+'fill')!='C9C9C9': continue
    struct=c.getparent().getparent()  # radPr->rad 等
    set_color(wrpr); stats['ctrlPr']+=1
    stats['公式结构']+=1
    for mr in struct.iter(M+'r'):
        mrpr=mr.find(M+'rPr')
        if mrpr is None:
            mrpr=etree.Element(M+'rPr'); mr.insert(0,mrpr)
        wr=mrpr.find(W+'rPr')
        if wr is None:
            wr=etree.SubElement(mrpr,W+'rPr')
        set_color(wr); stats['公式内m:r']+=1

parts['word/document.xml']=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
tmp=path+'.tmp'
for _ in range(12):
    try:
        with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zo:
            for n,d in parts.items(): zo.writestr(n,d)
        import os; os.replace(tmp,path); break
    except PermissionError: time.sleep(6)
print(stats)
