# -*- coding: utf-8 -*-
# 一次性勘察脚本：三件副本的页眉页脚/节标题/样式/sectPr现状
import sys, io, zipfile, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
def q(t): return '{%s}%s' % (W, t)

def para_text(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def inspect(path):
    print('=' * 70)
    print('##', path)
    z = zipfile.ZipFile(path)
    names = z.namelist()
    doc = etree.fromstring(z.read('word/document.xml'))
    styles = etree.fromstring(z.read('word/styles.xml'))

    # Normal styleId
    docdefaults = styles.find(q('docDefaults'))
    normal_sid = None
    for st in styles.findall(q('style')):
        stype = st.get(q('type'))
        dflt = st.get(q('default'))
        nm = st.find(q('name'))
        nv = (nm.get(q('val')) or '') if nm is not None else ''
        if stype == 'paragraph' and dflt == '1' and nv.lower() in ('normal',):
            normal_sid = st.get(q('styleId'))
        if stype == 'paragraph' and nv.lower() == 'normal':
            normal_sid = normal_sid or st.get(q('styleId'))
    print('Normal styleId =', normal_sid)
    # styles with name heading3-ish
    for st in styles.findall(q('style')):
        nm = st.find(q('name'))
        nv = (nm.get(q('val')) or '') if nm is not None else ''
        if 'heading 3' in nv.lower() or '标题 3' in nv or '标题3' in nv:
            print('  heading3样式: styleId=%s name=%r' % (st.get(q('styleId')), nv))
    # 是否已有节名锚样式
    for st in styles.findall(q('style')):
        nm = st.find(q('name'))
        nv = (nm.get(q('val')) or '') if nm is not None else ''
        if '节名锚' in nv or '节名锚' in (st.get(q('styleId')) or ''):
            print('  已有节名锚样式: styleId=%s' % st.get(q('styleId')))

    # docDefaults rPr/pPr摘要
    if docdefaults is not None:
        rpd = docdefaults.find(q('rPrDefault'))
        ppd = docdefaults.find(q('pPrDefault'))
        print('  rPrDefault:', etree.tostring(rpd, encoding='unicode')[:220] if rpd is not None else None)
        print('  pPrDefault:', etree.tostring(ppd, encoding='unicode')[:220] if ppd is not None else None)
    # docGrid
    dg = styles.find(q('docGrid'))
    print('  styles docGrid:', etree.tostring(dg, encoding='unicode')[:120] if dg is not None else None)

    # sectPr
    for i, sp in enumerate(doc.find(q('body')).findall(q('sectPr')), 1):
        mar = sp.find(q('pgMar'))
        sz = sp.find(q('pgSz'))
        pnt = sp.find(q('pgNumType'))
        tp = sp.find(q('titlePg'))
        refs = [(hr.tag.split('}')[-1], hr.get(q('type')), hr.get('{%s}id' % R)) for hr in sp.iter() if hr.tag in (q('headerReference'), q('footerReference'))]
        print('  sectPr#%d: pgSz=%s pgMar=%s pgNumType=%s titlePg=%s refs=%s' % (
            i, dict(sz.attrib) if sz is not None else None,
            {k.split('}')[-1]: v for k, v in mar.attrib.items()} if mar is not None else None,
            {k.split('}')[-1]: v for k, v in pnt.attrib.items()} if pnt is not None else None,
            tp is not None, refs))
    # 段内sectPr（节中断）
    n_inline_sect = sum(1 for p in doc.find(q('body')).iter(q('p')) if p.find(q('pPr')) is not None and p.find(q('pPr')).find(q('sectPr')) is not None)
    print('  段内sectPr数 =', n_inline_sect)

    # 页眉页脚部件
    rels = etree.fromstring(z.read('word/_rels/document.xml.rels'))
    relmap = {rel.get('Id'): rel.get('Target') for rel in rels}
    for hr in doc.iter(q('headerReference')):
        rid = hr.get('{%s}id' % R)
        tgt = relmap.get(rid, '?')
        print('  headerReference type=%s -> %s' % (hr.get(q('type')), tgt))
    for fr in doc.iter(q('footerReference')):
        rid = fr.get('{%s}id' % R)
        tgt = relmap.get(rid, '?')
        print('  footerReference type=%s -> %s' % (fr.get(q('type')), tgt))
    for n in names:
        if re.fullmatch(r'word/(header|footer)\d+\.xml', n):
            root = etree.fromstring(z.read(n))
            paras = root.findall(q('p'))
            txts = [para_text(p) for p in paras]
            fld = [fc.get(q('fldCharType')) for fc in root.iter(q('fldChar'))]
            instr = [it.text for it in root.iter(q('instrText'))]
            jc = []
            for p in paras:
                ppr = p.find(q('pPr'))
                j = ppr.find(q('jc')) if ppr is not None else None
                jc.append(j.get(q('val')) if j is not None else None)
            tabs = 'tabs' if any(ppr is not None and ppr.find(q('tabs')) is not None for ppr in [p.find(q('pPr')) for p in paras]) else 'no-tabs'
            print('  部件 %s: 段数=%d 文本=%r jc=%s fldChar=%s instrText=%s %s' % (n, len(paras), txts, jc, fld, instr, tabs))

    # 节标题段（heading3 styleId）
    sid3 = None
    for st in styles.findall(q('style')):
        nm = st.find(q('name'))
        nv = (nm.get(q('val')) or '') if nm is not None else ''
        if nv.strip().lower() in ('heading 3', '标题3') or nv == '标题 3':
            sid3 = st.get(q('styleId'))
            break
    body = doc.find(q('body'))
    h3_paras = []
    for p in body.iter(q('p')):
        ppr = p.find(q('pPr'))
        if ppr is None: continue
        ps = ppr.find(q('pStyle'))
        if ps is not None and sid3 and ps.get(q('val')) == sid3:
            h3_paras.append(para_text(p))
    print('  heading3节标题数=%d（styleId=%s）' % (len(h3_paras), sid3))
    for t in h3_paras[:8]:
        print('    节标题: %r' % t)
    if len(h3_paras) > 8: print('    ... 共%d个' % len(h3_paras))

    # settings.xml
    st = z.read('word/settings.xml').decode('utf-8')
    print('  settings: updateFields=%s evenAndOdd=%s' % ('<w:updateFields' in st, '<w:evenAndOddHeaders' in st))
    z.close()

for f in ['X2副本.docx', 'B副本.docx', 'C副本.docx']:
    inspect(f)
