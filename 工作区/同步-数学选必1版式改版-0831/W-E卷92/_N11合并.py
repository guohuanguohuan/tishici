# -*- coding: utf-8 -*-
"""W-E卷92 N11 短行合并扩面：①STEM枚举短行必并（16组，零字符）②节标题行×统计行合并（8处，分隔全角空格×1授权§2.3）
用法: python _N11合并.py <docx> [sample]   （sample=只做第一组枚举+第一个节标题合并的小样）"""
import zipfile, re, sys, os, time, json
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return '{%s}%s' % (W, t)

def lin(el):
    return ''.join(s.text or '' for s in el.iter() if isinstance(s.tag, str) and s.tag in (w('t'), '{%s}t' % M))

# 行索引＝当前body直接子元素序（快照）；首字符指纹防漂移
ENUM_MERGES = [
    ([112, 113], '(1)', '题干(1)(2)小问并一行（(1)尾；）'),
    ([125, 126], '(1)', '题干(1)(2)小问并一行'),
    ([201, 202], '(1)', '题干(1)(2)小问并一行'),
    ([212, 213, 214], '(1)', '题干(1)(2)(3)小问并一行'),
    ([329, 330], '(1)', '题干(1)(2)小问并一行（(1)尾半角;）'),
    ([358, 359], '(1)', '题干(1)(2)小问并一行'),
    ([408, 409, 410], '①', '题干①②③条件并一行'),
    ([484, 485, 486, 487], '(1)', '题干(1)—(4)小问并一行'),
    ([531, 532, 533, 534], '①', '题干①②③④判断条目并一行'),
    ([659, 660], '(1)', '题干(1)(2)小问并一行'),
    ([676, 677, 678], '(1)', '题干(1)(2)(3)小问并一行'),
    ([767, 768], '(1)', '题干(1)(2)小问并一行'),
    ([794, 795], '(1)', '题干(1)(2)小问并一行'),
    ([858, 859], '(1)', '题干(1)(2)小问并一行'),
    ([905, 906], '(1)', '题干(1)(2)小问并一行（尾半角;?）'),
    ([988, 989, 990], '(1)', '题干(1)(2)(3)小问并一行'),
]
EXEMPTIONS = [
    ('题2选项两行式AB/CD（行20-21）', '行尾无分隔——需增「；」不并'),
    ('题13选项两行式AB/CD（行74-75）', '行尾无分隔——需增「；」不并'),
    ('题15(1)(2)（行97-98）', '(1)行尾无标点——零字符并成「方程(2)」粘连，需增字符不并'),
    ('题28(1)(2)（行314-315）', '(1)含图——含图设问不并'),
    ('题33选项两行式AB/CD（行350-351）', '行尾无分隔（分数式）——需增「；」不并'),
    ('题44选项两行式AB/CD（行477-478）', '行尾无分隔——需增「；」不并'),
    ('题48选项两行式AB/CD（行518-519）', '行尾无分隔——需增「；」不并'),
    ('题64选项两行式AB/CD（行750-751）', '行尾无分隔（集合式）——需增「；」不并'),
    ('题35设问收尾行「其中真命题的是（）」（行411）', '题干设问收尾行——并前组尾「；」衔接生硬，保持独立'),
    ('题51设问收尾行「所有正确的是___」（行535）', '同上——设问焦点行保持独立'),
    ('题62①②③条件行（行658）', '条件行自成一段（其后(1)(2)已并）——跨族不并'),
    ('题20多选选项A—D四行（行237-240）', '多选选项各段无尾分隔——需增「；」不并'),
    ('题5选项AB/CD（行298-299）', '行尾无分隔——需增「；」不并'),
    ('ANS详解区∵∴/故选/故答案为短句碎片（约60段）', '前轮0827 R3已按三档处置存留——本轮不重复扩面（W-B同款先例）'),
    ('LECT讲部结构短行（详见知识清单回指句/法N锚行）', '讲部结构锚/回指句——结构锚不并'),
]
SEP_OK = '；;．。？：:'

def move_children(dst, src):
    moved = 0
    for ch in list(src):
        if ch.tag == w('pPr'):
            continue
        dst.append(ch)
        moved += 1
    return moved

def main(path, sample=False):
    with zipfile.ZipFile(path) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    doc = etree.fromstring(parts['word/document.xml'])
    body = doc.find(w('body'))
    log = []
    merges = ENUM_MERGES[:1] if sample else ENUM_MERGES
    els = list(body)
    enum_merged = 0
    for idxs, head, reason in sorted(merges, key=lambda x: -x[0][0]):
        dst = els[idxs[0]]
        for k in idxs:
            assert els[k].tag == w('p'), '组内非段落: %d' % k
        # 指纹防漂移：首段须以head开头，其余段不得含题号/标签
        assert lin(els[idxs[0]]).startswith(head), '指纹失配@%d: %r' % (idxs[0], lin(els[idxs[0]])[:20])
        for k in idxs[1:]:
            tk = lin(els[k])
            assert not re.match(r'^\d{1,3}．', tk) and not tk.startswith('【'), '组内混入题号/标签@%d' % k
        before = ''.join(lin(els[k]) for k in idxs)
        for k in idxs[1:]:
            move_children(dst, els[k])
            body.remove(els[k])
        after = lin(dst)
        assert after == before, '枚举合并零字符校验失败: %s' % reason
        enum_merged += 1
        log.append(('枚举合并', after[:56], reason))
    sect_merged = 0
    separators_added = 0
    children = list(body)
    limit = 1 if sample else 99
    for el in children:
        if sect_merged >= limit:
            break
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
        log.append(('节标题合并', t[:46], '统计段「%s」并入标题行；分隔全角空格×1（18半点，授权§2.3）' % nt[:26]))
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
    mode = 'SAMPLE' if sample else 'FULL'
    fn = 'N11决策清单.md' if not sample else 'N11决策清单-小样.md'
    with open(fn, 'w', encoding='utf-8') as f:
        f.write('# N11短行合并扩面·逐条决策清单（E卷92，%s）\n\n## 节标题行合并（%d处；分隔全角空格×%d——授权§2.3）\n\n' % (mode, sect_merged, separators_added))
        for kind, txt, why in log:
            if kind == '节标题合并':
                f.write('- %s｜%s\n' % (txt, why))
        f.write('\n## 枚举短行必并（%d组，零字符）\n\n' % enum_merged)
        for kind, txt, why in log:
            if kind == '枚举合并':
                f.write('- %s…｜%s\n' % (txt, why))
        f.write('\n## 豁免登记（%d条）\n\n' % len(EXEMPTIONS))
        for name, why in EXEMPTIONS:
            f.write('- %s｜%s\n' % (name, why))
        f.write('\n## 三档力度口径\n\n- 一档（必并）：STEM枚举条件/小问短行零字符可并者（各行自带；．？分隔）——本件%d组全并；节标题行×统计行——8处全并（分隔空格计入授权）。\n- 二档（保守）：合并后行宽>95%%或破坏层次方可回退——本件无回退。\n- 三档（不并/豁免）：含图、需增字符分隔、两行式选项行、讲部结构锚行、ANS区前轮已处置——见豁免登记。\n' % enum_merged)
    print(json.dumps({'模式': mode, '节标题合并': sect_merged, '分隔空格': separators_added, '枚举组合并': enum_merged, '豁免登记条数': len(EXEMPTIONS)}, ensure_ascii=False))

if __name__ == '__main__':
    main(sys.argv[1], sample=(len(sys.argv) > 2 and sys.argv[2] == 'sample'))
