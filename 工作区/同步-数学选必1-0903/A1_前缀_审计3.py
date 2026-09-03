# -*- coding: utf-8 -*-
"""A1审计第三遍：修正题号判定（题型号=前缀≥4段）、节内连续（按Heading3节映射）、
B/C跨卷同节、档位分布、分析超量定位、I1基进计数与说明句覆盖、E0E0E0归属自动核验、
选项行tab/粘连XML细节、B导航表值、孤儿图引个案、灰底抽检料"""
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
    pPr = p.find(q(W,'pPr'))
    if pPr is not None:
        st = pPr.find(q(W,'pStyle'))
        if st is not None: return st.get(q(W,'val'))
    return ''
def p_shd(p):
    pPr = p.find(q(W,'pPr'))
    if pPr is not None:
        sh = pPr.find(q(W,'shd'))
        if sh is not None: return sh.get(q(W,'fill'))
    return None

out=[]; P=out.append
SEC_OF = {}   # (tag) -> per call rebuilt
for tag in TAGS:
    doc, body, paras = load(tag)
    texts=[p_text(p) for p in paras]
    styles=[p_style(p) for p in paras]
    shds=[p_shd(p) for p in paras]
    P(f"\n########## {tag}")
    # Heading3 节号清单
    h3 = [(i, texts[i].split('\u3000')[0].strip()) for i,s in enumerate(styles) if s=='Heading3']
    h3nums = [t for _,t in h3 if re.match(r'\d+(\.\d+)+', t)]
    P(f"Heading3节号={h3nums}")
    def sec_of_prefix(pre):
        best=None
        for h in h3nums:
            if pre==h or pre.startswith(h+'.'):
                if best is None or len(h)>len(best): best=h
        return best
    # 题号/条目号
    qhao=[]; tiaom=[]
    for i,p in enumerate(paras):
        for r in p.findall(q(W,'r')):
            rPr=r.find(q(W,'rPr'))
            sh=rPr.find(q(W,'shd')) if rPr is not None else None
            if sh is None or sh.get(q(W,'fill'))!='C9C9C9': continue
            t=''.join(x.text or '' for x in r.findall(q(W,'t')))
            m=re.fullmatch(r'(\d+(?:\.\d+)+)-(\d+)．', t)
            if m:
                pre,seq=m.group(1),int(m.group(2))
                (qhao if pre.count('.')>=3 else tiaom).append((i,pre,seq))
    P(f"题号={len(qhao)} 条目号={len(tiaom)}")
    # 节内连续
    secmap={}
    for i,pre,seq in qhao:
        s=sec_of_prefix(pre) or '?'
        secmap.setdefault(s,[]).append((i,seq,pre))
    for s,items in sorted(secmap.items()):
        seqs=[x[1] for x in items]
        ok = sorted(seqs)==list(range(1,len(seqs)+1))
        P(f"  节{s}: {len(seqs)}题 序列{'连续1..%d'%max(seqs) if ok else '断点!'+str(sorted(seqs))}")
    # B/C 跨卷同节（B侧节号清单）
    if tag=='B': B_secs=set(secmap.keys())
    if tag=='C':
        overlap = B_secs & set(secmap.keys())
        P(f"B/C同节跨卷={overlap if overlap else '无'}")
    # 档位
    if tag in ('B','C'):
        dd={'简单':0,'中档':0,'难':0}
        for i,pre,seq in qhao:
            m=re.search(r'（(简单|中档|难)·', texts[i])
            if m: dd[m.group(1)]+=1
        P(f"档位分布={dd} Σ={sum(dd.values())}")
    # 【分析】超量定位（正确分组）
    qidx=[x[0] for x in qhao]
    import bisect
    perq={}
    for i,tx in enumerate(texts):
        if '【分析】' in tx:
            k=bisect.bisect_right(qidx,i)-1
            perq.setdefault(qidx[k] if k>=0 else -1,[]).append(i)
    multi={k:v for k,v in perq.items() if len(v)>1}
    P(f"【分析】块Σ={sum(len(v) for v in perq.values())} 多分析题={len(multi)}")
    for k,v in multi.items():
        P(f"    题@p#{k} {texts[k][:40]!r} 分析段={[x for x in v]}")
        for x in v: P(f"       p#{x}: {texts[x][:60]!r}")
    # I1 基进
    if tag=='I1':
        ji=sum(1 for tx in texts if re.match(r'\d+(?:\.\d+)+-\d+．〔基〕', tx))
        jin=sum(1 for tx in texts if re.match(r'\d+(?:\.\d+)+-\d+．〔进〕', tx))
        P(f"〔基〕={ji} 〔进〕={jin} Σ={ji+jin}")
        # 每条目说明句覆盖：条目号段落→其后至下一条目间的【编注】段
        tidx=[i for i,p in enumerate(paras) for r in [None] if False]
        tiaom_i=[i for i,pre,seq in tiaom]
        cov=[]
        for n,i in enumerate(tiaom_i):
            end = tiaom_i[n+1] if n+1<len(tiaom_i) else len(paras)
            has = any(texts[j].startswith('【编注】') for j in range(i+1,end))
            has_duibi = any('对比辨析' in texts[j] for j in range(i+1,end))
            cov.append((i, has, has_duibi))
        miss=[c for c in cov if not c[1]]
        P(f"条目说明句覆盖={sum(1 for c in cov if c[1])}/{len(cov)} 缺失例={[(i,texts[i][:30]) for i,_,_ in miss][:5]}")
        duibi_per_sec={}
        for i,pre,seq in tiaom:
            s=sec_of_prefix(pre) or '?'
            end_i=None
        duibi=[(i,texts[i][:50]) for i,tx in enumerate(texts) if tx.startswith('【编注】对比辨析')]
        secduibi={}
        for i,tx in duibi:
            prev=[x for x,_,_ in tiaom if x<i]
            k=max(prev) if prev else -1
            pre=[p for x,p,_ in [(a,b,c) for a,b,c in tiaom] ]
            # 找该编注所属节：向前最近Heading3
            hprev=[h for h,_ in [(a,b) for a,b in h3] if h<i]
            secno = None
            for h,t2 in h3:
                if h<i and re.match(r'\d',t2): secno=t2.split('\u3000')[0]
            secduibi.setdefault(secno,0); secduibi[secno]+=1
        P(f"对比辨析按节={secduibi} 总={len(duibi)}")
    # E0E0E0 归属自动核验
    e0=[i for i,s in enumerate(shds) if s=='E0E0E0']
    if e0:
        bad_attr=[]; img_e0=[]; tongshi_e0=[]
        for i in e0:
            # 所属题：向前最近题号块
            kq=max([x[0] for x in qhao if x[0]<=i], default=None)
            if kq is None: bad_attr.append((i,'题前',texts[i][:30])); continue
            # 该题的【答案】行位置
            nxt_q=[x[0] for x in qhao if x[0]>i]
            rng=range(kq, nxt_q[0] if nxt_q else len(paras))
            ans_i=[j for j in rng if '【答案】' in texts[j]]
            if not (ans_i and i < ans_i[0]):
                bad_attr.append((i,'在答案行后',texts[i][:30]))
            if paras[i].findall('.//'+q(WP,'inline')): img_e0.append(i)
            if '题型通式' in texts[i]: tongshi_e0.append(i)
        P(f"E0E0E0段={len(e0)} 归属违例={len(bad_attr)} {bad_attr[:5]} 图段挂E0={len(img_e0)} 通式句挂E0={len(tongshi_e0)}")
        # 反向：题号块起至【答案】行前的段落中，非E0E0E0的（图段豁免）
        miss_e0=[]
        for n,(kq,pre,seq) in enumerate(qhao):
            nxt_q=qhao[n+1][0] if n+1<len(qhao) else len(paras)
            ans_i=[j for j in range(kq,nxt_q) if '【答案】' in texts[j]]
            end=ans_i[0] if ans_i else nxt_q
            for j in range(kq,end):
                if shds[j] is None and not paras[j].findall('.//'+q(WP,'inline')) and texts[j].strip() and styles[j] not in ('JieMingMao','Heading3') and shds[j] is None:
                    miss_e0.append((j,texts[j][:30]))
        P(f"题干区漏挂E0段={len(miss_e0)} {miss_e0[:6]}")
    # 选项行tab/粘连 XML细节
    for i,tx in enumerate(texts):
        ntab=len(paras[i].findall('.//'+q(W,'tab')))
        if ntab and re.search(r'[AB]．', tx):
            seq=[]
            for ch in paras[i]:
                if ch.tag==q(W,'r'):
                    for el in ch:
                        if el.tag==q(W,'t'): seq.append('T:'+repr((el.text or '')[:12]))
                        elif el.tag==q(W,'tab'): seq.append('TAB')
                        elif el.tag==q(W,'drawing'): seq.append('IMG')
                elif ch.tag==q(M,'oMath'): seq.append('MATH')
            if tag=='X1' or len(out)<2000:
                P(f"tab选项行@p#{i} 结构={seq[:24]}")
            if tag=='X1': break_ = None
    # B 导航表
    if tag=='B':
        tbl=body.find(q(W,'tbl'))
        if tbl is not None:
            rows=tbl.findall(q(W,'tr'))
            P(f"导航表: 行数={len(rows)}")
            for tr in rows:
                cells=[''.join(t.text or '' for t in tc.findall('.//'+q(W,'t'))) for tc in tr.findall(q(W,'tc'))]
                P(f"    {'|'.join(cells)}")
    # 孤儿图引个案：B5+C2
    imgp=[i for i,p in enumerate(paras) if p.findall('.//'+q(WP,'inline'))]
    for i,tx in enumerate(texts):
        if re.search(r'如图|图所示|如下图', tx) and i not in imgp:
            near=[(abs(j-i),j) for j in imgp]
            near.sort()
            if near and near[0][0]>6:
                # 所属题
                kq=max([x[0] for x in qhao if x[0]<=i], default=None)
                inq=[j for d,j in near if kq is not None and j>kq]
                P(f"孤儿图引个案@p#{i} 最近图距离={near[0][0]} 同题内最近图距离={(min([abs(j-i) for j in inq]) if inq else None)} 文={tx[:50]!r}")

open(os.path.join(OUT,'精查3_四件.txt'),'w',encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
