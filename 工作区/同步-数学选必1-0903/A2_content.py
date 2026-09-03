# -*- coding: utf-8 -*-
"""A2第2章审计·内容向：七类底纹/题号核验/统计段求和/字号归一/禁排清零/空格卫生/
图形态/标签完整性/E导航表/F-G-H段0属性。只读。"""
import sys, io, os, zipfile, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)
def tag(e): return etree.QName(e).localname

FILES = {
 'X2': r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
 'I2': r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
 'E':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
 'F':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
 'G':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
 'H':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}
QTY = {'X2':13,'I2':0,'E':92,'F':90,'G':68,'H':89}
EXPECT_TGN = {'X2':8,'I2':0,'E':62,'F':61,'G':50,'H':61}   # 题型组数
EXPECT_JB = {'X2':0,'I2':0,'E':6,'F':8,'G':2,'H':12}        # 讲部数
EXPECT_E0 = {'X2':18,'I2':0,'E':161,'F':164,'G':118,'H':198} # ⑦题干底纹今晨值
QSTART = {'E':1,'F':93,'G':183,'H':251}
QEND = {'E':92,'F':182,'G':250,'H':339}

NUMPAT = re.compile(r'^(\d+(?:\.\d+)+-(\d+))．')
TGNPAT = re.compile(r'^(\d+(?:\.\d+)+)\s')

def para_text(p, math=True):
    out=[]
    for t in p.iter():
        ln=tag(t)
        if ln=='t' and t.text: out.append(t.text)
        elif ln=='delText' and t.text: out.append(t.text)
    return ''.join(out)

def linearize(p):
    """文字/公式交错线性流：⟦公式⟧、⟦图⟧"""
    out=[]
    def walk(el, in_math):
        for ch in el:
            ln=tag(ch)
            if ln=='oMath':
                s=''.join(t.text or '' for t in ch.iter(qm('t')))
                out.append('⟦%s⟧'%s); walk(ch, True)
            elif ln=='oMathPara':
                walk(ch, in_math)
            elif ln in ('drawing','pict','object'):
                out.append('⟦图⟧')
            elif ln=='r':
                if not in_math:
                    for t in ch.findall(q('t')):
                        if t.text: out.append(t.text)
                else:
                    pass
            else:
                walk(ch, in_math)
    walk(p, False)
    return ''.join(out)

def run_props(r):
    rpr=r.find(q('rPr'))
    sz=None; shd=None; b=False; color=None; strike=0; hl=None; vanish=False
    if rpr is not None:
        e=rpr.find(q('sz'))
        if e is not None: sz=e.get(q('val'))
        e=rpr.find(q('shd'))
        if e is not None: shd=(e.get(q('val')),e.get(q('fill')))
        b=rpr.find(q('b')) is not None
        e=rpr.find(q('color'))
        if e is not None: color=e.get(q('val'))
        strike=len(rpr.findall(q('strike')))+len(rpr.findall(q('dstrike')))
        e=rpr.find(q('highlight'))
        if e is not None: hl=e.get(q('val'))
        vanish=rpr.find(q('vanish')) is not None
    return sz,shd,b,color,strike,hl,vanish

for code,path in FILES.items():
    print('='*100)
    print('【%s】%s'%(code,os.path.basename(path)))
    z=zipfile.ZipFile(path)
    doc=etree.fromstring(z.read('word/document.xml'))
    styles=etree.fromstring(z.read('word/styles.xml'))
    body=doc.find(q('body'))
    # body子元素序列（前12个）
    seq=[]
    for ch in body:
        ln=tag(ch)
        if ln=='p': seq.append('p')
        elif ln=='tbl': seq.append('TBL')
        elif ln=='sectPr': seq.append('SECT')
    first_tbl=seq.index('TBL') if 'TBL' in seq else -1
    print('body子元素序列（前14）=%s ... 表格总数=%d 首表位置=%d'%(seq[:14],seq.count('TBL'),first_tbl))
    # 表格内段落文本抽样（首表=E导航表）
    if first_tbl>=0:
        tbls=body.findall(q('tbl'))
        t0=tbls[0]
        rows=t0.findall(q('tr'))
        print('首表行数=%d'%len(rows))
        for ri,row in enumerate(rows[:4]):
            cells=[''.join(x.text or '' for x in tc.iter(q('t'))) for tc in row.findall(q('tc'))]
            print('  行%d: %s'%(ri,' | '.join(cells)[:150]))
        lastrow=rows[-1]
        cells=[''.join(x.text or '' for x in tc.iter(q('t'))) for tc in lastrow.findall(q('tc'))]
        print('  末行: %s'%(' | '.join(cells)[:150]))

    paras=body.findall(q('p'))
    # 样式表解析
    style_rpr={}
    for s in styles.findall(q('style')):
        sid=s.get(q('styleId'))
        rpr=s.find(q('rPr'))
        d={}
        if rpr is not None:
            e=rpr.find(q('sz'));  d['sz']=e.get(q('val')) if e is not None else None
            e=rpr.find(q('rFonts'))
            if e is not None: d['fonts']=(e.get(q('ascii')),e.get(q('eastAsia')))
        bo=s.find(q('basedOn'))
        d['basedOn']=bo.get(q('val')) if bo is not None else None
        style_rpr[sid]=d
    def eff_style_sz(sid, depth=0):
        seen=set()
        while sid and sid in style_rpr and depth<10:
            d=style_rpr[sid]
            if d.get('sz'): return d['sz'], d.get('fonts')
            sid=d.get('basedOn'); depth+=1
        return None,None

    # ---------- 段级审计循环 ----------
    e0_paras=[]       # ⑦题干底纹段
    adc_no_style=[]   # 无样式ADC2DA段（隐藏属性检查）
    qblocks=[]        # 题号块 (idx, 题号, 序号, 档位)
    entries=[]        # 条目号
    tg_titles=[]      # 题型标题
    jb_titles=[]      # 讲部标题
    sz_off=[]         # 字号偏离（非数学区、例外外）
    jc_bad=0; ind_bad=0; sp_bad=[]
    chip_runs=[]      # 块标签
    sub1_runs=[]      # 第一子层
    ans_runs=[]       # 答案值文字
    omml_grey=0       # 公式挂灰
    qnum_grey=0; entry_grey=0
    label_ans=0; label_know=0; label_empty=[]; know_noprefix=[]
    bianzhu=0; analysis=0
    tgn_stat=[]       # 题型统计段
    sect_stat=[]      # 节统计段
    sect_ids=set()
    anchor_id=None
    for s in styles.findall(q('style')):
        n=s.find(q('name'))
        if n is not None and n.get(q('val'))=='节名锚': anchor_id=s.get(q('styleId'))
    h3id=None
    for s in styles.findall(q('style')):
        n=s.find(q('name'))
        if n is not None and n.get(q('val'))=='heading 3': h3id=s.get(q('styleId'))

    body_sect = body.find(q('sectPr'))
    for idx,p in enumerate(paras):
        ppr=p.find(q('pPr'))
        pstyle=None; pshd=None; jc=None; has_ind=False; sp=None; vanish_p=False
        if ppr is not None:
            ps=ppr.find(q('pStyle'))
            pstyle=ps.get(q('val')) if ps is not None else None
            sh=ppr.find(q('shd'))
            if sh is not None: pshd=sh.get(q('fill'))
            e=ppr.find(q('jc'))
            jc=e.get(q('val')) if e is not None else None
            has_ind=ppr.find(q('ind')) is not None
            e=ppr.find(q('spacing'))
            if e is not None: sp=(e.get(q('line')),e.get(q('lineRule')),e.get(q('before')),e.get(q('after')))
            vanish_p=ppr.find(q('rPr'))is not None and ppr.find(q('rPr')).find(q('vanish')) is not None
        txt=para_text(p)
        lin=linearize(p)
        # ⑦
        if pshd and pshd.upper()=='E0E0E0': e0_paras.append((idx,lin[:40]))
        if pshd and pshd.upper()=='ADC2DA' and pstyle in (None,'a'):
            # 检查vanish
            v=vanish_p
            adc_no_style.append((idx, txt[:40], v))
        # 节标题
        if pstyle==h3id:
            m=re.match(r'^(\d+(?:\.\d+)*)\s*([\u4e00-\u9fff（].*?)?\u3000?本节(\d+)题', txt)
            m2=re.search(r'本节(\d+)题[:：]?(?:简单(\d+)｜中档(\d+)｜难(\d+))?', txt)
            sect_stat.append((idx, txt.split('\u3000')[0], int(m2.group(1)) if m2 else None,
                              (int(m2.group(2)),int(m2.group(3)),int(m2.group(4))) if m2 and m2.group(2) else None))
        # 题型/讲部标题（C6D4E3）
        if pshd and pshd.upper()=='C6D4E3':
            m=TGNPAT.match(txt)
            if m:
                m3=re.search(r'\u3000(\d+)题[：:]', txt)
                tg_titles.append((idx, m.group(1), int(m3.group(1)) if m3 else None, txt[:40]))
            else:
                jb_titles.append((idx, txt[:50]))
        # 题号块/条目号
        m=NUMPAT.match(txt)
        if m:
            rest=txt[m.end():]
            is_q = bool(re.match(r'^（(简单·保60%|中档·保80%|难·冲100%|衔接必会)·卡壳看答案）', rest))
            if is_q:
                dang=re.match(r'^（(简单|中档|难|衔接必会)', rest).group(1)
                qblocks.append((idx, m.group(1), int(m.group(2)), dang))
            else:
                entries.append((idx, m.group(1), int(m.group(2))))
        # run级
        for r in p.findall(q('r')):
            sz,shd,b,color,strike,hl,van=run_props(r)
            rt=''.join(t.text or '' for t in r.findall(q('t')))
            if shd and (shd[1] or '').upper()=='C9C9C9':
                if NUMPAT.match(txt) and rt and txt.startswith(rt[:2] if rt else '\x00'):
                    pass
                # 分桶在下方统一
        # 标签计数
        if txt.startswith('【答案】'): label_ans+=1
        if txt.startswith('【知识点】'):
            label_know+=1
            v=txt.replace('【知识点】','').strip()
            if not v: label_empty.append((idx,'知识点空'))
            elif not re.match(r'^\d+(\.\d+)+', v): know_noprefix.append((idx,v[:40]))
        if txt.startswith('【答案】') and not txt.replace('【答案】','').strip():
            label_empty.append((idx,'答案空'))
        if txt.startswith('【编注】'): bianzhu+=1
        if txt.startswith('【分析】'): analysis+=1
        # 段落级格式
        if jc not in (None,'left'): jc_bad+=1
        if has_ind: ind_bad+=1

    # C9C9C9 分桶（重跑一次，按段落上下文）
    for idx,p in enumerate(paras):
        ppr=p.find(q('pPr'))
        pstyle=None
        if ppr is not None:
            ps=ppr.find(q('pStyle'))
            pstyle=ps.get(q('val')) if ps is not None else None
        txt=para_text(p)
        m=NUMPAT.match(txt)
        is_qblk = any(qb[0]==idx for qb in qblocks)
        is_entry = any(en[0]==idx for en in entries)
        for r in p.findall(q('r')):
            sz,shd,b,color,strike,hl,van=run_props(r)
            rt=''.join(t.text or '' for t in r.findall(q('t')))
            if shd and (shd[1] or '').upper()=='C9C9C9':
                if m and txt.startswith(rt) and re.match(r'^\d+(\.\d+)+-\d+．$', rt):
                    if is_qblk: qnum_grey+=1
                    else: entry_grey+=1
                elif re.match(r'^（\d+）$', rt):
                    sub1_runs.append((idx,rt))
                elif '【' in rt and '】' in rt:
                    chip_runs.append((idx,rt[:20]))
                else:
                    ans_runs.append((idx,rt[:30]))
    # OMML挂灰
    for om in doc.iter(qm('oMath')):
        for mr in om.iter(qm('r')):
            rpr=mr.find(q('rPr'))
            if rpr is not None and rpr.find(q('shd')) is not None and (rpr.find(q('shd')).get(q('fill')) or '').upper()=='C9C9C9':
                omml_grey+=1
        for cp in om.iter(qm('ctrlPr')):
            rpr=cp.find(q('rPr'))
            if rpr is not None and rpr.find(q('shd')) is not None and (rpr.find(q('shd')).get(q('fill')) or '').upper()=='C9C9C9':
                omml_grey+=1

    print('--- 七类底纹 ---')
    print('②题号块底纹run数=%d（题量=%d）｜⑤条目号底纹run数=%d｜④块标签run数=%d｜⑥第一子层run数=%d｜①答案值文字run=%d＋公式挂灰=%d' % (
        qnum_grey,QTY[code],entry_grey,len(chip_runs),len(sub1_runs),len(ans_runs),omml_grey))
    print('③ADC2DA无样式段（含vanish标记）=%s'%adc_no_style)
    print('⑦E0E0E0题干底纹段数=%d（今晨基线=%d，差=%d）'%(len(e0_paras),EXPECT_E0[code],len(e0_paras)-EXPECT_E0[code]))
    print('  E0E0E0段首20个样本：')
    for i,(idx,t) in enumerate(e0_paras[:20]): print('    [%d] %r'%(idx,t))
    print('--- 题号核验 ---')
    print('题块数=%d（文件名题量=%d）｜档位分布=%s'%(len(qblocks),QTY[code],
        {d:sum(1 for x in qblocks if x[3]==d) for d in ('简单','中档','难','衔接必会')}))
    seqs={}
    for idx,num,sn,dang in qblocks:
        pref=num.rsplit('-',1)[0]
        seqs.setdefault(pref,[]).append(sn)
    bad=0
    for pref,lst in seqs.items():
        if lst!=list(range(1,len(lst)+1)): bad+=1; print('  序列异常：%s %s'%(pref,lst[:20]))
    print('节内序列连续性：组数=%d 异常组=%d'%(len(seqs),bad))
    if code in QSTART:
        alltgs=sorted(sn for _,_,sn,_ in qblocks)
        print('全卷序号范围=%d..%d（预期%d..%d）'%(alltgs[0] if alltgs else -1, alltgs[-1] if alltgs else -1, QSTART[code],QEND[code]))
        gaps=[n for n in range(QSTART[code],QEND[code]+1) if n not in set(alltgs)]
        print('区间内缺号=%s'%(gaps[:20] if gaps else '无'))
    print('条目号序列=%s'%[ (idx,num,sn) for idx,num,sn in entries ])
    print('--- 统计段恒等 ---')
    tg_sum=sum(t[2] or 0 for t in tg_titles)
    print('题型标题数=%d（预期%d）｜讲部标题数=%d（预期%d）｜题型统计段题数Σ=%d'%(len(tg_titles),EXPECT_TGN[code],len(jb_titles),EXPECT_JB[code],tg_sum))
    for t in jb_titles: print('  讲部: %r'%(t[1],))
    ss=0; s3=(0,0,0)
    for idx,name,n,tri in sect_stat:
        ss+=n or 0
        if tri: s3=tuple(a+b for a,b in zip(s3,tri))
    print('节统计段Σ题数=%d 三档Σ=%s 节标题数=%d'%(ss,s3,len(sect_stat)))
    print('恒等：题型Σ(%d)+讲部0 == 节Σ(%d) == 文件名(%d) -> %s'%(tg_sum,ss,QTY[code],'PASS' if tg_sum==ss==QTY[code] else 'FAIL'))
    print('--- 标签完整性 ---')
    print('【答案】=%d 【知识点】=%d 【编注】=%d 【分析】=%d 空标签=%s'%(label_ans,label_know,bianzhu,analysis,label_empty[:5]))
    print('【知识点】无节号前缀=%s'%(know_noprefix[:5] if know_noprefix else '无'))
    print('--- 段落格式 ---')
    print('jc非左=%d w:ind存在段=%d'%(jc_bad,ind_bad))
    # 字号归一
    sz_count={}
    off_ex=[]
    for idx,p in enumerate(paras):
        ppr=p.find(q('pPr'))
        pstyle=None
        if ppr is not None:
            ps=ppr.find(q('pStyle'))
            pstyle=ps.get(q('val')) if ps is not None else None
        txt=para_text(p)
        is_anchor = pstyle==anchor_id
        for r in p.iter(q('r')):
            # 排除数学区内 m:r（其tag是r但ns是M）
            if not isinstance(r.tag,str) or not r.tag.startswith('{%s}'%W): continue
            sz,shd,b,color,strike,hl,van=run_props(r)
            ssz,fonts=eff_style_sz(pstyle) if sz is None else (sz,None)
            if ssz is None: ssz='24(docDef)'
            sz_count[ssz]=sz_count.get(ssz,0)+1
            if ssz not in ('24','24(docDef)','32','28','18') and not is_anchor:
                off_ex.append((idx,ssz,txt[:20]))
    print('--- 字号归一（正文run effective sz 分布）---')
    print('sz分布=%s'%sz_count)
    print('例外外偏离样本（≤10）=%s'%off_ex[:10])
    z.close()
print('DONE')
