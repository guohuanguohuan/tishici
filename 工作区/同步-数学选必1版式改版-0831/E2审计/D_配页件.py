# -*- coding: utf-8 -*-
"""E2任务D：配页件抽验（只读）。封面/使用说明/错题×2/部分封面×6/册目录页 XML层复测。"""
import zipfile, re, sys, io, os, json
from lxml import etree
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}
ROOT = r'C:\Users\28120\Desktop\提示词\高中数学\高中数学同步'
HERE = os.path.dirname(os.path.abspath(__file__))
out = {}

def load(fn):
    z = zipfile.ZipFile(os.path.join(ROOT, fn))
    doc = etree.fromstring(z.read('word/document.xml'))
    parts = {n: z.read(n) for n in z.namelist()}
    return z, doc, parts

def base_checks(doc, parts, z):
    r = {}
    s = doc.find('.//w:sectPr', NS)
    pg = s.find('w:pgSz', NS); mar = s.find('w:pgMar', NS)
    r['pgSz'] = (pg.get(f'{{{W}}}w'), pg.get(f'{{{W}}}h'))
    r['pgMar'] = {k.split('}')[1]: v for k, v in mar.attrib.items()} if mar is not None else None
    r['headerParts'] = [n for n in z.namelist() if re.match(r'word/header\d*\.xml$', n)]
    r['footerParts'] = [n for n in z.namelist() if re.match(r'word/footer\d*\.xml$', n)]
    xml = etree.tostring(doc, encoding='unicode')
    r['headerRefs'] = xml.count('headerReference')
    r['footerRefs'] = xml.count('footerReference')
    # 非左对齐段
    nonleft = 0
    for p in doc.findall('.//w:p', NS):
        jc = p.find('w:pPr/w:jc', NS)
        if jc is not None and jc.get(f'{{{W}}}val') != 'left':
            nonleft += 1
    r['nonleft_paras'] = nonleft
    r['w_ind_nonzero'] = sum(1 for i in doc.iter(f'{{{W}}}ind')
                             if (i.get(f'{{{W}}}left') not in (None, '0')
                                 or i.get(f'{{{W}}}firstLine') not in (None, '0')
                                 or i.get(f'{{{W}}}hanging') not in (None, '0')))
    st = etree.fromstring(parts['word/settings.xml'])
    r['updateFields'] = st.find('w:updateFields', NS) is not None
    core = parts.get('docProps/core.xml')
    if core:
        c = etree.fromstring(core)
        dc = '{http://purl.org/dc/elements/1.1/}title'
        r['core_title'] = c.findtext(dc)
    return r

# ---------- 1 封面 ----------
z, doc, parts = load('人教B版选必1·封面.docx')
r = base_checks(doc, parts, z)
full = ''.join(doc.itertext())
r['五要素'] = {k: (k in full) for k in ['高中同步讲练', '人教B版选必1', '数　学', '版次：2026年08月', '内部资料·仅供教学使用']}
r['段数'] = len(doc.findall('.//w:p', NS))
out['封面'] = r
print('封面:', json.dumps(r, ensure_ascii=False)[:400])

# ---------- 2 使用说明 ----------
z, doc, parts = load('人教B版选必1·使用说明.docx')
r = base_checks(doc, parts, z)
full = ''.join(doc.itertext())
r['三要素关键词'] = {k: (k in full) for k in
    ['题号难度块' if '题号难度块' in full else '（档位·提分线·卡壳看答案）',
     '卡壳超过10分钟', '遮住答案重做', '装订组合', '方案A', '方案B', '方案C',
     '〔基〕＝基础必会', '〔进〕＝进阶汇总', '衔接件', '部分封面']}
r['段数'] = len(doc.findall('.//w:p', NS))
# 图例区式样与B/I1同构：题号块run/节标题段/答案值run
def find_run(doc, txt):
    for p in doc.iter(f'{{{W}}}p'):
        for rn in p.findall(f'{{{W}}}r'):
            t = rn.find(f'{{{W}}}t')
            if t is not None and t.text and txt in t.text:
                rpr = rn.find(f'{{{W}}}rPr', NS)
                shd = rpr.find(f'{{{W}}}shd') if rpr is not None else None
                col = rpr.find(f'{{{W}}}color') if rpr is not None else None
                sz = rpr.find(f'{{{W}}}sz') if rpr is not None else None
                return {'text': t.text[:20], 'shd': shd.get(f'{{{W}}}fill') if shd is not None else None,
                        'color': col.get(f'{{{W}}}val') if col is not None else None,
                        'sz': sz.get(f'{{{W}}}val') if sz is not None else None,
                        'b': rpr is not None and rpr.find(f'{{{W}}}b', NS) is not None}
    return None
r['式样_题号块1．'] = find_run(doc, '1．')
r['式样_答案值'] = find_run(doc, '（简单·保60%·卡壳看答案）') or find_run(doc, '保60%')
# 定理框 pBdr
r['pBdr段数'] = sum(1 for p in doc.findall('.//w:p', NS) if p.find('w:pPr/w:pBdr', NS) is not None)
out['使用说明'] = r
print('使用说明:', json.dumps(r, ensure_ascii=False)[:600])

# ---------- 3 错题×2 ----------
for tag, fn in [('错题1', '人教B版选必1·错题记录（第1章 空间向量与立体几何）.docx'),
                ('错题2', '人教B版选必1·错题记录（第2章 平面解析几何）.docx')]:
    z, doc, parts = load(fn)
    r = base_checks(doc, parts, z)
    full = ''.join(doc.itertext())
    tbl = doc.find('.//w:tbl', NS)
    rows = tbl.findall('w:tr', NS) if tbl is not None else []
    r['表头'] = [ ''.join(tc.itertext()).strip() for tc in (rows[0].findall('w:tc', NS) if rows else []) ]
    empty_rows = 0; qcol_nonempty = 0
    for tr in rows[1:]:
        tcs = tr.findall('w:tc', NS)
        if len(tcs) == 3 and not ''.join(tcs[0].itertext()).strip():
            empty_rows += 1
        if len(tcs) >= 1 and ''.join(tcs[0].itertext()).strip():
            qcol_nonempty += 1
    r['空行数(题号列空)'] = empty_rows
    r['题号列非空行'] = qcol_nonempty
    r['示例行'] = '知识不会／方法没想到／计算错／审题错' in full or '知识不会' in full
    # 提醒句底纹
    rem = None
    for p in doc.findall('.//w:p', NS):
        if '卡壳超过10分钟' in ''.join(p.itertext()):
            shds = [s.get(f'{{{W}}}fill') for s in p.iter(f'{{{W}}}shd')]
            rem = shds
    r['提醒句底纹'] = rem
    r['表格行总数'] = len(rows)
    out[tag] = r
    print(tag, ':', json.dumps(r, ensure_ascii=False)[:450])

# ---------- 4 部分封面×6 ----------
for fn in ['人教B版选必1·部分封面（第1章 空间向量与立体几何·衔接）.docx',
           '人教B版选必1·部分封面（第1章 空间向量与立体几何·清单）.docx',
           '人教B版选必1·部分封面（第1章 空间向量与立体几何·讲练）.docx',
           '人教B版选必1·部分封面（第2章 平面解析几何·衔接）.docx',
           '人教B版选必1·部分封面（第2章 平面解析几何·清单）.docx',
           '人教B版选必1·部分封面（第2章 平面解析几何·讲练）.docx']:
    z, doc, parts = load(fn)
    r = base_checks(doc, parts, z)
    full = ''.join(doc.itertext())
    key = fn.split('（')[1].rstrip('）')
    r['要素'] = {k: (k in full) for k in ['羿郭工作室', '人教B版选必1', '衔接', '清单', '讲练',
                                          '【编注】', '题', '条']}
    r['大章号'] = bool(re.search(r'(?<![\d])\d(?![\d])', full))
    r['inline图'] = etree.tostring(doc, encoding='unicode').count('<wp:inline')
    r['anchor'] = etree.tostring(doc, encoding='unicode').count('<wp:anchor')
    # 统计行原文
    m = re.search(r'(衔接\d+题[^。\n]*|\d+条〔基\d+·进\d+〕|\d+题：简单\d+｜中档\d+｜难\d+)', full)
    r['统计行'] = m.group(1) if m else None
    out['部分封面_' + key] = r
    print('部分封面', key, ':', json.dumps({'统计行': r['统计行'], 'pgSz': r['pgSz'],
        'hdr': len(r['headerParts']), 'ftr': len(r['footerParts']), 'refs': r['headerRefs'] + r['footerRefs'],
        'nonleft': r['nonleft_paras'], 'ind': r['w_ind_nonzero'], 'inline': r['inline图'], 'anchor': r['anchor']}, ensure_ascii=False))

# ---------- 5 册目录页 ----------
z, doc, parts = load('人教B版选必1·册目录页.docx')
r = base_checks(doc, parts, z)
rows = []
for p in doc.findall('.//w:p', NS):
    t = ''.join(p.itertext()).strip()
    ind = p.find('w:pPr/w:ind', NS)
    indl = ind.get(f'{{{W}}}left') if ind is not None else None
    rows.append((t[:34], indl))
r['段数'] = len(rows)
r['缩进分布'] = {}
for t, indl in rows:
    if t:
        r['缩进分布'][str(indl)] = r['缩进分布'].get(str(indl), 0) + 1
r['树行'] = [(t, l) for t, l in rows if t]
# 页码列抽取：行尾数字
r['页码列'] = [m.group(1) for t, l in r['树行'] if (m := re.search(r'(\d+)\s*$', t))]
r['assert_缩进420'] = r['缩进分布'].get('420', 0)
r['assert_缩进840'] = r['缩进分布'].get('840', 0)
out['册目录页'] = {k: v for k, v in r.items() if k != '树行'}
print('册目录页:', json.dumps(out['册目录页'], ensure_ascii=False)[:500])
with open(os.path.join(HERE, 'D_配页件.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
with open(os.path.join(HERE, 'D_册目录树.txt'), 'w', encoding='utf-8') as f:
    for t, l in r['树行']:
        f.write(f'{l}\t{t}\n')
print('saved D_配页件.json / D_册目录树.txt')
