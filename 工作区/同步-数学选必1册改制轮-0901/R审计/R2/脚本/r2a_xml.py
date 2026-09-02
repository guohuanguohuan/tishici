# -*- coding: utf-8 -*-
"""R2终审计——XML层：X1/C六项重测＋十件抽验三项（序列/页眉页脚域/allowOverlap）。只读。"""
import sys, io, os, re, zipfile, json
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
def q(t): return '{%s}%s' % (W, t)

D = r'C:\提示词\高中数学\高中数学同步'
FILES = [
 ('X1','人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'),
 ('I1','人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx'),
 ('B','人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'),
 ('C','人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'),
 ('X2','人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx'),
 ('I2','人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'),
 ('E','人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx'),
 ('F','人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'),
 ('G','人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx'),
 ('H','人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'),
]
OUT = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\R2\输出'
HNUM = re.compile(r'^(\d{1,3}(?:\.\d{1,3}){1,3})-(\d{1,3})．')

def para_text(p):
    return ''.join(t.text or '' for t in p.iter(q('t'), '{%s}t' % M))

def get_sz(rpr):
    if rpr is None: return None
    sz = rpr.find(q('sz'))
    return int(sz.get(q('val'))) if sz is not None else None

def para_style_id(p):
    ps = p.find(q('pPr'))
    if ps is None: return None
    st = ps.find(q('pStyle'))
    return st.get(q('val')) if st is not None else None

def parse_styles(zf):
    styles = {}
    root = etree.fromstring(zf.read('word/styles.xml'))
    dd = root.find(q('docDefaults'))
    rpd = dd.find(q('rPrDefault')) if dd is not None else None
    rpr = rpd.find(q('rPr')) if rpd is not None else None
    rpd_sz = get_sz(rpr)
    ppd_ = dd.find(q('pPrDefault')) if dd is not None else None
    ppd = None
    if ppd_ is not None:
        ppr = ppd_.find(q('pPr'))
        if ppr is not None:
            sp = ppr.find(q('spacing'))
            ppd = norm(sp.attrib) if sp is not None else None
    for st in root.iter(q('style')):
        sid = st.get(q('styleId'))
        r2 = st.find(q('rPr')); bo = st.find(q('basedOn')); nm = st.find(q('name'))
        styles[sid] = {'sz': get_sz(r2), 'based': bo.get(q('val')) if bo is not None else None,
                       'name': nm.get(q('val')) if nm is not None else None,
                       'shd': (r2.find(q('shd')).get(q('fill')) if r2 is not None and r2.find(q('shd')) is not None else None)}
    return styles, rpd_sz, ppd

def norm(d): return {k.split('}')[1]: v for k, v in d.items()} if d else None

def style_chain_sz(styles, sid):
    seen = set(); sz = None
    while sid and sid in styles and sid not in seen:
        seen.add(sid)
        if sz is None and styles[sid]['sz'] is not None: sz = styles[sid]['sz']
        sid = styles[sid]['based']
    return sz

def eff_para_shd(p, styles):
    """段级底纹：直挂＞样式链。返回fill或None。"""
    ppr = p.find(q('pPr'))
    if ppr is not None:
        s = ppr.find(q('shd'))
        if s is not None and s.get(q('val')) == 'clear':
            return s.get(q('fill'))
    sid = para_style_id(p)
    seen = set()
    while sid and sid in styles and sid not in seen:
        seen.add(sid)
        f = styles[sid]['shd']
        if f: return f
        sid = styles[sid]['based']
    return None

out = open(os.path.join(OUT, 'r2a_xml审计.txt'), 'w', encoding='utf-8')
res = {}
def P(*a):
    print(*a); print(*a, file=out)

for code, fn in FILES:
    path = os.path.join(D, fn)
    P('=' * 96); P('### %s %s' % (code, fn))
    zf = zipfile.ZipFile(path)
    styles, rpd_sz, ppd = parse_styles(zf)
    doc = etree.fromstring(zf.read('word/document.xml'))
    body = doc.find(q('body'))
    r = {}

    # ---- 项1 字号解析值（X1/C全量落盘；全部件顺手统计）----
    szc = Counter(); szex = defaultdict(list)
    anchor_sid = None
    for sid, st in styles.items():
        if st['name'] == '节名锚': anchor_sid = sid
    for p in body.iter(q('p')):
        sid = para_style_id(p)
        for rn in p.iter(q('r')):
            if rn.find(q('t')) is None: continue
            txt = ''.join(t.text or '' for t in rn.findall(q('t')))
            if not txt.strip(): continue
            v = get_sz(rn.find(q('rPr')))
            if v is None: v = style_chain_sz(styles, sid)
            if v is None: v = rpd_sz
            szc[v] += 1
            if len(szex[v]) < 2: szex[v].append(txt[:18])
    r['sz分布'] = dict(sorted(szc.items(), key=lambda x: -(x[1])))
    P('run字号解析值分布: %s' % r['sz分布'])
    for v in sorted(szex, key=lambda x: -szc[x]):
        P('   sz=%s (%d) 例: %s' % (v, szc[v], szex[v]))

    # ---- 项2 题号/条目号层级制序列 ----
    # 题族=号起段且含【答案】；条目族=号起段且块内无【答案】（同恒等式核账口径）
    paras = [p for p in body.iter(q('p'))]
    texts = [para_text(p) for p in paras]
    starts = []
    for i, t in enumerate(texts):
        m = HNUM.match(t.strip())
        if m: starts.append((i, m.group(1), int(m.group(2))))
    # 块边界：从号起段到下一号起段（同族判定用块内文本——【答案】在详解块）
    qh = defaultdict(list); eh = defaultdict(list)
    for k, (i, sec, no) in enumerate(starts):
        j = starts[k+1][0] if k+1 < len(starts) else len(texts)
        block = '\n'.join(texts[i:j])
        if '【答案】' in block: qh[sec].append(no)
        else: eh[sec].append(no)
    qprobs = []; eprobs = []
    for sec in sorted(set(list(qh) + list(eh))):
        for fam, d, probs in (('题族', qh, qprobs), ('条目族', eh, eprobs)):
            if sec in d:
                seq = d[sec]
                exp = list(range(1, len(seq)+1))
                if seq != exp: probs.append((sec, seq))
    qtot = sum(len(v) for v in qh.values()); etot = sum(len(v) for v in eh.values())
    dist = {sec: (len(qh.get(sec, [])), len(eh.get(sec, []))) for sec in sorted(set(list(qh)+list(eh)))}
    r['序列'] = {'题族分布': {s: v[0] for s, v in dist.items() if v[0]}, '条目族分布': {s: v[1] for s, v in dist.items() if v[1]},
                 '题总数': qtot, '条目总数': etot, '题族断点重复': qprobs, '条目族断点重复': eprobs}
    P('序列: 题族=%s 合计%d｜条目族=%s 合计%d' % (
        {s: v[0] for s, v in dist.items() if v[0]}, qtot,
        {s: v[1] for s, v in dist.items() if v[1]}, etot))
    P('   题族断点/重复=%s 条目族断点/重复=%s（空=节内连续无重复）' % (qprobs, eprobs))

    # ---- 项3 七类底纹分桶（自写独立计数，与工具对照）----
    b1 = b2 = b7 = 0
    for p in body.iter(q('p')):
        f = eff_para_shd(p, styles)
        if f == 'ADC2DA': b1 += 1
        elif f == 'C6D4E3': b2 += 1
        elif f == 'F2F2F2': b7 += 1
    # run级C9C9C9分桶：题号块(加粗+号起)/块标签【×】/条目号(不加粗号起)/第一子层（N）/文字型答案值·需背
    b3 = b4 = b5 = b6 = b0 = 0
    for p in body.iter(q('p')):
        t = para_text(p).strip()
        for rn in p.iter(q('r')):
            rpr = rn.find(q('rPr'))
            if rpr is None: continue
            s = rpr.find(q('shd'))
            if s is None or s.get(q('fill')) != 'C9C9C9': continue
            rt = ''.join(x.text or '' for x in rn.findall(q('t')))
            bold = rpr.find(q('b')) is not None
            if HNUM.match(t) and t.startswith(rt):
                if bold: b3 += 1
                else: b5 += 1
            elif re.match(r'^【[^】]*】$', rt or ' '):
                b4 += 1
            elif re.match(r'^（\d{1,2}）$', rt or ' '):
                b6 += 1
            else:
                b0 += 1  # 文字型答案值/需背/并行解法标记等
    r['七类'] = {'①ADC2DA': b1, '②C6D4E3': b2, '③题号块': b3, '④块标签': b4, '⑤条目号': b5, '⑥第一子层': b6, '⑦F2F2F2段': b7, 'C9C9C9其他run(答案值/需背等)': b0}
    P('七类自算: %s' % r['七类'])

    # ---- 项5 锚定 ----
    na = ao0 = wrap = 0; ao_other = []
    for an in body.iter('{%s}anchor' % WP):
        na += 1
        ao = an.get('allowOverlap')
        if ao == '0': ao0 += 1
        else: ao_other.append(ao)
        if an.find('{%s}wrapSquare' % WP) is not None: wrap += 1
    ninline = len(list(body.iter('{%s}inline' % WP)))
    r['锚定'] = {'anchor': na, 'allowOverlap=0': ao0, '其他值': ao_other, 'wrapSquare': wrap, 'inline': ninline}
    P('锚定: anchor=%d allowOverlap=0=%d 其他=%s wrapSquare=%d inline=%d' % (na, ao0, ao_other, wrap, ninline))

    # ---- 项6 页眉页脚同串 ----
    hf = {}
    for hn in sorted(n for n in zf.namelist() if re.match(r'word/(header|footer)\d*\.xml$', n)):
        root = etree.fromstring(zf.read(hn))
        texts = []; instr = []; cached = []; state = 0; fld = Counter()
        for el in root.iter():
            ln = etree.QName(el).localname
            if ln == 'fldChar':
                fld[el.get(q('fldCharType'))] += 1
                if el.get(q('fldCharType')) == 'separate': state = 1
                elif el.get(q('fldCharType')) == 'end': state = 0
            elif ln == 'instrText': instr.append(el.text or '')
            elif ln == 't':
                texts.append(el.text or '')
                if state: cached.append(el.text or '')
        full = ''.join(texts)
        jc = []
        for pp in root.iter(q('p')):
            ppr = pp.find(q('pPr'))
            j = ppr.find(q('jc')) if ppr is not None else None
            jc.append(j.get(q('val')) if j is not None else 'absent')
        szs = Counter()
        for rn in root.iter(q('r')):
            if rn.find(q('t')) is None: continue
            txt = ''.join(x.text or '' for x in rn.findall(q('t')))
            if txt.strip(): szs[get_sz(rn.find(q('rPr')))] += 1
        hf[hn] = {'串': full, 'instr': instr, 'fldChar': dict(fld), '缓存': ''.join(cached),
                  'fldSimple': len(root.findall('.//' + q('fldSimple'))), 'jc': jc, 'run字号': dict(szs)}
        P('  %s:' % hn)
        P('     可见串=[%s]' % full)
        P('     instr=%s fldChar=%s fldSimple=%s NUMPAGES=%s 缓存=%r jc=%s run字号=%s' % (
            instr, dict(fld), hf[hn]['fldSimple'], sum(1 for i in instr if 'NUMPAGES' in i),
            ''.join(cached), jc, dict(szs)))
    st = zf.read('word/settings.xml').decode('utf-8', 'ignore')
    sect = body.find(q('sectPr'))
    pnt = sect.find(q('pgNumType')) if sect is not None else None
    r['页眉页脚'] = hf; r['settings_updateFields'] = 'w:updateFields' in st
    r['pgNumType_start'] = pnt.get(q('start')) if pnt is not None else None
    P('settings updateFields=%s sectPr pgNumType start=%s' % (r['settings_updateFields'], r['pgNumType_start']))
    pg = sect.find(q('pgSz')); mar = sect.find(q('pgMar'))
    r['pgSz'] = norm(pg.attrib); r['pgMar'] = norm(mar.attrib)
    P('pgSz=%s pgMar=%s' % (r['pgSz'], r['pgMar']))
    r['docDefaults'] = {'rPrDefault_sz': rpd_sz, 'pPrDefault_spacing': ppd}
    P('docDefaults: rPrDefault sz=%s pPrDefault spacing=%s' % (rpd_sz, ppd))
    zf.close()
    res[code] = r

json.dump(res, open(os.path.join(OUT, 'r2a_xml审计.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
out.close(); print('DONE')
