# -*- coding: utf-8 -*-
"""F0-定理框统一·I2手术：按统一口径重判结果执行框增删/样式归一。
- 剔除5段：题名行框×4（e0011,e0013,e0181,e0240）＋引导句框×1（e0256）
- 样式归一12段：space2→space4（sz=4 space=4 color=auto 四边，与I1既有框同款）
- 新增68段：合格〔进〕公式/结论级条目本体直接陈述段
文字零增删（纯pPr/pBdr变化）。判定表见 判定表_I2统一口径重判.md。"""
import zipfile, time, os
from lxml import etree

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
path = 'I2.docx'

REMOVE = {11: '1．〔基〕平面上的两点间的距离公式', 13: '2．〔基〕特别地',
          181: '32．〔基〕把平面内与两个定点', 240: '38．〔基〕(1)定义',
          256: '(2)等轴双曲线具有以下性质'}
RESTYLE = {21: '一条直线的倾斜角的正切值', 24: '过两点的直线的斜率公式为',
           27: '（1）定义：直线上的向量', 28: '（2）直线的斜率与直线方向向量的关系',
           47: '（1）定义：关于x，y的二元一次方程', 108: '（3）圆的标准方程',
           112: '当时，二元二次方程', 115: '圆的一般方程表示的圆的圆心为',
           255: '(1)实轴长与虚轴长相等', 257: '①方程形式为x²-y²=λ',
           324: '(1)定义：平面内与一个定点F', 383: '(2)弦长计算'}
ADD = {54: '①过已知点的直线系方程', 84: '的几何含义为过点', 87: '①的几何含义为点',
       92: '在平面直角坐标系中，点', 100: '①等曼线所在直线的斜率',
       119: '①圆系', 120: '那么圆系', 121: '③如果圆与圆有两个交点',
       130: '平面内到两个定点', 150: '隐圆第一定义', 151: '隐圆第二定义',
       154: '隐圆第三定义', 155: '隐圆第四定义', 157: '隐圆第五定义',
       176: '（1）到线段两端点相等', 177: '（2）到角的两边相等', 178: '（3）平面内到一定点',
       196: '①焦点三角形的周长', 197: '③设', 225: '①若r为焦点三角形的内切圆半径',
       226: '（2）椭圆内心定理', 230: '已知点', 264: '①若', 265: '②设',
       282: '①若点P在双曲线', 292: '（2）双曲线内心定理', 301: '已知点',
       302: '则点的轨迹是中心在原点', 313: '已知点', 337: '设P为圆锥曲线上任意一点',
       339: '①焦点在x轴上', 341: '①焦点在x轴上', 342: '（3）抛物线',
       355: '①', 359: '①过抛物线焦点的直线交抛物线', 360: '②', 361: '③',
       362: '⑤以AB为直径的圆与准线', 363: '⑥以MN为直径的圆与AB相切',
       364: '⑩设抛物线的顶点为O', 368: '如图，已知点', 374: '依葫芦画瓢',
       393: '若直线与椭圆交于', 399: '若直线与双曲线', 405: '若直线与抛物线交于',
       413: '如果直线与曲线', 421: '①判别式', 440: 'A、F、B三点共线',
       442: '①焦点在x轴上', 444: '①焦点在x轴上', 446: '①焦点在x轴上',
       452: '定理1', 464: '性质 1', 465: '性质 2', 471: '性质 1', 472: '性质 2',
       476: '①阿基米德三角形底边上的中线', 483: '②若阿基米德三角形的底边',
       484: '③若直线', 485: '④底边为', 486: '⑤若阿基米德三角形的底边过焦点',
       487: '⑥在阿基米德三角形中', 488: '⑧抛物线上任取一点',
       492: '①与椭圆相切', 494: '③与抛物线相切', 514: '定比分点',
       517: '定理1', 520: '定理2'}

PPR_ORDER = ['pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl',
             'numPr', 'suppressLineNumbers', 'pBdr', 'shd', 'tabs', 'suppressAutoHyphens', 'kinsoku',
             'wordWrap', 'overflowPunct', 'topLinePunct', 'autoSpaceDE', 'autoSpaceDN', 'bidi',
             'adjustRightInd', 'snapToGrid', 'spacing', 'ind', 'contextualSpacing', 'mirrorIndents',
             'suppressOverlap', 'jc', 'textDirection', 'textAlignment', 'textboxTightWrap',
             'outlineLvl', 'divId', 'cnfStyle', 'rPr', 'sectPr', 'pPrChange']


def make_pbdr():
    pbdr = etree.Element(W + 'pBdr')
    for side in ('top', 'left', 'bottom', 'right'):
        e = etree.SubElement(pbdr, W + side)
        e.set(W + 'val', 'single'); e.set(W + 'sz', '4')
        e.set(W + 'space', '4'); e.set(W + 'color', 'auto')
    return pbdr


def insert_pbdr(ppr, pbdr):
    pos = len(PPR_ORDER)
    for child in ppr:
        tag = child.tag.split('}')[-1]
        if tag in PPR_ORDER and PPR_ORDER.index(tag) > PPR_ORDER.index('pBdr'):
            pos = min(pos, list(ppr).index(child))
            break
    ppr.insert(pos, pbdr)


zin = zipfile.ZipFile(path); parts = {n: zin.read(n) for n in zin.namelist()}; zin.close()
root = etree.fromstring(parts['word/document.xml'])
els = list(root.find(W + 'body'))

n_rm = n_rs = n_add = 0
for idx, prefix in REMOVE.items():
    p = els[idx]; t = ''.join(x.text or '' for x in p.iter(W + 't'))
    assert t.startswith(prefix), 'e%d 文本不符: %r' % (idx, t[:24])
    ppr = p.find(W + 'pPr'); pb = ppr.find(W + 'pBdr') if ppr is not None else None
    assert pb is not None, 'e%d 无pBdr可剔' % idx
    ppr.remove(pb); n_rm += 1
for idx, prefix in RESTYLE.items():
    p = els[idx]; t = ''.join(x.text or '' for x in p.iter(W + 't'))
    assert t.startswith(prefix), 'e%d 文本不符: %r' % (idx, t[:24])
    ppr = p.find(W + 'pPr'); pb = ppr.find(W + 'pBdr') if ppr is not None else None
    assert pb is not None, 'e%d 无pBdr可归一' % idx
    ppr.remove(pb); insert_pbdr(ppr, make_pbdr()); n_rs += 1
for idx, prefix in ADD.items():
    p = els[idx]; t = ''.join(x.text or '' for x in p.iter(W + 't'))
    assert t.startswith(prefix), 'e%d 文本不符: 期望%r 实际%r' % (idx, prefix, t[:24])
    ppr = p.find(W + 'pPr')
    if ppr is None:
        ppr = etree.Element(W + 'pPr'); p.insert(0, ppr)
    assert ppr.find(W + 'pBdr') is None, 'e%d 已有pBdr' % idx
    insert_pbdr(ppr, make_pbdr()); n_add += 1

assert (n_rm, n_rs, n_add) == (5, 12, 68), (n_rm, n_rs, n_add)
# 终态断言：全文四边细框段恰80、space全4
final = []
for i, p in enumerate(els):
    ppr = p.find(W + 'pPr')
    if ppr is None: continue
    pb = ppr.find(W + 'pBdr')
    if pb is None: continue
    sides = {s: pb.find(W + s) for s in ('top', 'left', 'bottom', 'right')}
    if all(v is not None for v in sides.values()):
        assert all(v.get(W + 'sz') == '4' and v.get(W + 'space') == '4' for v in sides.values()), i
        final.append(i)
assert len(final) == 80, len(final)
assert set(final) == (set(RESTYLE) | set(ADD)), '终态框集不符'

parts['word/document.xml'] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
tmp = path + '.tmp'
for _ in range(12):
    try:
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
            for n, d in parts.items():
                zo.writestr(n, d)
        os.replace(tmp, path); break
    except PermissionError:
        time.sleep(6)
print('I2手术完成：剔除%d 归一%d 新增%d → 四边细框段合计%d（sz=4 space=4）' % (n_rm, n_rs, n_add, len(final)))
