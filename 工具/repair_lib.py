# -*- coding: utf-8 -*-
"""repair_lib.py — 体检修复共用手术库（2026-08-25 修复轮）
功能：页脚复杂域重建+updateFields / docDefaults显式化 / 行距规整 / 锚图转inline /
独立块级公式并入前文字段 / run字号规整。全部操作zip级，原文件不动。"""
import zipfile, re, os, sys, io, shutil
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
NS = {'w': W, 'm': M, 'wp': WP}

def q(t): return '{%s}%s' % (W, t)
def mq(t): return '{%s}%s' % (M, t)
def wq(t): return '{%s}%s' % (WP, t)
def tag(e): return etree.QName(e).localname

def ptext(p):
    return ''.join(t.text or '' for t in p.findall('.//' + q('t')))

RPR = '<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体" w:cs="Times New Roman"/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr>'

def footer_para(prefix, npages):
    """复杂域页脚段：件标识＋全角空格＋第X页（共Y页）。prefix 例：第1章·讲练"""
    def fld(instr, cache):
        return ('<w:r>%s<w:fldChar w:fldCharType="begin"/></w:r>'
                '<w:r>%s<w:instrText xml:space="preserve"> %s </w:instrText></w:r>'
                '<w:r>%s<w:fldChar w:fldCharType="separate"/></w:r>'
                '<w:r>%s<w:t>%s</w:t></w:r>'
                '<w:r>%s<w:fldChar w:fldCharType="end"/></w:r>') % (RPR, RPR, instr, RPR, RPR, cache, RPR)
    return ('<w:p xmlns:w="%s"><w:pPr><w:jc w:val="center"/></w:pPr>'
            '<w:r>%s<w:t xml:space="preserve">%s　</w:t></w:r>'
            '<w:r>%s<w:t>第</w:t></w:r>%s<w:r>%s<w:t>页（共</w:t></w:r>%s<w:r>%s<w:t>页）</w:t></w:r></w:p>'
            ) % (W, RPR, prefix, RPR, fld('PAGE', '1'), RPR, fld('NUMPAGES', str(npages)), RPR)

FOOTER_TMPL = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="%s">%s</w:ftr>'''

def rebuild_footer(path, out, prefix, npages, measure_note=True):
    """页脚整体重建（复杂域+缓存实测值）+settings updateFields+sectPr规整。zip级。"""
    z = zipfile.ZipFile(path)
    names = z.namelist()
    doc = z.read('word/document.xml').decode('utf-8')
    rels = z.read('word/_rels/document.xml.rels').decode('utf-8')
    ct = z.read('[Content_Types].xml').decode('utf-8')
    settings = z.read('word/settings.xml').decode('utf-8') if 'word/settings.xml' in names else '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:settings xmlns:w="%s"/>' % W
    footer_parts = [n for n in names if re.match(r'word/footer\d+\.xml', n)]
    header_parts = [n for n in names if re.match(r'word/header\d+\.xml', n)]
    # rels: 保留/新建 footer1 rId
    foot_rids = dict(re.findall(r'<Relationship Id="(rId\d+)"[^>]*Target="(footer\d+\.xml)"[^>]*/>', rels))
    keep_rid = None
    for rid, tgt in foot_rids.items():
        if tgt == 'footer1.xml':
            keep_rid = rid; break
    if keep_rid is None and foot_rids:
        first = sorted(foot_rids.items(), key=lambda kv: int(kv[1][6:-4]))[0]
        keep_rid = first[0]
        rels = rels.replace('Target="%s"' % first[1], 'Target="footer1.xml"')
    if keep_rid is None:
        used = [int(m) for m in re.findall(r'Id="rId(\d+)"', rels)]
        keep_rid = 'rId%d' % (max(used) + 1 if used else 1)
        rels = rels.replace('</Relationships>', '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/></Relationships>' % keep_rid)
    drop_parts = set()
    for rid, tgt in foot_rids.items():
        if rid != keep_rid and tgt != 'footer1.xml':
            rels = re.sub(r'<Relationship Id="%s"[^>]*/>' % rid, '', rels)
            drop_parts.add('word/' + tgt)
    head_rids = re.findall(r'<Relationship Id="(rId\d+)"[^>]*Target="header\d+\.xml"[^>]*/>', rels)
    for rid in head_rids:
        rels = re.sub(r'<Relationship Id="%s"[^>]*/>' % rid, '', rels)
    for p in drop_parts:
        ct = re.sub(r'<Override PartName="/%s"[^>]*/>' % re.escape(p), '', ct)
    for p in header_parts:
        ct = re.sub(r'<Override PartName="/%s"[^>]*/>' % re.escape(p), '', ct)
    if '/word/footer1.xml' not in ct:
        ct = ct.replace('</Types>', '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>')
    # sectPr: 唯一default footerReference、A4、850、start=1、无titlePg
    m = re.search(r'<w:sectPr\b.*?</w:sectPr>', doc, re.S)
    assert m, 'no sectPr'
    s = m.group(0)
    s2 = re.sub(r'<w:headerReference[^/]*/>|<w:footerReference[^/]*/>', '', s)
    s2 = re.sub(r'(<w:sectPr[^>]*>)', r'\1<w:footerReference w:type="default" r:id="%s"/>' % keep_rid, s2, count=1)
    s2 = re.sub(r'<w:pgSz[^/]*/>', '<w:pgSz w:w="11906" w:h="16838"/>', s2)
    s2 = re.sub(r'<w:pgMar[^/]*/>', '<w:pgMar w:top="850" w:right="850" w:bottom="850" w:left="850" w:header="850" w:footer="850" w:gutter="0"/>', s2)
    s2 = s2.replace('<w:titlePg/>', '')
    s2 = re.sub(r'<w:pgNumType[^/]*/>', '', s2)
    s2 = s2.replace('<w:pgMar w:top="850" w:right="850" w:bottom="850" w:left="850" w:header="850" w:footer="850" w:gutter="0"/>',
                    '<w:pgMar w:top="850" w:right="850" w:bottom="850" w:left="850" w:header="850" w:footer="850" w:gutter="0"/><w:pgNumType w:start="1"/>')
    doc = doc[:m.start()] + s2 + doc[m.end():]
    # settings: updateFields（插在compat前，无则settings尾）
    if '<w:updateFields' not in settings:
        if '<w:compat' in settings:
            settings = settings.replace('<w:compat', '<w:updateFields w:val="true"/><w:compat', 1)
        elif '<w:rsids' in settings:
            settings = settings.replace('<w:rsids', '<w:updateFields w:val="true"/><w:rsids', 1)
        else:
            settings = re.sub(r'(</w:settings>)', '<w:updateFields w:val="true"/>\\1', settings)
    settings = re.sub(r'<w:evenAndOddHeaders[^/>]*/>', '', settings)
    fxml = (FOOTER_TMPL % (W, footer_para(prefix, npages))).encode('utf-8')
    zo = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
    for n in names:
        if n in drop_parts or n in header_parts:
            continue
        if n == 'word/footer1.xml':
            zo.writestr(n, fxml)
        elif n == 'word/document.xml':
            zo.writestr(n, doc.encode('utf-8'))
        elif n == 'word/_rels/document.xml.rels':
            zo.writestr(n, rels.encode('utf-8'))
        elif n == '[Content_Types].xml':
            zo.writestr(n, ct.encode('utf-8'))
        elif n == 'word/settings.xml':
            zo.writestr(n, settings.encode('utf-8'))
        else:
            zo.writestr(n, z.read(n))
    zo.close(); z.close()

def fix_docdefaults(zbytes_dict):
    """styles.xml: rPrDefault显式 TNR/宋体/21 + pPrDefault spacing 0/0/300/auto。zbytes_dict: name->bytes"""
    sty = etree.fromstring(zbytes_dict['word/styles.xml'])
    root = sty.getroottree().getroot()
    dd = root.find(q('docDefaults'))
    if dd is None:
        dd = etree.SubElement(root, q('docDefaults'))
        root.insert(0, dd)
    rprd = dd.find(q('rPrDefault'))
    if rprd is None:
        rprd = etree.SubElement(dd, q('rPrDefault'))
    for c in list(rprd): rprd.remove(c)
    rpr = etree.SubElement(rprd, q('rPr'))
    rf = etree.SubElement(rpr, q('rFonts'))
    rf.set(q('ascii'), 'Times New Roman'); rf.set(q('hAnsi'), 'Times New Roman')
    rf.set(q('eastAsia'), '宋体'); rf.set(q('cs'), 'Times New Roman')
    sz = etree.SubElement(rpr, q('sz')); sz.set(q('val'), '21')
    szc = etree.SubElement(rpr, q('szCs')); szc.set(q('val'), '21')
    pprd = dd.find(q('pPrDefault'))
    if pprd is None:
        pprd = etree.SubElement(dd, q('pPrDefault'))
    for c in list(pprd): pprd.remove(c)
    ppr = etree.SubElement(pprd, q('pPr'))
    sp = etree.SubElement(ppr, q('spacing'))
    sp.set(q('before'), '0'); sp.set(q('after'), '0'); sp.set(q('line'), '300'); sp.set(q('lineRule'), 'auto')
    zbytes_dict['word/styles.xml'] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)

def normalize_spacing(body):
    """全部正文 w:spacing 规整为 0/0/300/auto；缺 spacing 的段落补齐（插在 pStyle 之后）。返回(补插数,规整数)"""
    ins = fixn = 0
    for p in body.iter(q('p')):
        pPr = p.find(q('pPr'))
        if pPr is None:
            pPr = etree.Element(q('pPr')); p.insert(0, pPr)
        sp = pPr.find(q('spacing'))
        if sp is None:
            sp = etree.Element(q('spacing'))
            # schema 序：pStyle 之后、其余常见子元素之前
            pos = 0
            for i, c in enumerate(list(pPr)):
                if tag(c) in ('pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl', 'numPr', 'suppressLineNumbers', 'pBdr', 'shd', 'tabs'):
                    pos = i + 1
                else:
                    break
            pPr.insert(pos, sp); ins += 1
        else:
            fixn += 1
        sp.set(q('before'), '0'); sp.set(q('after'), '0')
        sp.set(q('line'), '300'); sp.set(q('lineRule'), 'auto')
        for a in list(sp.attrib):
            if a not in (q('before'), q('after'), q('line'), q('lineRule')):
                del sp.attrib[a]
    return ins, fixn

def normalize_run_sz(doc_root):
    """全部 w:sz/w:szCs 显式值≠21 → 21（含页脚部件另做）。返回修改数（跳过注释等非元素节点）"""
    n = 0
    for el in doc_root.iter():
        if not isinstance(el.tag, str):
            continue
        if tag(el) in ('sz', 'szCs') and el.get(q('val')) not in (None, '21'):
            el.set(q('val'), '21'); n += 1
    return n

def anchors_to_inline(body):
    """wp:anchor→wp:inline；图run所在段有其他内容时移出独立成段（紧随其后）；表格内就地转。返回(转_inline数,移段数,保留数)"""
    conv = moved = kept = 0
    anchors = list(body.iter(wq('anchor')))
    for a in anchors:
        # mc:AlternateContent 包裹情形：直接处理其中 anchor，AlternateContent 整体由 inline 替换
        par = a.getparent()
        # 找承载 run
        run = par
        while run is not None and tag(run) != 'r':
            run = run.getparent()
        inline = etree.Element(wq('inline'))
        inline.set('distT', '0'); inline.set('distB', '0'); inline.set('distL', '0'); inline.set('distR', '0')
        for ch in a:
            t = tag(ch)
            if t in ('extent', 'effectExtent', 'docPr', 'cNvGraphicFramePr', 'graphic'):
                inline.append(ch)
        # 替换位置：若 anchor 直系父级是 AlternateContent，则用 inline 替换 AlternateContent 本身
        if tag(par) == 'AlternateContent':
            par.getparent().replace(par, inline)
        else:
            par.replace(a, inline)
        conv += 1
        # run 所在段落
        p = run
        while p is not None and tag(p) != 'p':
            p = p.getparent()
        if p is None:
            kept += 1; continue
        # 表格内：就地不移动
        e2 = p.getparent()
        intbl = False
        while e2 is not None:
            if tag(e2) == 'tbl': intbl = True; break
            if tag(e2) == 'body': break
            e2 = e2.getparent()
        # 段内除图run外是否有实质内容（文字/公式/其他drawing）
        has_content = bool(ptext(p).strip()) or p.find('.//' + mq('oMath')) is not None or len(p.findall('.//' + wq('inline'))) > 1 or p.find('.//' + q('pict')) is not None
        if intbl or not has_content:
            kept += 1; continue
        # 移出：新段紧随其后
        idx = list(p).index(run)
        run.getparent().remove(run)
        newp = etree.Element(q('p'))
        pPr = etree.SubElement(newp, q('pPr'))
        sp = etree.SubElement(pPr, q('spacing'))
        sp.set(q('before'), '0'); sp.set(q('after'), '0'); sp.set(q('line'), '300'); sp.set(q('lineRule'), 'auto')
        jc = etree.SubElement(pPr, q('jc')); jc.set(q('val'), 'left')
        newp.append(run)
        p.addnext(newp)
        moved += 1
    return conv, moved, kept

HEADING_RE = re.compile(r'^\d+(\.\d+)*\s+\S')

def merge_standalone_omathpara(body):
    """独立成段块级公式并入前文字段末尾（§5）；前段为标题/表格/文首则保留独立段（壳已剥）。返回(并入数,保留数)"""
    merged = kept = 0
    changed = True
    while changed:
        changed = False
        children = list(body)
        for i, el in enumerate(children):
            if el.tag != q('p'):
                continue
            omps = el.findall(mq('oMathPara'))
            if not omps:
                continue
            others = [c for c in el if tag(c) != 'pPr' and tag(c) != 'oMathPara']
            has_other = ptext(el).strip() or el.find('.//' + q('drawing')) is not None or el.find('.//' + q('pict')) is not None
            if others or has_other:
                continue
            target = None
            for j in range(i - 1, -1, -1):
                pe = children[j]
                if pe.tag != q('p'):
                    target = None; break  # 表格等：不并
                t = ptext(pe)
                if not t.strip() and not pe.findall(mq('oMathPara')) and not pe.findall('.//' + wq('inline')) and pe.find('.//' + q('pict')) is None:
                    continue  # 空段跳过
                if re.match(r'^\d+(\.\d+)*\s+\S', t):
                    target = None; break  # 标题（节/题型）：不并
                target = pe; break
            if target is None:
                # 壳剥为行内（左对齐渲染）
                for omp in omps:
                    idx = list(el).index(omp)
                    for om in list(omp.findall(mq('oMath'))):
                        idx += 1; el.insert(idx, om)
                    el.remove(omp)
                kept += 1
            else:
                for omp in omps:
                    for om in list(omp.findall(mq('oMath'))):
                        target.append(om)
                    el.remove(omp)
                body.remove(el)
                merged += 1
            changed = True
            break
    return merged, kept

def save_docx(src_zip_path, out_path, part_dict):
    """按 part_dict 覆盖/新增部件写出新包"""
    z = zipfile.ZipFile(src_zip_path)
    zo = zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED)
    for n in z.namelist():
        if n in part_dict:
            zo.writestr(n, part_dict[n])
        else:
            zo.writestr(n, z.read(n))
    for n, b in part_dict.items():
        if n not in z.namelist():
            zo.writestr(n, b)
    zo.close(); z.close()
