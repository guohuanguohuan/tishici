# -*- coding: utf-8 -*-
# W-I2清单2 步骤5+6：N16图例行（固定句9pt）＋N14章知识结构图8张插入开头；
# 2张源思维导图位图按差图处置替换（删图段+删media+删rels），登记见 报告.md
import zipfile, re, time, os
from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WP='http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
PIC='http://schemas.openxmlformats.org/drawingml/2006/picture'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PR='http://schemas.openxmlformats.org/package/2006/relationships'
def w(t): return '{%s}%s'%(W,t)
path='I2工作副本.docx'
T5=r'C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\T5图件生成\结构图I2'
LEGEND='〔基〕＝基础必会：必须学完本条目，才能做本章题目｜〔进〕＝进阶汇总：本章各题型常识/结论的汇总，方便复习，必须先做题再回看'
diagrams=[
 ('章知识结构图_第01组_2-1.png', 8.39, 2.36),
 ('章知识结构图_第02组_2-2.png',16.56,20.72),
 ('章知识结构图_第03组_2-3.png',16.20, 9.25),
 ('章知识结构图_第04组_2-4.png', 9.14, 3.51),
 ('章知识结构图_第05组_2-5.png',16.56, 7.91),
 ('章知识结构图_第06组_2-6.png',16.93, 9.71),
 ('章知识结构图_第07组_2-7.png',16.93, 9.21),
 ('章知识结构图_第08组_2-8.png',11.73,16.40),
]
zin=zipfile.ZipFile(path)
parts={n:zin.read(n) for n in zin.namelist()}
zin.close()

# --- 1. media & rels ---
media_new={}
existing_nums=[int(m.group(1)) for n in parts if (m:=re.match(r'word/media/image(\d+)\.png$',n))]
next_num=max(existing_nums)+1
rels=etree.fromstring(parts['word/_rels/document.xml.rels'])
max_rid=max(int(x.get('Id')[3:]) for x in rels)
rid_map={}
for i,(fn,_,_) in enumerate(diagrams):
    num=next_num+i
    tgt=f'media/image{num}.png'
    parts[f'word/{tgt}']=open(os.path.join(T5,fn),'rb').read()
    rid=f'rId{max_rid+1+i}'
    rel=etree.SubElement(rels,'{%s}Relationship'%PR)
    rel.set('Id',rid); rel.set('Type','http://schemas.openxmlformats.org/officeDocument/2006/relationships/image')
    rel.set('Target',tgt)
    rid_map[fn]=rid
# 删除源思维导图 rels（rId8/rId9）
for rid in ('rId8','rId9'):
    for rel in list(rels):
        if rel.get('Id')==rid: rels.remove(rel)
parts.pop('word/media/image1.png',None); parts.pop('word/media/image2.png',None)
parts['word/_rels/document.xml.rels']=etree.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)

# --- 2. document.xml ---
root=etree.fromstring(parts['word/document.xml'])
body=root.find(w('body'))
els=list(body)
title=els[0]
assert '人教B版选必1 第2章 平面解析几何·知识清单（完成）' in ''.join(t.text or '' for t in title.iter(w('t')))
# 差图处置：删除元素1、2（两张源思维导图段）
removed=[]
for idx in (1,2):
    p=els[idx]
    blip=p.find('.//{%s}blip'%A)
    rid=blip.get('{%s}embed'%R) if blip is not None else '?'
    removed.append((idx,rid))
    body.remove(p)
# 图例行
leg=etree.fromstring(f'''<w:p xmlns:w="{W}"><w:pPr><w:spacing w:before="0" w:after="0" w:line="280" w:lineRule="atLeast"/><w:jc w:val="left"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体" w:cs="Times New Roman"/><w:color w:val="000000"/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr><w:t xml:space="preserve">{LEGEND}</w:t></w:r></w:p>''')
title.addnext(leg)
anchor=leg
# 8张结构图（独立成段）
img_tmpl='''<w:p xmlns:w="{W}" xmlns:wp="{WP}" xmlns:a="{A}" xmlns:pic="{PIC}" xmlns:r="{R}"><w:pPr><w:spacing w:before="0" w:after="0" w:line="410" w:lineRule="atLeast"/><w:jc w:val="left"/></w:pPr><w:r><w:rPr><w:noProof/></w:rPr><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{CX}" cy="{CY}"/><wp:effectExtent l="0" t="0" r="0" b="0"/><wp:docPr id="{DID}" name="章知识结构图{IDX}"/><wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="{DID}" name="章知识结构图{IDX}"/><pic:cNvPicPr><a:picLocks noChangeAspect="1"/></pic:cNvPicPr></pic:nvPicPr><pic:blipFill><a:blip r:embed="{RID}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{CX}" cy="{CY}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'''
for i,(fn,cmw,cmh) in enumerate(diagrams):
    p=etree.fromstring(img_tmpl.format(W=W,WP=WP,A=A,PIC=PIC,R=R,CX=int(cmw*360000),CY=int(cmh*360000),DID=900001+i,IDX=i+1,RID=rid_map[fn]))
    anchor.addnext(p); anchor=p
parts['word/document.xml']=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)

tmp=path+'.tmp'
for _ in range(12):
    try:
        with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zo:
            for n,d in parts.items(): zo.writestr(n,d)
        os.replace(tmp,path); break
    except PermissionError: time.sleep(6)
print('removed mindmap paras:',removed)
print('new rIds:',rid_map)
print('OK')
