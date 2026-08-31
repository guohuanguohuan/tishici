# -*- coding: utf-8 -*-
"""任务C：错题记录×2版式升级（工作副本手术）。
升级项：
1. 表格内段落按N1/N2规整——提醒句/表头/错因示例行/空行段＝解析档9pt(18半点)＋line=280 atLeast＋jc=left＋rFonts显式。
2. 标题行＝普通加粗段落：12pt(24半点)＋line=410 atLeast（正文档档位）。
3. 答案用法提醒句C9C9C9底纹维持（run级）、文字黑字、不挂深蓝。
4. styles.xml docDefaults：sz 21→18、line 288 auto→280 atLeast（解析档组值，禁模板默认）。
5. 补settings.xml标准化打包（含updateFields——E1#3备查项清偿）。
6. 补docProps/core.xml（title=文件名去扩展名、creator清空）＋app.xml。
7. pgMar header/footer 283→850（配页件属性与部分封面/使用说明一致）。
8. 空行trHeight=320 atLeast维持（40空行一页内的行距保障）。
"""
import zipfile, shutil, os, re
from lxml import etree
from xml.sax.saxutils import escape

WNS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
W = '{%s}' % WNS
NSMAP = {'w': WNS}
FONTS = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体" w:cs="Times New Roman"/>'

WS = r"C:/Users/28120/Desktop/提示词/工作区/同步-数学选必1版式改版-0831/M3-配页"
SRC = r"C:/Users/28120/Desktop/提示词/高中数学/高中数学同步"
FILES = [
    "人教B版选必1·错题记录（第1章 空间向量与立体几何）.docx",
    "人教B版选必1·错题记录（第2章 平面解析几何）.docx",
]

def w(tag):
    return '{%s}%s' % (WNS, tag)

def ensure_ppr(p):
    ppr = p.find(w('pPr'))
    if ppr is None:
        ppr = etree.SubElement(p, w('pPr'))
        p.remove(ppr)
        p.insert(0, ppr)
    return ppr

def set_spacing(ppr, line, rule='atLeast'):
    for old in ppr.findall(w('spacing')):
        ppr.remove(old)
    sp = etree.SubElement(ppr, w('spacing'))
    sp.set(w('before'), '0'); sp.set(w('after'), '0')
    sp.set(w('line'), line); sp.set(w('lineRule'), rule)
    # pPr子元素顺序：spacing须在jc前
    jcs = ppr.findall(w('jc'))
    for jc in jcs:
        ppr.remove(jc)
    if jcs:
        ppr.append(jcs[0])

def set_jc_left(ppr):
    for jc in ppr.findall(w('jc')):
        ppr.remove(jc)
    jc = etree.SubElement(ppr, w('jc'))
    jc.set(w('val'), 'left')

def ensure_rfonts_sz(rpr, sz):
    for tag in ('rFonts',):
        for old in rpr.findall(w(tag)):
            rpr.remove(old)
    rf = etree.Element(w('rFonts'))
    rf.set(w('ascii'), 'Times New Roman'); rf.set(w('hAnsi'), 'Times New Roman')
    rf.set(w('eastAsia'), '宋体'); rf.set(w('cs'), 'Times New Roman')
    rpr.insert(0, rf)
    for tag in ('sz', 'szCs'):
        for old in rpr.findall(w(tag)):
            rpr.remove(old)
    for tag in ('sz', 'szCs'):
        e = etree.SubElement(rpr, w(tag))
        e.set(w('val'), sz)

def para_regularize(p, sz, line, keep_shd=True):
    """规整一个段落：spacing line、jc left、每个含文字run补rFonts+sz（保留shd/b等既有属性）。"""
    ppr = ensure_ppr(p)
    set_spacing(ppr, line)
    set_jc_left(ppr)
    for r in p.findall(w('r')):
        rpr = r.find(w('rPr'))
        if rpr is None:
            rpr = etree.Element(w('rPr'))
            r.insert(0, rpr)
        ensure_rfonts_sz(rpr, sz)

for fn in FILES:
    src = os.path.join(SRC, fn)
    dst = os.path.join(WS, fn)
    shutil.copy2(src, dst)
    with zipfile.ZipFile(dst) as z:
        names = z.namelist()
        contents = {n: z.read(n) for n in names}
    docxml = contents['word/document.xml'].decode('utf-8')
    doc = etree.fromstring(contents['word/document.xml'])
    body = doc.find(w('body'))

    # 1) pgMar header/footer -> 850
    sect = body.find(w('sectPr'))
    pgmar = sect.find(w('pgMar'))
    pgmar.set(w('header'), '850'); pgmar.set(w('footer'), '850')

    # 2) 标题段（body第一个段落）＝12pt bold + 410 atLeast
    paras = body.findall(w('p'))
    title_p = paras[0]
    para_regularize(title_p, '24', '410')
    # 3) 提醒句段＝9pt + 280 atLeast，run shd维持
    remind_p = paras[1]
    para_regularize(remind_p, '18', '280')
    for r in remind_p.findall(w('r')):
        rpr = r.find(w('rPr'))
        if rpr is not None and rpr.find(w('shd')) is None:
            shd = etree.SubElement(rpr, w('shd'))
            shd.set(w('val'), 'clear'); shd.set(w('color'), 'auto'); shd.set(w('fill'), 'C9C9C9')

    # 4) 表格内段落全部规整＝9pt + 280 atLeast（表头/示例行/空行）
    tbl = body.find(w('tbl'))
    cellcount = 0
    for tc in tbl.iter(w('tc')):
        for p in tc.findall(w('p')):
            para_regularize(p, '18', '280')
            cellcount += 1

    contents['word/document.xml'] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)

    # 5) styles.xml：docDefaults改解析档组值
    styles = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
     '<w:styles xmlns:w="%s">'
     '<w:docDefaults><w:rPrDefault><w:rPr>%s<w:sz w:val="18"/><w:szCs w:val="18"/>'
     '<w:lang w:val="en-US" w:eastAsia="zh-CN"/></w:rPr></w:rPrDefault>'
     '<w:pPrDefault><w:pPr><w:spacing w:before="0" w:after="0" w:line="280" w:lineRule="atLeast"/>'
     '<w:jc w:val="left"/></w:pPr></w:pPrDefault></w:docDefaults>'
     '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/>'
     '<w:pPr><w:spacing w:before="0" w:after="0" w:line="280" w:lineRule="atLeast"/><w:jc w:val="left"/></w:pPr>'
     '<w:rPr>%s<w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr></w:style></w:styles>' % (WNS, FONTS, FONTS))
    contents['word/styles.xml'] = styles.encode('utf-8')

    # 6) settings.xml新增（含updateFields）
    settings = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
     '<w:settings xmlns:w="%s">'
     '<w:updateFields w:val="true"/><w:zoom w:percent="100"/>'
     '<w:defaultTabStop w:val="420"/>'
     '<w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat>'
     '</w:settings>' % WNS)
    contents['word/settings.xml'] = settings.encode('utf-8')

    # 7) docProps新增
    title = fn[:-5]
    core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
     '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
     'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
     'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
     '<dc:title>%s</dc:title><dc:creator></dc:creator><cp:lastModifiedBy></cp:lastModifiedBy>'
     '<dcterms:created xsi:type="dcterms:W3CDTF">2026-08-31T00:00:00Z</dcterms:created>'
     '<dcterms:modified xsi:type="dcterms:W3CDTF">2026-08-31T00:00:00Z</dcterms:modified></cp:coreProperties>' % escape(title))
    contents['docProps/core.xml'] = core.encode('utf-8')
    app = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
     '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
     '<Application>Microsoft Office Word</Application></Properties>')
    contents['docProps/app.xml'] = app.encode('utf-8')

    # 8) CT + rels 注册
    ct = contents['[Content_Types].xml'].decode('utf-8')
    ct = ct.replace('</Types>',
      '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
      '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
      '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
      '</Types>')
    contents['[Content_Types].xml'] = ct.encode('utf-8')
    rels = contents['word/_rels/document.xml.rels'].decode('utf-8')
    rels = rels.replace('</Relationships>',
      '<Relationship Id="rIdSet1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
      '</Relationships>')
    contents['word/_rels/document.xml.rels'] = rels.encode('utf-8')
    root_rels = contents['_rels/.rels'].decode('utf-8')
    root_rels = root_rels.replace('</Relationships>',
      '<Relationship Id="rIdCore1" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
      '<Relationship Id="rIdApp1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
      '</Relationships>')
    contents['_rels/.rels'] = root_rels.encode('utf-8')

    # 9) 重打包（member顺序保持原序+新增尾部）
    order = list(names)
    for extra in ['word/settings.xml', 'docProps/core.xml', 'docProps/app.xml']:
        if extra not in order:
            order.append(extra)
    tmp = dst + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for n in order:
            zout.writestr(n, contents[n])
    os.replace(tmp, dst)
    print('upgraded:', fn, 'cell paras regularized:', cellcount, os.path.getsize(dst), 'bytes')
