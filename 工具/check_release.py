# -*- coding: utf-8 -*-
"""check_release.py — 成品讲练件八项排版自检+结构恒等式（数字落盘）
用法: python check_release.py <docx> [<docx>...]  输出 排版自检报告.md"""
import sys, io, zipfile, re, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname

def ptext(p):
    return ''.join(t.text or '' for t in p.findall('.//' + q('t')))

def check(path):
    R = {'file': os.path.basename(path)}
    z = zipfile.ZipFile(path)
    names = z.namelist()
    doc = etree.fromstring(z.read('word/document.xml'))
    body = doc.find(q('body'))
    paras_all = [p for p in body.iter(q('p'))]
    body_children = list(body)
    body_paras = [el for el in body_children if el.tag == q('p')]

    # ---- 题块与结构 ----
    texts = {id(p): ptext(p) for p in paras_all}
    items = []
    for i, el in enumerate(body_children):
        if el.tag == q('p'):
            t = ptext(el)
            if re.match(r'^\d+(\.\d+)*\s+\S', t):
                kind = 'group' if ('：' in t and re.match(r'^\d+(\.\d+)+\s', t)) else 'section'
            elif re.match(r'^\d+．', t):
                kind = 'qstart'
            elif t.startswith('题型通式：'):
                kind = 'formula_sent'
            else:
                kind = 'para'
            items.append({'kind': kind, 'el': i, 'text': t, 'node': el})
        else:
            items.append({'kind': 'other', 'el': i, 'text': '[TBL]' if el.tag == q('tbl') else tag(el), 'node': el})
    qs = []
    n = len(items); i = 0
    while i < n:
        if items[i]['kind'] == 'qstart':
            j = i + 1
            while j < n and items[j]['kind'] == 'para':
                j += 1
            blk = '\n'.join(items[k]['text'] for k in range(i, j))
            md = re.search(r'【难度】(简单|中档|难)', blk)
            mno = re.match(r'^(\d+)．', items[i]['text'])
            if md and mno:
                qs.append({'no': int(mno.group(1)), 'diff': md.group(1), 'i0': items[i]['el']})
                i = j; continue
        i += 1
    nos = [x['no'] for x in qs]
    gaps = [(nos[k-1], nos[k]) for k in range(1, len(nos)) if nos[k] != nos[k-1] + 1]
    mfile = re.search(r'（(\d+)题）', R['file'])
    fn_n = int(mfile.group(1)) if mfile else -1
    R['题块'] = dict(count=len(qs), first=nos[0] if nos else 0, last=nos[-1] if nos else 0,
                     断点=gaps, 文件名题量=fn_n, 恒等=(len(qs) == fn_n))
    # 标签计数（题块级）
    lab_ok = 0; lab_missing = []
    for k, x in enumerate(qs):
        i0 = x['i0']
        i1 = qs[k+1]['i0'] if k+1 < len(qs) else len(body_children)
        blk = '\n'.join(ptext(el) for el in body_children[i0:i1] if el.tag == q('p'))
        ok = ('【答案】' in blk) and ('【难度】' in blk) and ('【知识点】' in blk)
        if ok: lab_ok += 1
        else: lab_missing.append(x['no'])
    R['标签'] = dict(三标签齐全题数=lab_ok, 缺失题号=lab_missing[:10])
    # 单独占行标签段
    solo_label = sum(1 for el in body_paras if re.fullmatch(r'【(答案|难度|知识点|分析)】[\s\u3000]*', ptext(el)))
    R['单独占行标签段'] = solo_label
    # ---- ① 标题结构 ----
    secs = [x for x in items if x['kind'] == 'section']
    grps = [x for x in items if x['kind'] == 'group']
    bad_after = []
    for g in grps:
        # 找标题后第一个非标题内容（跳过通式句）
        nxt = g['el'] + 1
        while nxt < len(body_children):
            el = body_children[nxt]
            if el.tag != q('p'):
                bad_after.append(('TBL after group', g['text'][:30])); break
            t = ptext(el)
            if t.startswith('题型通式：') or not t.strip():
                nxt += 1; continue
            if re.match(r'^\d+．', t) or t.startswith('【答案】') or t.startswith('【难度】'):
                break
            # 讲部分内容（非题非标签非通式句）→ 合法（讲在题前）
            break
    # 首题前标题链
    first_q_i = qs[0]['i0'] if qs else 0
    chain = []
    for el in body_children[:first_q_i]:
        if el.tag == q('p'):
            t = ptext(el)
            if re.match(r'^\d+(\.\d+)*\s+\S', t) or t.startswith('题型通式：') or t.startswith('本卷') or t.startswith('全件') or t.startswith('人教B版'):
                chain.append(t[:20])
            elif not t.strip():
                chain.append('<空>')
    R['结构'] = dict(节标题=len(secs), 题型标题=len(grps), 通式句=sum(1 for x in items if x['kind'] == 'formula_sent'),
                     题型标题后异常=len(bad_after), 样例=bad_after[:3], 首题前元素链=chain[:12])
    # ---- ③ 空行 ----
    max_empty = 0; cur = 0
    for el in body_paras:
        if not ptext(el).strip() and el.find('.//' + q('drawing')) is None and el.find('.//' + q('pict')) is None and not el.findall('.//' + '{%s}oMath' % M):
            cur += 1; max_empty = max(max_empty, cur)
        else:
            cur = 0
    R['连续空行最大'] = max_empty
    pbb = sum(1 for el in body_paras if el.find(q('pPr')) is not None and el.find(q('pPr')).find(q('pageBreakBefore')) is not None)
    R['pageBreakBefore'] = pbb
    # ---- ④ 栏目残留 ----
    residue = []
    pat = re.compile(r'^(题型[一二三四五六七八九十\d]+|变式练习|【典例\d|大招\d|模块\d|专题练\d|A组|B组|第\d+讲)')
    for el in body_paras:
        t = ptext(el).strip()
        if pat.match(t):
            residue.append(t[:30])
    R['栏目残留'] = dict(count=len(residue), 样例=residue[:5])
    # ---- ⑤ 页脚 ----
    sect = doc.find('.//' + q('sectPr'))
    sz_el = sect.find(q('pgSz')); mar_el = sect.find(q('pgMar'))
    frefs = sect.findall(q('footerReference')); hrefs = sect.findall(q('headerReference'))
    R['页面'] = dict(pgsz=(sz_el.get(q('w')), sz_el.get(q('h'))) if sz_el is not None else None,
                     pgmar={k.split('}')[1]: v for k, v in mar_el.attrib.items()} if mar_el is not None else None,
                     footerReference=len(frefs), headerReference=len(hrefs),
                     titlePg=sect.find(q('titlePg')) is not None,
                     pgNumStart=sect.find(q('pgNumType')).get(q('start')) if sect.find(q('pgNumType')) is not None else None)
    footer_files = [n_ for n_ in names if re.match(r'word/footer\d+\.xml', n_)]
    header_files = [n_ for n_ in names if re.match(r'word/header\d+\.xml', n_)]
    finfo = []
    for fn in footer_files:
        f = etree.fromstring(z.read(fn))
        simple = f.findall('.//' + q('fldSimple'))
        instrs = [t.text for t in f.findall('.//' + q('instrText'))]
        txt = ''.join(t.text or '' for t in f.findall('.//' + q('t')))
        jc = f.find('.//' + q('jc'))
        szs = {s.get(q('val')) for s in f.findall('.//' + q('sz'))}
        finfo.append(dict(part=fn, fldSimple=len(simple), instr=instrs, text=txt[:30], jc=jc.get(q('val')) if jc is not None else None, sz=sorted(szs)))
    st = z.read('word/settings.xml').decode('utf-8') if 'word/settings.xml' in names else ''
    R['页脚'] = dict(parts=finfo, header_parts=len(header_files), updateFields=('updateFields' in st), evenOdd=('evenAndOddHeaders' in st))
    # ---- ⑥ 残留与图 ----
    ins = len(doc.findall('.//' + q('ins'))); dele = len(doc.findall('.//' + q('del')))
    strike = sum(1 for s in doc.findall('.//' + q('strike')) if s.get(q('val'), '1') not in ('0', 'false'))
    color = sum(1 for c in doc.findall('.//' + q('color')) if c.get(q('val')) not in ('auto', '000000', None))
    hl = len(doc.findall('.//' + q('highlight')))
    anchor = len(body.findall('.//' + '{%s}anchor' % WP))
    inline = len(body.findall('.//' + '{%s}inline' % WP))
    omp_std = 0; omp_tbl = 0
    for p in paras_all:
        for omp in p.findall('.//' + '{%s}oMathPara' % M):
            others = [c for c in p if tag(c) not in ('pPr', 'oMathPara')]
            has_other = ptext(p).strip() or p.find('.//' + q('drawing')) is not None
            if not others and not has_other:
                e = p.getparent(); intbl = False
                while e is not None:
                    if tag(e) == 'tbl': intbl = True; break
                    if tag(e) == 'body': break
                    e = e.getparent()
                if intbl: omp_tbl += 1
                else: omp_std += 1
    # 孤儿图引：段含如图/图所示 且 本段与相邻段无图
    orphan = []
    for i, p in enumerate(body_paras):
        t = ptext(p)
        if re.search(r'(如图|图所示|图甲|图乙|图丙|图丁)', t):
            window = [p]
            for d in (1, 2):
                if i-d >= 0: window.append(body_paras[i-d])
                if i+d < len(body_paras): window.append(body_paras[i+d])
            has_img = any(wp.find('.//' + q('drawing')) is not None or wp.find('.//' + q('pict')) is not None for wp in window)
            if not has_img:
                orphan.append(t[:40])
    R['图与残留'] = dict(ins=ins, **{'del': dele}, strike=strike, color=color, highlight=hl,
                        anchor=anchor, inline=inline, 独立公式段_正文=omp_std, 独立公式段_表格内=omp_tbl,
                        孤儿图引候选=len(orphan), 样例=orphan[:5])
    # ---- ⑦ 编号形态 ----
    dbl = [x['text'][:30] for x in items if x['kind'] == 'qstart' and re.match(r'^\d+．[．\d]', x['text'])]
    R['编号形态'] = dict(双句点或双编号=len(dbl), 样例=dbl[:5])
    # ---- ⑧ 格式继承 ----
    sty = etree.fromstring(z.read('word/styles.xml'))
    dd = sty.find(q('docDefaults'))
    rprd = dd.find('.//' + q('rPrDefault') + '/' + q('rPr')) if dd is not None else None
    pprd = dd.find('.//' + q('pPrDefault') + '/' + q('pPr')) if dd is not None else None
    rfonts = rprd.find(q('rFonts')) if rprd is not None else None
    szd = rprd.find(q('sz')) if rprd is not None else None
    spd = pprd.find(q('spacing')) if pprd is not None else None
    nosp = 0; badsp = 0; nofont = 0; runs = 0; wrongsz = 0
    for p in paras_all:
        pPr = p.find(q('pPr'))
        sp = pPr.find(q('spacing')) if pPr is not None else None
        if sp is None: nosp += 1
        elif (sp.get(q('line')), sp.get(q('lineRule')), sp.get(q('before')) or '0', sp.get(q('after')) or '0') != ('300', 'auto', '0', '0'):
            badsp += 1
        for r in p.findall(q('r')):
            if not (r.find(q('t')) is not None or r.find('.//' + q('drawing')) is not None):
                continue
            runs += 1
            rPr = r.find(q('rPr'))
            if rPr is None or rPr.find(q('rFonts')) is None: nofont += 1
            if rPr is not None and rPr.find(q('sz')) is not None and rPr.find(q('sz')).get(q('val')) != '21': wrongsz += 1
    R['格式继承'] = dict(rprdef=(rfonts.get(q('ascii')), rfonts.get(q('eastAsia')), szd.get(q('val')) if szd is not None else None) if rfonts is not None else None,
                         pprdef=(spd.get(q('before')), spd.get(q('after')), spd.get(q('line')), spd.get(q('lineRule'))) if spd is not None else None,
                         无spacing段=nosp, 违规spacing段=badsp, run总数=runs, 无rFonts=round(nofont/runs*100) if runs else 0, 显式非21字号=wrongsz)
    return R

if __name__ == '__main__':
    out = ['# 成品排版自检报告（自动生成，' + sys.argv[0 + 0] + '）']
    for p in sys.argv[1:]:
        r = check(p)
        out.append('\n## ' + r['file'] + '\n')
        for k, v in r.items():
            if k == 'file': continue
            out.append('- **%s**: %s' % (k, json.dumps(v, ensure_ascii=False)))
    open('排版自检报告.md', 'w', encoding='utf-8').write('\n'.join(out))
    print('\n'.join(out))
