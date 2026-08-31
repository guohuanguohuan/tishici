# -*- coding: utf-8 -*-
"""E1独立复审计·只读XML探针：不改任何成品件，仅zip只读解析，输出JSON到本子文件夹。"""
import sys, os, re, json, zipfile
from lxml import etree

NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
}
W = NS['w']
def q(tag): return '{%s}%s' % (W, tag)

def linear_omml(el):
    """线性化oMath，取全部m:t文本。"""
    out = []
    for t in el.iter('{http://schemas.openxmlformats.org/officeDocument/2006/math}t'):
        out.append(t.text or '')
    return ''.join(out)

def probe(path, out_json):
    z = zipfile.ZipFile(path)
    res = {'file': os.path.basename(path)}
    doc = etree.fromstring(z.read('word/document.xml'))
    body = doc.find(q('body'))

    # ---- sectPr pgNumType start ----
    starts = []
    for sect in doc.iter(q('sectPr')):
        pgn = sect.find(q('pgNumType'))
        starts.append(pgn.get(q('start')) if pgn is not None else None)
    res['sectPr_starts'] = starts
    # pgSz / pgMar
    sect0 = doc.find('.//' + q('sectPr'))
    pgsz = sect0.find(q('pgSz')); pgmar = sect0.find(q('pgMar'))
    res['pgSz'] = (pgsz.get(q('w')), pgsz.get(q('h'))) if pgsz is not None else None
    res['pgMar'] = {k.split('}')[1]: v for k, v in pgmar.attrib.items()} if pgmar is not None else None
    res['titlePg'] = doc.find('.//' + q('titlePg')) is not None

    # ---- footer parts ----
    footers = [n for n in z.namelist() if n.startswith('word/footer')]
    foot_info = []
    rels = etree.fromstring(z.read('word/_rels/document.xml.rels'))
    relmap = {r.get('Id'): r.get('Target') for r in rels}
    for sect in doc.iter(q('sectPr')):
        for fr in sect.findall(q('footerReference')):
            rid = fr.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            foot_info.append(relmap.get(rid))
    res['footer_refs'] = foot_info
    fdata = []
    for n in sorted(footers):
        f = etree.fromstring(z.read(n))
        flds = [e for e in f.iter(q('fldChar'))]
        kinds = [e.get(q('fldCharType')) for e in flds]
        instr = [(e.text or '') for e in f.iter(q('instrText'))]
        simple = len(f.findall('.//' + q('fldSimple')))
        # visible text
        txt = ''.join(t.text or '' for t in f.iter(q('t')))
        szs = [r.get(q('val')) for r in f.iter(q('sz'))]
        jcs = [p.find(q('jc')).get(q('val')) if p.find(q('jc')) is not None else None
               for p in f.iter(q('p'))]
        fdata.append({'part': n, 'fldChar_kinds': kinds, 'instrText': instr,
                      'fldSimple': simple, 'NUMPAGES': 'NUMPAGES' in ''.join(instr).upper(),
                      'text': txt, 'sz_vals': sorted(set(szs)), 'jc': jcs,
                      'fonts': sorted({r.get('{%s}ascii' % W) for r in f.iter(q('rFonts')) if r.get('{%s}ascii' % W)})})
    res['footers'] = fdata
    # header refs & pgMar header already in pgMar
    # settings.xml
    try:
        s = etree.fromstring(z.read('word/settings.xml'))
        res['updateFields'] = s.find(q('updateFields')) is not None
        res['evenAndOddHeaders'] = s.find(q('evenAndOddHeaders')) is not None
    except KeyError:
        res['updateFields'] = 'no settings.xml'

    # ---- run sz histogram (explicit), samples ----
    sz_hist = {}
    sz24_samples, sz18_samples, sz28_samples, sz32_samples = [], [], [], []
    for r in doc.iter(q('r')):
        rpr = r.find(q('rPr'))
        if rpr is None: continue
        szel = rpr.find(q('sz'))
        if szel is None: continue
        v = szel.get(q('val'))
        sz_hist[v] = sz_hist.get(v, 0) + 1
        t = ''.join(tt.text or '' for tt in r.iter(q('t')))
        if v == '24' and len(sz24_samples) < 12 and t.strip(): sz24_samples.append(t[:40])
        if v == '18' and len(sz18_samples) < 12 and t.strip(): sz18_samples.append(t[:40])
        if v == '28' and len(sz28_samples) < 12 and t.strip(): sz28_samples.append(t[:40])
        if v == '32' and len(sz32_samples) < 12 and t.strip(): sz32_samples.append(t[:40])
    res['sz_hist'] = dict(sorted(sz_hist.items(), key=lambda x: -x[1]))
    res['sz_samples'] = {'24': sz24_samples, '18': sz18_samples, '28': sz28_samples, '32': sz32_samples}

    # ---- paragraph spacing histogram ----
    sp_hist = {}
    for sp in doc.iter(q('spacing')):
        key = (sp.get(q('line')), sp.get(q('lineRule')))
        sp_hist[str(key)] = sp_hist.get(str(key), 0) + 1
    res['spacing_hist'] = sp_hist
    paras = body.findall(q('p'))
    res['body_para_count'] = len(paras)

    # ---- paragraph shading fills ----
    pshd = {}
    for p in paras:
        ppr = p.find(q('pPr'))
        if ppr is None: continue
        shd = ppr.find(q('shd'))
        if shd is None: continue
        fill = shd.get(q('fill'))
        if fill and fill != 'auto':
            pshd[fill.upper()] = pshd.get(fill.upper(), 0) + 1
    res['para_shading'] = pshd

    # ---- run shading C9C9C9 与题号块形态 ----
    run_shd = {}
    qblock_shaded, qblock_ann = [], []
    pat_ann = re.compile(r'^\d+．（(衔接必会|简单·保60%|中档·保80%|难·冲100%)·卡壳看答案）')
    for p in paras:
        runs = p.findall(q('r'))
        first_txt = ''.join(''.join(t.text or '' for t in r.iter(q('t'))) for r in runs[:4])
        p_has_q = False
        for r in runs:
            rpr = r.find(q('rPr'))
            if rpr is None: continue
            shd = rpr.find(q('shd'))
            if shd is None: continue
            fill = (shd.get(q('fill')) or '').upper()
            if not fill or fill == 'AUTO': continue
            run_shd[fill] = run_shd.get(fill, 0) + 1
        # 题号块：段内首个run
    # 题号块统计：文本形如 N．（…卡壳看答案）… 的段落
    nq = 0; nq_shaded_ok = 0; nq_ann_unshaded_ok = 0; bad = []
    for p in paras:
        runs = p.findall(q('r'))
        full = ''.join(''.join(t.text or '' for t in r.iter(q('t'))) for r in runs)
        m = pat_ann.match(full)
        if not m: continue
        nq += 1
        # run1 = "N．" 需C9C9C9+加粗；run2 = 括注 无底纹
        r1 = runs[0]; rpr1 = r1.find(q('rPr'))
        sh1 = rpr1.find(q('shd')) if rpr1 is not None else None
        b1 = rpr1.find(q('b')) if rpr1 is not None else None
        t1 = ''.join(t.text or '' for t in r1.iter(q('t')))
        ok1 = (sh1 is not None and (sh1.get(q('fill')) or '').upper() == 'C9C9C9' and b1 is not None
               and re.fullmatch(r'\d+．', t1))
        if ok1: nq_shaded_ok += 1
        else: bad.append(t1 + '|' + full[:20])
        # 括注run无底纹
        r2 = runs[1] if len(runs) > 1 else None
        if r2 is not None:
            rpr2 = r2.find(q('rPr'))
            sh2 = rpr2.find(q('shd')) if rpr2 is not None else None
            t2 = ''.join(t.text or '' for t in r2.iter(q('t')))
            if sh2 is None and '（' in t2:
                nq_ann_unshaded_ok += 1
    res['qblock'] = {'count': nq, 'shaded_N_only': nq_shaded_ok, 'ann_unshaded': nq_ann_unshaded_ok, 'bad': bad[:6]}
    res['run_shading'] = run_shd

    # ---- 条目号 run（C9C9C9 且文本 ^\d+．$ 且不加粗）----
    ent = 0
    for r in doc.iter(q('r')):
        rpr = r.find(q('rPr'))
        if rpr is None: continue
        shd = rpr.find(q('shd'))
        if shd is None or (shd.get(q('fill')) or '').upper() != 'C9C9C9': continue
        b = rpr.find(q('b'))
        t = ''.join(t.text or '' for t in r.iter(q('t')))
        if re.fullmatch(r'\d+．', t) and b is None:
            ent += 1
    res['entry_shaded_unbold'] = ent

    # ---- 块标签【×】C9C9C9 run 计数 ----
    chip = 0
    for r in doc.iter(q('r')):
        rpr = r.find(q('rPr'))
        if rpr is None: continue
        shd = rpr.find(q('shd'))
        if shd is None or (shd.get(q('fill')) or '').upper() != 'C9C9C9': continue
        t = ''.join(t.text or '' for t in r.iter(q('t')))
        if re.fullmatch(r'【[^】]{1,8}】', t):
            chip += 1
    res['chip_runs'] = chip

    # ---- 深蓝 #1F4E79 ----
    blue = sum(1 for c in doc.iter(q('color')) if (c.get(q('val')) or '').upper() == '1F4E79')
    res['blue_runs_nodes'] = blue
    other_color = {}
    for c in doc.iter(q('color')):
        v = (c.get(q('val')) or '').upper()
        if v in ('1F4E79', 'AUTO'): continue
        other_color[v] = other_color.get(v, 0) + 1
    res['other_colors'] = other_color

    # ---- w:ind / anchor / inline / oMathPara ----
    ind_body = 0
    for p in paras:
        ppr = p.find(q('pPr'))
        if ppr is None: continue
        if ppr.find(q('ind')) is not None: ind_body += 1
    res['body_ind_paras'] = ind_body
    res['anchor'] = len(doc.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}anchor'))
    res['inline'] = len(doc.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}inline'))
    om = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
    res['oMath'] = len(doc.findall('.//{%s}oMath' % om))
    res['oMathPara'] = len(doc.findall('.//{%s}oMathPara' % om))
    # 残留样式
    res['w_ins'] = len(doc.findall('.//' + q('ins')))
    res['w_del'] = len(doc.findall('.//' + q('del')))
    res['strike'] = sum(1 for s in doc.iter(q('strike')))
    res['highlight'] = sum(1 for h in doc.iter(q('highlight')))
    res['pageBreakBefore'] = sum(1 for x in doc.iter(q('pageBreakBefore')))
    res['keepNext'] = sum(1 for x in doc.iter(q('keepNext')))
    res['w_br'] = sum(1 for x in doc.iter(q('br')))

    # ---- styles.xml docDefaults ----
    st = etree.fromstring(z.read('word/styles.xml'))
    dd = st.find(q('docDefaults'))
    rpd = dd.find('.//' + q('rPrDefault') + '/' + q('rPr')) if dd is not None else None
    ppd = dd.find('.//' + q('pPrDefault') + '/' + q('pPr')) if dd is not None else None
    rfonts = rpd.find(q('rFonts')) if rpd is not None else None
    res['docDefaults'] = {
        'sz': rpd.find(q('sz')).get(q('val')) if rpd is not None and rpd.find(q('sz')) is not None else None,
        'ascii': rfonts.get(q('ascii')) if rfonts is not None else None,
        'eastAsia': rfonts.get(q('eastAsia')) if rfonts is not None else None,
        'themeFont': (rfonts is not None and (rfonts.get(q('asciiTheme')) is not None or rfonts.get(q('eastAsiaTheme')) is not None)),
        'pPr_spacing': ({k.split('}')[1]: v for k, v in ppd.find(q('spacing')).attrib.items()}
                        if ppd is not None and ppd.find(q('spacing')) is not None else None),
    }
    # docGrid
    dg = sect0.find(q('docGrid')) if sect0 is not None else None
    res['docGrid'] = ({k.split('}')[1]: v for k, v in dg.attrib.items()} if dg is not None else None)

    # ---- 正文/解析段数（按line值归类）----
    c410 = c280 = cother = 0
    for p in paras:
        ppr = p.find(q('pPr'))
        sp = ppr.find(q('spacing')) if ppr is not None else None
        if sp is None:
            cother += 1; continue
        ln, lr = sp.get(q('line')), sp.get(q('lineRule'))
        if ln == '410' and lr == 'atLeast': c410 += 1
        elif ln == '280' and lr == 'atLeast': c280 += 1
        else: cother += 1
    res['para_line'] = {'410': c410, '280': c280, 'other': cother}

    # ---- ＿＿ 残留（挖空双标记）----
    blanks = sum((''.join(t.text or '' for t in p.iter(q('t')))).count('＿＿') for p in paras)
    res['fullwidth_blank_pairs'] = blanks

    # ---- 随机公式条目抽取（内容抽检用）----
    M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
    formula_paras = []
    for i, p in enumerate(paras):
        oms = p.findall('.//{%s}oMath' % M)
        if oms:
            wt = ''.join(t.text or '' for t in p.iter(q('t')))
            lin = ' ‖ '.join(linear_omml(o) for o in oms)[:300]
            if lin.strip():
                formula_paras.append({'idx': i, 'wtext': wt[:80], 'math': lin})
    # 均匀抽4条（确定性：取len//4*k位置）
    picks = []
    if formula_paras:
        step = max(1, len(formula_paras) // 4)
        for k in range(0, len(formula_paras), step):
            picks.append(formula_paras[k])
            if len(picks) >= 4: break
    res['formula_samples'] = picks

    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print('OK', os.path.basename(path), '->', os.path.basename(out_json),
          '| sz:', res['sz_hist'], '| line:', res['para_line'],
          '| qblock:', res['qblock']['count'], '| starts:', res['sectPr_starts'])

if __name__ == '__main__':
    base = r'C:\Users\28120\Desktop\提示词\高中数学\高中数学同步'
    outd = r'C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\E1审计'
    files = [
        ('X1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'),
        ('I1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx'),
        ('B',  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'),
        ('C',  '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'),
        ('X2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx'),
        ('I2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'),
        ('E',  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx'),
        ('F',  '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'),
        ('G',  '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx'),
        ('H',  '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'),
    ]
    for code, fn in files:
        probe(os.path.join(base, fn), os.path.join(outd, 'probe_%s.json' % code))
