# -*- coding: utf-8 -*-
"""R1独立复审计——XML级全量清点：run字号解析值/段落spacing/w:ind/jc/docDefaults/
页眉页脚域形态/件标识/allowOverlap/docGrid/OMML w:sz残留。只读，不改任何产出文件。"""
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

def style_sz(styles, sid):
    seen = set()
    sz = None
    while sid and sid in styles and sid not in seen:
        seen.add(sid)
        st = styles[sid]
        if sz is None and st['sz'] is not None:
            sz = st['sz']
        sid = st['based']
    return sz

def resolve_run_sz(r, p, styles, docdef_sz):
    rpr = r.find(q('rPr'))
    v = get_sz(rpr)
    if v is not None: return v, 'run'
    sid = para_style_id(p)
    if sid:
        v = style_sz(styles, sid)
        if v is not None: return v, 'style:' + sid
    return docdef_sz, 'docDefaults'

def parse_styles(zf):
    styles = {}
    try:
        root = etree.fromstring(zf.read('word/styles.xml'))
    except KeyError:
        return styles, None, None
    dd = root.find(q('docDefaults'))
    rpd_sz = None; rpd_fonts = None; ppd = None
    if dd is not None:
        rpd = dd.find(q('rPrDefault'))
        if rpd is not None:
            rpr = rpd.find(q('rPr'))
            if rpr is not None:
                rpd_sz = get_sz(rpr)
                f = rpr.find(q('rFonts'))
                if f is not None:
                    rpd_fonts = {k.split('}')[1]: v for k, v in f.attrib.items()}
        ppd_ = dd.find(q('pPrDefault'))
        if ppd_ is not None:
            ppr = ppd_.find(q('pPr'))
            if ppr is not None:
                sp = ppr.find(q('spacing')); ind = ppr.find(q('ind')); jc = ppr.find(q('jc'))
                ppd = {'spacing': dict(sp.attrib) if sp is not None else None,
                       'ind': dict(ind.attrib) if ind is not None else None,
                       'jc': jc.get(q('val')) if jc is not None else None}
    for st in root.iter(q('style')):
        sid = st.get(q('styleId'))
        rpr = st.find(q('rPr'))
        bo = st.find(q('basedOn'))
        nm = st.find(q('name'))
        styles[sid] = {'sz': get_sz(rpr),
                       'based': bo.get(q('val')) if bo is not None else None,
                       'name': nm.get(q('val')) if nm is not None else None}
    return styles, (rpd_sz, rpd_fonts), ppd

def norm_attrs(d):
    return {k.split('}')[1]: v for k, v in d.items()} if d else {}

out = open(r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\输出\a1_xml审计.txt', 'w', encoding='utf-8')
def P(*a):
    print(*a)
    print(*a, file=out)

for code, fn in FILES:
    path = os.path.join(D, fn)
    P('=' * 100)
    P('### %s %s' % (code, fn))
    zf = zipfile.ZipFile(path)
    styles, (rpd_sz, rpd_fonts), ppd = parse_styles(zf)
    P('docDefaults rPrDefault: sz=%s fonts=%s' % (rpd_sz, rpd_fonts))
    P('docDefaults pPrDefault: %s' % (ppd,))
    # 显式rFonts核对（中文宋体/西文TNR）
    exp_fonts = {'eastAsia': '宋体', 'ascii': 'Times New Roman', 'hAnsi': 'Times New Roman'}

    doc = etree.fromstring(zf.read('word/document.xml'))
    body = doc.find(q('body'))

    # ---- sectPr / docGrid / pgMar ----
    for sect in body.iter(q('sectPr')):
        dg = sect.find(q('docGrid'))
        pg = sect.find(q('pgSz')); mar = sect.find(q('pgMar')); pnt = sect.find(q('pgNumType'))
        P('sectPr: pgSz=%s pgMar=%s pgNumType=%s docGrid=%s' % (
            norm_attrs(pg.attrib) if pg is not None else None,
            norm_attrs(mar.attrib) if mar is not None else None,
            norm_attrs(pnt.attrib) if pnt is not None else None,
            norm_attrs(dg.attrib) if dg is not None else 'ABSENT'))

    # ---- 段落与run全量清点（含表格内段落；页眉页脚另查） ----
    sz_counter = Counter(); sz_ex = defaultdict(list)
    spacing_bad = []; ind_bad = []; jc_bad = []
    npara = 0
    anchor_name = None
    for sid, st in styles.items():
        if st['name'] == '节名锚':
            anchor_name = sid
    for p in body.iter(q('p')):
        npara += 1
        ppr = p.find(q('pPr'))
        sid = para_style_id(p)
        is_anchor = (sid == anchor_name)
        # spacing
        sp = ppr.find(q('spacing')) if ppr is not None else None
        spa = norm_attrs(sp.attrib) if sp is not None else None
        if is_anchor:
            ok = spa and spa.get('line') == '20' and spa.get('lineRule') == 'exact'
            if not ok: spacing_bad.append(('锚段spacing异常', spa, para_text(p)[:30]))
        else:
            ok = spa and spa.get('line') == '410' and spa.get('lineRule') == 'atLeast'
            if not ok:
                # 无显式→继承style链
                sv = None
                if sid and sid in styles:
                    # style链上的spacing
                    cur = sid; hops = 0
                    while cur and cur in styles and hops < 10:
                        hops += 1
                        rootst = None
                        cur2 = styles[cur]['based']
                        cur = cur2
                if not ok and spa is None:
                    spacing_bad.append(('无显式spacing(继承)', sid, para_text(p)[:30]))
                elif not ok:
                    spacing_bad.append(('spacing偏离', spa, para_text(p)[:30]))
        # ind
        ind = ppr.find(q('ind')) if ppr is not None else None
        if ind is not None:
            ia = norm_attrs(ind.attrib)
            if any(v not in ('0',) for v in ia.values()):
                ind_bad.append((ia, para_text(p)[:30]))
        # jc
        jc = ppr.find(q('jc')) if ppr is not None else None
        if jc is not None and jc.get(q('val')) != 'left':
            jc_bad.append((jc.get(q('val')), para_text(p)[:30]))
        # run字号
        for r in p.iter(q('r')):
            has_t = r.find(q('t')) is not None
            if not has_t: continue
            txt = ''.join(t.text or '' for t in r.findall(q('t')))
            if not txt.strip(): continue
            v, src = resolve_run_sz(r, p, styles, rpd_sz)
            sz_counter[v] += 1
            if len(sz_ex[v]) < 3:
                sz_ex[v].append((src, sid, txt[:24]))
    P('正文run字号解析值分布: %s （段落总数=%d）' % (dict(sorted(sz_counter.items(), key=lambda x: -(x[1] if x[1] else 0))), npara))
    for v, exs in sorted(sz_ex.items(), key=lambda x: -(x[0] or 0)):
        P('  sz=%s 例: %s' % (v, exs))
    P('spacing偏离/无显式数=%d（前8例: %s）' % (len(spacing_bad), spacing_bad[:8]))
    P('w:ind非零数=%d（前8例: %s）' % (len(ind_bad), ind_bad[:8]))
    P('jc非left数=%d（例: %s）' % (len(jc_bad), jc_bad[:3]))

    # OMML 内 w:sz 残留（裁决1剥除断言）
    omml_sz = 0
    for om in body.iter('{%s}oMath' % M):
        for rpr in om.iter(q('rPr')):
            if rpr.find(q('sz')) is not None:
                omml_sz += 1
    P('OMML子树内w:sz挂点数=%d（期望0）' % omml_sz)

    # ---- 环绕/anchor/allowOverlap ----
    n_anchor = 0; ao0 = 0; ao_other = []; n_inline = 0; n_wrapsq = 0
    for an in body.iter('{%s}anchor' % WP):
        n_anchor += 1
        ao = an.get('allowOverlap')
        if ao == '0': ao0 += 1
        else: ao_other.append(ao)
        if an.find('{%s}wrapSquare' % WP) is not None: n_wrapsq += 1
    n_inline = len(list(body.iter('{%s}inline' % WP)))
    P('wp:anchor=%d allowOverlap=0=%d 其他=%s wrapSquare=%d wp:inline=%d' % (
        n_anchor, ao0, Counter(ao_other), n_wrapsq, n_inline))

    # ---- 页眉页脚部件 ----
    hf_parts = [n for n in zf.namelist() if re.match(r'word/(header|footer)\d*\.xml$', n)]
    P('页眉页脚部件: %s' % hf_parts)
    for hn in sorted(hf_parts):
        root = etree.fromstring(zf.read(hn))
        paras = root.find(q('p')) is not None and root.findall(q('p')) or root.iter(q('p'))
        texts = []
        fld = Counter(); instr = []
        cached = []
        state = 0
        for el in root.iter():
            t_ = etree.QName(el).localname
            if t_ == 'fldChar':
                fld[el.get(q('fldCharType'))] += 1
                if el.get(q('fldCharType')) == 'separate': state = 1
                elif el.get(q('fldCharType')) == 'end': state = 0
            elif t_ == 'instrText':
                instr.append(el.text or '')
            elif t_ == 't':
                texts.append(el.text or '')
                if state: cached.append(el.text or '')
        full = ''.join(texts)
        jc_all = [pp.find(q('jc')).get(q('val') ) if pp.find(q('jc')) is not None else '(absent)' 
                  for pp in root.iter(q('p')) for ppr in [pp.find(q('pPr')) or etree.Element('x')] ]
        # run字号
        szs = Counter()
        for r_ in root.iter(q('r')):
            if r_.find(q('t')) is None: continue
            txt = ''.join(t.text or '' for t in r_.findall(q('t')))
            if not txt.strip(): continue
            szs[get_sz(r_.find(q('rPr')))] += 1
        P('  %s: 可见串=[%s]' % (hn, full))
        P('     域: fldChar=%s instr=%s fldSimple=%s NUMPAGES=%s 缓存值=%r run字号=%s' % (
            dict(fld), instr, len(root.findall('.//' + q('fldSimple'))),
            sum(1 for i in instr if 'NUMPAGES' in i), ''.join(cached), dict(szs)))
        # 位置对齐/jc/spacing of hf paras
        for pp in root.iter(q('p')):
            ppr = pp.find(q('pPr'))
            jc = ppr.find(q('jc')) if ppr is not None else None
            sp = ppr.find(q('spacing')) if ppr is not None else None
            P('     段落 jc=%s spacing=%s' % (jc.get(q('val')) if jc is not None else 'absent',
               norm_attrs(sp.attrib) if sp is not None else 'absent'))
    # settings updateFields
    st = zf.read('word/settings.xml').decode('utf-8', 'ignore')
    P('settings updateFields=%s' % ('w:updateFields' in st))
    zf.close()

out.close()
print('DONE')
