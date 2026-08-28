# -*- coding: utf-8 -*-
"""audit_docx.py — 全量体检扫描：页脚域形态/字体继承/行距/锚图/残留/页面设置
用法: python audit_docx.py <docx...>   输出每件一行JSON到stdout（管道收集）"""
import sys, io, zipfile, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)

def audit(path):
    r = {'file': path.split('\\')[-1].split('/')[-1]}
    z = zipfile.ZipFile(path)
    names = z.namelist()
    doc = etree.fromstring(z.read('word/document.xml'))
    body = doc.find(q('body'))

    # --- 页面设置 ---
    sect = doc.find('.//' + q('sectPr'))
    if sect is None:
        r['pgsz'] = 'NONE'
    else:
        sz = sect.find(q('pgSz')); mar = sect.find(q('pgMar'))
        r['pgsz'] = ('%s,%s' % (sz.get(q('w')), sz.get(q('h')))) if sz is not None else 'noPgsz'
        if mar is not None:
            vals = {k.split('}')[1]: v for k, v in mar.attrib.items()}
            r['pgmar'] = 'all850' if all(vals.get(t) == '850' for t in ('top','right','bottom','left','header','footer')) and vals.get('gutter') == '0' else str(vals)
        else:
            r['pgmar'] = 'noPgmar'
        frefs = sect.findall(q('footerReference')); hrefs = sect.findall(q('headerReference'))
        r['footrefs'] = len(frefs); r['headrefs'] = len(hrefs)
        r['titlepg'] = 1 if sect.find(q('titlePg')) is not None else 0
        pnt = sect.find(q('pgNumType'))
        r['pgnum_start'] = pnt.get(q('start')) if pnt is not None else 'none'

    # --- 页脚 ---
    footers = [n for n in names if re.match(r'word/footer\d+\.xml', n)]
    r['n_footer_parts'] = len(footers)
    fld_info = []
    for fn in footers:
        f = etree.fromstring(z.read(fn))
        simple = f.findall('.//' + q('fldSimple'))
        cx = f.findall('.//' + q('fldChar'))
        instr = [t.text for t in f.findall('.//' + q('instrText'))]
        txt = ''.join(t.text or '' for t in f.findall('.//' + q('t')))
        jc = f.find('.//' + q('jc'))
        szs = {s.get(q('val')) for s in f.findall('.//' + q('sz'))}
        fld_info.append({
            'part': fn, 'fldSimple': [s.get(q('instr')) for s in simple],
            'complex_instr': instr, 'cache_txt': txt[:40],
            'jc': jc.get(q('val')) if jc is not None else None, 'sz': sorted(szs)})
    r['footers'] = fld_info

    # --- settings ---
    if 'word/settings.xml' in names:
        st = z.read('word/settings.xml').decode('utf-8')
        r['updateFields'] = 1 if 'updateFields' in st else 0
        r['evenOdd'] = 1 if 'evenAndOddHeaders' in st else 0
    else:
        r['updateFields'] = -1; r['evenOdd'] = -1

    # --- styles docDefaults ---
    if 'word/styles.xml' in names:
        sty = etree.fromstring(z.read('word/styles.xml'))
        dd = sty.find(q('docDefaults'))
        rPrDef = pPrDef = None
        if dd is not None:
            rPrDef = dd.find('.//' + q('rPrDefault') + '/' + q('rPr'))
            pPrDef = dd.find('.//' + q('pPrDefault') + '/' + q('pPr'))
        if rPrDef is not None:
            fnt = rPrDef.find(q('rFonts'))
            r['rprdef_fonts'] = ('%s|%s|%s' % (fnt.get(q('ascii')), fnt.get(q('hAnsi')), fnt.get(q('eastAsia')))) if fnt is not None else 'none'
            if fnt is not None and (fnt.get(q('ascii')) and 'Theme' in (fnt.get(q('ascii')) or '')):
                r['rprdef_fonts'] = 'THEME:' + r['rprdef_fonts']
            szel = rPrDef.find(q('sz'))
            r['rprdef_sz'] = szel.get(q('val')) if szel is not None else 'none'
        else:
            r['rprdef_fonts'] = 'noRPrDefault'; r['rprdef_sz'] = 'noRPrDefault'
        if pPrDef is not None:
            sp = pPrDef.find(q('spacing'))
            r['pprdef_spacing'] = ('%s/%s/%s/%s' % (sp.get(q('before')), sp.get(q('after')), sp.get(q('line')), sp.get(q('lineRule')))) if sp is not None else 'none'
        else:
            r['pprdef_spacing'] = 'noPPrDefault'

    # --- 正文段落/run 统计（非空段；跳过数学区内部） ---
    n_nofont_runs = 0; n_runs = 0; n_para_nosp = 0; n_para_badsp = 0; n_para = 0
    n_anchor = 0; n_inline = 0; n_ins = len(doc.findall('.//' + q('ins')))
    n_del = len(doc.findall('.//' + q('del')))
    n_strike = sum(1 for s in doc.findall('.//' + q('strike')) if s.get(q('val'), '1') not in ('0', 'false'))
    n_color = sum(1 for c in doc.findall('.//' + q('color')) if c.get(q('val')) not in ('auto', '000000', None))
    n_hl = len(doc.findall('.//' + q('highlight')))
    n_omathpara = len(doc.findall('.//{http://schemas.openxmlformats.org/officeDocument/2006/math}oMathPara'))
    for p in body.iter(q('p')):
        # 非空段判定：含 w:t 文本或公式或图
        has_txt = any((t.text or '').strip() for t in p.findall('.//' + q('t')))
        has_math = p.find('.//{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath') is not None
        has_draw = p.find('.//' + q('drawing')) is not None or p.find('.//' + q('pict')) is not None
        if not (has_txt or has_math or has_draw):
            continue
        n_para += 1
        pPr = p.find(q('pPr'))
        sp = pPr.find(q('spacing')) if pPr is not None else None
        if sp is None:
            n_para_nosp += 1
        else:
            if sp.get(q('line')) != '300' or sp.get(q('lineRule')) != 'auto' or sp.get(q('before')) not in (None, '0') or sp.get(q('after')) not in (None, '0'):
                n_para_badsp += 1
        # run 字体（跳过 m:oMath 内部与 rPr 无关的）
        for run in p.findall(q('r')):
            rPr = run.find(q('rPr'))
            has_content = run.find(q('t')) is not None or run.find(q('drawing')) is not None or run.find(q('pict')) is not None
            if not has_content: continue
            n_runs += 1
            if rPr is None or rPr.find(q('rFonts')) is None:
                # 检查是否主题字体情形——无 rFonts 一律计（需docDefaults显式才安全）
                n_nofont_runs += 1
    WP = '{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'
    n_anchor = len(doc.findall('.//' + WP + 'anchor'))
    n_inline = len(doc.findall('.//' + WP + 'inline'))
    # 块级公式形态：独立成段（段落唯一内容是 oMathPara）vs 段内混排
    M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
    n_omathpara_standalone = 0; n_omathpara_mixed = 0
    for omp in doc.findall('.//' + M + 'oMathPara'):
        p = omp.getparent()
        while p is not None and p.tag != q('p'):
            p = p.getparent()
        if p is None:
            n_omathpara_mixed += 1; continue
        others = [c for c in p if c.tag not in (q('pPr'), M + 'oMathPara')]
        has_txt = any((t.text or '').strip() for t in p.findall('.//' + q('t')))
        if others or has_txt:
            n_omathpara_mixed += 1
        else:
            n_omathpara_standalone += 1
    r['body'] = {'paras': n_para, 'para_nospacing': n_para_nosp, 'para_badspacing': n_para_badsp,
                 'runs': n_runs, 'runs_norfonts': n_nofont_runs,
                 'anchor': n_anchor, 'inline': n_inline, 'ins': n_ins, 'del': n_del,
                 'strike': n_strike, 'color': n_color, 'highlight': n_hl,
                 'oMathPara': n_omathpara, 'omp_standalone': n_omathpara_standalone, 'omp_mixed': n_omathpara_mixed}
    # 修订痕迹
    return r

if __name__ == '__main__':
    for p in sys.argv[1:]:
        try:
            print(json.dumps(audit(p), ensure_ascii=False))
        except Exception as e:
            print(json.dumps({'file': p, 'ERROR': str(e)}, ensure_ascii=False))
