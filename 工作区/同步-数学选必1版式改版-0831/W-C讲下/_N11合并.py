# -*- coding: utf-8 -*-
"""N11 短行合并扩面（W-C讲下）：STEM枚举/小问短行必并（7组，当前body子元素序）→ 节标题行×统计行合并（1处，正则定位）
铁律：零字符增删（合并段间不加任何字符；节标题行分隔＝全角空格×1计入授权项§2.3）"""
import zipfile, re, sys, os, time, json
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return '{%s}%s' % (W, t)

def lin(el):
    return ''.join(s.text or '' for s in el.iter() if isinstance(s.tag, str) and s.tag in (w('t'), '{%s}t' % M))

ENUM_MERGES = [
    ([13, 14], '题63(1)(2)小问并一行（(1)尾全角；零字符）'),
    ([27, 28], '题64求：(1)(2)小问并一行（(1)尾全角；零字符）'),
    ([603, 604], '题干选项A．B．段＋；C．D．拆行并一行（后段起头；零字符）'),
    ([638, 639], '题干选项A．B．段＋；C．D．拆行并一行（后段起头；零字符）'),
    ([984, 985], '题138(1)(2)小问并一行（(1)尾全角；零字符）'),
    ([1026, 1027], '题140(1)(2)小问并一行（(1)尾全角；零字符）'),
    ([1082, 1083], '题干选项A．B．段＋；C．D．拆行并一行（后段起头；零字符）'),
]
EXEMPTIONS = [
    ('题66选项A-D（行143-146）', '多选选项各段无尾分隔——并需增字符「；」不并（W-B先例同款）'),
    ('讲部①②③④墙角补形条目（行42/44/46/48）', '81~131字符长条目＋间隔图段——非短行、讲部结构锚不并'),
    ('讲部①②内切球条目（行348/350）', '131/81字符长条目——非短行不并'),
    ('讲部方法/第1步/第2步/第3步锚行（行356-360）', '讲部结构锚行——不并'),
    ('「4．秒杀公式」条目题名行（行361）', '条目号锚行——不并（条目号底纹恒等对象）'),
    ('图1/图2图注段（行557/564）', '图形段周边白名单断点'),
    ('「（详见知识清单1.2.5条目NN）」回指句×7（行37/52/172/218/220/352/354）', '结构性衔接语独立行（常识出清轮回指句）'),
    ('类型Ⅰ…讲部分类锚行（行197等）', '讲部结构锚行'),
    ('「方法一：直接法」并行解法标记行（行370）', '并行解法标记锚行'),
    ('ANS详解区∵∴碎片短行（约70段）', '前轮0827 R3已按三档处置存留——本轮不重复扩面（防层次拥挤回退，W-B先例同款）'),
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
    # ---- B先：枚举组合并（行索引＝当前body子元素序，自后向前防位移）----
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
        f.write('# N11短行合并扩面·逐条决策清单（C讲下）\n\n## 节标题行合并（%d处；分隔全角空格×%d个——授权项§2.3）\n\n' % (sect_merged, separators_added))
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
        f.write('\n## 三档力度口径\n\n- 一档（必并）：STEM枚举条件/小问短行与选项拆行零字符可并者——本件%d组全并；节标题行×统计行——%d处全并（分隔空格计入授权）。\n- 二档（宜并）：详解锚后碎片——前轮0827 R3已按三档处置（本件约70段），本轮维持不重开（W-B先例同款）。\n- 三档（不并/豁免）：含图、需增字符分隔、讲部结构锚行、条目号锚行、回指句、图注——见豁免登记。\n' % (enum_merged, sect_merged))
    print(json.dumps({'节标题合并': sect_merged, '分隔空格': separators_added, '枚举组合并': enum_merged, '豁免登记条数': len(EXEMPTIONS)}, ensure_ascii=False))

if __name__ == '__main__':
    main(sys.argv[1])
