# -*- coding: utf-8 -*-
"""assemble_ch1_v2.py — 第1章讲练件精装配：62题底版 + 78恢复块，细分题型组，锚定到62题对应题型组之后
规范：每恢复题一个独立新题型标题（"节号 节标题：细分名"），锚定到其子主题对应的62题原题型标题之后；
组内至多2题（同细分合并），题号重编号。格式对齐复用 assemble2 方法。
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

doc=Document(SRC62)
body=doc.element.body
srcs={}
def get_src(path):
    if path not in srcs: srcs[path]=Document(path)
    return srcs[path]
# 模板段
paras=[c for c in body if c.tag==WC+'p']
TMPL_TITLE=None; TMPL_LABEL=None
for p in paras:
    t=ptext(p)
    if TMPL_TITLE is None and t.startswith('1.2.5 空间中的距离：动点最值与运动不变量'):
        TMPL_TITLE=p
    if TMPL_LABEL is None and t.startswith('【答案】') and '【难度】' in t:
        TMPL_LABEL=p
    if TMPL_TITLE is not None and TMPL_LABEL is not None: break
assert TMPL_TITLE is not None, '标题模板未找到'
def make_title_para(text):
    p=TMPL_TITLE.makeelement(WC+'p',{})
    pPr=TMPL_TITLE.find(WC+'pPr')
    if pPr is not None: p.append(copy.deepcopy(pPr))
    r=TMPL_TITLE.find(WC+'r')
    nr=copy.deepcopy(r)
    for t in nr.findall(WC+'t'): nr.remove(t)
    nt=nr.makeelement(WC+'t',{}); nt.text=text; nr.append(nt)
    p.append(nr); return p

# 节标题文本（用于生成新题型标题前缀）
SEC_TITLE={
 '1.1.1':'1.1.1 空间向量及其运算',
 '1.1.2':'1.1.2 空间向量基本定理',
 '1.1.3':'1.1.3 空间向量的坐标与空间直角坐标系',
 '1.2.1':'1.2.1 空间中的点、直线与空间向量',
 '1.2.2':'1.2.2 空间中的平面与空间向量',
 '1.2.3':'1.2.3 直线与平面的夹角',
 '1.2.4':'1.2.4 二面角',
 '1.2.5':'1.2.5 空间中的距离',
}
# 子主题->锚点（62题现有题型标题），基于tname前缀识别
def subanchor(tname):
    if '外接球' in tname or '特殊四面体' in tname:
        return '1.2.5 空间中的距离：外接球模型（折叠与双外心）'
    if '内切球' in tname:
        return '1.2.5 空间中的距离：内切球与球相切模型（等体积法与临界）'
    if '截面' in tname:
        return '1.2.5 空间中的距离：球的截面问题（截面圆）'
    if '轨迹' in tname:
        return '1.2.5 空间中的距离：空间动点轨迹（圆与球）'
    if '翻折' in tname:
        return '1.2.5 空间中的距离：翻折与展开求最短路径（平面化）'
    if '最值' in tname:
        return '1.2.5 空间中的距离：动点最值与运动不变量'
    return None
# 节级锚点（非1.2.5）
SEC_ANCHOR={
 '1.1.1':'1.1.1 空间向量及其运算：数量积求夹角与投影（非坐标法）',
 '1.2.1':'1.2.1 空间中的点、直线与空间向量：求异面直线所成角',
 '1.2.2':'1.2.2 空间中的平面与空间向量：多面体截面问题（补全截面）',
 '1.2.3':'1.2.3 直线与平面的夹角：求线面角的值（向量法与三余弦定理）',
 '1.2.4':'1.2.4 二面角：二面角的向量求法（含锐钝判定）',
}
def find_anchor(prefix):
    hit=None
    for p in body.iter(WC+'p'):
        if ptext(p).strip().startswith(prefix): hit=p
    return hit
def insert_block(after_el,b):
    sdoc=get_src(b['src'])
    sch=list(sdoc.element.body.iterchildren())
    last=after_el; n=0; first=None
    for i in range(b['start'],min(b['end']+1,len(sch))):
        el=sch[i]
        if el.tag==WC+'p':
            t=ptext(el).strip()
            if t=='【举一反三】': continue
            if re.match(r'^\d+(\.\d+)+\s*\S',t): continue
            if el.find(WC+'pPr') is not None and el.find(WC+'pPr').find(WC+'sectPr') is not None: continue
        if el.tag==WC+'sectPr': continue
        ne=copy.deepcopy(el)
        remap_images(doc,sdoc,ne)
        last.addnext(ne); last=ne
        if el.tag==WC+'p' and first is None: first=ne
        n+=1
    return first,last,n

blocks=json.load(open(os.path.join(WORK,'restored_blocks.json'),encoding='utf-8'))
# 为每块确定：锚点 + 新题型标题
plan=[]
for b in blocks:
    topic=b['topic']; tname=b['tname']
    if topic=='1.2.5':
        anchor=subanchor(tname)
        if anchor is None: anchor=SEC_TITLE['1.2.5']
    else:
        anchor=SEC_ANCHOR.get(topic, SEC_TITLE[topic])
    newtitle='%s：%s'%(SEC_TITLE[topic], tname)
    plan.append((anchor,newtitle,b))
# 处理：同一锚点下，若新标题重复（同tname）则合并；否则每个b插"新标题+题"
# 按锚点分组，组内按tname聚合（同tname合为同组，组内多题）
from collections import OrderedDict
order=OrderedDict()
for anchor,newtitle,b in plan:
    order.setdefault(anchor,[]).append((newtitle,b))
inserted=0; newq=0
for anchor,items in order.items():
    anchor_el=find_anchor(anchor)
    if anchor_el is None:
        print('锚点未找到:',anchor); continue
    # 组内按新标题聚合（同tname连续）
    sub=OrderedDict()
    for newtitle,b in items:
        sub.setdefault(newtitle,[]).append(b)
    last=anchor_el
    for newtitle,blist in sub.items():
        gt=make_title_para(newtitle)
        last.addnext(gt); last=gt
        newq+=1
        for b in blist:
            first,last,n=insert_block(last,b)
            inserted+=n
print('插入元素数:',inserted,'新题型组数:',newq)
doc.save(OUT)
print('保存精配草稿→',OUT)
