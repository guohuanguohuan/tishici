# -*- coding: utf-8 -*-
"""A2第2章审计·修正核验：节分组题号/【知识点】含计数/E0E0E0双路复核/空格卫生/禁排清零/
图形态/21半点run定点解剖/选项分隔。只读。"""
import sys, io, os, zipfile, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
PR = 'http://schemas.openxmlformats.org/package/2006/relationships'
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
SECTS = {'E':['2.1','2.2.1','2.2.2','2.2.3','2.2.4','2.3.1','2.3.2','2.3.3'],
         'F':['2.3.4','2.4','2.5.1','2.5.2'],
         'G':['2.6.1','2.6.2','2.7.1','2.7.2'],
         'H':['2.8'],'X2':['2.8'],'I2':[]}
QTY={'X2':13,'I2':0,'E':92,'F':90,'G':68,'H':89}
NUMPAT = re.compile(r'^(\d+(?:\.\d+)+)-(\d+)．')

def para_text(p):
    return ''.join(t.text or '' for t in p.iter() if tag(t)=='t')

for code,path in FILES.items():
    print('='*100)
    print('【%s】'%code)
    z=zipfile.ZipFile(path)
    doc=etree.fromstring(z.read('word/document.xml'))
    body=doc.find(q('body'))
    paras=body.findall(q('p'))
    raw=z.read('word/document.xml').decode('utf-8')

    # --- E0E0E0 双路复核（regex on raw + lxml 段级）---
    n_raw=raw.count('E0E0E0')
    n_para=0
    for p in paras:
        ppr=p.find(q('pPr'))
        if ppr is not None:
            sh=ppr.find(q('shd'))
            if sh is not None and (sh.get(q('fill')) or '').upper()=='E0E0E0': n_para+=1
    # 表格内段落
    n_tbl=0
    for tbl in body.findall(q('tbl')):
        for p in tbl.iter(q('p')):
            ppr=p.find(q('pPr'))
            if ppr is not None:
                sh=ppr.find(q('shd'))
                if sh is not None and (sh.get(q('fill')) or '').upper()=='E0E0E0': n_tbl+=1
    print('E0E0E0: regex全XML计数=%d  lxml段级=%d（正文段） 表内段=%d'%(n_raw,n_para,n_tbl))
    print('F2F2F2: regex计数=%d（应为0）  ADC2DA regex=%d C6D4E3 regex=%d C9C9C9 regex=%d'%(
        raw.count('F2F2F2'),raw.count('ADC2DA'),raw.count('C6D4E3'),raw.count('C9C9C9')))
    print('A6A6A6=%d D9D9D9=%d w:bdr字符边框=%d'%(raw.count('A6A6A6'),raw.count('D9D9D9'),len(re.findall(r'<w:bdr\b',raw))))

    # --- 题号按节分组 ---
    if SECTS[code]:
        bysect={s:[] for s in SECTS[code]}
        unmatched=[]
        for idx,p in enumerate(paras):
            txt=para_text(p)
            m=NUMPAT.match(txt)
            if m:
                rest=txt[m.end():]
                if re.match(r'^（(简单·保60%|中档·保80%|难·冲100%|衔接必会)·卡壳看答案）',rest):
                    num=m.group(1); sn=int(m.group(2))
                    hit=None
                    for s in SECTS[code]:
                        if num==s or num.startswith(s+'.'):
                            hit=s; break
                    if hit: bysect[hit].append(sn)
                    else: unmatched.append(num)
        tot=0; ok=True
        for s,lst in bysect.items():
            lst.sort()
            exp=list(range(1,len(lst)+1))
            if lst!=exp: ok=False; print('  节%s序列异常: %s'%(s,lst[:30]))
            tot+=len(lst)
        print('节分组题号：总题数=%d 各节=%s 节内1..N连续=%s 未匹配=%s'%(
            tot,{s:len(l) for s,l in bysect.items()},'PASS' if ok else 'FAIL',unmatched[:5]))

    # --- 【知识点】含计数 ---
    n_know=0; n_know_nopfx=[]; n_ans=0
    for idx,p in enumerate(paras):
        txt=para_text(p)
        if '【知识点】' in txt:
            n_know+=1
            v=txt.split('【知识点】')[-1].strip()
            if v and not re.match(r'^\d+(\.\d+)+',v): n_know_nopfx.append((idx,v[:30]))
        if '【答案】' in txt: n_ans+=1
    # 表内段落也查（不适用一般）
    print('含【知识点】段=%d（题量%d）含【答案】段=%d 无节号前缀值=%s'%(n_know,QTY[code],n_ans,n_know_nopfx[:5]))

    # --- 空格卫生 ---
    dbl_sp=[]; fw_sp=[]; tail_sp=[]; nbsp_run=[]; tab_n=0
    for idx,p in enumerate(paras):
        txt=para_text(p)
        lin=[]
        for t in p.iter():
            if tag(t)=='t' and t.text: lin.append(t.text)
        # 连续双半空格（跨run拼接后）
        full=''.join(lin)
        for m in re.finditer(r'[ ]{2,}', full):
            dbl_sp.append((idx,m.group(0)[:6],full[max(0,m.start()-10):m.end()+10])); break
        for m in re.finditer(r'[\u3000\u00a0 ]+[，。；：、？！]', full):
            fw_sp.append((idx,full[max(0,m.start()-8):m.end()+8])); break
        if full!=full.rstrip(' \u00a0'):
            tail_sp.append((idx,full[-12:]))
        if re.search(r'\u00a0{2,}', full):
            nbsp_run.append((idx,re.search(r'\u00a0{2,}',full).group(0)[:6],full[:40]))
    tab_n=len(doc.findall('.//'+q('tab')))
    print('连续双半空格段=%d（首5例%s）'%(len(dbl_sp),dbl_sp[:5]))
    print('全角标点前空格段=%d（首5例%s）'%(len(fw_sp),fw_sp[:5]))
    print('段尾空格段=%d（首5例%s）  连续nbsp段=%d（首5例%s） w:tab=%d'%(len(tail_sp),tail_sp[:5],len(nbsp_run),nbsp_run[:5],tab_n))

    # --- 禁排清零 ---
    ins=len(doc.findall('.//'+q('ins'))); dele=len(doc.findall('.//'+q('del')))
    strike=len(re.findall(r'<w:strike\b',raw))+len(re.findall(r'<w:dstrike\b',raw))
    hl=len(re.findall(r'<w:highlight\b',raw))
    pbb=len(re.findall(r'<w:pageBreakBefore\b',raw)); kn=len(re.findall(r'<w:keepNext\b',raw)); kl=len(re.findall(r'<w:keepLines\b',raw))
    brs=doc.findall('.//'+q('br'))
    br_page=len([b for b in brs if b.get(q('type'))=='page'])
    colors=set()
    for c in doc.iter(q('color')):
        v=c.get(q('val'))
        if v and v.upper() not in ('auto','FFFFFF'): colors.add(v)
    omp=doc.findall('.//'+qm('oMathPara'))
    omp_standalone=0
    for om in omp:
        # 所在段
        par=om.getparent()
        while par is not None and tag(par)!='p': par=par.getparent()
        if par is not None:
            t=para_text(par)
            if not t.strip(): omp_standalone+=1
    print('w:ins=%d w:del=%d 删除线=%d 突出显示=%d pageBreakBefore=%d keepNext=%d keepLines=%d w:br总=%d 分页br=%d'%(ins,dele,strike,hl,pbb,kn,kl,len(brs),br_page))
    print('非auto/FFFFFF颜色值=%s oMathPara=%d（零文字独立段=%d）'%(sorted(colors),len(omp),omp_standalone))

    # --- 图形态 ---
    anchors=len(re.findall(r'<wp:anchor\b',raw.split('<w:ftr')[-1]))
    anchor_el=[e for e in doc.iter() if tag(e)=='anchor']
    inlines=[e for e in doc.iter() if tag(e)=='inline']
    print('wp:anchor=%d wp:inline=%d'%(len(anchor_el),len(inlines)))
    wide=[]
    for e in inlines:
        ext=e.find('{%s}extent'%WP)
        if ext is None: continue
        cx=int(ext.get('cx')); cy=int(ext.get('cy'))
        wcm=cx/360000.0; hcm=cy/360000.0
        if wcm>8.6: wide.append((wcm,hcm))
    print('显示宽>8.6cm图=%d %s'%(len(wide),wide[:5]))
    tiny=[]
    for e in inlines:
        ext=e.find('{%s}extent'%WP)
        if ext is None: continue
        cx=int(ext.get('cx')); cy=int(ext.get('cy'))
        if cx/360000.0<3/28.35 or cy/360000.0<3/28.35:  # <3磅≈0.106cm
            tiny.append((cx/360000.0,cy/360000.0))
    print('显示<3磅图=%d %s'%(len(tiny),tiny[:5]))
    # 位图<50x50
    tinybmp=0; bmpinfo=[]
    for n in z.namelist():
        if n.startswith('word/media/'):
            d=z.read(n)
            if d[:8]==b'\x89PNG\r\n\x1a\n':
                w=int.from_bytes(d[16:20],'big'); h=int.from_bytes(d[20:24],'big')
                if w<50 and h<50: tinybmp+=1; bmpinfo.append((n,w,h))
            elif d[:2]==b'\xff\xd8':
                # JPEG粗略
                i=2
                try:
                    while i<len(d):
                        if d[i]!=0xFF: break
                        m=d[i+1]
                        if m in (0xC0,0xC1,0xC2,0xC3):
                            h=int.from_bytes(d[i+5:i+7],'big'); w=int.from_bytes(d[i+7:i+9],'big')
                            if w<50 and h<50: tinybmp+=1; bmpinfo.append((n,w,h))
                            break
                        ln=int.from_bytes(d[i+2:i+4],'big'); i+=2+ln
                except Exception: pass
    print('media位图<50x50像素=%d %s'%(tinybmp,bmpinfo[:5]))
    # 孤儿图引
    orph=[]
    for idx,p in enumerate(paras):
        txt=para_text(p)
        if re.search(r'如图|图甲|图乙|图丙|图丁|图所示|如图所示',txt):
            has=False
            for j in range(max(0,idx-2),min(len(paras),idx+3)):
                if paras[j].find('.//'+q('drawing')) is not None or paras[j].find('.//{%s}pict'%W) is not None: has=True
            if not has: orph.append((idx,txt[:40]))
    print('「如图」类引用段无邻图=%d（首5例%s）'%(len(orph),orph[:5]))

    # --- 21半点run定点解剖 ---
    styles=etree.fromstring(z.read('word/styles.xml'))
    def dump_runs(pidx):
        p=paras[pidx]
        print('  段[%d] XML首1200字：'%pidx)
        s=etree.tostring(p,encoding='unicode')
        print('   ',s[:1200].replace('\n',''))
    probes={'X2':[],'I2':[53,75],'E':[24,27,166],'F':[],'G':[52,69],'H':[193,74]}[code]
    for pp in probes: dump_runs(pp)

    # --- 选项「A．；」形态 ---
    weird=[]
    for idx,p in enumerate(paras):
        txt=para_text(p)
        if re.search(r'[A-D]．；',txt): weird.append((idx,txt[:50]))
    print('「A．；」空值选项形态段=%d（首5例%s）'%(len(weird),weird[:5]))

    # --- 创作句线性数学 ---
    lin_math=[]
    for idx,p in enumerate(paras):
        txt=para_text(p)
        if txt.startswith('【编注】'):
            if re.search(r'[√²³ⁿ₀-₉]',txt): lin_math.append((idx,txt[:50]))
    print('【编注】含线性数学字符段=%d %s'%(len(lin_math),lin_math[:3]))
    z.close()
print('DONE')
