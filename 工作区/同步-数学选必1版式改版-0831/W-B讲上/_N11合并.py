# -*- coding: utf-8 -*-
"""N11 短行合并扩面：STEM枚举短行必并（20组，原始行索引）→ 节标题行×统计行合并（7，正则定位）
铁律：零字符增删（合并段间不加任何字符；节标题行分隔＝全角空格×1计入授权项§2.3）"""
import zipfile, re, sys, os, time, json
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return '{%s}%s' % (W, t)

def lin(el):
    return ''.join(s.text or '' for s in el.iter() if isinstance(s.tag, str) and s.tag in (w('t'), '{%s}t' % M))

ENUM_MERGES = [
    ([34, 35, 36, 37, 38], '题4①②③④条件＋设问行并一行（各行自带；．分隔，零字符）'),
    ([121, 122], '题12(1)(2)小问并一行'),
    ([155, 156, 157], '题15(1)(2)(3)小问并一行'),
    ([186, 187], '题17(1)(2)小问并一行'),
    ([209, 210], '题19(1)(2)小问并一行'),
    ([220, 221], '题20(1)(2)小问并一行'),
    ([233, 234], '题23(2)①②小问并一行'),
    ([274, 275], '题25(1)(2)小问并一行'),
    ([363, 364], '题36求证(1)(2)并一行'),
    ([379, 380], '题38(1)(2)小问并一行'),
    ([426, 427, 428], '题39②③④条件并一行（①与②间隔图不入）'),
    ([567, 568], '题45(1)(2)小问并一行'),
    ([580, 581], '题46(1)(2)小问并一行'),
    ([644, 645], '题49(1)(2)小问并一行'),
    ([658, 659], '题50(1)(2)小问并一行'),
    ([762, 763], '题52(1)(2)小问并一行'),
    ([802, 803], '题53(1)(2)小问并一行'),
    ([944, 945], '题55(3)并入(1)(2)行'),
    ([1010, 1011], '题57(1)(2)小问并一行'),
    ([1074, 1075, 1076], '题60(1)(2)(3)小问并一行'),
]
EXEMPTIONS = [
    ('题23(1)(2)（行230-231）', '(2)含图——含图设问不并'),
    ('题31选项A-D（行328-331）', '多选选项各段无尾分隔——并需增字符「；」不并'),
    ('题37选项A-D（行395-398）', '多选选项各段无尾分隔——并需增字符「；」不并'),
    ('题39①（行423）', '①与②之间隔两图段——含图不并（②③④已并）'),
    ('题51(1)(2)及续行（行700-702）', '(2)含图、行702接图段——含图不并'),
    ('ANS详解区∵∴短句碎片（约80段）', '前轮0827 R3已按三档处置存留——本轮不重复扩面（防层次拥挤回退）'),
    ('LECT讲部结构短行（法一/法三/总结规律/注意/使用提醒等）', '讲部方法锚行/注释字头行（R5同类）——结构锚不并'),
]

def move_children(dst, src):
    moved = 0
    for ch in list(src):
        if ch.tag == w('pPr'):
            continue
        dst.append(ch)
        moved += 1
    return moved

def main(path):
    with zipfile.ZipFile(path) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    doc = etree.fromstring(parts['word/document.xml'])
    body = doc.find(w('body'))
    log = []
    # ---- B先：枚举组合并（行索引＝当前body子元素序）----
    els = list(body)
    enum_merged = 0
    for idxs, reason in sorted(ENUM_MERGES, key=lambda x: -x[0][0]):
        dst = els[idxs[0]]
        for k in idxs[1:]:
            assert els[k].tag == w('p'), '组内非段落: %d' % k
        before = ''.join(lin(els[k]) for k in idxs)
        for k in idxs[1:]:
            move_children(dst, els[k])
            body.remove(els[k])
        after = lin(dst)
        assert after == before, '枚举合并零字符校验失败: %s' % reason
        enum_merged += 1
        log.append(('枚举合并', after[:60], reason))
    # ---- A后：节标题行×统计行合并（正则定位，索引无关）----
    sect_merged = 0
    separators_added = 0
    children = list(body)
    for el in children:
        if not isinstance(el.tag, str) or el.tag != w('p'):
            continue
        t = lin(el)
        if not re.match(r'^\d+(\.\d+)+\s.*（第\d+—\d+题）', t):
            continue
        nxt = el.getnext()
        while nxt is not None and isinstance(nxt.tag, str) and nxt.tag == w('p') and not lin(nxt).strip():
            nxt = nxt.getnext()
        if nxt is None or not (isinstance(nxt.tag, str) and nxt.tag == w('p')):
            continue
        nt = lin(nxt)
        if not nt.startswith('本节'):
            continue
        before = t + nt
        sep_r = etree.SubElement(el, w('r'))
        rPr = etree.SubElement(sep_r, w('rPr'))
        sz = etree.SubElement(rPr, w('sz')); sz.set(w('val'), '18')
        szCs = etree.SubElement(rPr, w('szCs')); szCs.set(w('val'), '18')
        wt = etree.SubElement(sep_r, w('t')); wt.text = '\u3000'
        for ch in list(nxt):
            if ch.tag == w('pPr'):
                continue
            el.append(ch)
        body.remove(nxt)
        after = lin(el)
        assert after == t + '\u3000' + nt, '节标题合并字符校验失败: %s' % t[:30]
        sect_merged += 1
        separators_added += 1
        log.append(('节标题合并', t[:46], '统计段「%s」并入标题行；分隔全角空格×1（18半点）' % nt[:24]))
    parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    tmp = path + '.n11tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
        for n, b in parts.items():
            zo.writestr(n, b)
    for i2 in range(12):
        try:
            os.replace(tmp, path); break
        except PermissionError:
            time.sleep(5)
    with open('N11决策清单.md', 'w', encoding='utf-8') as f:
        f.write('# N11短行合并扩面·逐条决策清单（B讲上）\n\n## 节标题行合并（%d处；分隔全角空格×%d个——授权项§2.3）\n\n' % (sect_merged, separators_added))
        for kind, txt, why in log:
            if kind == '节标题合并':
                f.write('- %s｜%s\n' % (txt, why))
        f.write('\n## 枚举短行必并（%d组，零字符）\n\n' % enum_merged)
        for kind, txt, why in log:
            if kind == '枚举合并':
                f.write('- %s｜%s\n' % (txt, why))
        f.write('\n## 豁免登记（%d条）\n\n' % len(EXEMPTIONS))
        for name, why in EXEMPTIONS:
            f.write('- %s｜%s\n' % (name, why))
        f.write('\n## 三档力度口径\n\n- 一档（必并）：STEM枚举条件/小问短行零字符可并者——本件%d组全并；节标题行×统计行——%d处全并（分隔空格计入授权）。\n- 二档（宜并）：详解锚后碎片——前轮0827 R3已按三档处置（本件142处），本轮维持不重开。\n- 三档（不并/豁免）：含图、需增字符分隔、讲部结构锚行、注释字头行——见豁免登记。\n' % (enum_merged, sect_merged))
    print(json.dumps({'节标题合并': sect_merged, '分隔空格': separators_added, '枚举组合并': enum_merged, '豁免登记条数': len(EXEMPTIONS)}, ensure_ascii=False))

if __name__ == '__main__':
    main(sys.argv[1])
