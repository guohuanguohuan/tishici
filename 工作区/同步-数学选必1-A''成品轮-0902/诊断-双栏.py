# -*- coding: utf-8 -*-
"""双栏工具内部二分：--only cols|img"""
import sys, zipfile, os, importlib.util, copy
from lxml import etree
spec = importlib.util.spec_from_file_location('dc', r'C:\提示词\工具\双栏改制工具.py')
dc = importlib.util.module_from_spec(spec); spec.loader.exec_module(dc)
only = sys.argv[2]
path = sys.argv[1]
z = zipfile.ZipFile(path); parts = {n: z.read(n) for n in z.namelist()}; z.close()
doc = etree.fromstring(parts['word/document.xml'])
body = doc.find(dc.q('body'))
stats = {}
if only in ('img', 'both'):
    for anchor in list(body.iter(dc.wq('anchor'))):
        run = anchor.getparent()
        while run is not None and dc.tag(run) != 'r': run = run.getparent()
        p = anchor.getparent()
        while p is not None and dc.tag(p) != 'p': p = p.getparent()
        inline = dc.convert_anchor(p, anchor)
        p_txt = dc.ptext(p)
        other = [e for e in p.iter() if dc.tag(e) == 't' and (e.text or '').strip()]
        has_math = next(p.iter(dc.q('oMath')), None) is not None
        if not other and not has_math:
            anchor.getparent().replace(anchor, inline)
        else:
            newp = etree.Element(dc.q('p'))
            ppr = etree.SubElement(newp, dc.q('pPr'))
            jc = etree.SubElement(ppr, dc.q('jc')); jc.set(dc.q('val'), 'left')
            newr = etree.SubElement(newp, dc.q('r'))
            dr = etree.SubElement(newr, dc.q('drawing')); dr.append(inline)
            p.addnext(newp)
            if all(dc.tag(c) in ('rPr',) or c is anchor for c in run):
                run.getparent().remove(run)
            else:
                anchor.getparent().remove(anchor)
if only in ('cols', 'both'):
    body_sect = body.find(dc.q('sectPr'))
    head_end = dc.find_header_end(body)
    cand = None
    for j in range(head_end - 1, -1, -1):
        if dc.tag(body[j]) == 'p':
            ppr_j = body[j].find(dc.q('pPr'))
            sid_j = None
            if ppr_j is not None:
                ps_j = ppr_j.find(dc.q('pStyle'))
                sid_j = ps_j.get(dc.q('val')) if ps_j is not None else None
            if sid_j in ('JieMingMao', '节名锚'): continue
            cand = body[j]; break
    head_sect = dc.make_head_sectpr(body_sect)
    ppr = cand.find(dc.q('pPr'))
    if ppr is None:
        ppr = etree.Element(dc.q('pPr')); cand.insert(0, ppr)
    ppr.append(head_sect)
    for ref in ('headerReference', 'footerReference'):
        for el in body_sect.findall(dc.q(ref)): body_sect.remove(el)
    hsect = cand.find(dc.q('pPr')).find(dc.q('sectPr'))
    dc.set_cols(hsect, 1); dc.set_cols(body_sect, 2)
    ty = hsect.find(dc.q('type'))
    if ty is None:
        ty = etree.Element(dc.q('type')); hsect.insert(0, ty)
    ty.set(dc.q('val'), 'continuous')
parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
tmp = path + '.diag'
zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
for nm, b in parts.items(): zo.writestr(nm, b)
zo.close(); os.replace(tmp, path)
print(only, 'done')
