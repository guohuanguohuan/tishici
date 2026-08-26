# -*- coding: utf-8 -*-
"""标记转灰底.py — 必背标记方案批量转换：w:bdr 方框 → w:shd 浅灰底纹（2026-08-26 用户拍板；同日二拍色值加深）
用法: python 标记转灰底.py <docx...>   就地转换（原文件不动时先复制）
说明: rPr 内 w:bdr 原位替换为 w:shd val="clear" color="auto" fill="A6A6A6"（35%灰，
      2026-08-26 同日二拍：初版 D9D9D9＝15%灰一眼难辨已全量加深；新转换一律用本值，
      黑白打印可见、画在文字下层机制上不压字）；w:shd 在 CT_RPr 序中紧随 w:bdr，位置合法。
      运行级与 ctrlPr 级（OMML 结构）同样处理。输出每件转换计数。"""
import sys, io, zipfile, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
FILL = 'A6A6A6'

def convert(path):
    z = zipfile.ZipFile(path)
    parts = {n: z.read(n) for n in z.namelist()}
    z.close()
    doc = etree.fromstring(parts['word/document.xml'])
    n = 0
    # 全部 rPr 内的 w:bdr（run 级 + ctrlPr 级共用 w:rPr）
    for bdr in list(doc.iter(q('bdr'))):
        rpr = bdr.getparent()
        if etree.QName(rpr).localname != 'rPr':
            continue
        idx = list(rpr).index(bdr)
        rpr.remove(bdr)
        shd = etree.Element(q('shd'))
        shd.set(q('val'), 'clear'); shd.set(q('color'), 'auto'); shd.set(q('fill'), FILL)
        rpr.insert(idx, shd)
        n += 1
    parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    tmp = path + '.graying'
    zo = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for name, b in parts.items():
        zo.writestr(name, b)
    zo.close()
    # 重试替换（防同步盘/杀软瞬时锁）
    import time
    for i in range(12):
        try:
            os.replace(tmp, path)
            return n
        except PermissionError:
            time.sleep(6)
    raise RuntimeError('locked: ' + path)

if __name__ == '__main__':
    total = 0
    for p in sys.argv[1:]:
        n = convert(p)
        total += n
        print('%-46s 转换 %d 处' % (os.path.basename(p)[:46], n))
    print('合计', total)
