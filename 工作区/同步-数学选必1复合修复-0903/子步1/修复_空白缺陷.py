# -*- coding: utf-8 -*-
r"""修复_空白缺陷.py（子步1·一次性脚本）——选必1六件首页空白修复。
修法（附则修复纪律②两并列手段）：
  A 触发属性消除：正文节（文末）sectPr 插入 <w:type w:val="continuous"/>（schema位＝pgSz之前）——
    消除缺省nextPage触发的换页。六件全做。
  B 头部要素整体位移＋落点修正（仅B/E）：章首导航表从双栏正文区（body子元素idx2）整体迁入头部单栏区
    （统计行之后）；头部节sectPr从统计行段迁入导航表后新建的最小空承载段（表后承载段，H4口径）。
文本流零变更：段落与run内容＋顺序不动（B/E仅导航表块整体位移＋新增零字符空承载段）。
zip其余成员逐字节原样拷贝。
"""
import sys, io, os, zipfile, shutil
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

def fix(code, src, dst, move_nav=False):
    z = zipfile.ZipFile(src)
    members = [(i, z.read(i.filename)) for i in z.infolist()]
    z.close()
    root = etree.fromstring(dict((i.filename, b) for i, b in members)['word/document.xml'])
    body = root.find(q('body'))
    log = []
    # ---- A 触发属性消除
    bsect = body.find(q('sectPr'))
    if bsect.find(q('type')) is None:
        tel = etree.Element(q('type'))
        tel.set(q('val'), 'continuous')
        bsect.insert(0, tel)   # schema序：type在pgSz之前；本节无header/footerReference
        log.append('A: 正文节sectPr插入w:type=continuous')
    else:
        log.append('A: 正文节sectPr已有w:type=%s（幂等跳过）' % bsect.find(q('type')).get(q('val')))
    # ---- B 导航表位移（仅B/E）
    if move_nav:
        kids = list(body)
        brk = None
        for i, el in enumerate(kids):
            if etree.QName(el).localname == 'p':
                ppr = el.find(q('pPr'))
                if ppr is not None and ppr.find(q('sectPr')) is not None:
                    brk = i; break
        assert brk is not None, '无段落级sectPr'
        carrier = kids[brk]
        nav = None; nav_idx = None
        for i in range(brk + 1, len(kids)):
            if etree.QName(kids[i]).localname == 'tbl' and is_navtbl(kids[i]):
                nav = kids[i]; nav_idx = i; break
        assert nav is not None, '正文区未检出导航表'
        sect = carrier.find(q('pPr')).find(q('sectPr'))
        # 位移：sectPr迁出统计行段；导航表移到统计行段之后；新建空承载段挂sectPr
        carrier.find(q('pPr')).remove(sect)
        body.remove(nav)
        carrier.addnext(nav)
        newp = etree.Element(q('p'))
        newppr = etree.SubElement(newp, q('pPr'))
        sp = etree.SubElement(newppr, q('spacing'))
        sp.set(q('before'), '0'); sp.set(q('after'), '0'); sp.set(q('line'), '20'); sp.set(q('lineRule'), 'exact')
        jc = etree.SubElement(newppr, q('jc')); jc.set(q('val'), 'left')
        rpr = etree.SubElement(newppr, q('rPr'))
        sz = etree.SubElement(rpr, q('sz')); sz.set(q('val'), '2')
        szcs = etree.SubElement(rpr, q('szCs')); szcs.set(q('val'), '2')
        newppr.append(sect)   # pPr序：…spacing/jc/rPr/sectPr
        nav.addnext(newp)
        log.append('B: 导航表body子元素idx%d→头部区（统计行idx%d之后）；sectPr承载段 idx%d(统计行)→新空段(表后)'
                   % (nav_idx, brk, brk))
    xml = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    assert b'ns0:' not in xml, 'ns0前缀污染'
    # 重打包：其余成员逐字节拷贝
    tmp = dst + '.tmp'
    zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for info, blob in members:
        ni = zipfile.ZipInfo(info.filename, date_time=info.date_time)
        ni.compress_type = zipfile.ZIP_DEFLATED
        ni.external_attr = info.external_attr
        zo.writestr(ni, xml if info.filename == 'word/document.xml' else blob)
    zo.close()
    os.replace(tmp, dst)
    # 复核：重开解析
    z2 = zipfile.ZipFile(dst)
    etree.fromstring(z2.read('word/document.xml'))
    z2.close()
    log.append('复核: 重开XML解析通过，无ns0')
    return log

if __name__ == '__main__':
    code, src, dst = sys.argv[1], sys.argv[2], sys.argv[3]
    mv = len(sys.argv) > 4 and sys.argv[4] == '--move-nav'
    for line in fix(code, src, dst, mv):
        print('[%s] %s' % (code, line))
