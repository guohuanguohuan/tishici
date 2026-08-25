# -*- coding: utf-8 -*-
"""renumber_ch1_v2.py — 第1章讲练件精配草稿全件题号重编号（1..N连续）
兼容题块起点三种：①"N．"起段 ②"N．xxx"（数字与句点拆run）③"【典例N】"起段（源例题，改为连续题号）。
题块判定：题干所在段到下一题号段之间含答案标签(【答案】/【标准答案】/【解析】/【详解】/【分析】/【解法】/【答案思路】/【大招指引】)。
【典例N】/【图】前缀剥除后改题号；保留全角"．"。
"""
import re, copy
from docx import Document
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'; M='http://schemas.openxmlformats.org/officeDocument/2006/math'
WC='{'+W+'}'; MC='{'+M+'}'
SRC=r'C:\Users\28120\Desktop\同步-数学选必1整册-0825\第1章\work\讲练件_精配草稿.docx'
ANS=('【答案】','【标准答案】','【解析】','【详解】','【分析】','【解法】','【答案思路】','【大招指引】')
def ptext(p):
    return ''.join(c.text or '' for c in p.iter() if c.tag==WC+'t' or c.tag==MC+'t')
def realtext(p):
    """段落文本（不含公式），用于题号段识别"""
    return ptext(p)
def set_qnum(p, newnum):
    """把段内的题号（数字．拆run 或 【典例N】拆run）改为 newnum．"""
    rs=p.findall(WC+'r')
    # 情形A：【典例 拆run（"【典例"+"N"+"】"）——优先识别
    texts=[(''.join(t.text or '' for t in r.findall(WC+'t')) for r in rs)]
    for k,txt in enumerate(texts):
        if txt=='【典例' or txt.startswith('【典例'):
            # 该run含【典例标记；后续run含N 或 】。把整段首部改为 newnum．
            # 方案：清空"【典例"run与"】"run，把数字run改newnum＋．
            j=k
            # 先清空当前【典例 run
            ts_cur=rs[j].findall(WC+'t')
            if ts_cur: ts_cur[0].text=''
            # 向后找数字run和】run
            for m in range(j+1,len(rs)):
                mtxt=texts[m]
                ts=rs[m].findall(WC+'t')
                if re.match(r'^\d{1,3}$',mtxt) and not mtxt=='':
                    if ts: ts[0].text=str(newnum)+'．'
                    break
            # 清空后续 "】" run
            for m in range(j+1,len(rs)):
                if texts[m]=='】':
                    ts=rs[m].findall(WC+'t')
                    if ts: ts[0].text=''
                    break
            return True
    # 情形B：常规
    for r in rs:
        ts=r.findall(WC+'t'); txt=''.join(t.text or '' for t in ts)
        m=re.match(r'^(\d{1,3})(．.+)$',txt)
        if m:
            if ts:
                ts[0].text=str(newnum)+m.group(2)
                for t in ts[1:]: ts[0].text+=(t.text or ''); r.remove(t)
            return True
        m2=re.match(r'^(\d{1,3})．$',txt)
        if m2:
            if ts: ts[0].text=str(newnum)+'．'
            return True
        m3=re.match(r'^(\d{1,3})$',txt)
        if m3:
            if ts: ts[0].text=str(newnum)
            return True
    return False
def is_qstart(t):
    """识别题号段：剥【图】【典例】等前缀后，判断是否以 N． 或 【典例N】 开头"""
    tt=re.sub(r'^(\[图\]|【图】|\d+[．.])+','',t)  # 剥【图】前缀
    m=re.match(r'^((\d{1,3})．)',t)
    if m and len(t)>=8: return True
    m2=re.match(r'^【典例(\d+)】',t)
    if m2: return True
    m3=re.match(r'^【图】\s*((\d{1,3})．)',t)
    if m3 and len(t)>=8: return True
    return False
def get_qnum(t):
    m=re.match(r'^(\d{1,3})．',t)
    if m: return int(m.group(1))
    m2=re.match(r'^【典例(\d+)】',t)
    if m2: return int(m2.group(1))
    m3=re.match(r'^【图】\s*(\d{1,3})．',t)
    if m3: return int(m3.group(1))
    return None
doc=Document(SRC); body=doc.element.body
paras=[c for c in body if c.tag==WC+'p']
cand=[]
for i,p in enumerate(paras):
    t=ptext(p).strip()
    tt=re.sub(r'^(\[图\]|【图】)+','',t)
    if re.match(r'^\d{1,3}．',tt) and len(tt)>=8: cand.append(i)
    elif re.match(r'^【典例\d*】',tt): cand.append(i)
print('题号候选段:',len(cand))
n=0; skip=[]
for k,i in enumerate(cand):
    j=cand[k+1]-1 if k+1<len(cand) else len(paras)-1
    if j<i: j=i
    joined='\n'.join(ptext(paras[ii]) for ii in range(i,j+1))
    if any(a in joined for a in ANS):
        n+=1
        if not set_qnum(paras[i],n):
            print('!! 未改题号:',i,ptext(paras[i])[:24])
    else:
        skip.append((i,ptext(paras[i])[:26]))
print('重编号题目数:',n)
print('跳过(讲部分):',len(skip))
for s in skip: print('  跳过:',s)
doc.save(SRC)
print('保存重编号→',SRC)
