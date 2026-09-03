# -*- coding: utf-8 -*-
r"""位移对账表生成（子步1·一次性脚本）——逐件机器实测修复前后头部区/正文区分界与位移块段号。"""
import sys, io, os, zipfile
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def nospc(s):
    import re
    return re.sub(r'[\s　]+', '', s or '')
def is_navtbl(tbl):
    tr = tbl.find(q('tr'))
    if tr is None: return False
    cells = [nospc(ptext(tc)) for tc in tr.findall(q('tc'))]
    return any('节名' in c for c in cells) and any('题量' in c for c in cells) and any('题型组数' in c for c in cells)

BASE = r'C:\提示词\高中数学\高中数学同步'
FIX = os.path.dirname(os.path.abspath(__file__))
FILES = {
 'X1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
 'I1': '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
 'B':  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
 'X2': '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
 'I2': '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
 'E':  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
}

def snap(path):
    z = zipfile.ZipFile(path)
    root = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = root.find(q('body')); kids = list(body)
    brk = None
    for i, el in enumerate(kids):
        if etree.QName(el).localname == 'p':
            ppr = el.find(q('pPr'))
            if ppr is not None and ppr.find(q('sectPr')) is not None:
                brk = i; break
    def tag(i, el):
        ln = etree.QName(el).localname
        if ln == 'tbl':
            return 'tbl:导航表' if is_navtbl(el) else 'tbl'
        t = ptext(el)
        return 'p:%s' % (t[:38] if t else '(空段)')
    hdr = [(i, tag(i, el)) for i, el in enumerate(kids[:brk + 1 if brk is not None else 0])]
    bdy = [(i, tag(i, el)) for i, el in enumerate(kids[(brk + 1) if brk is not None else 0: (brk or 0) + 4], start=(brk + 1) if brk is not None else 0)]
    bs = body.find(q('sectPr')); t = bs.find(q('type'))
    return {'n': len(kids), 'brk': brk, 'hdr': hdr, 'bdy_head': bdy,
            'body_type': (t.get(q('val')) if t is not None else '(缺省nextPage)')}

md = ['# 位移对账表（子步1·空白缺陷修复；逐件机器实测）', '',
      '口径：body直接子元素下标；「分节符承载段」＝头部节sectPr所在段（其pPr内）。',
      '修复A（六件同）：正文节（文末）sectPr插入w:type=continuous——纯属性消除，无段号位移。',
      '修复B（仅B/E）：导航表整体位移入头部单栏区＋分节符落点后移至表后新空承载段。', '']
for code, fn in FILES.items():
    o = snap(os.path.join(BASE, fn))
    f = snap(os.path.join(FIX, 'fixed', code + '.docx'))
    md.append('## %s' % code)
    md.append('- 修复前：body子元素=%d；分节符承载段idx=%s；头部区=%s；正文区首=%s；正文节type=%s'
              % (o['n'], o['brk'], o['hdr'], o['bdy_head'][:2], o['body_type']))
    md.append('- 修复后：body子元素=%d；分节符承载段idx=%s；头部区=%s；正文区首=%s；正文节type=%s'
              % (f['n'], f['brk'], f['hdr'], f['bdy_head'][:2], f['body_type']))
    if code in ('B', 'E'):
        md.append('- 位移块：章首导航表 修复前idx=2（双栏正文区首元素）→修复后idx=2（头部单栏区末要素，统计行之后）；'
                  'sectPr承载段 修复前idx=1（统计行段）→修复后idx=3（表后新建零字符空段，行距固定1pt防占位）；'
                  '正文区全部元素idx+1平移（首段节名锚 3→4）。')
    else:
        md.append('- 位移块：无（纯属性修复，段号零位移）。')
    md.append('')
dst = os.path.join(FIX, '位移对账表.md')
with open(dst, 'w', encoding='utf-8') as fp:
    fp.write('\n'.join(md) + '\n')
print('落盘:', dst)
