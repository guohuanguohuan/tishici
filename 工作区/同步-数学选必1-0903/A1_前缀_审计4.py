# -*- coding: utf-8 -*-
"""A1审计第四遍：节号纯数字映射修正＋节内连续断言、图段挂E0的小图尺寸、孤儿图引方向、
页眉run字体、灰底答案值抽检样本（人工过目料）、④多赋值粘连OMML结构抽验"""
import os, re, sys, io
from lxml import etree
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

W  = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
M  = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(p,t): return '{%s}%s' % (p,t)
PARTS = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\A1_parts"
OUT   = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\A1_reports"
TAGS = ['X1','I1','B','C']

def load(tag):
    doc = etree.parse(os.path.join(PARTS,tag,'word','document.xml'))
    body = doc.getroot().find(q(W,'body'))
    paras = [p for p in body if p.tag==q(W,'p')]
    return doc, body, paras
def p_text(p): return ''.join(t.text or '' for t in p.findall('.//'+q(W,'t')))
def p_style(p):
    pPr=p.find(q(W,'pPr'))
    if pPr is not None:
        st=pPr.find(q(W,'pStyle'))
        if st is not None: return st.get(q(W,'val'))
    return ''
def p_shd(p):
    pPr=p.find(q(W,'pPr'))
    if pPr is not None:
        sh=pPr.find(q(W,'shd'))
        if sh is not None: return sh.get(q(W,'fill'))
    return None

out=[]; P=out.append
for tag in TAGS:
    doc, body, paras = load(tag)
    texts=[p_text(p) for p in paras]
    styles=[p_style(p) for p in paras]
    shds=[p_shd(p) for p in paras]
    P(f"\n########## {tag}")
    h3={}
    for i,s in enumerate(styles):
        if s=='Heading3':
            m=re.match(r'(\d+(?:\.\d+)+)', texts[i])
            if m: h3[m.group(1)]=i
    def sec_of(pre):
        best=None
        for h in h3:
            if pre==h or pre.startswith(h+'.'):
                if best is None or len(h)>len(best): best=h
        return best
    qhao=[]; tiaom=[]
    for i,p in enumerate(paras):
        for r in p.findall(q(W,'r')):
            rPr=r.find(q(W,'rPr'))
            sh=rPr.find(q(W,'shd')) if rPr is not None else None
            if sh is None or sh.get(q(W,'fill'))!='C9C9C9': continue
            t=''.join(x.text or '' for x in r.findall(q(W,'t')))
            m=re.fullmatch(r'(\d+(?:\.\d+)+)-(\d+)．', t)
            if m:
                (qhao if m.group(1).count('.')>=3 else tiaom).append((i,m.group(1),int(m.group(2))))
    secmap={}
    for i,pre,seq in qhao:
        secmap.setdefault(sec_of(pre) or '?',[]).append((i,seq))
    for s,items in sorted(secmap.items()):
        seqs=sorted(x[1] for x in items)
        ok = seqs==list(range(1,len(seqs)+1))
        P(f"  节{s}: {len(seqs)}题 序列{'连续1..%d ✓'%max(seqs) if ok else '断点! '+str(seqs)}")
    # 图段挂E0的小图尺寸
    for i,s in enumerate(shds):
        if s=='E0E0E0':
            exts=[(int(e.get('cx')),int(e.get('cy'))) for e in paras[i].findall('.//'+q(WP,'extent'))]
            if exts:
                P(f"  E0E0E0+图段@p#{i}: 图显示尺寸cm={[(round(cx/360000,2),round(cy/360000,2)) for cx,cy in exts]} 文={texts[i][:40]!r}")
    # 孤儿图引方向
    imgp=[i for i,p in enumerate(paras) if p.findall('.//'+q(WP,'inline'))]
    for i,tx in enumerate(texts):
        if re.search(r'如图|图所示|如下图', tx) and i not in imgp:
            near=sorted(((abs(j-i), j) for j in imgp))
            if near and near[0][0]>6:
                d,j=near[0]
                P(f"  远距图引@p#{i}: 最近图@p#{j} 方向={'后' if j>i else '前'} 距={d} 文={tx[:44]!r}")
    # 页眉字体
    hf=etree.parse(os.path.join(PARTS,tag,'word','header1.xml'))
    fonts=set(); colors=set()
    for rf in hf.getroot().iter(q(W,'rFonts')):
        fonts.add((rf.get(q(W,'ascii')),rf.get(q(W,'eastAsia'))))
    P(f"  页眉rFonts={fonts}")

print('\n'.join(out))
open(os.path.join(OUT,'精查4_四件.txt'),'w',encoding='utf-8').write('\n'.join(out))

# ============ 灰底抽检样本（人工过目料）============
samp=[]
S=samp.append
for tag in TAGS:
    doc, body, paras = load(tag)
    texts=[p_text(p) for p in paras]
    # 抽C9C9C9 run（答案值/需背）：跳过题号块/条目号/标签芯片/（N）子层
    cands=[]
    for i,p in enumerate(paras):
        for r in p.findall(q(W,'r')):
            rPr=r.find(q(W,'rPr'))
            if rPr is None: continue
            sh=rPr.find(q(W,'shd'))
            if sh is None or sh.get(q(W,'fill'))!='C9C9C9': continue
            t=''.join(x.text or '' for x in r.findall(q(W,'t')))
            if not t.strip(): continue
            if re.fullmatch(r'\d+(?:\.\d+)+-\d+．', t): continue
            if re.fullmatch(r'【[^】]{1,12}】', t): continue
            if re.fullmatch(r'（\d+）', t): continue
            cands.append((i,t))
    S(f"\n===== {tag} 灰底run候选总数={len(cands)}")
    step=max(1,len(cands)//12)
    for i,t in cands[::step][:12]:
        S(f"  p#{i}: {t[:60]!r} | 段落首={texts[i][:35]!r}")
    # OMML挂灰块样本
    om=[]
    for i,p in enumerate(paras):
        for mth in p.findall('.//'+q(M,'oMath')):
            mr=mth.findall('.//'+q(M,'r'))
            if not mr: continue
            rPr=mr[0].find(q(M,'rPr'))
            sh=None
            if rPr is not None:
                wsh=rPr.find(q(W,'shd'))
                if wsh is not None: sh=wsh.get(q(W,'fill'))
            if sh=='C9C9C9':
                mt=''.join(x.text or '' for x in mth.findall('.//'+q(M,'t')))
                om.append((i,mt))
    S(f"  OMML挂灰块数={len(om)} 样本:")
    step=max(1,len(om)//8)
    for i,mt in om[::step][:8]:
        S(f"    p#{i}: {mt[:50]!r}")
open(os.path.join(OUT,'灰底抽检样本.txt'),'w',encoding='utf-8').write('\n'.join(samp))
print('\n'.join(samp[:40]))

# ============ ④多赋值粘连 OMML 结构抽验（B 3例）============
v=[]
doc, body, paras = load('B')
texts=[p_text(p) for p in paras]
for target in (263, 539, 989):
    p=paras[target]
    for mth in p.findall('.//'+q(M,'oMath')):
        mt=''.join(x.text or '' for x in mth.findall('.//'+q(M,'t')))
        if re.search(r'[\w）)]\w*=', mt) and len(mt)>8:
            kinds=set(etree.QName(e).localname for e in mth.iter() if etree.QName(e).localname in ('eqArr','m','f','mat','d'))
            v.append(f"p#{target} OMML: {mt[:60]!r} 结构元素={sorted(kinds)}")
open(os.path.join(OUT,'粘连结构抽验.txt'),'w',encoding='utf-8').write('\n'.join(v))
print('\n'.join(v))
