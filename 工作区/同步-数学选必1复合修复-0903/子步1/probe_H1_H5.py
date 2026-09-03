# -*- coding: utf-8 -*-
r"""H1~H5假设集排查探针（子步1·一次性脚本）——对X2最小复现件逐假设实测取证。
H1 段落级显式分页（w:br type=page／pageBreakBefore／栏break／表格keepNext+cantSplit／widowControl）
H2 全宽表落栏（X2表数实测）
H3 两节docGrid不等
H4 sectPr落位（表后缺承载段）
H5 页眉页脚/titlePg不对称
另：两节sectPr全属性对照（pgSz/pgMar/vAlign/textDirection/lnNumType/printerSettings等），防漏项。
"""
import sys, io, os, zipfile
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)

def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def probe(path):
    z = zipfile.ZipFile(path)
    xml = z.read('word/document.xml')
    names = z.namelist()
    root = etree.fromstring(xml)
    z.close()
    body = root.find(q('body'))
    kids = list(body)
    out = []
    out.append('文件: %s' % os.path.basename(path))
    out.append('body直接子元素总数: %d' % len(kids))
    # ---- 定位段落级sectPr（分节符承载段）
    brk = None
    for i, el in enumerate(kids):
        if etree.QName(el).localname == 'p':
            ppr = el.find(q('pPr'))
            if ppr is not None and ppr.find(q('sectPr')) is not None:
                brk = i
                break
    out.append('段落级sectPr承载段下标: %s' % brk)
    if brk is None:
        out.append('!! 无段落级sectPr —— 单节文档')
        return '\n'.join(out)
    # 承载段全文与其pPr除sectPr外的内容
    carrier = kids[brk]
    out.append('承载段文本: %r' % ptext(carrier))
    ppr = carrier.find(q('pPr'))
    ppr_others = [etree.QName(c).localname for c in ppr if etree.QName(c).localname != 'sectPr']
    out.append('承载段pPr除sectPr外子元素: %s' % ppr_others)
    out.append('承载段其余run数: %d' % len(carrier.findall(q('r'))))
    # 分节符前后各2个元素
    for j in range(max(0, brk - 2), min(len(kids), brk + 3)):
        el = kids[j]
        ln = etree.QName(el).localname
        txt = ptext(el)[:60] if ln == 'p' else '(tbl)'
        out.append('  邻域[%d] %s: %r' % (j, ln, txt))
    sect1 = ppr.find(q('sectPr'))
    sect2 = body.find(q('sectPr'))
    # ---- H1 段落级显式分页
    out.append('\n== H1 段落级显式分页 ==')
    n_brpage = len(root.findall('.//' + q('br') + '[@' + q('type') + '="page"]'))
    n_brcol = len(root.findall('.//' + q('br') + '[@' + q('type') + '="column"]'))
    # 全角文档中 w:br 属性名是 w:type
    brs = root.findall('.//' + q('br'))
    br_types = {}
    for b in brs:
        t = b.get(q('type'), 'textWrapping')
        br_types[t] = br_types.get(t, 0) + 1
    out.append('w:br 总数=%d 类型分布=%s' % (len(brs), br_types))
    pbb = root.findall('.//' + q('pageBreakBefore'))
    out.append('pageBreakBefore 总数=%d' % len(pbb))
    for p in root.iter(q('p')):
        pp = p.find(q('pPr'))
        if pp is not None and pp.find(q('pageBreakBefore')) is not None:
            out.append('  pageBreakBefore段落: %r' % ptext(p)[:50])
    kn = root.findall('.//' + q('keepNext'))
    kl = root.findall('.//' + q('keepLines'))
    wc = root.findall('.//' + q('widowControl'))
    out.append('keepNext=%d keepLines=%d widowControl=%d' % (len(kn), len(kl), len(wc)))
    tbls = body.findall(q('tbl'))
    out.append('表格数（body直接子级）=%d' % len(tbls))
    cant = root.findall('.//' + q('cantSplit'))
    out.append('表格cantSplit=%d' % len(cant))
    # ---- H2 全宽表落栏
    out.append('\n== H2 全宽表落栏 ==')
    out.append('body级表格数=%d（X2应=0，衔接2无表仍现缺陷＝表非唯一成因）' % len(tbls))
    # ---- H3 两节docGrid
    out.append('\n== H3 docGrid对照 ==')
    for tag, s in (('头部节(段落级sectPr)', sect1), ('正文节(文末sectPr)', sect2)):
        dg = s.find(q('docGrid'))
        if dg is None:
            out.append('%s docGrid: 无' % tag)
        else:
            attrs = {etree.QName(k).localname: v for k, v in dg.attrib.items()}
            out.append('%s docGrid: %s' % (tag, attrs))
    # ---- H4 sectPr落位
    out.append('\n== H4 sectPr落位 ==')
    prev_el = kids[brk - 1] if brk > 0 else None
    out.append('承载段前一元素: %s' % (etree.QName(prev_el).localname if prev_el is not None else 'None'))
    out.append('（若前元素为tbl而承载段缺失＝表后缺承载段缺陷）')
    # ---- H5 页眉页脚/titlePg
    out.append('\n== H5 页眉页脚/titlePg对照 ==')
    for tag, s in (('头部节', sect1), ('正文节', sect2)):
        hr = s.findall(q('headerReference'))
        fr = s.findall(q('footerReference'))
        tp = s.find(q('titlePg'))
        out.append('%s: headerReference=%s footerReference=%s titlePg=%s' % (
            tag,
            [{etree.QName(k).localname: v for k, v in r.attrib.items()} for r in hr],
            [{etree.QName(k).localname: v for k, v in r.attrib.items()} for r in fr],
            tp is not None))
    # ---- 两节sectPr全属性对照（防漏项）
    out.append('\n== 两节sectPr全量子元素对照 ==')
    def sect_dump(s):
        d = []
        for c in s:
            ln = etree.QName(c).localname
            attrs = {etree.QName(k).localname: v for k, v in c.attrib.items()}
            d.append('%s%s' % (ln, attrs if attrs else ''))
        return d
    d1, d2 = sect_dump(sect1), sect_dump(sect2)
    out.append('头部节: %s' % d1)
    out.append('正文节: %s' % d2)
    # ---- 正文区首段pPr全文（首段属性可疑点）
    out.append('\n== 正文区前3段pPr原文 ==')
    shown = 0
    for el in kids[brk + 1:]:
        if etree.QName(el).localname != 'p':
            continue
        pp = el.find(q('pPr'))
        out.append('段[%r] pPr=%s' % (ptext(el)[:30],
                   etree.tostring(pp, encoding='unicode')[:400] if pp is not None else 'None'))
        shown += 1
        if shown >= 3:
            break
    return '\n'.join(out)


if __name__ == '__main__':
    src = sys.argv[1]
    txt = probe(src)
    print(txt)
    dst = sys.argv[2]
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(txt + '\n')
