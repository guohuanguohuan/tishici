# -*- coding: utf-8 -*-
"""W-E卷92 步骤0：复制重读校验（zip成员级SHA256恒等）＋基线dump（w:t/m:t流＋逐段索引）"""
import sys, io, hashlib, zipfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return '{%s}%s' % (W, t)

SRC = r"C:\Users\28120\Desktop\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx"
WK  = r"C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-E卷92\E卷92-工作副本.docx"

def zsha(path):
    h = {}
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            h[n] = hashlib.sha256(z.read(n)).hexdigest()
    return h

hs, hw = zsha(SRC), zsha(WK)
assert set(hs) == set(hw), '成员集不等: %s vs %s' % (len(hs), len(hw))
diff = [n for n in hs if hs[n] != hw[n]]
print('zip成员级SHA256恒等: %d/%d, 差异%d' % (len(hs)-len(diff), len(hs), len(diff)))
assert not diff, diff

# 基线dump
def dump(path, out_prefix):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml')
    tree = etree.fromstring(xml)
    body = tree.find(w('body'))
    stream_parts = []
    for el in body.iter():
        if not isinstance(el.tag, str): continue
        if el.tag in (w('t'), '{%s}t' % M):
            stream_parts.append(el.text or '')
    stream = ''.join(stream_parts)
    with io.open(out_prefix + '.stream.txt', 'w', encoding='utf-8') as f:
        f.write(stream)
    lines = []
    for i, el in enumerate(body):
        if not isinstance(el.tag, str): continue
        if el.tag == w('p'):
            texts = []; has_math = False; has_draw = False
            for sub in el.iter():
                if not isinstance(sub.tag, str): continue
                if sub.tag in (w('t'), '{%s}t' % M): texts.append(sub.text or '')
                elif sub.tag == '{%s}oMath' % M: has_math = True
                elif sub.tag in (w('drawing'), w('pict')): has_draw = True
            t = ''.join(texts)
            flags = ('M' if has_math else '') + ('D' if has_draw else '')
            lines.append('[P%04d]%s %s' % (i, flags, t))
        elif el.tag == w('tbl'):
            first = []
            for sub in el.iter(w('t')):
                first.append(sub.text or '')
                if len(first) > 40: break
            lines.append('[T%04d][TBL] %s' % (i, ''.join(first)[:150]))
        elif el.tag == w('sectPr'):
            lines.append('[S%04d][SECTPR]' % i)
    with io.open(out_prefix + '.paras.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    n_p = sum(1 for l in lines if l.startswith('[P'))
    n_tbl = sum(1 for l in lines if '[TBL]' in l)
    print('paras:', n_p, 'tables:', n_tbl, 'stream_chars:', len(stream))

dump(WK, r"C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-E卷92\基线")
