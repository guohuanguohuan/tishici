# -*- coding: utf-8 -*-
"""W-G N11 短行合并扩面：STEM枚举短行必并（4组）＋节标题行×统计行合并（4处，区间28/统计段18——主会话裁决）
铁律：零字符增删（合并段间不加任何字符；节标题行分隔＝全角空格×1计入授权项§2.3）
行索引＝当前body子元素序（本件0表，行号=body子元素序）"""
import zipfile, re, os, time
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def w(t): return '{%s}%s' % (W, t)

def lin(el):
    return ''.join(s.text or '' for s in el.iter() if isinstance(s.tag, str) and s.tag in (w('t'), '{%s}t' % M))

ENUM_MERGES = [
    ([7, 8, 9, 10, 11], '题183(1)~(5)条件行并一行（各行自带；．分隔，零字符）'),
    ([93, 94, 95], '题191(1)(2)(3)设问并一行'),
    ([116, 117, 118, 119], '题193(1)~(4)条件行并一行'),
    ([189, 190, 191, 192], '题199(1)~(4)条件行并一行'),
]
EXEMPTIONS = [
    ('题217(1)(2)（行369-370）', '(2)长设问52字——长式设问不并；(1)单行无并对象'),
    ('题224选项A-D（行481-484）', '多选选项各段无尾分隔——并需增字符「；」不并'),
    ('题228选项A-D（行500-503）', '多选选项各段无尾分隔——并需增字符不且D行41字长'),
    ('题233选项A-D（行543-546）', '多选选项各段无尾分隔——并需增字符「；」不并'),
    ('ANS详解区结论短句碎片（约50段，故选：/∴选：类）', '前轮0827 R3已按三档处置存留——本轮不重复扩面（W-B同款防层次拥挤回退）'),
    ('LECT讲部（详见知识清单…条目N）回指句（行712/715）', '常识出清轮结构性衔接语——结构锚不并'),
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
        log.append(('节标题合并', t[:46], '统计段「%s」并入标题行（区间28/统计段18）；分隔全角空格×1（18半点）' % nt[:24]))
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
        f.write('# N11短行合并扩面·逐条决策清单（G卷68）\n\n## 节标题行合并（%d处；分隔全角空格×%d个——授权项§2.3；区间28/统计段18＝主会话裁决）\n\n' % (sect_merged, separators_added))
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
    print('枚举合并 %d 组（零字符）｜节标题合并 %d 处（分隔空格×%d）｜豁免 %d 条' % (enum_merged, sect_merged, separators_added, len(EXEMPTIONS)))

if __name__ == '__main__':
    main(r"C:\Users\28120\Desktop\提示词\工作区\同步-数学选必1版式改版-0831\W-G卷68\G工作副本.docx")
