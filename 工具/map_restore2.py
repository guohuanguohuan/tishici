# -*- coding: utf-8 -*-
"""map_restore2.py — 第1章恢复题定位（新算法）
verify 的"(第M块)" = 目标文件内"题目块"（含【答案】的块）累计序号（从1起）。
对每个恢复题：文件短名→真实文件；在该文件内建题目块序列（含【答案】判题目块）；
用 verify 给的题目块号定位；用题干前段字符校验一致性。
输出 loc 供人核对。不自动装配。
"""
import os, re, json, io, sys, glob
sys.path.insert(0, '工具')
from docx import Document
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'; M='http://schemas.openxmlformats.org/officeDocument/2006/math'
WC='{'+W+'}'; MC='{'+M+'}'
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
    if t=='d': return '('+''.join(omml(c) for c in el.findall(MC+'e'))+')'
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

short2real={
 '大招1文件':'模块7大招1四面体的特殊模型（完成）.docx',
 '大招2文件':'模块7大招2三余弦定理（完成）.docx',
 '大招3文件':'模块7大招3运动中找不变量（完成）.docx',
 '大招4文件':'模块7大招4动点轨迹的确定（完成）.docx',
 '大招5文件':'模块7大招5翻折问题之平面化（完成）.docx',
 '大招6文件':'模块7大招6截面问题之补全截面图（完成）.docx',
 '大招7文件':'模块7大招7叉乘法快速求法向量（完成）.docx',
 '大招8文件':'模块7大招8判二面角的锐钝问题（完成）.docx',
 '大招9文件':'模块7大招9空间正余弦定理（完成）.docx',
 '大招10文件':'模块7大招10投影法求二面角（完成）.docx',
 '大招12文件':'模块7大招12内切球与球相切模型.docx',
 '补形法文件':'模块7立体几何大招2外接球问题之补形法（完成）.docx',
 '墙角文件':'模块六立体几何大招10外接球之墙角模型.docx',
 '汉堡文件':'模块六立体几何大招11外接球之汉堡模型.docx',
 '切瓜文件':'模块六立体几何大招12外接球之切瓜模型.docx',
 '折叠文件':'模块六立体几何大招13外接球之折叠模型.docx',
 '双外心文件':'模块六立体几何大招3外接球问题之双外心模型.docx',
}
master=json.load(open('C:/Users/28120/Desktop/同步-数学选必1整册-0825/第1章/work/block_master.json',encoding='utf-8'))
byfile={b['file']:b['blocks'] for b in master}

def is_topic_block(blocks, k, i, j):
    """判定块是否为题目块：块区间内文本含【答案】 或 首句是题号/【典例】且区间内含【解析】/【详解】/【分析】"""
    # 直接用区间文本含【答案】
    pass
def block_text(doc, i, j):
    children=list(doc.element.body.iterchildren())
    buf=[]
    for k2 in range(i,j+1):
        ch=children[k2]
        if ch.tag==WC+'p': buf.append(ptext(ch))
        elif ch.tag==WC+'tbl': buf.append('[表格]')
    return '\n'.join(buf)

def topic_blocks(fname):
    doc=Document('高中数学/参考/组卷网/高中数学解题大招（二级结论）荟萃/04_原始资料/模块7立体几何/'+fname)
    blocks=byfile[fname]
    seq=[]
    for k,(lab,i,j,first) in enumerate(blocks):
        txt=block_text(doc,i,j)
        if '【答案】' in txt or '【解析】' in txt or '【详解】' in txt or '【分析】' in txt:
            seq.append((lab,i,j,first,k))
    return seq

# 加载 verify review_table 原位置
rt=open('C:/Users/28120/Desktop/同步-数学选必1整册-0825/第1章_review_table.md',encoding='utf-8').read()
loc={}
for m in re.finditer(r'^\| (\d+) \| (?:旧让|进阶) \| ([^|]+) \|.*?\| (.+)$', rt, re.M):
    r=int(m.group(1)); src=m.group(2).strip(); stem=m.group(3).strip()
    loc[r]=(src,stem)

R=[9,26,28,30,31,32,33,34,35,36,38,39,41,42,43,44,46,48,50,51,53,58,59,60,64,66,68,69,71,74,75,76,82,83,86,88,89,93,96,100,101,102,103,104,108,110,115,121,122,124,125,128,130,131,139,148,149,150,153,155,156,157,158,159,160,161,164,165,167,169,174,177,191,192,200,217,234,241]
out=[]
for r in R:
    if r not in loc: out.append((r,'??','缺review行')); continue
    src,stem=loc[r]
    if '·' not in src:
        out.append((r,src,'旧让位·回旧体系存档定位')); continue
    short=src.split('·')[0]
    tihao=src.split('·')[1]
    tihao=tihao.split('（')[0].strip()  # 如 '典1'/'1'/'典2'
    # 提取第M块
    mm=re.search(r'第(\d+)块',src)
    mnum=int(mm.group(1)) if mm else 0
    real=short2real.get(short)
    if not real: out.append((r,src,'短名未映射')); continue
    seq=topic_blocks(real)
    if mnum<1 or mnum>len(seq):
        out.append((r,src,'块号越界(题目块%d)'%len(seq))); continue
    lab,i,j,first,k=seq[mnum-1]
    # 交叉校验：verify题干首句 vs 真实块首句
    sk=re.sub(r'[⟦⟧▲▽【】\s]','',stem[:25])
    fk=re.sub(r'[⟦⟧▲▽【】\s]','',first[:25])
    common=sum(1 for a,b in zip(sk,fk) if a==b and a and a!='图')
    out.append((r,src,'题号块%d 标=%s 区间%d-%d 首句="%s" 校验=%d'%(mnum,lab,i,j,first[:28],common)))
for r,src,note in out:
    print(r,'|',src,'|',note)
# 校验高置信度统计
ok=sum(1 for _,_,n in out if '验证=' in n and int(n.split('校验=')[-1])>=10)
print('高置信(校验>=10):',ok,'/',len(out))
