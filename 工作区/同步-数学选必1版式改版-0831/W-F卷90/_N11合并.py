# -*- coding: utf-8 -*-
"""W-F卷90 N11 短行合并扩面：STEM枚举短行必并（13组）→ 节标题行×统计行合并（4处）
铁律：零字符增删（合并段间不加任何字符；节标题行分隔＝全角空格×1计入授权项§2.3）
区间28/统计段18＝主会话裁决：标题runs保持28半点，统计段runs已由步骤1置18半点，合并后行内双档。"""
import zipfile, re, sys, os, time, json
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return '{%s}%s' % (W, t)

def lin(el):
    return ''.join(s.text or '' for s in el.iter() if isinstance(s.tag, str) and s.tag in (w('t'), '{%s}t' % M))

ENUM_MERGES = [
    ([6, 7, 8], '题93①(1)(2)(3)圆方程条件并一行（各行自带；．分隔，零字符）'),
    ([22, 23, 24], '题95(1)(2)(3)小问并一行（自带；；．分隔）'),
    ([59, 60], '题97(1)(2)小问并一行'),
    ([265, 266], '题99(1)(2)小问并一行'),
    ([386, 387, 388, 389], '题122(1)＋条件①＋条件②＋(2)并一行（条件①／(2)标记自带分隔）'),
    ([422, 423], '题107(1)(2)焦半径小问并一行'),
    ([593, 594, 595], '题115(1)(2)(3)小问并一行（自带；；．分隔）'),
    ([610, 611], '题117(1)(2)条件小问并一行'),
    ([672, 673, 674, 675], '题119(1)-(4)椭圆方程条件并一行（纯式短行，自带；．分隔）'),
    ([703, 704], '题121(1)(2)条件并一行'),
    ([754, 755], '题124(1)(2)小问并一行'),
    ([865, 866, 867, 868], '题126①②③④卫星多选条件并一行（①标记自带分隔）'),
    ([1066, 1067], '题182(1)(2)小问并一行（(1)自带；分隔）'),
]
EXEMPTIONS = [
    ('题96选项A-D（行37-40）', '多选选项各段无尾分隔——并需增字符「；」不并（W-B同款豁免）'),
    ('题100(2)（行151）', '(2)长式93字——含长设问不并'),
    ('题104(2)（行245）', '(2)长式90字——含长设问不并'),
    ('题110①-⑤（行302-306）', '多选长陈述（32~52字/项）——长式不并'),
    ('题134选项A-D（行512-513）', '多选选项各段无尾分隔——并需增字符「；」不并（W-B同款豁免）'),
    ('题135选项A-D（行526-528）', '多选长选项（45~54字/项）且无尾分隔——长式不并'),
    ('题178①②③＋(1)(2)(3)（行928-933）', '类比推理长题组（34~82字/项）——长式不并'),
    ('题180(2)（行970）', '(2)长式57字——含长设问不并'),
    ('题182①②（行1068-1069）', '①②真命题长陈述（54~69字）——长式不并（(1)(2)已并）'),
    ('ANS详解区∵∴短句碎片', '前轮0827整册轮已按三档处置存留——本轮不重复扩面（防层次拥挤回退，W-B同款）'),
    ('LECT讲部结构短行', '讲部方法锚行/条目行——结构锚不并'),
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
    els = list(body)
    enum_merged = 0
    for idxs, reason in sorted(ENUM_MERGES, key=lambda x: -x[0][0]):
        dst = els[idxs[0]]
        for k in idxs:
            assert els[k].tag == w('p'), '组内非段落: %d' % k
        before = ''.join(lin(els[k]) for k in idxs)
        for k in idxs[1:]:
            move_children(dst, els[k])
            body.remove(els[k])
        after = lin(dst)
        assert after == before, '枚举合并零字符校验失败: %s' % reason
        enum_merged += 1
        log.append(('枚举合并', after[:60], reason))
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
        log.append(('节标题合并', t[:46], '统计段「%s」并入标题行；分隔全角空格×1（18半点）；标题runs保持28（区间28/统计段18＝主会话裁决）' % nt[:24]))
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
        f.write('# N11短行合并扩面·逐条决策清单（W-F卷90）\n\n## 节标题行合并（%d处；分隔全角空格×%d个——授权项§2.3；区间28/统计段18＝主会话裁决）\n\n' % (sect_merged, separators_added))
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
        f.write('\n## 三档力度口径\n\n- 一档（必并）：STEM枚举条件/小问短行零字符可并者——本件%d组全并；节标题行×统计行——%d处全并（分隔空格计入授权）。\n- 二档（宜并）：详解锚后碎片——前轮0827整册轮已按三档处置，本轮维持不重开。\n- 三档（不并/豁免）：含图、需增字符分隔、长式（>40字单项）、讲部结构锚行——见豁免登记。\n' % (enum_merged, sect_merged))
    print(json.dumps({'节标题合并': sect_merged, '分隔空格': separators_added, '枚举组合并': enum_merged, '豁免登记条数': len(EXEMPTIONS)}, ensure_ascii=False))

if __name__ == '__main__':
    main(sys.argv[1])
