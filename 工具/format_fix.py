# -*- coding: utf-8 -*-
"""format_fix.py — 正文格式规整（字号21/行距300/左对齐/栏目序号剥离/字体规范）
只动正文 run/pPr 属性与栏目序号文本，不碰内容结构。页脚另行手术。"""
import sys, io, os, zipfile, re, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WC = '{%s}' % W

def qn(t):
    p, l = t.split(':')
    return {'w': WC}[p] + l

# 组织性栏目序号：「一、」「（一）」开头且后接知识性文字（≤20字、非句子）→ 只剥前缀
# 保护：自建分组标题（落选题清单分组）不剥
GROUP_WORDS = ('超纲', '高度重复', '组合内让位', '前序章内容', '其它淘汰', '后续章节内容')
LUMU = re.compile(r'^([一二三四五六七八九十]+、|（[一二三四五六七八九十]+）)\s*(.{1,24})$')

def fix_document_xml(doc_bytes):
    root = etree.fromstring(doc_bytes)
    stats = {'sz': 0, 'line': 0, 'jc': 0, 'lumuprefix': 0, 'fonts': 0}
    # 1) 字号 24→21（显式 sz/szCs）
    for el in root.iter(qn('w:sz'), qn('w:szCs')):
        v = el.get(qn('w:val'))
        if v and v not in ('21', '2'):
            el.set(qn('w:val'), '21')
            stats['sz'] += 1
        elif v == '2':
            el.set(qn('w:val'), '21'); stats['sz'] += 1
    # 2) 行距 360→300
    for sp in root.iter(qn('w:spacing')):
        v = sp.get(qn('w:line'))
        if v and v != '300':
            sp.set(qn('w:line'), '300')
            sp.set(qn('w:lineRule'), 'auto')
            stats['line'] += 1
    # 3) 对齐 center/right/both→left（页脚在独立 part，不受影响）
    for jc in root.iter(qn('w:jc')):
        v = jc.get(qn('w:val'))
        if v in ('center', 'right', 'both', 'distribute'):
            jc.set(qn('w:val'), 'left')
            stats['jc'] += 1
    # 4) 字体规范：ascii/hAnsi 非 TNR → TNR；eastAsia 非宋体 → 宋体
    for rf in root.iter(qn('w:rFonts')):
        for att in ('w:ascii', 'w:hAnsi'):
            v = rf.get(qn(att))
            if v and v != 'Times New Roman':
                rf.set(qn(att), 'Times New Roman'); stats['fonts'] += 1
        v = rf.get(qn('w:eastAsia'))
        if v and v not in ('宋体',):
            rf.set(qn('w:eastAsia'), '宋体'); stats['fonts'] += 1
    # 5) 栏目序号剥离（只处理纯标题形态段：短文字＋加粗，且剥后仍非空）
    for p in root.iter(qn('w:p')):
        ts = list(p.iter(qn('w:t')))
        if not ts: continue
        full = ''.join(t.text or '' for t in ts)
        fs = full.strip()
        if not fs or len(fs) > 26: continue
        m = LUMU.match(fs)
        if not m: continue
        rest = m.group(2).strip()
        if not rest: continue
        if rest.startswith(GROUP_WORDS): continue
        # 剥前缀：首个 t 写 rest，其余 t 清空
        first = ts[0]
        if first.text and first.text.strip().startswith(('一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '（')):
            first.text = rest
            for t in ts[1:]:
                t.text = ''
            stats['lumuprefix'] += 1
    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True), stats

def fix(path, out):
    z = zipfile.ZipFile(path)
    zo = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
    total = None
    for n in z.namelist():
        data = z.read(n)
        if n == 'word/document.xml':
            data, total = fix_document_xml(data)
        zo.writestr(n, data)
    zo.close(); z.close()
    print('%-58s %s' % (os.path.basename(path)[:58], total))

if __name__ == '__main__':
    for p in sys.argv[1:]:
        out = p[:-5] + '.fmt.docx'
        fix(p, out)
