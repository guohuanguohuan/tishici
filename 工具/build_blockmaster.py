# -*- coding: utf-8 -*-
"""build_blockmaster.py — 重建模块7 18个文件的块主索引（题号/栏目+元素区间+首句），供第1章重审定位恢复题块"""
import os, re, sys, json, glob
sys.path.insert(0, '工具')
from docx import Document
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'; M='http://schemas.openxmlformats.org/officeDocument/2006/math'
WC='{'+W+'}'; MC='{'+M+'}'
_c=[0]
def omml(el):
    t=el.tag.split('}')[-1]
    if t=='t': return el.text or ''
    if t=='f':
        n=el.find(MC+'num');d=el.find(MC+'den');return '('+''.join(omml(c) for c in n)+')/('+''.join(omml(c) for c in d)+')'
    if t=='rad':
        e=el.find(MC+'e');return '√('+''.join(omml(c) for c in e)+')'
    if t=='sSup':
        e=el.find(MC+'e');s=el.find(MC+'sup');return ''.join(omml(c) for c in e)+'^('+''.join(omml(c) for c in s)+')'
    if t=='sSub':
        e=el.find(MC+'e');s=el.find(MC+'sub');return ''.join(omml(c) for c in e)+'_('+''.join(omml(c) for c in s)+')'
    if t=='d':
        return '('+''.join(omml(c) for c in el.findall(MC+'e'))+')'
    buf=[]
    for c in el:
        ct=c.tag.split('}')[-1]
        if ct.endswith('Pr'): continue
        buf.append(omml(c))
    return ''.join(buf)
def ptext(p):
    buf=[]
    def w(e):
        for c in e:
            ct=c.tag.split('}')[-1]
            if ct=='t' and c.tag.startswith(WC): buf.append(c.text or '')
            elif ct=='oMath': buf.append('⟦'+omml(c)+'⟧')
            elif ct=='oMathPara':
                for om in c.findall(MC+'oMath'): buf.append('⟦'+omml(om)+'⟧')
            elif ct in ('drawing','pict','object'): buf.append('【图】')
            else: w(c)
    w(p); return ''.join(buf)
QNUM=re.compile(r'^(\d{1,3})．')
MARK=re.compile(r'^(【例题】|【典例\d*】|【举一反三】|【练习题】|【易错题)')
targets=glob.glob('高中数学/参考/组卷网/高中数学解题大招（二级结论）荟萃/04_原始资料/模块7立体几何/*.docx')
out=[]
for f in sorted(targets):
    doc=Document(f); body=doc.element.body
    children=list(body.iterchildren())
    n=len(children)
    name=os.path.basename(f)
    starts=[]
    for i,ch in enumerate(children):
        if ch.tag!=WC+'p': continue
        t=ptext(ch).strip()
        if len(t)>=8 and QNUM.match(t): starts.append((i,QNUM.match(t).group(1),t[:45]))
        elif MARK.match(t): starts.append((i,t[:8],t[:45]))
    blocks=[]
    for k,(i,lab,first) in enumerate(starts):
        j=starts[k+1][0]-1 if k+1<len(starts) else n-1
        blocks.append([lab,i,j,first])
    out.append({'file':name,'blocks':blocks})
os.makedirs('C:/Users/28120/Desktop/同步-数学选必1整册-0825/第1章/work',exist_ok=True)
json.dump(out, open('C:/Users/28120/Desktop/同步-数学选必1整册-0825/第1章/work/block_master.json','w'), ensure_ascii=False)
print('文件数:',len(out),'总块数:',sum(len(b['blocks']) for b in out))
for b2 in out:
    print('---',b2['file'],'块数',len(b2['blocks']))
