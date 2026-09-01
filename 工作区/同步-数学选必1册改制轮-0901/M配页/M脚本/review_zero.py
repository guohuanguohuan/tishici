# -*- coding: utf-8 -*-
"""M配页·零改动复核（只读）：封面（五要素/无页眉页脚）、错题×2（配页件属性/表格行数/专项要素）、
部分封面×6（统计行数字三向核对＋图内零文字媒体清点）。不写任何文件。"""
import io, re, sys, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def qn(t): return '{%s}%s' % (W, t)
BASE = r'C:/提示词/高中数学/高中数学同步/'

def load_parts(path):
    with zipfile.ZipFile(path) as z:
        return z.namelist(), {n: z.read(n) for n in z.namelist()}

def no_header_footer(names, contents):
    """配页件属性断言：无header/footer部件、body无footerReference/headerReference。"""
    hf = [n for n in names if re.search(r'word/(header|footer)\d*\.xml$', n)]
    doc = contents['word/document.xml'].decode('utf-8', errors='ignore')
    refs = 'headerReference' in doc or 'footerReference' in doc
    return (not hf) and (not refs)

def ptexts(path):
    names, contents = load_parts(path)
    root = etree.fromstring(contents['word/document.xml'])
    body = root.find(qn('body'))
    out = []
    for p in body.iter(qn('p')):
        out.append(''.join(t.text or '' for t in p.iter(qn('t'))))
    return out, names, contents, root, body

print('========== 封面 ==========')
f = BASE + '人教B版选必1·封面.docx'
ts, names, contents, root, body = ptexts(f)
full = '\n'.join(ts)
for kw in ['高中数学同步', '人教B版选必1', '数学', '版次：', '内部资料']:
    print(f"  要素含「{kw}」:", kw in full)
print('  五要素行摘录：', [t for t in ts if t][:8])
print('  无页眉页脚:', no_header_footer(names, contents))
print('  表格数:', len(body.findall(qn('tbl'))), '图数:', len(list(body.iter(qn('drawing')))))

for ch in ['第1章 空间向量与立体几何', '第2章 平面解析几何']:
    print(f'========== 错题记录（{ch}） ==========')
    f = BASE + f'人教B版选必1·错题记录（{ch}）.docx'
    ts, names, contents, root, body = ptexts(f)
    tbls = body.findall(qn('tbl'))
    print('  无页眉页脚:', no_header_footer(names, contents), '| 表格数:', len(tbls))
    if tbls:
        rows = tbls[0].findall(qn('tr'))
        print('  表格行数:', len(rows), '（期望42）')
        hdr = [''.join(t.text or '' for t in row.iter(qn('t'))) for row in rows[:2]]
        print('  表头+示例行:', hdr)
        # 题号列全空断言：每数据行第一单元格无文字
        empt = all(not ''.join(t.text or '' for t in row.findall(qn('tc'))[0].iter(qn('t'))).strip()
                   for row in rows[2:])
        print('  题号列全空:', empt, '| 数据空行数:', len(rows) - 2)
    # 答案用法提醒句带底纹
    hit = [p for p in body.findall(qn('p')) if '每题先独立读题动手' in ''.join(t.text or '' for t in p.iter(qn('t')))]
    ok = False
    if hit:
        r0 = [r for r in hit[0].findall(qn('r')) if r.find(qn('t')) is not None]
        ok = any((r.find(qn('rPr')) is not None and r.find(qn('rPr')).find(qn('shd')) is not None) for r in r0)
    print('  答案用法提醒句在位且带底纹:', ok)

print('========== 部分封面×6 ==========')
# 三向核对基准：文件名/册目录页/装订单
_mn, _mc = load_parts('册目录页_wip.docx')
mulu = ''.join(t.text or '' for t in etree.fromstring(_mc['word/document.xml']).iter(qn('t')))
zd = open('装订单_wip.md', encoding='utf-8').read()
EXP = {
    '第1章 空间向量与立体几何·衔接': ('29题', '衔接件（29题）'),
    '第1章 空间向量与立体几何·清单': ('47条', '知识清单（47条）'),
    '第1章 空间向量与立体几何·讲练': ('140', '讲练件（140题：简单21｜中档104｜难15）'),
    '第2章 平面解析几何·衔接': ('13题', '衔接件（13题）'),
    '第2章 平面解析几何·清单': ('67条', '知识清单（67条）'),
    '第2章 平面解析几何·讲练': ('339', '讲练件（339题：简单47｜中档246｜难46）'),
}
for key, (num, mulu_row) in EXP.items():
    f = BASE + f'人教B版选必1·部分封面（{key}）.docx'
    ts, names, contents, root, body = ptexts(f)
    full = '\n'.join(ts)
    stat = [t for t in ts if re.search(r'\d', t) and ('题' in t or '条' in t)]
    print(f'--- {key} ---')
    print('  统计行:', stat[:4])
    if '讲练' in key:
        m = re.search(r'(\d+)题', full)
        trio = re.search(r'简单(\d+)｜中档(\d+)｜难(\d+)', full)
        if m and trio:
            tot, s, z, n = int(m.group(1)), int(trio.group(1)), int(trio.group(2)), int(trio.group(3))
            print(f'  三向：统计{tot}={s}+{z}+{n}={s+z+n} →', tot == s + z + n and tot == int(num),
                  '| 册目录行在位:', mulu_row in mulu, '| 装订单行在位:', num + '题（' in zd or num + '题' in zd)
    else:
        print('  统计数字在位:', num in full, '| 册目录行在位:', mulu_row in mulu, '| 装订单题量在位:', num in zd)
    print('  无页眉页脚:', no_header_footer(names, contents))
    media = [n for n in names if n.startswith('word/media/')]
    print('  媒体文件:', media)
