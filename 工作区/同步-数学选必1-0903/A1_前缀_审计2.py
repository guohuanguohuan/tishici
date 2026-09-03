# -*- coding: utf-8 -*-
"""A1审计第二轮精查：题号/条目号分离＋节内连续、B/C跨卷、括注、空格卫生（XML精确）、
w:tab定位、孤儿图引距离、【分析】超量定位、空标签精确、创作句、I1〔基〕〔进〕与编注分类、
题干底纹归属抽验料、灰底抽检料"""
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
    return doc, body, [p for p in body if p.tag==q(W,'p')]

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

out = []
P = out.append
for tag in TAGS:
    doc, body, paras = load(tag)
    texts = [p_text(p) for p in paras]
    styles = [p_style(p) for p in paras]
    shds = [p_shd(p) for p in paras]
    P(f"\n########## {tag}")

    # ---- 题号/条目号分离：题号=前缀3个点(4段)；条目号=前缀2个点(3段)
    qhao = []   # (pidx, prefix, seq)
    tiaom = []
    for i,p in enumerate(paras):
        for r in p.findall(q(W,'r')):
            rPr = r.find(q(W,'rPr'))
            sh = rPr.find(q(W,'shd')) if rPr is not None else None
            if sh is None or sh.get(q(W,'fill'))!='C9C9C9': continue
            t = ''.join(x.text or '' for x in r.findall(q(W,'t')))
            m = re.fullmatch(r'(\d+(?:\.\d+)+)-(\d+)．', t)
            if m:
                pre = m.group(1); seq = int(m.group(2))
                if pre.count('.') == 3: qhao.append((i,pre,seq,t))
                elif pre.count('.') == 2: tiaom.append((i,pre,seq,t))
    P(f"题号run={len(qhao)} 条目号run={len(tiaom)}")
    # 节内连续（节=题号前缀前两段 a.b）
    secmap = {}
    for i,pre,seq,t in qhao:
        sec = '.'.join(pre.split('.')[:2])
        secmap.setdefault(sec, []).append(seq)
    bad = []
    for sec, seqs in secmap.items():
        if sorted(seqs) != list(range(1, len(seqs)+1)):
            bad.append((sec, sorted(seqs)))
    P("题号按节：" + '; '.join(f"{s}:{len(v)}题(1..{max(v)})" for s,v in sorted(secmap.items())))
    P(f"节内序列断点/重复={bad if bad else '无（全部1..N连续）'}")
    # 条目号节内连续
    tm = {}
    for i,pre,seq,t in tiaom:
        tm.setdefault(pre, []).append(seq)
    tbad = {k:sorted(v) for k,v in tm.items() if sorted(v)!=list(range(1,len(v)+1))}
    P(f"条目号族：{ {k:len(v) for k,v in tm.items()} } 序列异常={tbad if tbad else '无'}")
    # 括注（仅题号行）
    badann = []
    for i,pre,seq,t in qhao:
        line = texts[i]
        if tag=='X1':
            ok = re.search(r'（衔接必会·卡壳看答案）', line)
        else:
            ok = re.search(r'（(简单|中档|难)·(保60%|保80%|冲100%)·卡壳看答案）', line)
        if not ok: badann.append((i,line[:70]))
    P(f"题号括注违例={len(badann)} {badann[:4]}")
    # 档位计数（B/C）
    if tag in ('B','C'):
        dd = {'简单':0,'中档':0,'难':0}
        for i,pre,seq,t in qhao:
            m = re.search(r'（(简单|中档|难)·', texts[i])
            if m: dd[m.group(1)] += 1
        P(f"档位分布={dd} Σ={sum(dd.values())}")
    # 题号块底纹只盖题号本身（该run文本恰=题号）＋加粗
    nb = 0
    for i,pre,seq,t in qhao:
        p = paras[i]
        # 找到该run，看其rPr是否有b
        for r in p.findall(q(W,'r')):
            rPr = r.find(q(W,'rPr'))
            rt = ''.join(x.text or '' for x in r.findall(q(W,'t')))
            if rt == t and rPr is not None:
                sh = rPr.find(q(W,'shd'))
                b = rPr.find(q(W,'b'))
                if sh is not None and sh.get(q(W,'fill'))=='C9C9C9' and b is not None: nb += 1
    P(f"题号块run（C9C9C9＋加粗、文本恰=题号）={nb}")

    # ---- 空格卫生 XML精确：单个w:t内连续双半空格；单w:t内半/全角空格+全角标点；真段尾空格
    dbl = []; fwp = []; trl = []
    for i,p in enumerate(paras):
        for t in p.findall('.//'+q(W,'t')):
            s = t.text or ''
            if '  ' in s: dbl.append((i, s[:50]))
            for mm in re.finditer(r'[ \u3000]([，。；：、！？）》】])', s):
                fwp.append((i, s[max(0,mm.start()-10):mm.end()+4]))
        # 真段尾：最后含文本的w:t（其后无oMath）
        last_t = None; after_math = False
        for ch in p.iter():
            if ch.tag == q(M,'oMath'): after_math = True; continue
            if ch.tag == q(W,'t') and (ch.text or ''):
                if not after_math or True: last_t = ch  # 记录最后一个w:t
        if last_t is not None and (last_t.text or '').rstrip() != (last_t.text or '') \
           and last_t.text.endswith((' ','\u3000')):
            # 检查该w:t是否为段内最后内容元素（粗略：其后同段无oMath/w:t）
            tail = True
            seen = False
            for ch in p.iter():
                if ch is last_t: seen = True; continue
                if seen and ch.tag in (q(W,'t'), q(M,'oMath')) and (ch.tag==q(M,'oMath') or (ch.text or '')):
                    tail = False; break
            if tail: trl.append((i, repr(last_t.text[-20:])))
    P(f"[8精] 单w:t内连续双半空格={len(dbl)} {dbl[:5]}")
    P(f"[8精] 单w:t内空格+全角标点={len(fwp)} {fwp[:6]}")
    P(f"[8精] 真段尾空格={len(trl)} {trl[:5]}")

    # ---- w:tab定位
    tabs = []
    for i,p in enumerate(paras):
        for r in p.findall(q(W,'r')):
            for _ in r.findall(q(W,'tab')):
                tabs.append((i, texts[i][:50]))
    P(f"[8] w:tab总数={len(tabs)} 涉及段={len(set(t[0] for t in tabs))}")
    for tset in tabs[:6]: P(f"    tab@p#{tset[0]} {tset[1]!r}")

    # ---- 孤儿图引：引用段→最近图段距离
    imgp = set()
    for i,p in enumerate(paras):
        if p.findall('.//'+q(WP,'inline')) or p.findall('.//'+q(WP,'anchor')):
            imgp.add(i)
    orph = []
    dists = []
    for i,tx in enumerate(texts):
        if re.search(r'如图|图甲|图乙|图丙|图丁|图所示|如下图|图1|图2|图3|图①|图②|图③', tx):
            if i in imgp: dists.append((i,0)); continue
            near = [j for j in imgp if abs(j-i) <= 6]
            if near:
                dists.append((i, min(abs(j-i) for j in near)))
            else:
                orph.append((i, tx[:60]))
    far = [(i,d) for i,d in dists if d >= 3]
    P(f"[9] 图引段总数={len(dists)} 距图段≥3段={len(far)} {far[:10]}")
    P(f"[9] 孤儿图引（±6段无图）={len(orph)} {orph[:6]}")

    # ---- 【分析】块定位（超量）
    ana = [(i, texts[i][:60]) for i,tx in enumerate(texts) if '【分析】' in tx]
    if tag in ('B','C'):
        from collections import Counter
        # 每题块一个分析？统计题号段索引
        qidx = [q[0] for q in qhao]
        extra = []
        for k,(i,tx) in enumerate(ana):
            # 找它属于哪个题：前一个题号
            prev = [x for x in qidx if x < i]
            nxt = [x for x in qidx if x > i]
            if prev:
                # 该题内分析数
                pass
        # 简化：按题分组数分析
        perq = {}
        for i,tx in ana:
            prev = max([x for x in qidx if x < i], default=-1)
            perq.setdefault(prev, []).append(i)
        multi = {k:v for k,v in perq.items() if len(v)>1}
        P(f"[12] 分析块={len(ana)} 多分析题数={len(multi)} 例={[(k, texts[k][:30] if k>=0 else '题前', len(v)) for k,v in list(multi.items())[:6]]}")

    # ---- 空标签精确（【答案】/【知识点】后无文字且无紧邻oMath）
    empt = []
    for i,tx in enumerate(texts):
        for lab in ('答案','知识点'):
            for mm in re.finditer(f'【{lab}】', tx):
                rest_text = tx[mm.end():]
                p = paras[i]
                # 该段或下一段是否有oMath/后续文字
                has_om = len(p.findall('.//'+q(M,'oMath')))>0 or \
                         (i+1<len(paras) and len(paras[i+1].findall('.//'+q(M,'oMath')))>0 and not rest_text.strip())
                if not rest_text.strip() and not has_om:
                    empt.append((i, tx[:50]))
    P(f"[12] 真·空标签={len(empt)} {empt[:4]}")

    # ---- 创作句线性数学细节
    for i,tx in enumerate(texts):
        if ('【编注】' in tx or '题型通式' in tx):
            hits = re.findall(r'[√²³¹⁰⁴⁵⁶⁷⁸⁹₀-₉]+', tx)
            if hits and len(paras[i].findall('.//'+q(M,'oMath')))==0:
                P(f"[8] 创作句线性数学@p#{i}: 命中字符={hits} 文={tx[:80]!r}")

    # ---- I1: 〔基〕〔进〕计数＋编注分类（说明句/对比辨析）
    if tag == 'I1':
        ji = sum(1 for tx in texts if re.match(r'\d+\.\d+-\d+．〔基〕', tx))
        jin = sum(1 for tx in texts if re.match(r'\d+\.\d+-\d+．〔进〕', tx))
        P(f"[I1] 条目〔基〕={ji} 〔进〕={jin} Σ={ji+jin}")
        duibi = [(i,tx[:50]) for i,tx in enumerate(texts) if '对比辨析' in tx]
        P(f"[I1] 对比辨析段={len(duibi)} {duibi[:8]}")
        bz = [(i,tx[:60]) for i,tx in enumerate(texts) if tx.startswith('【编注】')]
        P(f"[I1] 【编注】起段={len(bz)}（应=说明句47＋对比辨析引句）")

    # ---- 题干底纹归属抽验料：E0E0E0段样本（首5段＋随机）
    e0 = [i for i,s in enumerate(shds) if s=='E0E0E0']
    if e0:
        P(f"[⑦] E0E0E0段数={len(e0)} 样本（首3＋中2＋末2）:")
        for i in e0[:3]+e0[len(e0)//2:len(e0)//2+2]+e0[-2:]:
            P(f"    p#{i}: {texts[i][:55]!r}")

open(os.path.join(OUT,'精查_四件.txt'),'w',encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
