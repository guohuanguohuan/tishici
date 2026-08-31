# -*- coding: utf-8 -*-
"""W-H卷89 N11 短行合并：STEM枚举小问短行必并（32组，零字符）→ 节标题行×统计行合并（1处）
铁律：零字符增删（合并段间不加任何字符；节标题行分隔＝全角空格×1计入授权项§2.3）"""
import zipfile, re, sys, os, time, json
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return '{%s}%s' % (W, t)

def lin(el):
    return ''.join(s.text or '' for s in el.iter()
                   if isinstance(s.tag, str) and s.tag in (w('t'), '{%s}t' % M))

ENUM_MERGES = [
    ([50, 51, 52, 53], '题254(1)(2)(3)(4)小问并一行'),
    ([86, 87], '题259(1)(2)小问并一行'),
    ([160, 161], '题258(2)并入题干段（(1)在题号段内）'),
    ([207, 208], '题262(1)(2)小问并一行'),
    ([311, 312], '题266(1)(2)小问并一行'),
    ([326, 327], '题268(1)(2)小问并一行'),
    ([343, 344], '题269(1)(2)小问并一行'),
    ([455, 456], '题278(1)(2)小问并一行'),
    ([478, 479], '题280(1)(2)小问并一行'),
    ([786, 787], '题302(1)(2)小问并一行'),
    ([803, 804, 805], '题304①②条件＋(1)(2)小问并一行'),
    ([839, 840, 841], '题308（Ⅰ）（Ⅱ）（Ⅲ）小问并一行'),
    ([864, 865], '题311(1)(2)小问并一行'),
    ([921, 922], '题314(1)(2)小问并一行'),
    ([941, 942], '题316(1)(2)小问并一行'),
    ([957, 958], '题318(1)(2)小问并一行'),
    ([974, 975], '题320(1)(2)小问并一行'),
    ([989, 990], '题322(1)(2)小问并一行'),
    ([1005, 1006], '题324(1)(2)小问并一行'),
    ([1029, 1030, 1031], '题327(1)(2)(3)小问并一行'),
    ([1053, 1054], '题329(1)(2)小问并一行'),
    ([1066, 1067], '题330(1)(2)小问并一行'),
    ([1097, 1098], '题333(1)(2)小问并一行'),
    ([1107, 1108], '题334(1)(2)小问并一行'),
    ([1163, 1164], '题337(1)(2)小问并一行'),
    ([1180, 1181], '题340(1)(2)小问并一行'),
    ([1193, 1194], '题341(1)(2)小问并一行'),
    ([1211, 1212], '题343(1)(2)小问并一行'),
    ([1228, 1229, 1230], '题345(1)(2)(3)小问并一行'),
    ([1247, 1248], '题336(1)(2)小问并一行'),
    ([1272, 1273], '题346(1)(2)小问并一行'),
    ([1292, 1293], '题348(1)(2)小问并一行'),
]
EXEMPTIONS = [
    ('行429 题276选项行A-D', '含行内公式图片（图）——含图不并（单段自带形态）'),
    ('行696-699（1）~（4）', '条目「1．点差法的基本题型」第一子层（N）——结构锚不并'),
    ('行765-766 ①②', '非对称处理讲部方法步骤＋韦达长式——讲部步骤/长式不并'),
    ('行1085-1091 ①~④及公式行', '齐次化讲部方法步骤＋长式——讲部步骤/长式不并'),
    ('ANS详解区短句碎片（约70段）', '前轮0827 R3已按三档处置存留——本轮不重复扩面（防层次拥挤回退）'),
    ('LECT讲部结构短行（步骤一/二/三、包装路线、（详见知识清单…）回指句）', '讲部方法锚行/结构锚不并'),
    ('选项行', '本件选项均已是单段形态（A．…B．…同段），无多段无尾分隔形态'),
]
EXPECT_PREFIX = {
    50: '(1)求直线l的方程', 86: '(1)求证：直线y1y', 160: '258．（中档', 207: '(1)证明：直线PA',
    311: '(1)求抛物线E的方程', 326: '(1)求△APB', 343: '(1)证明：直线AB过定点',
    455: '(1)求双曲线C的方程', 478: '(1)求实数k的取值范围', 786: '(1)求椭圆E的方程',
    803: '①P1(1,1)', 839: '（Ⅰ）求椭圆E的方程', 864: '(1)求椭圆C的方程',
    921: '(1)求椭圆Ω的方程', 941: '(1)求椭圆E的方程', 957: '(1)求曲线C的方程',
    974: '(1)求椭圆E的方程', 989: '(1)求椭圆C的方程', 1005: '(1)求曲线C的方程',
    1029: '(1)求双曲线C的方程', 1053: '(1)求双曲线C：', 1066: '(1)求双曲线C的离心率',
    1097: '(1)求抛物线C的方程', 1107: '(1)求动点M的轨迹方程', 1163: '(1)求双曲线的离心率',
    1180: '(1)求椭圆的方程', 1193: '(1)求抛物线C的标准方程', 1211: '(1)求点A关于M',
    1228: '(1)若点E，F的纵坐标', 1247: '(1)农艺园的最大面积', 1272: '(1)求抛物线的标准方程',
    1292: '(1)若点T是MN的中点',
}

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
    # ---- A先：枚举组合并（降序处理防索引失效）----
    els = list(body)
    enum_merged = 0
    for idxs, reason in sorted(ENUM_MERGES, key=lambda x: -x[0][0]):
        dst = els[idxs[0]]
        exp = EXPECT_PREFIX[idxs[0]]
        got = lin(dst)
        assert got.startswith(exp), '索引完整性门失败: 行%d 期望%r 实得%r' % (idxs[0], exp, got[:30])
        for k in idxs[1:]:
            assert els[k].tag == w('p'), '组内非段落: %d' % k
        before = ''.join(lin(els[k]) for k in idxs)
        for k in idxs[1:]:
            move_children(dst, els[k])
            body.remove(els[k])
        after = lin(dst)
        assert after == before, '枚举合并零字符校验失败: %s' % reason
        enum_merged += 1
        log.append(('枚举合并', after[:64], reason))
    # ---- B后：节标题行×统计行合并（正则定位，索引无关）----
    sect_merged = 0
    separators_added = 0
    for el in list(body):
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
        assert lin(el) == t + '\u3000' + nt, '节标题合并字符校验失败'
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
        f.write('# N11短行合并扩面·逐条决策清单（W-H卷89）\n\n## 节标题行合并（%d处；分隔全角空格×%d个——授权项§2.3）\n\n' % (sect_merged, separators_added))
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
        f.write('\n## 三档力度口径\n\n- 一档（必并）：STEM枚举条件/小问短行零字符可并者——本件%d组全并；节标题行×统计行——%d处全并（分隔空格计入授权）。\n- 二档（宜并）：详解锚后碎片——前轮0827 R3已按三档处置，本轮维持不重开。\n- 三档（不并/豁免）：含图、讲部方法步骤（长式）、条目第一子层结构锚、需增字符分隔——见豁免登记。\n' % (enum_merged, sect_merged))
    print(json.dumps({'节标题合并': sect_merged, '分隔空格': separators_added,
                      '枚举组合并': enum_merged, '豁免登记条数': len(EXEMPTIONS)}, ensure_ascii=False))

if __name__ == '__main__':
    main(sys.argv[1])
