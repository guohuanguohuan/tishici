# -*- coding: utf-8 -*-
"""A1审计主脚本：XML级全量检查（规格书二、清单1/2/3/5/6/7/8/9/12＋底纹③ADC2DA段定位）
只读审计，输出 tmp/A1_reports/主审计_{tag}.txt"""
import os, re, sys, io, json
from lxml import etree

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

W  = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A  = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R  = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
M  = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(p, t): return '{%s}%s' % (p, t)

PARTS = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\A1_parts"
OUT   = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\A1_reports"
FILES = {"X1": 29, "I1": 47, "B": 61, "C": 79}   # tag -> 文件名题量/条数
EXPECT_PAGES = {"X1": 16, "I1": 14, "B": 53, "C": 61}
STARTS = {"X1": 1, "I1": 1, "B": 1, "C": 54}

def para_info(p):
    """提取段落级信息"""
    d = {}
    pPr = p.find(q(W,'pPr'))
    d['style'] = ''
    d['shd'] = None; d['pBdr'] = False
    d['jc'] = None; d['ind'] = {}
    d['spacing'] = None; d['pbb']=False; d['kn']=False; d['kl']=False
    d['sectPr'] = None
    if pPr is not None:
        st = pPr.find(q(W,'pStyle'))
        if st is not None: d['style'] = st.get(q(W,'val'),'')
        sh = pPr.find(q(W,'shd'))
        if sh is not None: d['shd'] = sh.get(q(W,'fill'))
        d['pBdr'] = pPr.find(q(W,'pBdr')) is not None
        jc = pPr.find(q(W,'jc'))
        if jc is not None: d['jc'] = jc.get(q(W,'val'))
        ind = pPr.find(q(W,'ind'))
        if ind is not None:
            for k in ('left','right','firstLine','hanging','start','end'):
                v = ind.get(q(W,k))
                if v: d['ind'][k]=v
        sp = pPr.find(q(W,'spacing'))
        if sp is not None:
            d['spacing'] = {k:sp.get(q(W,k)) for k in ('before','after','line','lineRule') if sp.get(q(W,k))}
        d['pbb'] = pPr.find(q(W,'pageBreakBefore')) is not None
        d['kn']  = pPr.find(q(W,'keepNext')) is not None
        d['kl']  = pPr.find(q(W,'keepLines')) is not None
        sect = pPr.find(q(W,'sectPr'))
        if sect is not None: d['sectPr'] = sect
    # runs
    runs = []
    for r_ in p.findall(q(W,'r')):
        rd = {'text':'', 'sz':None,'b':None,'shd':None,'color':None,
              'strike':0,'hl':0,'bdr':0,'fonts':{},'tab':0,'br':0}
        rPr = r_.find(q(W,'rPr'))
        if rPr is not None:
            sz = rPr.find(q(W,'sz'));  rd['sz'] = sz.get(q(W,'val')) if sz is not None else None
            rd['b'] = rPr.find(q(W,'b')) is not None
            sh = rPr.find(q(W,'shd'))
            if sh is not None: rd['shd'] = sh.get(q(W,'fill'))
            co = rPr.find(q(W,'color'))
            if co is not None: rd['color'] = co.get(q(W,'val'))
            rd['strike'] = 1 if rPr.find(q(W,'strike')) is not None else 0
            hl = rPr.find(q(W,'highlight'))
            rd['hl'] = hl.get(q(W,'val')) if hl is not None else None
            rd['bdr'] = 1 if rPr.find(q(W,'bdr')) is not None else 0
            fo = rPr.find(q(W,'rFonts'))
            if fo is not None:
                for k in ('ascii','eastAsia','hAnsi'):
                    v = fo.get(q(W,k))
                    if v: rd['fonts'][k]=v
        for t in r_.findall(q(W,'t')):
            rd['text'] += t.text or ''
        rd['tab'] = len(r_.findall(q(W,'tab')))
        rd['br'] = len(r_.findall(q(W,'br')))
        runs.append(rd)
    d['runs'] = runs
    d['text'] = ''.join(r['text'] for r in runs)
    # oMath
    d['omath'] = len(p.findall(q(M,'oMath')))
    d['oMathPara'] = len(p.findall(q(M,'oMathPara')))
    mts = p.findall('.//'+q(M,'t'))
    d['mtext'] = ''.join((t.text or '') for t in mts)
    # drawings
    anchors = p.findall('.//'+q(WP,'anchor'))
    inlines = p.findall('.//'+q(WP,'inline'))
    d['anchor'] = len(anchors); d['inline'] = len(inlines)
    ext = []
    for dr in p.findall('.//'+q(WP,'inline')) + p.findall('.//'+q(WP,'anchor')):
        e = dr.find(q(WP,'extent'))
        if e is not None:
            ext.append((int(e.get('cx')), int(e.get('cy'))))
    d['extents'] = ext
    d['ins'] = len(p.findall('.//'+q(W,'ins')))
    d['del'] = len(p.findall('.//'+q(W,'del')))
    return d

def sect_info(sect):
    d = {}
    pg = sect.find(q(W,'pgSz'))
    d['pgSz'] = (pg.get(q(W,'w')), pg.get(q(W,'h'))) if pg is not None else None
    mg = sect.find(q(W,'pgMar'))
    d['pgMar'] = ({k:mg.get(q(W,k)) for k in ('top','right','bottom','left','header','footer','gutter')}
                  if mg is not None else None)
    co = sect.find(q(W,'cols'))
    d['cols'] = ({'num':co.get(q(W,'num')),'space':co.get(q(W,'space')),'sep':co.get(q(W,'sep'))}
                 if co is not None else None)
    d['hdrRefs'] = [(h.get(q(W,'type')), h.get(q(R,'id'))) for h in sect.findall(q(W,'headerReference'))]
    d['ftrRefs'] = [(h.get(q(W,'type')), h.get(q(R,'id'))) for h in sect.findall(q(W,'footerReference'))]
    pn = sect.find(q(W,'pgNumType'))
    d['pgNumType_start'] = pn.get(q(W,'start')) if pn is not None else None
    d['type'] = sect.find(q(W,'type'))
    d['type'] = d['type'].get(q(W,'val')) if d['type'] is not None else None
    return d

def parse_hf(path):
    """页眉/页脚解析：域结构、文本、字号"""
    x = etree.parse(path)
    root = x.getroot()
    res = {'fldChars':[], 'instr':[], 'texts':[], 'cache':[], 'sizes':[], 'jc':[], 'color':[], 'b':[]}
    for fc in root.iter(q(W,'fldChar')):
        res['fldChars'].append(fc.get(q(W,'fldCharType')))
    for it in root.iter(q(W,'instrText')):
        res['instr'].append(it.text or '')
    # cached values: runs between separate and end
    state = 0
    for r_ in root.iter(q(W,'r')):
        fcs = r_.findall(q(W,'fldChar'))
        txts = r_.findall(q(W,'t'))
        if state == 1:
            for t in txts: res['cache'].append(t.text or '')
        for fc in fcs:
            ty = fc.get(q(W,'fldCharType'))
            if ty == 'separate': state = 1
            elif ty == 'end': state = 0
        rPr = r_.find(q(W,'rPr'))
        sz = None
        if rPr is not None:
            s = rPr.find(q(W,'sz'))
            if s is not None: sz = s.get(q(W,'val'))
        if sz: res['sizes'].append(sz)
        for t in txts: res['texts'].append(t.text or '')
    for p in root.iter(q(W,'p')):
        pPr = p.find(q(W,'pPr'))
        jc = pPr.find(q(W,'jc')) if pPr is not None else None
        res['jc'].append(jc.get(q(W,'val')) if jc is not None else '(default)')
        sh = pPr.find(q(W,'shd')) if pPr is not None else None
        res['shd_p'] = sh.get(q(W,'fill')) if sh is not None else None
    res['fldSimple'] = len(root.findall('.//'+q(W,'fldSimple')))
    res['NUMPAGES'] = any('NUMPAGES' in i for i in res['instr'])
    res['line'] = []
    return res

def resolve_sz(run_rd, stylemap, docdef_sz='24'):
    if run_rd['sz']: return run_rd['sz']
    st = stylemap.get(run_rd.get('style',''))
    # style chain
    seen = set()
    while st and st['id'] not in seen:
        seen.add(st['id'])
        if st['sz']: return st['sz']
        st = stylemap.get(st['basedOn'])
    return docdef_sz

def audit(tag):
    base = os.path.join(PARTS, tag)
    out = []
    P = out.append
    doc = etree.parse(os.path.join(base,'word','document.xml'))
    body = doc.getroot().find(q(W,'body'))
    # ---- styles
    sdoc = etree.parse(os.path.join(base,'word','styles.xml'))
    stylemap = {}
    for st in sdoc.getroot().findall(q(W,'style')):
        sid = st.get(q(W,'styleId'))
        name = st.find(q(W,'name'))
        namev = name.get(q(W,'val')) if name is not None else ''
        based = st.find(q(W,'basedOn'))
        rPr = st.find(q(W,'rPr'))
        sz = None
        if rPr is not None:
            s = rPr.find(q(W,'sz'))
            if s is not None: sz = s.get(q(W,'val'))
        stylemap[sid] = {'id':sid,'name':namev,'basedOn':based.get(q(W,'val')) if based is not None else None,'sz':sz}
    # ---- settings
    sett = open(os.path.join(base,'word','settings.xml'),encoding='utf-8').read()
    P(f"== {tag} ==")
    P(f"[2] settings.xml updateFields: {'w:updateFields' in sett}")
    # ---- 段落全列
    paras = []
    children = list(body)
    for ch in children:
        if ch.tag == q(W,'p'):
            paras.append(ch)
    infos = [para_info(p) for p in paras]
    final_sect = body.find(q(W,'sectPr'))
    # ---- 1 版面
    P("[1] sectPr 结构：")
    sects = []
    for i,inf in enumerate(infos):
        if inf['sectPr'] is not None:
            si = sect_info(inf['sectPr']); si['pos'] = f"p#{i}"
            sects.append(si)
    if final_sect is not None:
        si = sect_info(final_sect); si['pos'] = 'body-final'
        sects.append(si)
    hdr_ref_total = sum(len(s['hdrRefs']) for s in sects)
    ftr_ref_total = sum(len(s['ftrRefs']) for s in sects)
    for s in sects:
        P(f"    sectPr@{s['pos']}: type={s['type']} pgSz={s['pgSz']} pgMar={s['pgMar']} cols={s['cols']} "
          f"hdr={s['hdrRefs']} ftr={s['ftrRefs']} start={s['pgNumType_start']}")
    P(f"    sectPr数={len(sects)} headerReference总数={hdr_ref_total} footerReference总数={ftr_ref_total}")
    # ---- 2 页眉页脚
    for kind in ('header1','footer1'):
        hf = parse_hf(os.path.join(base,'word',kind+'.xml'))
        joined_instr = [i for i in hf['instr']]
        P(f"[2] {kind}: fldChar={'|'.join(hf['fldChars'])} instr={joined_instr} fldSimple={hf['fldSimple']} NUMPAGES={hf['NUMPAGES']}")
        P(f"    文本={''.join(hf['texts'])!r}")
        P(f"    缓存值={hf['cache']} run字号集合={sorted(set(hf['sizes']))} jc={hf['jc']} 段底纹={hf.get('shd_p')}")
    # ---- 3 节名锚
    anchors = []
    headings3 = []
    for i,inf in enumerate(infos):
        if inf['style'] == 'JieMingMao':
            anchors.append((i, inf['text'], inf['runs'][0]['sz'] if inf['runs'] else None))
        if inf['style'] == 'Heading3':
            headings3.append((i, inf['text'][:60]))
    P(f"[3] 节名锚段数={len(anchors)} Heading3节标题数={len(headings3)}")
    for a in anchors: P(f"    锚@p#{a[0]} sz={a[1] if isinstance(a[1],str) else a[1]} text={a[1]!r}" if False else f"    锚@p#{a[0]} 首run_sz={a[2]} text={a[1]!r}")
    for h in headings3: P(f"    节标题@p#{h[0]} {h[1]!r}")
    # 锚前置断言：每个Heading3段的前一段是锚
    miss = 0
    for (i, t) in headings3:
        if i == 0 or infos[i-1]['style'] != 'JieMingMao': miss += 1; P(f"    !! 节标题p#{i}前一段非锚")
    P(f"    锚前置缺失={miss}")
    # 锚run属性核验（1pt白、非隐藏）
    bad_anchor = 0
    for i,inf in enumerate(infos):
        if inf['style']=='JieMingMao':
            colors = [r['color'] for r in inf['runs']]
            szs = [r['sz'] for r in inf['runs']]
            if not all(c=='FFFFFF' for c in colors) or not all(s=='2' for s in szs): bad_anchor+=1; P(f"    !! 锚p#{i}属性 colors={colors} szs={szs}")
    P(f"    锚属性异常段={bad_anchor}")
    # ---- 4③ ADC2DA/C6D4E3 段定位
    P("[4③] 标题整行底纹段定位：")
    for i,inf in enumerate(infos):
        if inf['shd'] == 'ADC2DA':
            P(f"    ADC2DA@p#{i} style={inf['style']!r} text={inf['text'][:50]!r}")
    n_adc = sum(1 for inf in infos if inf['shd']=='ADC2DA')
    n_c6 = sum(1 for inf in infos if inf['shd']=='C6D4E3')
    P(f"    ADC2DA段数={n_adc} C6D4E3段数={n_c6}")
    # ---- 5 题号核验
    P("[5] 题号块：")
    qnums = []   # (pidx, 题型号, 序号, full)
    for i,inf in enumerate(infos):
        for r in inf['runs']:
            if r['shd']=='C9C9C9' and re.fullmatch(r'\d+(\.\d+)+-\d+．', r['text']):
                qnums.append((i, r['text']))
    P(f"    题号块run数={len(qnums)} 文件名题量={FILES[tag]}")
    fams = {}
    for i,t in qnums:
        m = re.fullmatch(r'(\d+(?:\.\d+)+)-(\d+)．', t)
        fams.setdefault(m.group(1), []).append(int(m.group(2)))
    fams_sorted = sorted(fams.items(), key=lambda kv: [int(x) for x in kv[0].split('.')])
    seq_bad = []
    for fam, seq in fams_sorted:
        if seq != list(range(1, len(seq)+1)):
            seq_bad.append((fam, seq))
    P(f"    题号族数={len(fams)} 序列断点/重复族={seq_bad if seq_bad else 0}")
    P(f"    族明细：{'; '.join(f'{f}:{len(s)}题(1..{max(s) if s else 0})' for f,s in fams_sorted)}")
    # 括注形态
    bad_ann = []
    diff_cnt = {'简单':0,'中档':0,'难':0,'衔接必会':0,'其他':0}
    for i,t in qnums:
        line = infos[i]['text']
        if tag in ('X1',):
            ok = re.search(r'（衔接必会·卡壳看答案）', line)
        else:
            ok = re.search(r'（(简单|中档|难)·(保60%|保80%|冲100%)·卡壳看答案）', line)
        if not ok:
            bad_ann.append((i, line[:60]))
        else:
            for k in ('简单','中档','难','衔接必会'):
                if k in ok.group(0): diff_cnt[k]+=1
    P(f"    括注形态违例={len(bad_ann)} {bad_ann[:5]}")
    if tag in ('B','C'): P(f"    档位分布={diff_cnt}")
    # ---- 6 统计段
    P("[6] 统计段：")
    for i,inf in enumerate(infos):
        t = inf['text']
        if re.search(r'全件\d+题', t): P(f"    全件统计行@p#{i}: {t[:80]!r}")
    for i,inf in enumerate(infos):
        if inf['shd']=='ADC2DA' and re.search(r'本节\d+题', inf['text']):
            m = re.search(r'本节(\d+)题', inf['text'])
            P(f"    节统计段@p#{i}: 节内{m.group(1)}题 | {inf['text'][:60]!r}")
    grp_stats = []
    for i,inf in enumerate(infos):
        if inf['shd']=='C6D4E3':
            m = re.search(r'　(\d+)题：([\d～.\-]+)$', inf['text'].strip()+'　' if inf['text'].endswith('　') else inf['text'].strip())
            m2 = re.search(r'　(\d+)题：(.+)$', inf['text'])
            if m2: grp_stats.append((i, int(m2.group(1)), m2.group(2), inf['text'][:40]))
    P(f"    题型统计段数={len(grp_stats)}")
    grp_sum = sum(g[1] for g in grp_stats)
    P(f"    题型统计段Σ={grp_sum}")
    for g in grp_stats[:80]:
        pass
    # 节统计段总和
    sec_sums = [int(m.group(1)) for i,inf in enumerate(infos) if inf['shd']=='ADC2DA'
                for m in [re.search(r'本节(\d+)题', inf['text'])] if m]
    P(f"    节统计段明细={sec_sums} Σ={sum(sec_sums)}")
    # ---- 7 字号/段落
    P("[7] 字号偏离（正文run有效字号≠24，例外：32文内/28节/2锚）：")
    dev = {}
    for i,inf in enumerate(infos):
        if inf['style']=='JieMingMao': continue
        for j,r in enumerate(inf['runs']):
            if not r['text'] and not r['shd']: continue
            sz = r['sz'] or stylemap.get(inf['style'],{}).get('sz') or '24'
            if sz not in ('24',):
                key = (sz, inf['style'])
                dev.setdefault(key, []).append((i, r['text'][:20]))
    for k,v in dev.items():
        P(f"    有效字号{k[0]} style={k[1]!r}: run数={len(v)} 例={v[:3]}")
    P(f"    字号偏离类数={len(dev)}")
    # run字体
    fdev = 0; fdev_ex = []
    for i,inf in enumerate(infos):
        for r in inf['runs']:
            f = r['fonts']
            if f and not (f.get('ascii','Times New Roman')=='Times New Roman' and f.get('eastAsia','宋体')=='宋体'):
                fdev += 1
                if len(fdev_ex)<5: fdev_ex.append((i, f, r['text'][:15]))
    P(f"    显式字体偏离run数={fdev} 例={fdev_ex}")
    # 段落 spacing/jc/ind
    sp_bad = []; jc_bad = []; ind_bad = []
    for i,inf in enumerate(infos):
        if inf['style']=='JieMingMao': continue
        sp = inf['spacing'] or {}
        if not (sp.get('line')=='410' and sp.get('lineRule')=='atLeast' and sp.get('before','0')=='0' and sp.get('after','0')=='0'):
            # 继承docDefault也算合规：显式不全时仅当显式值冲突才记
            conflict = (sp and (sp.get('line') not in (None,'410') or sp.get('lineRule') not in (None,'atLeast')
                        or sp.get('before') not in (None,'0') or sp.get('after') not in (None,'0')))
            if conflict: sp_bad.append((i, sp, inf['text'][:25]))
        if inf['jc'] not in (None,'left'): jc_bad.append((i, inf['jc'], inf['text'][:25]))
        if inf['ind']: ind_bad.append((i, inf['ind'], inf['text'][:25]))
    P(f"    段spacing显式冲突={len(sp_bad)} {sp_bad[:4]}")
    P(f"    jc非left段={len(jc_bad)} {jc_bad[:4]}")
    P(f"    w:ind非零段={len(ind_bad)} {ind_bad[:4]}")
    # ---- 8 残留
    P("[8] 残留计数：")
    cnt = lambda name: sum(1 for _ in doc.getroot().iter(q(W,name)))
    ins_n = sum(inf['ins'] for inf in infos); del_n = sum(inf['del'] for inf in infos)
    color_bad = []; strike_n=0; hl_n=0
    for i,inf in enumerate(infos):
        for r in inf['runs']:
            if r['color'] and r['color']!='auto': color_bad.append((i,r['color'],r['text'][:15]))
            strike_n += r['strike']
            if r['hl']: hl_n += 1
    P(f"    w:ins={ins_n} w:del={del_n} 非auto w:color={len(color_bad)} {color_bad[:3]} w:strike={strike_n} w:highlight={hl_n}")
    pbb = sum(1 for inf in infos if inf['pbb']); kn = sum(1 for inf in infos if inf['kn']); kl = sum(1 for inf in infos if inf['kl'])
    br_n = sum(r['br'] for inf in infos for r in inf['runs'])
    tab_n = sum(r['tab'] for inf in infos for r in inf['runs'])
    omp = sum(inf['oMathPara'] for inf in infos)
    manual_break = len(doc.getroot().findall('.//'+q(W,'br')))
    P(f"    pageBreakBefore={pbb} keepNext={kn} keepLines={kl} w:br(全部)={manual_break} w:tab={tab_n} oMathPara={omp}")
    # 空格卫生
    dbl_sp = 0; fw_sp = 0; fw_ex=[]; trail = 0
    for i,inf in enumerate(infos):
        t = inf['text']
        if '  ' in t: dbl_sp += 1
        for mm in re.finditer(r'[ \u3000]([，。；：、！？）》】])', t):
            fw_sp += 1
            if len(fw_ex)<6: fw_ex.append((i, t[max(0,mm.start()-8):mm.end()+4]))
        if t != t.rstrip(): trail += 1
    P(f"    连续双半空格段={dbl_sp} 全角标点前空格={fw_sp} 例={fw_ex} 段尾空格段={trail}")
    # 创作句线性数学（【编注】段与题型通式句）
    lin = []
    for i,inf in enumerate(infos):
        if '【编注】' in inf['text'] or '题型通式' in inf['text']:
            if re.search(r'[√²³¹⁰⁴⁵⁶⁷⁸⁹₀-₉]', inf['text']) and inf['omath']==0:
                lin.append((i, inf['text'][:50]))
    P(f"    创作句线性数学={len(lin)} {lin[:3]}")
    # 选项分隔与粘连（抽验：A．B．C．D．行）
    opt_bad = []
    for i,inf in enumerate(infos):
        if re.search(r'[AB]．', inf['text']) and inf['omath']==0 and not inf['runs'][0]['text'].startswith(('A．','B．')) :
            pass
    P(f"    选项行逐条抽验：手工复核（见报告人工段）")
    # ---- 9 图形态
    P("[9] 图形态：")
    anch = sum(inf['anchor'] for inf in infos); inl = sum(inf['inline'] for inf in infos)
    exts = [e for inf in infos for e in inf['extents']]
    wide = [(round(cx/360000,2), round(cy/360000,2)) for cx,cy in exts if cx/360000 > 8.6]
    P(f"    wp:anchor={anch} wp:inline={inl} 图总数={len(exts)} 显示宽>8.6cm={len(wide)} {wide[:5]}")
    maxw = max((cx/360000 for cx,cy in exts), default=0)
    P(f"    最宽图={maxw:.2f}cm")
    # 孤儿图引
    orphan = []
    for i,inf in enumerate(infos):
        if re.search(r'如图|图甲|图乙|图丙|图丁|图所示', inf['text']):
            has_img = inf['inline']+inf['anchor']>0
            ctx = False
            for j in range(max(0,i-1), min(len(infos), i+3)):
                if infos[j]['inline']+infos[j]['anchor']>0: ctx=True
            if not (has_img or ctx): orphan.append((i, inf['text'][:60]))
    P(f"    孤儿图引候选（±2段无图）={len(orphan)} {orphan[:8]}")
    # ---- 12 标签
    P("[12] 标签：")
    lab = {}
    for i,inf in enumerate(infos):
        for mm in re.finditer(r'【(答案|知识点|分析|详解|点睛|编注|大招指引|题后反思|温馨提醒)】', inf['text']):
            lab[mm.group(1)] = lab.get(mm.group(1),0)+1
    P(f"    标签分计={lab}")
    empty_lab = []
    for i,inf in enumerate(infos):
        t = inf['text']
        for mm in re.finditer(r'【(答案|知识点)】([^\n]{0,3})', t):
            after = t[mm.end():mm.end()+3]
            if not after.strip(): empty_lab.append((i, t[:40]))
    P(f"    空【答案】/【知识点】候选={len(empty_lab)} {empty_lab[:4]}")
    kp_vals = []
    for i,inf in enumerate(infos):
        mm = re.search(r'【知识点】\s*(\S{0,30})', inf['text'])
        if mm: kp_vals.append(mm.group(1))
    pref_ok = sum(1 for v in kp_vals if re.match(r'\d+(\.\d+)*', v))
    P(f"    【知识点】值数={len(kp_vals)} 带节号前缀={pref_ok} 例={kp_vals[:6]}")
    # 【分析】块首是否带【编注】
    ana_bianzhu = 0; ana_total = 0
    for i,inf in enumerate(infos):
        if '【分析】' in inf['text']:
            ana_total += 1
            if '【编注】' in inf['text']: ana_bianzhu += 1
    P(f"    【分析】块数={ana_total} 内含【编注】={ana_bianzhu}")
    # ---- 输出
    rep = os.path.join(OUT, f"主审计_{tag}.txt")
    open(rep,'w',encoding='utf-8').write('\n'.join(out))
    print(f"---- {tag} written {len(out)} lines")
    return infos

for tag in ('X1','I1','B','C'):
    audit(tag)
print("done")
