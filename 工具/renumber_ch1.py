# -*- coding: utf-8 -*-
"""renumber_ch1.py — 第1章讲练件精配草稿全件题号重编号（1..N连续）
题块判定：以"数字．"起段的段落为潜在题号段；该段到下一潜在题号段之间含答案标签(【答案】/【标准答案】/【解析】/【详解】/【分析】/【解法】)则为真题目，重编号；
不含则为讲部分方法条目/非题目，跳过。保留全角"．"，只改数字。
"""
import re, copy, io, sys
from docx import Document
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'; M='http://schemas.openxmlformats.org/officeDocument/2006/math'
WC='{'+W+'}'; MC='{'+M+'}'
SRC=r'C:\Users\28120\Desktop\同步-数学选必1整册-0825\第1章\work\讲练件_精配草稿.docx'
OUT=SRC
ANS=('【答案】','【标准答案】','【解析】','【详解】','【分析】','【解法】','【答案思路】','【大招指引】')
def ptext(p):
    buf=[]
    for c in p.iter():
        ct=c.tag.split('}')[-1]
        if ct=='t' and c.tag.startswith(WC): buf.append(c.text or '')
    return ''.join(buf)
def set_qnum(p, newnum):
    """段内找第一个数字run（题号），改为newnum；后缀．保留。兼容 数字/数字．/数字．xxx 三种run形态。"""
    rs=p.findall(WC+'r')
    for ri,r in enumerate(rs):
        txt=''.join(t.text or '' for t in r.findall(WC+'t'))
        m=re.match(r'^(\d{1,3})(.*)$', txt)
        if not m: continue
        num=m.group(1); tail_after=0
        # 该run可能是纯数字（句点在后run）或"数字．xxx"
        if m.group(2).startswith('．'):
            # 本run含句点：newnum+句点+后缀
            ts=r.findall(WC+'t')
            if ts:
                ts[0].text=str(newnum)+m.group(2)
                for t in ts[1:]: ts[0].text+=(t.text or ''); r.remove(t)
            return True
        else:
            # 数字run独立；改数字run为newnum（句点在下一run，保留）
            ts=r.findall(WC+'t')
            if ts:
                ts[0].text=str(newnum)
                for t in ts[1:]: ts[0].text+=(t.text or ''); r.remove(t)
            return True
    return False
doc=Document(SRC)
body=doc.element.body
paras=[c for c in body if c.tag==WC+'p']
# 潜在题号段索引
cand=[]
for i,p in enumerate(paras):
    t=ptext(p).strip()
    if re.match(r'^\d{1,3}．',t) and len(t)>=8:
        cand.append(i)
print('潜在题号段:',len(cand))
# 对每个候选，判断块（到下一候选前）是否含答案标签
n=0; skipped=[]
for k,i in enumerate(cand):
    j=cand[k+1]-1 if k+1<len(cand) else len(paras)-1
    if j<i: j=i
    block_txt=[]
    for ii in range(i,j+1):
        block_txt.append(ptext(paras[ii]))
    joined='\n'.join(block_txt)
    has_ans=any(a in joined for a in ANS)
    if has_ans:
        n+=1
        ok=set_qnum(paras[i],n)
        if not ok: print('!! 重编号失败题号段:',i,ptext(paras[i])[:20])
    else:
        skipped.append((i,ptext(paras[i])[:24]))
print('重编号题目数:',n)
print('跳过(非题)段数:',len(skipped))
for s in skipped[:15]: print('  跳过:',s)
doc.save(OUT)
print('保存重编号→',OUT)
