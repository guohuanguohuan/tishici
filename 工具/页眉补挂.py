# -*- coding: utf-8 -*-
"""页眉补挂.py — 2026-08-28 拍板页眉条款（品牌「羿郭工作室」＋册名·章名导航案）：
为无页眉的成品件补单行页眉（存量件页眉回扫轮的执行工具；讲练上卷样张先行验证）。
规格（公共规则§7页眉条款）：左对齐、小五（18半点）、中文宋体西文 Times New Roman、
无底纹无边框、w:pgMar header=283（页眉距0.5厘米；283＋小五行高＜850 上边距，不推挤正文）。
内容＝「羿郭工作室·册名 第X章 章名」（无「章」概念的件取体系前缀＋单位编号与名称，由调用方给全串）。
幂等：已有 headerReference 的件跳过不覆盖。
用法: python 页眉补挂.py <docx> <页眉文字>"""
import sys, io, zipfile, re, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
RT_HEADER = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/header'

HEADER_TMPL = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:hdr xmlns:w="%s"><w:p><w:pPr><w:jc w:val="left"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体" w:cs="Times New Roman"/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr><w:t xml:space="preserve">%s</w:t></w:r></w:p></w:hdr>'''

def add_header(path, text):
    z = zipfile.ZipFile(path)
    parts = {n: z.read(n) for n in z.namelist()}
    z.close()
    doc = parts['word/document.xml'].decode('utf-8')
    if '<w:headerReference' in doc:
        print('已有页眉引用，跳过:', path)
        return
    rels = parts['word/_rels/document.xml.rels'].decode('utf-8')
    ct = parts['[Content_Types].xml'].decode('utf-8')
    # 新 rId＝现存最大+1；新 header 部件名 header1.xml（已有则递增）
    used = [int(m) for m in re.findall(r'Id="rId(\d+)"', rels)]
    rid = 'rId%d' % (max(used) + 1 if used else 1)
    hn = 1
    while 'word/header%d.xml' % hn in parts:
        hn += 1
    hname = 'header%d.xml' % hn
    rels = rels.replace('</Relationships>',
        '<Relationship Id="%s" Type="%s" Target="%s"/></Relationships>' % (rid, RT_HEADER, hname))
    if '/word/%s' % hname not in ct:
        ct = ct.replace('</Types>',
            '<Override PartName="/word/%s" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/></Types>' % hname)
    # sectPr：headerReference 插在 footerReference 前（CT_SectPr 序），pgMar header=283
    m = re.search(r'<w:sectPr\b.*?</w:sectPr>', doc, re.S)
    assert m, 'no sectPr'
    s = m.group(0)
    s2 = s.replace('<w:footerReference',
                   '<w:headerReference w:type="default" r:id="%s"/><w:footerReference' % rid, 1)
    s2 = re.sub(r'(<w:pgMar\b[^>]*?)w:header="\d+"', r'\1w:header="283"', s2)
    assert s2 != s or 'w:header="283"' in s2
    doc = doc[:m.start()] + s2 + doc[m.end():]
    parts['word/document.xml'] = doc.encode('utf-8')
    parts['word/_rels/document.xml.rels'] = rels.encode('utf-8')
    parts['[Content_Types].xml'] = ct.encode('utf-8')
    parts['word/%s' % hname] = (HEADER_TMPL % (W, text)).encode('utf-8')
    tmp = path + '.hdr'
    zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for name, b in parts.items():
        zo.writestr(name, b)
    zo.close()
    for k in range(12):
        try:
            os.replace(tmp, path)
            break
        except PermissionError:
            time.sleep(6)
    else:
        raise RuntimeError('locked: ' + path)
    print('页眉补挂:', os.path.basename(path), '->', hname, rid, repr(text))

if __name__ == '__main__':
    add_header(sys.argv[1], sys.argv[2])
