# -*- coding: utf-8 -*-
"""W-G卷68 步骤0：复制重读校验（zip成员SHA256）＋基线dump（段落/表/字符流）＋文件概况"""
import sys, io, json, hashlib, zipfile, re
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return '{%s}%s' % (W, t)
def m(t): return '{%s}%s' % (M, t)

SRC = r"C:\Users\28120\Desktop\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx"
CPY = r"C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-G卷68\G工作副本.docx"
OUT = r"C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-G卷68"

def sha(b): return hashlib.sha256(b).hexdigest()

# --- 0a 复制重读校验 ---
zs = zipfile.ZipFile(SRC); zc = zipfile.ZipFile(CPY)
ns_s = sorted(zs.namelist()); ns_c = sorted(zc.namelist())
assert ns_s == ns_c, '成员清单不一致'
diff = [n for n in ns_s if sha(zs.read(n)) != sha(zc.read(n))]
zs.close(); zc.close()
print('zip成员SHA256恒等 %d/%d，差异=%s' % (len(ns_s)-len(diff), len(ns_s), diff or '无'))

# --- 0b 基线dump ---
z = zipfile.ZipFile(CPY)
tree = etree.fromstring(z.read('word/document.xml'))
body = tree.find(w('body'))
stream_parts = []
for el in body.iter():
    if not isinstance(el.tag, str): continue
    if el.tag in (w('t'), m('t')):
        stream_parts.append(el.text or '')
stream = ''.join(stream_parts)
io.open(OUT + r'\基线.stream.txt', 'w', encoding='utf-8').write(stream)

lines = []; ntbl = 0; npar = 0
for i, el in enumerate(body):
    if not isinstance(el.tag, str): continue
    if el.tag == w('p'):
        npar += 1
        texts = []; has_math = False; has_draw = False
        for sub in el.iter():
            if not isinstance(sub.tag, str): continue
            if sub.tag in (w('t'), m('t')): texts.append(sub.text or '')
            elif sub.tag == m('oMath'): has_math = True
            elif sub.tag in (w('drawing'), w('pict')): has_draw = True
        t = ''.join(texts)
        flags = ('M' if has_math else '') + ('D' if has_draw else '')
        lines.append('[P%04d]%s %s' % (i, flags, t))
    elif el.tag == w('tbl'):
        ntbl += 1
        first = ''.join((sub.text or '') for sub in el.iter(w('t')))[:60]
        lines.append('[T%04d]BL %s' % (i, first))
io.open(OUT + r'\基线.paras.txt', 'w', encoding='utf-8').write('\n'.join(lines))

# --- 0c 概况：题号块、节标题、讲部/题型标题、页数线索 ---
qblocks = [l for l in lines if re.match(r'\[P\d+\]M?D? ?\d{1,4}．（', l)]
sects = [l for l in lines if re.match(r'\[P\d+\]M?D? ?2\.\d+(\.\d+)? [^\d＝]', l) and '（第' in l or re.match(r'\[P\d+\]M?D? ?2\.\d+(\.\d+)? ', l)]
lect = [l for l in lines if re.match(r'\[P\d+\]M?D? ?\d+(\.\d+)+\s*方法讲解', l)]
qtype = [l for l in lines if re.match(r'\[P\d+\]M?D? ?\d+(\.\d+){2,}\s+\S', l) and '方法讲解' not in l]
print(json.dumps({
  '段落数': npar, '表格数': ntbl, '流字符数': len(stream),
  '题号块数': len(qblocks),
  '讲部标题数': len(lect), '题型标题候选数': len(qtype),
  '题号序列': [re.search(r'(\d{1,4})．（', l).group(1) for l in qblocks][:80],
}, ensure_ascii=False, indent=1))
z.close()
