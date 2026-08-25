# -*- coding: utf-8 -*-
"""assemble_ch1_v3.py — 第1章讲练件精装配（合并版）
恢复题按子主题大类合并成少数题型组（每组一标题+多题），每组第一题紧贴组标题（不悬空）。
大类 -> (组标题, 锚点=62题原题型标题)。题号重编号在装配后单独做。
"""
import json, os, re, copy, io, sys
from docx import Document
from docx.oxml.ns import qn
from docx.opc.part import Part
from docx.opc.packuri import PackURI
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'; M='http://schemas.openxmlformats.org/officeDocument/2006/math'
WC='{'+W+'}'; MC='{'+M+'}'
WORK=r'C:\Users\28120\Desktop\同步-数学选必1整册-0825\第1章\work'
SRC62=r'C:\sync\syncall\ai\ai相关\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何·讲练件（62题）.docx'
OUT=os.path.join(WORK,'讲练件_精配草稿.docx')
def ptext(el):
    return ''.join(t.text or '' for t in el.iter() if t.tag==WC+'t' or t.tag==MC+'t')
_img_seq=[0]
def remap_images(dst_doc,src_doc,el):
    for blip in el.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
        rid=blip.get(qn('r:embed'))
        if rid:
            nr=_to_dst(dst_doc,src_doc,rid)
            if nr: blip.set(qn('r:embed'),nr)
    VML='{urn:schemas-microsoft-com:vml}'
    for imd in el.iter(VML+'imagedata'):
        rid=imd.get(qn('r:id'))
        if rid:
            nr=_to_dst(dst_doc,src_doc,rid)
            if nr: imd.set(qn('r:id'),nr)
def _to_dst(dst_doc,src_doc,rid):
    try: ipart=src_doc.part.related_parts[rid]
    except KeyError: return None
    ct=ipart.content_type
    if 'emf' in ct or 'wmf' in ct:
        _img_seq[0]+=1
        ext='emf' if 'emf' in ct else 'wmf'
        pname='/word/media/fix_%03d.%s'%(_img_seq[0],ext)
        part=Part(PackURI(pname),ct,ipart.blob,dst_doc.part.package)
        dst_doc.part.package.parts.append(part)
        return dst_doc.part.relate_to(part,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image')
    r,_=dst_doc.part.get_or_add_image(io.BytesIO(ipart.blob))
    return r
doc=Document(SRC62); body=doc.element.body
srcs={}
def get_src(p):
    if p not in srcs: srcs[p]=Document(p)
    return srcs[p]
paras=[c for c in body if c.tag==WC+'p']
TMPL_TITLE=None
for p in paras:
    if TMPL_TITLE is None and ptext(p).startswith('1.2.5 空间中的距离：动点最值与运动不变量'):
        TMPL_TITLE=p; break
assert TMPL_TITLE is not None
def make_title_para(text):
    p=TMPL_TITLE.makeelement(WC+'p',{})
    pPr=TMPL_TITLE.find(WC+'pPr')
    if pPr is not None: p.append(copy.deepcopy(pPr))
    r=TMPL_TITLE.find(WC+'r'); nr=copy.deepcopy(r)
    for t in nr.findall(WC+'t'): nr.remove(t)
    nt=nr.makeelement(WC+'t',{}); nt.text=text; nr.append(nt)
    p.append(nr); return p
SEC_TITLE={'1.1.1':'1.1.1 空间向量及其运算','1.1.2':'1.1.2 空间向量基本定理','1.1.3':'1.1.3 空间向量的坐标与空间直角坐标系','1.2.1':'1.2.1 空间中的点、直线与空间向量','1.2.2':'1.2.2 空间中的平面与空间向量','1.2.3':'1.2.3 直线与平面的夹角','1.2.4':'1.2.4 二面角','1.2.5':'1.2.5 空间中的距离'}
# 大类映射：tname前缀 -> (组标题后缀, 锚点文本)
def classify(tname):
    t=tname
    if '外接球' in t or '特殊四面体' in t: return ('外接球模型（重审补充）','1.2.5 空间中的距离：外接球模型（折叠与双外心）')
    if '内切球' in t: return ('内切球与球相切模型（重审补充）','1.2.5 空间中的距离：内切球与球相切模型（等体积法与临界）')
    if '截面' in t: return ('球的截面问题（重审补充）','1.2.5 空间中的距离：球的截面问题（截面圆）')
    if '轨迹' in t: return ('空间动点轨迹（重审补充）','1.2.5 空间中的距离：空间动点轨迹（圆与球）')
    if '翻折' in t: return ('翻折与展开求最短路径（重审补充）','1.2.5 空间中的距离：翻折与展开求最短路径（平面化）')
    if '最值' in t: return ('动点最值与运动不变量（重审补充）','1.2.5 空间中的距离：动点最值与运动不变量')
    if '线面角' in t: return ('求线面角的值（重审补充）','1.2.3 直线与平面的夹角：求线面角的值（向量法与三余弦定理）')
    if '二面角' in t or '叉乘' in t or '空间余弦' in t or '射影' in t or '正方体+异面' in t: return ('二面角的向量求法（重审补充）','1.2.4 二面角：二面角的向量求法（含锐钝判定）')
    return None
def find_anchor(prefix):
    hit=None
    for p in body.iter(WC+'p'):
        if ptext(p).strip().startswith(prefix): hit=p
    return hit
def insert_block(after_el,b):
    sdoc=get_src(b['src']); sch=list(sdoc.element.body.iterchildren())
    last=after_el; n=0; first=None
    for i in range(b['start'],min(b['end']+1,len(sch))):
        el=sch[i]
        if el.tag==WC+'p':
            t=ptext(el).strip()
            if t=='【举一反三】': continue
            if re.match(r'^\d+(\.\d+)+\s*\S',t): continue
            if el.find(WC+'pPr') is not None and el.find(WC+'pPr').find(WC+'sectPr') is not None: continue
        if el.tag==WC+'sectPr': continue
        ne=copy.deepcopy(el); remap_images(doc,sdoc,ne)
        last.addnext(ne); last=ne
        if el.tag==WC+'p' and first is None: first=ne
        n+=1
    return first,last,n
blocks=json.load(open(os.path.join(WORK,'restored_blocks.json'),encoding='utf-8'))
# 逐块分类（1.2.5按tname；非1.2.5按topic单独处理）
from collections import OrderedDict
# 非1.2.5锚点映射（定义在使用前）
SEC_ANCHOR_MAP={
 '1.1.1':('1.1.1 空间向量及其运算：数量积求夹角与投影（非坐标法）','1.1.1 空间向量及其运算：数量积应用（重审补充）'),
 '1.2.1':('1.2.1 空间中的点、直线与空间向量：求异面直线所成角','1.2.1 空间中的点、直线与空间向量：异面直线角（重审补充）'),
 '1.2.2':('1.2.2 空间中的平面与空间向量：多面体截面问题（补全截面）','1.2.2 空间中的平面与空间向量：建系存在性（重审补充）'),
 '1.2.3':('1.2.3 直线与平面的夹角：求线面角的值（向量法与三余弦定理）','1.2.3 直线与平面的夹角：求线面角的值（重审补充）'),
 '1.2.4':('1.2.4 二面角：二面角的向量求法（含锐钝判定）','1.2.4 二面角：二面角的向量求法（重审补充）'),
}
groups=OrderedDict()   # (锚点,组标题) -> [blocks]
others=[]
for b in blocks:
    if b['topic']=='1.2.5':
        cls=classify(b['tname'])
        if cls:
            gtitle,anchor=cls
        else:
            gtitle='空间中的距离（重审补充）'; anchor='1.2.5 空间中的距离：立体几何新定义题'
        groups.setdefault((anchor,gtitle),[]).append(b)
    else:
        others.append(b)
for b in others:
    topic=b['topic']
    if topic in SEC_ANCHOR_MAP:
        anchor,gt=SEC_ANCHOR_MAP[topic]
    else:
        anchor,gt=SEC_TITLE[topic],SEC_TITLE[topic]+'（重审补充）'
    groups.setdefault((anchor,gt),[]).append(b)
inserted=0; ngrp=0
for (anchor,gtitle),blist in groups.items():
    anchor_el=find_anchor(anchor)
    if anchor_el is None:
        print('锚点未找到:',anchor); continue
    last=anchor_el
    gt=make_title_para(gtitle)
    last.addnext(gt); last=gt; ngrp+=1
    for b in blist:
        first,last,n=insert_block(last,b)
        inserted+=n
print('组数:',ngrp,'插入元素数:',inserted)
doc.save(OUT)
print('保存精配草稿→',OUT)
