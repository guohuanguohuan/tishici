# -*- coding: utf-8 -*-
"""标记方案批量转换：加粗+下划线（w:u） → 仅方框（w:bdr）。

【已废案 2026-08-26】方框方案已废弃：w:bdr 字符边框内边距机制固定 0~1.3pt、箭头/上标/分数等
高字形必然贴线压字（双渲染链实测），现行标记方案＝浅灰底纹 w:shd A6A6A6（35%灰，见
工具/标记转灰底.py 与 工具/灰底改色.py）。本工具仅留作历史存档与定向回滚，禁止再用于新成品。

用途：2026-08-25 标记方案切换后，把旧方案存量成品（知识清单/讲练件/实验卷等）
的「答案加粗＋粗下划线」批量转为「仅字符边框方框」。转换规则：
  - 普通文字 run：w:rPr 去 w:b/w:bCs/w:u，挂 w:bdr(single, sz=8)
  - 公式：按 oMath 顶层标记元素逐个挂框——m:r 在 w:rPr 挂 bdr；
    分数/上下标/括号等结构在各自 Pr>ctrlPr 的 w:rPr 挂 bdr（整个结构一个框）
  - 含挖空空位（下划线空位）的件不在本工具处理范围（该类空位保留线样式；学史默写版已于2026-08-25取消不再产出）
  - 公式标记区域内去粗（w:b、m:sty b→p bi→i），文字区结构标题的加粗不受影响
注意：就地改写传入文件（先自动留 .bak），转换后必须重跑该件全部对账自检；
Word 打开实测 + PyMuPDF 抽验（竖边≈2×框数、四边完整包裹）后方可报完成。

用法：python 标记转方框.py <docx> [docx ...]
"""
import sys
import shutil
import zipfile
from lxml import etree

WNS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
MNS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
W = '{%s}' % WNS
M = '{%s}' % MNS

PRE_BDR = {W + t for t in (
    'rFonts', 'b', 'bCs', 'i', 'iCs', 'caps', 'smallCaps', 'strike', 'dstrike',
    'outline', 'shadow', 'emboss', 'imprint', 'noProof', 'snapToGrid', 'vanish',
    'webHidden', 'color', 'spacing', 'w', 'kern', 'position', 'sz', 'szCs',
    'highlight', 'u', 'effect')}

CTRL = {M + 'f': M + 'fPr', M + 'sSub': M + 'sSubPr', M + 'sSup': M + 'sSupPr',
        M + 'sSubSup': M + 'sSubSupPr', M + 'd': M + 'dPr', M + 'rad': M + 'radPr',
        M + 'nary': M + 'naryPr', M + 'bar': M + 'barPr', M + 'func': M + 'funcPr',
        # 2026-08-25 补：m:acc（向量箭头/着重号）等罕见结构（第1章知识清单实测54处u残留即acc顶层漏挂）
        M + 'acc': M + 'accPr', M + 'limLow': M + 'limLowPr', M + 'limUp': M + 'limUpPr',
        M + 'box': M + 'boxPr', M + 'borderBox': M + 'borderBoxPr', M + 'groupChr': M + 'groupChrPr',
        M + 'phant': M + 'phantPr', M + 'eqArr': M + 'eqArrPr', M + 'm': M + 'mPr'}


def add_bdr(rpr):
    for el in rpr.findall(W + 'bdr'):
        rpr.remove(el)
    bdr = etree.Element(W + 'bdr')
    bdr.set(W + 'val', 'single')
    bdr.set(W + 'sz', '8')
    bdr.set(W + 'space', '0')
    bdr.set(W + 'color', 'auto')
    pos = 0
    for i, ch in enumerate(rpr):
        if ch.tag in PRE_BDR:
            pos = i + 1
    rpr.insert(pos, bdr)


def strip_bu(rpr):
    for tag in ('u', 'b', 'bCs'):
        for el in rpr.findall(W + tag):
            rpr.remove(el)


def fix_sty(region):
    for sty in region.iter(M + 'sty'):
        v = sty.get(M + 'val')
        if v == 'b':
            sty.set(M + 'val', 'p')
        elif v == 'bi':
            sty.set(M + 'val', 'i')


def convert(root):
    text_runs = 0
    math_boxes = 0
    for r in root.iter(W + 'r'):
        rpr = r.find(W + 'rPr')
        if rpr is not None and rpr.find(W + 'u') is not None:
            strip_bu(rpr)
            add_bdr(rpr)
            text_runs += 1
    for omath in root.iter(M + 'oMath'):
        for el in list(omath):
            if el.tag == M + 'r':
                rpr = el.find(W + 'rPr')
                if rpr is not None and rpr.find(W + 'u') is not None:
                    strip_bu(rpr)
                    add_bdr(rpr)
                    fix_sty(el)
                    math_boxes += 1
            elif el.tag in CTRL:
                if el.find('.//' + W + 'u') is not None:
                    pr = el.find(CTRL[el.tag])
                    if pr is None:
                        pr = etree.SubElement(el, CTRL[el.tag])
                        el.remove(pr)
                        el.insert(0, pr)
                    ctrl = pr.find(M + 'ctrlPr')
                    if ctrl is None:
                        ctrl = etree.SubElement(pr, M + 'ctrlPr')
                    rpr = ctrl.find(W + 'rPr')
                    if rpr is None:
                        rpr = etree.SubElement(ctrl, W + 'rPr')
                    strip_bu(rpr)
                    add_bdr(rpr)
                    for sub_rpr in el.iter(W + 'rPr'):
                        strip_bu(sub_rpr)
                    fix_sty(el)
                    math_boxes += 1
    return text_runs, math_boxes


def process(path):
    shutil.copy(path, path + '.bak')
    with zipfile.ZipFile(path) as zin:
        names = zin.namelist()
        data = {n: zin.read(n) for n in names}
    root = etree.fromstring(data['word/document.xml'])
    text_runs, math_boxes = convert(root)
    out = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    remnant = out.count(b'<w:u ') + out.count(b'<w:u/>')
    if remnant:
        raise SystemExit(f"{path}: 仍有 {remnant} 处 w:u 残留（含下划线空位的件勿用本工具），已写 .bak 未覆盖")
    data['word/document.xml'] = out
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for n in names:
            zout.writestr(n, data[n])
    print(f"OK {path} 文字框={text_runs} 公式框={math_boxes} 备份={path}.bak")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for p in sys.argv[1:]:
        process(p)
