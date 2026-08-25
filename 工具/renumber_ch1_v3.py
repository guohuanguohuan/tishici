# -*- coding: utf-8 -*-
"""renumber_ch1_v3.py — 最清晰重编号。对每个题号段，把题号run改为"新号．"。
run形态：①[N．]=一个run ②[N]+[．]两run ③[N．句点结尾] ④[N纯数字] ⑤【典例N】整体run ⑥【典例】+[N]+【】三run
统一处理：找段内"题号文本"（正则从段ptext定位），定位到对应run并替换；段内公式/图片run不碰。"""
import re
from docx import Document
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'; M='http://schemas.openxmlformats.org/officeDocument/2006/math'
WC='{'+W+'}'; MC='{'+M+'}'
SRC=r'C:\Users\28120\Desktop\同步-数学选必1整册-0825\第1章\work\讲练件_精配草稿.docx'
ANS=('【答案】','【标准答案】','【解析】','【详解】','【分析】','【解法】','【答案思路】','【大招指引】')
def para_text_with_pos(p):
    """返回[(text, runElem, isMath, isDraw)]按w:r顺序，用于定位题号run"""
    seq=[]
    for r in p.findall(WC+'r'):
        txt=''.join(t.text or '' for t in r.findall(WC+'t'))
        has_math=bool(r.findall('.//'+MC+'t'))
        has_draw=bool(r.findall('{http://schemas.openxmlformats.org/drawingml/2006/main}blip')) or bool(r.findall('{urn:schemas-microsoft-com:vml}imagedata'))
        seq.append({'t':txt,'r':r,'math':has_math,'draw':has_draw})
    return seq
def set_qnum(p, n):
    seq=para_text_with_pos(p)
    # 情形：段首【典例拆三run："【典例"+"N"+"】"
    for k,it in enumerate(seq):
        if it['t']=='【典例' or it['t'].startswith('【典例'):
            # 清空该run
            _clr(it['r'])
            # 找数字run改
            for m in range(k+1,len(seq)):
                if re.match(r'^\d{1,3}$',seq[m]['t']):
                    _set(seq[m]['r'],str(n)+'．'); break
            # 清空]run
            for m in range(k+1,len(seq)):
                if seq[m]['t']=='】': _clr(seq[m]['r']); break
            return True
    # 常规：找第一个含"数字"的run作为题号run
    for k,it in enumerate(seq):
        if it['math'] or it['draw']: continue
        m=re.match(r'^(\d{1,3})(.*)$',it['t'])
        if m:
            tail=m.group(2)
            if tail.startswith('．'):
                _set(it['r'], str(n)+'．'+tail[1:])  # 数字．xxx → 新号．xxx（保留句点后）
            else:
                _set(it['r'], str(n))  # 纯数字 → 新号（句点在邻run保留）
            return True
    return False
def _clr(r):
    ts=r.findall(WC+'t')
    if ts: ts[0].text=''
    for t in ts[1:]: ts[0].text+=(t.text or '') if t.text else ''
    for t in ts[1:]: r.remove(t)
def _set(r, txt):
    ts=r.findall(WC+'t')
    if ts:
        ts[0].text=txt
        for t in ts[1:]: r.remove(t)
doc=Document(SRC); body=doc.element.body
paras=[c for c in body if c.tag==WC+'p']
def ptext(p): return ''.join(c.text or '' for c in p.iter() if c.tag==WC+'t' or c.tag==MC+'t')
cand=[]
for i,p in enumerate(paras):
    t=ptext(p).strip(); tt=re.sub(r'^(\[图\]|【图】)+','',t)
    if (re.match(r'^\d{1,3}．',tt) and len(tt)>=8) or re.match(r'^【典例\d*】',tt): cand.append(i)
print('候选:',len(cand))
n=0; skip=[]; fail=[]
for k,i in enumerate(cand):
    j=cand[k+1]-1 if k+1<len(cand) else len(paras)-1
    if j<i: j=i
    joined='\n'.join(ptext(paras[ii]) for ii in range(i,j+1))
    if any(a in joined for a in ANS):
        n+=1
        if not set_qnum(paras[i],n): fail.append((i,ptext(paras[i])[:20]))
    else:
        skip.append((i,ptext(paras[i])[:24]))
print('重编号:',n,'跳过:',len(skip),'失败:',len(fail))
for f in fail: print('  未改:',f)
# 用同一cand验证连续性
qq=[]
for k,i in enumerate(cand):
    j=cand[k+1]-1 if k+1<len(cand) else len(paras)-1
    if j<i: j=i
    if any(a in '\n'.join(ptext(paras[ii]) for ii in range(i,j+1)) for a in ANS):
        t=ptext(paras[i]).strip(); tt=re.sub(r'^(\[图\]|【图】)+','',t)
        m=re.match(r'^(\d{1,3})．',tt); qq.append(int(m.group(1)) if m else 0)
print('同cand题目数:',len(qq),'连续1..N:',qq==list(range(1,len(qq)+1)))
if qq!=list(range(1,len(qq)+1)):
    for idx in range(1,len(qq)):
        if qq[idx]!=qq[idx-1]+1: print('  断裂 idx=%d %d->%d'%(idx,qq[idx-1],qq[idx]))
    # 打印值为0的段（未被验证识别）
    for idx,v in enumerate(qq):
        if v==0: print('  段未识别题号 cand[%d]=%d:'%(idx,cand[idx]),ptext(paras[cand[idx]])[:30])
doc.save(SRC); print('保存→',SRC)
