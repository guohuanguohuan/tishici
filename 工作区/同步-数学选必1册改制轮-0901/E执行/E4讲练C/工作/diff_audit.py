# -*- coding: utf-8 -*-
"""一次性脚本（E4讲练C）——归一化diff对账（规则重建法，模板同E3/B卷v2）：
基线每段施加授权文本变换后与终态非锚段做多重集比对。C卷授权差异五类：
①题号/条目号重编（79题+8条目，序位映射）②区间括注删除（1段）③页眉页脚2部件（整体重建）
④节名锚段1（锚文本=节标题前缀）⑤KP横排合并3笔（基线两段→终态一段，norm空白剥离恒等）。
空段记账：环绕删空图段64、KP合并删段3（并入前段）。任何多重集残差=授权外差异，必须清零。"""
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
KP_RE=re.compile(r'^【知识点】')
def paras(path):
    z=zipfile.ZipFile(path); doc=etree.fromstring(z.read('word/document.xml')); z.close()
    body=doc.find(q('body')); out=[]
    for el in body:
        if el.tag==q('p'):
            t=''.join(x.text or '' for x in el.iter() if isinstance(x.tag,str) and etree.QName(x).localname=='t')
            ppr=el.find(q('pPr')); style=None
            if ppr is not None:
                ps=ppr.find(q('pStyle')); style=ps.get(q('val')) if ps is not None else None
            out.append((t,style))
        else: out.append(('<tbl>','TBL'))
    return out
base=paras('C.docx'); fin=paras('C_同串.docx')
fin_anchors=[t for t,s in fin if s==ANCHOR_STYLE]
fin_newtoks=[]
for t,s in fin:
    m=NEWTOK_RE.match(t)
    if m: fin_newtoks.append(m.group(1))
base_toks=[]
for t,s in base:
    m=Q3_RE.match(t) or BARE_RE.match(t)
    if m: base_toks.append((m.group(1), bool(Q3_RE.match(t))))
n_q=sum(1 for _,isq in base_toks if isq); n_e=len(base_toks)-n_q
print('基线号段: 题%d＋条%d＝%d｜终态token: %d｜锚段: %d'%(n_q,n_e,len(base_toks),len(fin_newtoks),len(fin_anchors)))
assert n_q==79 and n_e==8 and len(fin_newtoks)==87
positions=iter(fin_newtoks)
expected=[]; n_renum=0; n_iv=0; n_kpmerge=0
i=0
while i<len(base):
    t,s=base[i]
    if not norm(t): i+=1; continue
    if i+1<len(base) and base[i+1][1]!='TBL' and KP_RE.match(base[i+1][0]):
        # KP合并：前段（含可能的号段改写）+后段
        e=t
        m3=Q3_RE.match(e)
        if m3:
            new=next(positions); n_renum+=1; e=new+e[m3.end(1):]
        else:
            mb=BARE_RE.match(e)
            if mb:
                new=next(positions); n_renum+=1; e=new+'．'+e[mb.end():]
        if IV_RE.search(e): e=IV_RE.sub('',e); n_iv+=1
        e=e+base[i+1][0]; n_kpmerge+=1
        expected.append(norm(e)); i+=2; continue
    e=t
    m3=Q3_RE.match(e)
    if m3:
        new=next(positions); n_renum+=1; e=new+e[m3.end(1):]
    else:
        mb=BARE_RE.match(e)
        if mb:
            new=next(positions); n_renum+=1; e=new+'．'+e[mb.end():]
    if IV_RE.search(e): e=IV_RE.sub('',e); n_iv+=1
    expected.append(norm(e)); i+=1
fin_nonanchor=[norm(t) for t,s in fin if t and norm(t) and s!=ANCHOR_STYLE]
cE=Counter(expected); cF=Counter(fin_nonanchor)
onlyE=cE-cF; onlyF=cF-cE
print('重建期望段数: %d｜终态非锚非空段数: %d'%(len(expected),len(fin_nonanchor)))
print('期望-终态残差: %d｜终态-期望残差: %d'%(sum(onlyE.values()),sum(onlyF.values())))
for k,v in list(onlyE.items())[:10]: print('  仅期望:',v,repr(k[:70]))
for k,v in list(onlyF.items())[:10]: print('  仅终态:',v,repr(k[:70]))
n_empty_base=sum(1 for t,s in base if not norm(t) and s!='TBL')
n_empty_fin=sum(1 for t,s in fin if not norm(t) and s!=ANCHOR_STYLE)
print('空段: 基线%d → 终态%d（差=%d；环绕删空图段64＋KP并入删段3）'%(n_empty_base,n_empty_fin,n_empty_base-n_empty_fin))
print('锚段前缀断言:')
sec_titles=[norm(t) for t,s in fin if t and s!=ANCHOR_STYLE]
ok=0
for a in fin_anchors:
    an=norm(a); ok+=1 if any(st.startswith(an) for st in sec_titles) else 0
print('  锚段文本=某段前缀: %d/%d'%(ok,len(fin_anchors)))
json.dump({'基线号段题':n_q,'基线条目':n_e,'终态token':len(fin_newtoks),'重编段':n_renum,'区间括注删段':n_iv,
           'KP合并段':n_kpmerge,'锚段':len(fin_anchors),'残差_期望减终态':sum(onlyE.values()),'残差_终态减期望':sum(onlyF.values()),
           '仅期望样本':[k[:80] for k in list(onlyE)[:10]],'仅终态样本':[k[:80] for k in list(onlyF)[:10]],
           '空段基线':n_empty_base,'空段终态':n_empty_fin},
          open('../登记/09_归一化diff对账.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('落盘 ok')
