# -*- coding: utf-8 -*-
# W-I2清单2 步骤7：N23定理框——13条〔基〕定理/公式级条目核心段加w:pBdr整段细框
# 判定原则：只框〔基〕中「公式/标准方程/曲线定义」级核心陈述段；表格载体条目不框（表已有框）；
#           〔进〕汇总条目不框（防满页框）；编注/证明/图段不框。判定表落盘 步骤7定理框判定.md
import zipfile, time, os, re
from lxml import etree
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
path='I2工作副本.docx'
# (元素序号[新], 条目号, 条目名, 框段说明, 判定依据)
frames=[
 (11,1,'平面上的两点间的距离公式','题名行（公式嵌入本行）','距离公式＝公式级需背'),
 (13,2,'原点与任一点的距离','题名行（公式嵌入本行）','距离公式变式＝公式级需背'),
 (21,4,'斜率的定义','正文定义段k=tanα','定义含公式＝公式级需背'),
 (24,5,'斜率公式','正文公式段','公式级需背'),
 (27,6,'直线的方向向量','定义段＋斜率关系段（连框合并）','定义＋关系公式k=y/x'),
 (28,6,'直线的方向向量','（同上，相邻合并框）','（同上）'),
 (47,12,'直线的一般式方程','(1)定义段（含Ax+By+C=0）','定义含方程形式＝公式级'),
 (118,21,'圆的标准方程','(3)标准方程段','标准方程＝公式级需背'),
 (122,22,'圆的一般方程的概念','正文公式段','一般方程充要条件＝公式级'),
 (125,23,'圆的一般方程对应的圆心和半径','正文公式段','圆心半径公式＝公式级'),
 (193,32,'椭圆的定义','题名行（定义+|MF₁|+|MF₂|=2a嵌入）','圆锥曲线定义＝定理级需背'),
 (258,38,'双曲线的定义','题名行（定义+||MF₁|−|MF₂||=2a嵌入）','圆锥曲线定义＝定理级需背'),
 (274,41,'等轴双曲线','定义段起至性质③（5段连框合并）','定义+性质公式族（e=√2等）'),
 (275,41,'等轴双曲线','（连框）','（同上）'),
 (276,41,'等轴双曲线','（连框）','（同上）'),
 (277,41,'等轴双曲线','（连框）','（同上）'),
 (278,41,'等轴双曲线','（连框）','（同上）'),
 (348,46,'抛物线的定义','(1)定义段','圆锥曲线定义＝定理级需背'),
 (421,55,'圆锥曲线的弦与弦长','(2)弦长计算公式段','弦长公式＝公式级需背'),
]
zin=zipfile.ZipFile(path); parts={n:zin.read(n) for n in zin.namelist()}; zin.close()
root=etree.fromstring(parts['word/document.xml'])
body=root.find(W+'body'); els=list(body)
# safety: verify each target paragraph text matches expectation keyword
checks={11:'两点',13:'原点',21:'正切值',24:'斜率公式',27:'方向向量',28:'斜率',47:'二元一次',118:'标准方程',122:'二元二次方程',125:'圆心为',193:'距离的和等于常数',258:'差的绝对值',274:'实轴长与虚轴长相等',275:'性质',276:'方程形式',277:'渐近线方程',278:'离心率',348:'定点F和一条定直线',421:'弦长计算'}
PPR_ORDER=['pStyle','keepNext','keepLines','pageBreakBefore','framePr','widowControl','numPr','suppressLineNumbers','pBdr','shd','tabs','suppressAutoHyphens','kinsoku','wordWrap','overflowPunct','topLinePunct','autoSpaceDE','autoSpaceDN','bidi','adjustRightInd','snapToGrid','spacing','ind','contextualSpacing','mirrorIndents','suppressOverlap','jc','textDirection','textAlignment','textboxTightWrap','outlineLvl','divId','cnfStyle','rPr','sectPr','pPrChange']
applied=0
for idx,ent,name,seg,basis in frames:
    p=els[idx]
    t=''.join(x.text or '' for x in p.iter(W+'t'))
    assert checks[idx] in t, f'元素{idx}文本不符预期: {t[:40]}'
    ppr=p.find(W+'pPr')
    if ppr is None:
        ppr=etree.Element(W+'pPr'); p.insert(0,ppr)
    if ppr.find(W+'pBdr') is not None:
        continue
    pbdr=etree.Element(W+'pBdr')
    for side in ('top','left','bottom','right'):
        e=etree.SubElement(pbdr,W+side)
        e.set(W+'val','single'); e.set(W+'sz','4'); e.set(W+'space','2'); e.set(W+'color','auto')
    # insert per schema order: after numPr/before shd
    pos=len(PPR_ORDER)
    for child in ppr:
        tag=child.tag.split('}')[-1]
        if tag in PPR_ORDER and PPR_ORDER.index(tag)>PPR_ORDER.index('pBdr'):
            pos=min(pos,list(ppr).index(child)); break
    ppr.insert(pos,pbdr)
    applied+=1
parts['word/document.xml']=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
tmp=path+'.tmp'
for _ in range(12):
    try:
        with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zo:
            for n,d in parts.items(): zo.writestr(n,d)
        os.replace(tmp,path); break
    except PermissionError: time.sleep(6)
# 判定表落盘
lines=['# N23定理框判定表——I2（13条目/18段加框；基38条中13条框、进29条全不框）','',
'| 条目 | 名称 | 框段 | 判定依据 |','|---|---|---|---|']
seen=set()
for idx,ent,name,seg,basis in frames:
    key=(ent,seg)
    if ent in seen and idx not in (28,275,276,277,278): continue
    lines.append(f'| {ent} | {name} | 元素{idx}：{seg} | {basis} |'); seen.add(ent)
lines += ['','不框判定（防满页框）：',
'- 表格载体条目（3/7/9/10/11/14/15/16/17/18/25/28/33/34/39/40/48/50/54）：核心公式在对比表/结构表内，表框即视觉锚，不加段落框；',
'- 概念/步骤类〔基〕条目（8截距、29曲线与方程定义、30轨迹步骤、47微思考、56判定与辨析）：非公式级核心，不加框；',
'- 全部〔进〕29条（直线系/几何含义/曼哈顿/圆系/阿波罗尼斯/隐圆/焦点三角形族/第三定义族/焦半径/中点弦/硬解/焦点弦/阿基米德/蒙日圆/定比分点/定比点差/齐次式/齐次方程/非对称等）：进阶汇总「做题后回看」性质，加框会稀释定理框锚点且多含大段证明，全不框；',
'- 编注段、证明段、图段、对比辨析表一律不框。']
open('步骤7定理框判定.md','w',encoding='utf-8').write('\n'.join(lines))
print('applied pBdr on', applied, 'paragraphs; entries framed:', len({f[1] for f in frames}))
