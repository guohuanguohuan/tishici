# -*- coding: utf-8 -*-
"""W-I1 步骤4：N7深蓝字——内容标记族run（C9C9C9挂点，除条目号/块标签chip）文字色→#1F4E79。
条目号（N．）与块标签【×】chip 黑字不变；OMML m:r 与 ctrlPr 挂点同改。零文字改动。"""
import zipfile, os, re, sys, json
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
WC, MC = '{%s}' % W, '{%s}' % M
def q(t): return WC + t
def mq(t): return MC + t

RPR_ORDER = ['rStyle', 'rFonts', 'b', 'bCs', 'i', 'iCs', 'caps', 'smallCaps', 'strike',
             'dstrike', 'outline', 'shadow', 'emboss', 'imprint', 'noProof', 'snapToGrid',
             'vanish', 'webHidden', 'color', 'spacing', 'w', 'kern', 'position', 'sz', 'szCs',
             'highlight', 'u', 'effect', 'bdr', 'shd', 'fitText', 'vertAlign', 'rtl', 'cs',
             'em', 'lang', 'eastAsianLayout', 'specVanish', 'oMath']

DEEP = '1F4E79'
CHIP_RE = re.compile(r'^【[^】]{1,30}】$')
NUM_RE = re.compile(r'^\d{1,4}．$')

def set_color(rpr):
    """在 rPr 内按 OOXML 序插入/更新 w:color val=DEEP；返回是否改动。"""
    c = rpr.find(q('color'))
    if c is not None:
        if c.get(q('val')) == DEEP:
            return False
        c.set(q('val'), DEEP)
        # themeColor 等残余属性清掉防覆盖
        for a in ('themeColor', 'themeShade', 'themeTint'):
            if c.get(q(a)) is not None:
                del c.attrib[q(a)]
        return True
    c = etree.Element(q('color'))
    c.set(q('val'), DEEP)
    # 按序插入
    idx_new = RPR_ORDER.index('color')
    inserted = False
    for child in rpr:
        name = etree.QName(child).localname
        if name in RPR_ORDER and RPR_ORDER.index(name) > idx_new:
            child.addprevious(c)
            inserted = True
            break
    if not inserted:
        rpr.append(c)
    return True

def run_text(r):
    return ''.join(t.text or '' for t in r.findall(q('t')))

def main(src, dst, report):
    zin = zipfile.ZipFile(src)
    doc = etree.fromstring(zin.read('word/document.xml'))
    stats = {'正文run值': 0, '正文run空': 0, '跳过_条目号': 0, '跳过_chip': 0,
             'omml_m_r': 0, 'ctrlPr': 0, '已有同值': 0}
    # ① 普通文字 run
    for r in doc.iter(q('r')):
        # 跳过 OMML 内部（m:r 的子 w:r 不存在；w:r 只在普通流）——iter 会进 m:r 吗？w:r 命名空间不同，iter(q('r')) 只匹配 w:r
        rpr = r.find(q('rPr'))
        if rpr is None:
            continue
        shd = rpr.find(q('shd'))
        if shd is None or shd.get(q('fill')) != 'C9C9C9':
            continue
        t = run_text(r)
        if t.strip():
            if NUM_RE.fullmatch(t.strip()):
                stats['跳过_条目号'] += 1
                continue
            if CHIP_RE.fullmatch(t.strip()):
                stats['跳过_chip'] += 1
                continue
            if set_color(rpr):
                stats['正文run值'] += 1
            else:
                stats['已有同值'] += 1
        else:
            if set_color(rpr):
                stats['正文run空'] += 1
    # ② OMML m:r（w:rPr 挂 C9C9C9）
    for mr in doc.iter(mq('r')):
        wrpr = mr.find(q('rPr'))
        if wrpr is None:
            continue
        shd = wrpr.find(q('shd'))
        if shd is None or shd.get(q('fill')) != 'C9C9C9':
            continue
        if set_color(wrpr):
            stats['omml_m_r'] += 1
    # ③ ctrlPr
    for cp in doc.iter(mq('ctrlPr')):
        wrpr = cp.find(q('rPr'))
        if wrpr is None:
            continue
        shd = wrpr.find(q('shd'))
        if shd is None or shd.get(q('fill')) != 'C9C9C9':
            continue
        if set_color(wrpr):
            stats['ctrlPr'] += 1

    # 零文字断言：w:t/m:t 流恒等（与源件比对）
    def textstream(root):
        out = []
        for el in root.iter():
            ln = etree.QName(el).localname
            if ln in ('t',):
                out.append(el.text or '')
        return ''.join(out)
    assert textstream(doc) == textstream(etree.fromstring(zin.read('word/document.xml'))), '文字流变化！'
    zin.close()

    new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    with zipfile.ZipFile(src) as z2, zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in z2.infolist():
            data = new_xml if item.filename == 'word/document.xml' else z2.read(item.filename)
            zout.writestr(item, data)
    json.dump(stats, open(report, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('N7深蓝:', json.dumps(stats, ensure_ascii=False))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
