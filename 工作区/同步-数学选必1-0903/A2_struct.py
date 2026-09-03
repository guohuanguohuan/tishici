# -*- coding: utf-8 -*-
"""A2第2章审计·结构向：版面/页眉页脚域/节名锚/节标题/标题整行底纹ADC2DA逐段定位/文内标题/统计段/sectPr。
只读，不写任何被审文件。输出到 stdout（重定向到报告片段）。"""
import sys, io, os, zipfile, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname

FILES = {
 'X2': r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
 'I2': r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
 'E':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
 'F':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
 'G':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
 'H':  r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}
EXPECT_START = {'X2':1,'I2':1,'E':1,'F':50,'G':103,'H':142}
EXPECT_N = {'X2':6,'I2':28,'E':205,'F':205,'G':205,'H':205}
EXPECT_BEN = {'X2':4,'I2':5,'E':6,'F':6,'G':6,'H':6}
EXPECT_M = 6

def para_text(p):
    out=[]
    for t in p.iter():
        ln=tag(t)
        if ln=='t' and t.text: out.append(t.text)
        elif ln=='instrText' and t.text: out.append('⟦I:%s⟧'%t.text)
        elif ln=='delText' and t.text: out.append(t.text)
    return ''.join(out)

def get(e, path):
    c=e.find(path)
    return c

for code,path in FILES.items():
    print('='*100)
    print('【%s】%s'%(code,os.path.basename(path)))
    z=zipfile.ZipFile(path)
    doc=etree.fromstring(z.read('word/document.xml'))
    styles=etree.fromstring(z.read('word/styles.xml'))
    settings=etree.fromstring(z.read('word/settings.xml'))
    body=doc.find(q('body'))
    paras=body.findall(q('p'))
    print('document.xml 段落总数=%d, 文件大小=%.2f MB'%(len(paras), os.path.getsize(path)/1048576.0))

    # --- settings ---
    uf=settings.find(q('updateFields'))
    print('settings updateFields=%s'%(uf.get(q('val')) if uf is not None else 'MISSING'))

    # --- styles: 节名锚 & 标题3 & docDefaults ---
    anchor_id=None; h3_id=None; h2_id=None
    for s in styles.findall(q('style')):
        name_el=s.find(q('name'))
        nm=name_el.get(q('val')) if name_el is not None else ''
        if nm=='节名锚': anchor_id=s.get(q('styleId'))
        if nm=='heading 3': h3_id=s.get(q('styleId'))
        if nm=='heading 2': h2_id=s.get(q('styleId'))
    print('styles: 节名锚 styleId=%r, heading3 styleId=%r, heading2 styleId=%r'%(anchor_id,h3_id,h2_id))
    if anchor_id:
        for s in styles.findall(q('style')):
            if s.get(q('styleId'))==anchor_id:
                rpr=s.find(q('rPr'))
                det={}
                if rpr is not None:
                    for ch in rpr:
                        det[tag(ch)]=dict(ch.attrib)
                print('  节名锚样式rPr=%s'%json.dumps(det,ensure_ascii=False))
                ppr=s.find(q('pPr'))
                det2={}
                if ppr is not None:
                    for ch in ppr: det2[tag(ch)]=dict(ch.attrib)
                print('  节名锚样式pPr=%s'%json.dumps(det2,ensure_ascii=False))
    dd=styles.find(q('docDefaults'))
    if dd is not None:
        rpd=dd.find(q('rPrDefault')); ppd=dd.find(q('pPrDefault'))
        def dump_rpr(el):
            if el is None: return None
            r=el.find(q('rPr'))
            if r is None: return None
            d={}
            for ch in r: d[tag(ch)]=dict(ch.attrib)
            return d
        def dump_ppr(el):
            if el is None: return None
            r=el.find(q('pPr'))
            if r is None: return None
            d={}
            for ch in r: d[tag(ch)]=dict(ch.attrib)
            return d
        print('  docDefaults rPrDefault=%s'%json.dumps(dump_rpr(rpd),ensure_ascii=False))
        print('  docDefaults pPrDefault=%s'%json.dumps(dump_ppr(ppd),ensure_ascii=False))

    # --- sectPr 结构 ---
    sects=[]
    for sec in body.iter(q('sectPr')):
        info={}
        pgsz=sec.find(q('pgSz')); pgmar=sec.find(q('pgMar')); cols=sec.find(q('cols'))
        pn=sec.find(q('pgNumType'))
        hr=sec.findall(q('headerReference')); fr=sec.findall(q('footerReference'))
        info['pgSz']=(pgsz.get(q('w')),pgsz.get(q('h'))) if pgsz is not None else None
        if pgmar is not None:
            info['pgMar']={k:pgmar.get(q(k)) for k in ('top','bottom','left','right','header','footer','gutter')}
        if cols is not None:
            info['cols']={k:cols.get(q(k)) for k in ('num','space','sep')}
        if pn is not None: info['pgNumType_start']=pn.get(q('start'))
        info['hdrRefs']=[(h.get(q('type')),h.get('{%s}id'%R)) for h in hr]
        info['ftrRefs']=[(f.get(q('type')),f.get('{%s}id'%R)) for f in fr]
        sects.append(info)
    print('sectPr 总数=%d'%len(sects))
    for i,s in enumerate(sects):
        print('  sect[%d] %s'%(i,json.dumps(s,ensure_ascii=False)))
    # 末段sectPr所在位置判断（body级=最后）
    body_sect = body.find(q('sectPr'))
    print('  body末级sectPr存在=%s'%('是' if body_sect is not None else '否'))

    # rels -> header/footer part名
    rels=etree.fromstring(z.read('word/_rels/document.xml.rels'))
    relmap={r.get('Id'):r.get('Target') for r in rels}
    hf_parts=set()
    for s in sects:
        for t,i in s['hdrRefs']+s['ftrRefs']:
            hf_parts.add(relmap.get(i,'?'))
    print('引用的header/footer parts=%s'%sorted(hf_parts))
    all_hf=[n for n in z.namelist() if re.match(r'word/(header|footer)\d*\.xml$',n)]
    print('包内全部header/footer parts=%s'%sorted(all_hf))

    # --- header/footer 内容审计 ---
    for part in sorted(hf_parts):
        x=etree.fromstring(z.read('word/'+part))
        n_fldchar_b=x.findall('.//'+q('fldChar'))
        kinds=[f.get(q('fldCharType')) for f in n_fldchar_b]
        instrs=[t.text for t in x.iter(q('instrText'))]
        fldsimple=x.findall('.//'+q('fldSimple'))
        # 提取完整文字流（含缓存）
        txt=para_text_x=[]
        for p in x.iter(q('p')):
            txt.append(para_text(p))
        full=' | '.join(t for t in txt if t.strip())
        # run字号统计
        szs={}
        for r in x.iter(q('r')):
            rpr=r.find(q('rPr'))
            sz=None
            if rpr is not None:
                e2=rpr.find(q('sz'))
                if e2 is not None: sz=e2.get(q('val'))
            szs[sz]=szs.get(sz,0)+1
        jcs=set()
        for p in x.iter(q('p')):
            ppr=p.find(q('pPr'))
            jc=ppr.find(q('jc')) if ppr is not None else None
            jcs.add(jc.get(q('val')) if jc is not None else '(无jc)')
        print('  [%s] fldChar=%s instr=%s fldSimple=%d NUMPAGES域=%s'%(part,kinds,instrs,len(fldsimple),('NUMPAGES' in full)))
        print('    run字号分布=%s 段落jc=%s'%(szs,jcs))
        print('    文字流=%r'%full[:400])
    # settings里evenAndOddHeaders / titlePg
    eo=settings.find(q('evenAndOddHeaders')); tp=[s for s in doc.iter(q('titlePg'))]
    print('evenAndOddHeaders=%s titlePg数=%d'%(eo is not None,len(tp)))

    # --- 节名锚 & 节标题 & 标题整行底纹 ---
    anchor_paras=[]; h3_paras=[]; adc=[]; c6=[]
    for idx,p in enumerate(paras):
        ppr=p.find(q('pPr'))
        pstyle=None; pshd=None
        if ppr is not None:
            ps=ppr.find(q('pStyle'))
            pstyle=ps.get(q('val')) if ps is not None else None
            sh=ppr.find(q('shd'))
            pshd=sh.get(q('fill')) if sh is not None else None
        t=para_text(p)
        if pstyle==anchor_id: anchor_paras.append((idx,t))
        if pstyle==h3_id: h3_paras.append((idx,t))
        if pshd and pshd.upper()=='ADC2DA': adc.append((idx,pstyle,t))
        if pshd and pshd.upper()=='C6D4E3': c6.append((idx,pstyle,t))
    print('节名锚段数=%d（样式%r）'%(len(anchor_paras),anchor_id))
    for i,t in anchor_paras: print('  锚[%d] %r'%(i,t))
    print('节标题(样式heading3=%r)段数=%d'%(h3_id,len(h3_paras)))
    for i,t in h3_paras: print('  节[%d] %r'%(i,t))
    print('段级ADC2DA段数=%d；段级C6D4E3段数=%d'%(len(adc),len(c6)))
    print('--- ADC2DA 逐段定位（idx|pStyle|文本前60）---')
    for i,ps,t in adc: print('  ADC2DA[%d] style=%s %r'%(i,ps,t[:60]))
    # run级ADC2DA误挂检查
    run_adc=[r for r in doc.iter(q('r')) if (lambda rp: rp is not None and rp.find(q('shd')) is not None and (rp.find(q('shd')).get(q('fill')) or '').upper()=='ADC2DA')(r.find(q('rPr')))]
    print('run级ADC2DA挂点=%d（应为0）'%len(run_adc))
    run_c6=[r for r in doc.iter(q('r')) if (lambda rp: rp is not None and rp.find(q('shd')) is not None and (rp.find(q('shd')).get(q('fill')) or '').upper()=='C6D4E3')(r.find(q('rPr')))]
    print('run级C6D4E3挂点=%d（应为0）'%len(run_c6))

    # --- 文内开头标题（首个非空段）---
    for idx,p in enumerate(paras):
        t=para_text(p)
        if t.strip():
            print('首个非空段[%d]=%r'%(idx,t[:100]))
            break
    # --- 统计段与全件统计行 ---
    print('--- 统计段（含「题：」的段落，截前80字）---')
    for idx,p in enumerate(paras):
        t=para_text(p)
        if re.search(r'(全件\d+题|本节\d+题|\d+题：)', t):
            print('  [%d] %r'%(idx,t[:80]))

    # --- 每件锚段与其后段关系（锚后一段是否heading3）---
    miss=0
    for i,t in anchor_paras:
        nxt=None
        for j in range(i+1,len(paras)):
            if para_text(paras[j]).strip(): nxt=j; break
        if nxt is None or nxt!=(i+1): miss+=1; print('  锚[%d]后非紧邻内容段(下个非空=%s)'%(i,nxt))
        else:
            ppr=paras[nxt].find(q('pPr'))
            ps=ppr.find(q('pStyle')) if ppr is not None else None
            sid=ps.get(q('val')) if ps is not None else None
            if sid!=h3_id:
                print('  锚[%d]后段style=%s 非heading3 文本=%r'%(i,sid,para_text(paras[nxt])[:40]))
    z.close()
print('DONE')
