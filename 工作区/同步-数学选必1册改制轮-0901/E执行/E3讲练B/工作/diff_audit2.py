# -*- coding: utf-8 -*-
"""一次性脚本（E3讲练B）——归一化diff对账v2（规则重建法）：
基线每段施加授权文本变换（①题号/条目号重编——按文档序号序位映射新token；
②节标题区间括注删除），与终态非锚段做多重集比对；
锚段单独断言（9段、各为其节标题前缀）；空段记账（环绕删60空图段+锚段+9）；
页眉页脚按授权③登记。任何多重集残差=授权外差异，必须清零。"""
import zipfile, re, json
from collections import Counter
from lxml import etree

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s'%(W,t)
def norm(s): return re.sub(r'\s+','',s)

Q3_RE=re.compile(r'^(\d+)．（(简单|中档|难)·(保60%|保80%|冲100%)·卡壳看答案）')
BARE_RE=re.compile(r'^(\d+)．')
IV_RE=re.compile(r'（第[0-9．\-—–~～]+题）')
NUM_CORE=r'(?:\d+(?:\.\d+)+-\d+|\d+)'
NEWTOK_RE=re.compile(r'^(%s)．'%NUM_CORE)
ANCHOR_STYLE='JieMingMao'

def paras(path):
    z=zipfile.ZipFile(path)
    doc=etree.fromstring(z.read('word/document.xml'))
    z.close()
    body=doc.find(q('body'))
    out=[]
    for el in body:
        if el.tag==q('p'):
            t=''.join(x.text or '' for x in el.iter() if isinstance(x.tag,str) and etree.QName(x).localname=='t')
            ppr=el.find(q('pPr'))
            style=None
            if ppr is not None:
                ps=ppr.find(q('pStyle'))
                style=ps.get(q('val')) if ps is not None else None
            out.append((t,style))
        else:
            out.append(('<tbl>','TBL'))
    return out

base=paras(r"C:\提示词\工作区\同步-数学选必1册改制轮-0901\E执行\E3讲练B\工作\B.docx")
fin=paras(r"C:\提示词\工作区\同步-数学选必1册改制轮-0901\E执行\E3讲练B\工作\B_终.docx")

# 终态锚段（style=JieMingMao）
fin_anchors=[t for t,s in fin if s==ANCHOR_STYLE]
# 终态新token有序清单（题块三段式+条目，文档序）
fin_newtoks=[]
for t,s in fin:
    m=NEWTOK_RE.match(t)
    if m: fin_newtoks.append(m.group(1))
# 基线号段有序清单（q3或bare）
base_toks=[]
for t,s in base:
    m=Q3_RE.match(t) or BARE_RE.match(t)
    if m: base_toks.append(m.group(1))
print('基线号段数:', len(base_toks), '｜终态token数:', len(fin_newtoks), '｜锚段数:', len(fin_anchors))

# 授权重建
expected=[]
n_renum=0; n_iv=0
tokmap=dict(zip(base_toks, fin_newtoks))  # 按文档序位映射（同序遍历）
# 注意：基线号段含题族61+条目2（条目为裸「1．」，重复token！按序位映射须按位置而非值）
positions=iter(fin_newtoks)
for t,s in base:
    if not t:
        continue
    e=t
    m3=Q3_RE.match(t)
    if m3:
        new=next(positions); n_renum+=1
        e=new+t[m3.end(1):]   # 仅替换数字本体，句点与括注原文保留
    else:
        mb=BARE_RE.match(t)
        if mb:
            new=next(positions); n_renum+=1
            e=new+'．'+t[mb.end():]
    if IV_RE.search(e):
        e=IV_RE.sub('',e); n_iv+=1
    expected.append(norm(e))

fin_nonanchor=[norm(t) for t,s in fin if t and s!=ANCHOR_STYLE]
base_nonempty=[norm(t) for t,s in base if t]

cE=Counter(expected); cF=Counter(fin_nonanchor)
onlyE=cE-cF; onlyF=cF-cE
print('重建期望段数:', len(expected), '｜终态非锚非空段数:', len(fin_nonanchor))
print('期望-终态残差:', sum(onlyE.values()), '｜终态-期望残差:', sum(onlyF.values()))
for k,v in list(onlyE.items())[:10]: print('  仅期望:', v, repr(k[:70]))
for k,v in list(onlyF.items())[:10]: print('  仅终态:', v, repr(k[:70]))

# 空段记账
n_empty_base=sum(1 for t,s in base if not t and s!='TBL')
n_empty_fin=sum(1 for t,s in fin if not t and s!=ANCHOR_STYLE)
print('空段: 基线%d → 终态%d（差=%d；环绕删空图段60、锚段非空）'%(n_empty_base,n_empty_fin,n_empty_base-n_empty_fin))
print('锚段前缀断言:')
sec_titles=[norm(t) for t,s in fin if t and s!=ANCHOR_STYLE and re.match(r'^\d+\.\d+(\.\d+)?[ \u3000]',t) and ('本节' in t or not re.match(r'^\d+(\.\d+)+\.\d',t))]
ok=0
for a in fin_anchors:
    an=norm(a)
    hit=[st for st in sec_titles if st.startswith(an)]
    ok+= 1 if hit else 0
print('  锚段文本=某节标题前缀: %d/%d'%(ok,len(fin_anchors)))

json.dump({'基线号段':len(base_toks),'终态token':len(fin_newtoks),'重编段':n_renum,'区间括注删段':n_iv,
           '锚段':len(fin_anchors),'残差_期望减终态':sum(onlyE.values()),'残差_终态减期望':sum(onlyF.values()),
           '仅期望样本':[k[:80] for k in list(onlyE)[:10]],'仅终态样本':[k[:80] for k in list(onlyF)[:10]],
           '空段基线':n_empty_base,'空段终态':n_empty_fin},
          open(r"C:\提示词\工作区\同步-数学选必1册改制轮-0901\E执行\E3讲练B\登记\09_归一化diff对账.json",'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('落盘 ok')
