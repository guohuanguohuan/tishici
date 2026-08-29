# -*- coding: utf-8 -*-
"""页眉补挂.py — 2026-08-28 拍板页眉条款（品牌「羿郭工作室」＋册名·章名导航案）：
为无页眉的成品件补单行页眉（存量件页眉回扫轮的执行工具；讲练上卷样张先行验证）。
规格（公共规则§7页眉条款）：左对齐、小五（18半点）、中文宋体西文 Times New Roman、
无底纹无边框、w:pgMar header=283（页眉距0.5厘米；283＋小五行高＜850 上边距，不推挤正文）。
内容＝「羿郭工作室·册名 第X章 章名」（无「章」概念的件取体系前缀＋单位编号与名称，由调用方给全串）。
幂等：已有 headerReference 的件跳过不覆盖。
用法: python 页眉补挂.py <docx> <页眉文字>
【2026-08-29 成书形态拍板增·件型后缀模式（规格§3.2）】
用法: python 页眉补挂.py suffix <docx> <件型>
  —— 既有页眉文本末尾 append「·件型」（衔接/清单/讲练等，与页脚件标识同源；分卷不加卷次、
  同章各件一致）。幂等：页眉已以「·件型」收尾则跳过；已含该后缀但不在末尾的警告跳过不重复加。
  其余页眉属性（小五18半点、左对齐、283缇、无边框底纹）不动——只改末 run 文本，零格式变更。"""
import sys, io, zipfile, re, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
RT_HEADER = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/header'

HEADER_TMPL = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:hdr xmlns:w="%s"><w:p><w:pPr><w:jc w:val="left"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体" w:cs="Times New Roman"/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr><w:t xml:space="preserve">%s</w:t></w:r></w:p></w:hdr>'''

def _save(path, parts):
    tmp = path + '.hdr2'
    zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for name, b in parts.items():
        zo.writestr(name, b)
    zo.close()
    for k in range(12):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            time.sleep(6)
    raise RuntimeError('locked: ' + path)

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

def append_suffix(path, jx):
    """件型后缀模式：既有页眉文本末尾 append「·件型」。幂等（已含跳过）。"""
    jx = jx.strip()
    sfx = jx if jx.startswith('·') else '·' + jx
    z = zipfile.ZipFile(path)
    parts = {n: z.read(n) for n in z.namelist()}
    z.close()
    doc = parts['word/document.xml'].decode('utf-8')
    refs = re.findall(r'<w:headerReference w:type="default" r:id="(rId\d+)"/>', doc)
    assert refs, '无 default headerReference（页眉不存在——先用两参模式补挂页眉）: %s' % path
    rels = parts['word/_rels/document.xml.rels'].decode('utf-8')
    hit = 0
    for rid in refs:
        m = re.search(r'<Relationship Id="%s"[^>]*Target="([^"]+)"' % rid, rels)
        assert m, 'rels 中找不到 %s' % rid
        hname = 'word/' + m.group(1).lstrip('/')
        hdr = parts[hname].decode('utf-8')
        vis = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', hdr))
        if vis.rstrip().endswith(sfx):
            print('页眉已含件型后缀，幂等跳过:', os.path.basename(path), repr(vis))
            hit += 1
            continue
        if sfx in vis:
            print('!! 页眉已含「%s」但不在末尾，跳过不重复加（人工核验）: %r' % (sfx, vis))
            hit += 1
            continue
        # 末个含文本的 w:t 追加后缀（继承该 run 全部格式；置 preserve 防吞）
        tpos = [mm for mm in re.finditer(r'<w:t[^>]*>([^<]*)</w:t>', hdr) if mm.group(1)]
        assert tpos, '页眉内无文本 run: %s' % hname
        last = tpos[-1]
        new_t = last.group(0).replace('>' + last.group(1) + '<', '>' + last.group(1) + sfx + '<')
        if 'xml:space' not in new_t.split('>')[0]:
            new_t = new_t.replace('<w:t ', '<w:t xml:space="preserve" ', 1) \
                         if '<w:t ' in new_t else new_t.replace('<w:t>', '<w:t xml:space="preserve">', 1)
        hdr2 = hdr[:last.start()] + new_t + hdr[last.end():]
        parts[hname] = hdr2.encode('utf-8')
        vis2 = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', hdr2))
        print('页眉件型后缀:', os.path.basename(path), hname, repr(vis2))
        hit += 1
    _save(path, parts)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'suffix':
        append_suffix(sys.argv[2], sys.argv[3])
    else:
        add_header(sys.argv[1], sys.argv[2])
