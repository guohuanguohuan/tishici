# -*- coding: utf-8 -*-
"""W-F卷90 基线dump：w:t/m:t流 + 逐段索引（复制件重读校验＋基线文字流）"""
import sys, io, json
from lxml import etree

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'}

def clark(tag):
    p, t = tag.split(':')
    return '{%s}%s' % (NS[p], t)

def dump(path, out_prefix):
    import zipfile
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml')
    tree = etree.fromstring(xml)
    body = tree.find(clark('w:body'))
    stream_parts = []
    for el in body.iter():
        if not isinstance(el.tag, str):
            continue
        if el.tag in (clark('w:t'), clark('m:t')):
            stream_parts.append(el.text or '')
    stream = ''.join(stream_parts)
    with io.open(out_prefix + '.stream.txt', 'w', encoding='utf-8') as f:
        f.write(stream)
    lines = []
    for i, el in enumerate(body):
        if not isinstance(el.tag, str):
            continue
        if el.tag == clark('w:p'):
            texts = []
            has_math = False; has_draw = False
            for sub in el.iter():
                if not isinstance(sub.tag, str): continue
                if sub.tag in (clark('w:t'), clark('m:t')):
                    texts.append(sub.text or '')
                elif sub.tag == clark('m:oMath'):
                    has_math = True
                elif sub.tag in (clark('w:drawing'), clark('w:pict')):
                    has_draw = True
            t = ''.join(texts)
            flags = ('M' if has_math else '') + ('D' if has_draw else '')
            lines.append('[P%04d]%s %s' % (i, flags, t))
        elif el.tag == clark('w:tbl'):
            first_texts = []
            for sub in el.iter(clark('w:t')):
                first_texts.append(sub.text or '')
                if len(first_texts) > 30: break
            lines.append('[T%04d][TBL] %s' % (i, ''.join(first_texts)[:120]))
        elif el.tag == clark('w:sectPr'):
            lines.append('[S%04d][SECTPR]' % i)
    with io.open(out_prefix + '.paras.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    n_p = sum(1 for l in lines if l.startswith('[P'))
    n_tbl = sum(1 for l in lines if '[TBL]' in l)
    print('paras:', n_p, 'tables:', n_tbl, 'stream_chars:', len(stream))

if __name__ == '__main__':
    dump(sys.argv[1], sys.argv[2])
