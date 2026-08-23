# -*- coding: utf-8 -*-
"""footer_fix.py — 页脚规范重建 zip 手术（经验配方：footer part整体替换＋sectPr三处＋settings＋rels/ContentTypes）
用法: python footer_fix.py <docx路径...>   输出到同目录 <原名>.footfixed.docx（人工验收后改名替换）"""
import zipfile, re, os, sys, io, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

FOOTER_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr><w:t xml:space="preserve">第</w:t></w:r><w:fldSimple w:instr=" PAGE "><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr><w:t xml:space="preserve">1</w:t></w:r></w:fldSimple><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr><w:t xml:space="preserve">页（共</w:t></w:r><w:fldSimple w:instr=" NUMPAGES "><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr><w:t xml:space="preserve">1</w:t></w:r></w:fldSimple><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr><w:t xml:space="preserve">页）</w:t></w:r></w:p></w:ftr>'''

def check_footer_ok(fxml):
    """footer part 是否已是合规 fldSimple 模板"""
    ok_instr = ('w:instr=" PAGE "' in fxml or "w:instr=' PAGE '" in fxml) and ('w:instr=" NUMPAGES "' in fxml or "w:instr=' NUMPAGES '" in fxml)
    txt = re.sub(r'<[^>]+>', '', fxml)
    ok_txt = re.match(r'^第\d*页（共\d*页）$', txt) is not None or txt == '第页（共页）'
    ok_jc = '<w:jc w:val="center"/>' in fxml
    return ok_instr and ok_txt and ok_jc and 'w:val="21"' in fxml

def fix(path, out):
    z = zipfile.ZipFile(path)
    names = z.namelist()
    doc = z.read('word/document.xml').decode('utf-8')
    rels = z.read('word/_rels/document.xml.rels').decode('utf-8')
    settings = z.read('word/settings.xml').decode('utf-8') if 'word/settings.xml' in names else None
    ct = z.read('[Content_Types].xml').decode('utf-8')

    footer_parts = [n for n in names if re.match(r'word/footer\d+\.xml', n)]
    header_parts = [n for n in names if re.match(r'word/header\d+\.xml', n)]

    # 1) rels：找/建 footer1 rId，删其余 footer/header rel
    foot_rids = dict(re.findall(r'<Relationship Id="(rId\d+)"[^>]*Target="(footer\d+\.xml)"[^>]*/>', rels))
    head_rids = re.findall(r'<Relationship Id="(rId\d+)"[^>]*Target="header\d+\.xml"[^>]*/>', rels)
    keep_rid = None
    for rid, tgt in foot_rids.items():
        if tgt == 'footer1.xml':
            keep_rid = rid; break
    if keep_rid is None and foot_rids:
        first = sorted(foot_rids.items(), key=lambda kv: int(kv[1][6:-4]))[0]
        keep_rid = first[0]
    if keep_rid is None:
        # 新建 rId
        used = [int(m) for m in re.findall(r'Id="rId(\d+)"', rels)]
        keep_rid = 'rId%d' % (max(used) + 1 if used else 1)
        rels = rels.replace('</Relationships>', '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/></Relationships>' % keep_rid)
    drop_parts = set()
    for rid, tgt in foot_rids.items():
        if rid != keep_rid:
            rels = re.sub(r'<Relationship Id="%s"[^>]*/>' % rid, '', rels)
            drop_parts.add('word/' + tgt)
    for rid in head_rids:
        rels = re.sub(r'<Relationship Id="%s"[^>]*/>' % rid, '', rels)

    # 2) Content_Types：删多余件声明，确保 footer1 声明
    for p in list(drop_parts) + ['word/' + t for t in []]:
        ct = re.sub(r'<Override PartName="/%s"[^>]*/>' % re.escape(p), '', ct)
    for p in header_parts:
        ct = re.sub(r'<Override PartName="/%s"[^>]*/>' % re.escape(p), '', ct)
    if '/word/footer1.xml' not in ct:
        ct = ct.replace('</Types>', '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>')

    # 3) document.xml sectPr 手术
    m = re.search(r'<w:sectPr\b.*?</w:sectPr>', doc, re.S)
    assert m, 'no sectPr'
    s = m.group(0)
    s2 = re.sub(r'<w:headerReference[^/]*/>|<w:footerReference[^/]*/>', '', s)
    s2 = s2.replace('<w:sectPr', '<w:sectPr', 1)
    # footerReference 插到 sectPr 开头（schema 首位）
    s2 = re.sub(r'(<w:sectPr[^>]*>)', r'\1<w:footerReference w:type="default" r:id="%s"/>' % keep_rid, s2, count=1)
    # pgSz → A4
    s2 = re.sub(r'<w:pgSz[^/]*/>', '<w:pgSz w:w="11906" w:h="16838"/>', s2)
    # pgMar → 全 720（footer 同值）
    s2 = re.sub(r'<w:pgMar[^/]*/>', '<w:pgMar w:top="720" w:right="720" w:bottom="720" w:left="720" w:header="720" w:footer="720" w:gutter="0"/>', s2)
    # 删 titlePg / even refs
    s2 = s2.replace('<w:titlePg/>', '')
    # pgNumType start=1（schema 位：pgMar 之后）
    s2 = re.sub(r'<w:pgNumType[^/]*/>', '', s2)
    s2 = s2.replace('<w:pgMar w:top="720" w:right="720" w:bottom="720" w:left="720" w:header="720" w:footer="720" w:gutter="0"/>',
                    '<w:pgMar w:top="720" w:right="720" w:bottom="720" w:left="720" w:header="720" w:footer="720" w:gutter="0"/><w:pgNumType w:start="1"/>')
    doc = doc[:m.start()] + s2 + doc[m.end():]

    # 4) settings：删 evenAndOddHeaders
    if settings and '<w:evenAndOddHeaders' in settings:
        settings = re.sub(r'<w:evenAndOddHeaders[^/>]*/>', '', settings)

    # 5) 写新包：替换 footer1.xml 内容、删多余 footer/header parts
    zo = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
    for n in names:
        if n in drop_parts or n in header_parts:
            continue
        if n == 'word/footer1.xml':
            zo.writestr(n, FOOTER_XML)
        elif n == 'word/document.xml':
            zo.writestr(n, doc)
        elif n == 'word/_rels/document.xml.rels':
            zo.writestr(n, rels)
        elif n == '[Content_Types].xml':
            zo.writestr(n, ct)
        elif n == 'word/settings.xml' and settings is not None:
            zo.writestr(n, settings)
        else:
            zo.writestr(n, z.read(n))
    zo.close()
    z.close()
    return drop_parts | set(header_parts)

if __name__ == '__main__':
    for p in sys.argv[1:]:
        out = p[:-5] + '.footfixed.docx'
        dropped = fix(p, out)
        print('fixed:', os.path.basename(p), '-> dropped parts:', len(dropped))
