# -*- coding: utf-8 -*-
"""任务A：6张部分封面复制入产出＋逐件复核（A4/pgMar850/无页眉页脚部件/全左对齐/8要素/统计口径/inline图）。"""
import zipfile, re, json, shutil, sys, os
from lxml import etree

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
WP = '{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'

SRC = r"C:/Users/28120/Desktop/提示词/工作区/同步-数学选必1版式改版-0831/T5图件生成/部分封面"
DST = r"C:/Users/28120/Desktop/提示词/高中数学/高中数学同步"

FILES = [
    "人教B版选必1·部分封面（第1章 空间向量与立体几何·衔接）.docx",
    "人教B版选必1·部分封面（第1章 空间向量与立体几何·清单）.docx",
    "人教B版选必1·部分封面（第1章 空间向量与立体几何·讲练）.docx",
    "人教B版选必1·部分封面（第2章 平面解析几何·衔接）.docx",
    "人教B版选必1·部分封面（第2章 平面解析几何·清单）.docx",
    "人教B版选必1·部分封面（第2章 平面解析几何·讲练）.docx",
]

# 统计口径台账（派发语给定）：文件名关键词 → 应含统计文本片段
STAT = {
    "第1章 空间向量与立体几何·衔接": ["29题", "全部必会"],
    "第1章 空间向量与立体几何·清单": ["47条", "33", "14"],
    "第1章 空间向量与立体几何·讲练": ["140题", "21", "104", "15"],
    "第2章 平面解析几何·衔接": ["13题", "全部必会"],
    "第2章 平面解析几何·清单": ["67条", "38", "29"],
    "第2章 平面解析几何·讲练": ["339题", "47", "246", "46"],
}

def compact(s):
    s = re.sub(r'\s+xmlns:\w+="[^"]*"', '', s)
    s = re.sub(r' w:rsid\w*="[^"]*"', '', s)
    return s

def ptext(el):
    return ''.join(t.text or '' for t in el.iter(W+'t'))

results = {}
for fn in FILES:
    key = fn.split('·部分封面（')[1].rstrip('）.docx')
    src = os.path.join(SRC, fn)
    dst = os.path.join(DST, fn)
    # 1) copy
    existed = os.path.exists(dst)
    shutil.copy2(src, dst)
    # re-read to guard sync-disk interference
    with zipfile.ZipFile(dst) as z:
        names = z.namelist()
        doc = z.read('word/document.xml')
        rels = z.read('word/_rels/document.xml.rels').decode('utf-8') if 'word/_rels/document.xml.rels' in names else ''
    root = etree.fromstring(doc)
    body = root.find(W+'body')
    checks = {}
    # A4 & pgMar
    sect = body.find(W+'sectPr')
    pgsz = sect.find(W+'pgSz'); pgmar = sect.find(W+'pgMar')
    checks['pgSz'] = (pgsz.get(W+'w'), pgsz.get(W+'h'))
    checks['pgMar'] = {k.split('}')[-1]: v for k, v in pgmar.attrib.items()}
    # header/footer parts
    hp = [n for n in names if re.match(r'word/header\d*\.xml', n)]
    fp = [n for n in names if re.match(r'word/footer\d*\.xml', n)]
    checks['headerParts'] = len(hp); checks['footerParts'] = len(fp)
    checks['headerRefs'] = doc.decode('utf-8').count('headerReference')
    checks['footerRefs'] = doc.decode('utf-8').count('footerReference')
    # paragraphs: jc left, w:ind
    paras = body.findall(W+'p')
    nonleft = 0; inds = 0; texts = []
    for p in paras:
        s = compact(etree.tostring(p, encoding='unicode'))
        jc = re.search(r'<w:jc w:val="(\w+)"/>', s)
        if not jc or jc.group(1) != 'left':
            nonleft += 1
        if '<w:ind ' in s or '<w:ind/' in s:
            inds += 1
        texts.append(ptext(p))
    checks['paraCount'] = len(paras); checks['nonLeftPara'] = nonleft; checks['indParas'] = inds
    fulltext = '\n'.join(texts)
    # 8 elements
    els = {}
    els['羿郭工作室'] = ('羿郭工作室' in fulltext)
    els['册名'] = ('人教B版选必1' in fulltext)
    els['大章号数字'] = any(re.match(r'^\s*(1|2)\s*$', t) for t in texts)
    els['章名'] = ('空间向量与立体几何' in fulltext if '第1章' in key else '平面解析几何' in fulltext)
    els['件型'] = any(('·衔接' in key and t.strip() == '衔接件') or ('·清单' in key and t.strip() == '知识清单') or ('·讲练' in key and t.strip() == '章讲练件') for t in texts)
    els['统计'] = any(re.search(r'\d+[题条]', t) for t in texts)
    els['编注导读'] = any(t.startswith('【编注】') for t in texts)
    # theme image inline
    inline = len(doc.decode('utf-8').count and [1] or []) # placeholder
    inline_count = doc.decode('utf-8').count('<wp:inline')
    anchor_count = doc.decode('utf-8').count('<wp:anchor')
    els['主题图inline'] = (inline_count >= 1 and anchor_count == 0)
    checks['inline'] = inline_count; checks['anchor'] = anchor_count
    # statistics text
    stat_texts = [t for t in texts if re.search(r'\d+[题条]', t)]
    checks['statLine'] = stat_texts
    checks['statOK'] = all(any(k in t for t in stat_texts + [fulltext]) for k in STAT[key])
    # core title
    with zipfile.ZipFile(dst) as z:
        if 'docProps/core.xml' in names:
            core = z.read('docProps/core.xml').decode('utf-8')
            m = re.search(r'<dc:title>([^<]*)</dc:title>', core)
            checks['coreTitle'] = m.group(1) if m else None
        else:
            checks['coreTitle'] = 'NO-CORE'
    results[fn] = {'existedBefore': existed, 'checks': checks, 'elements': els, 'texts': texts}

print(json.dumps(results, ensure_ascii=False, indent=1, default=str))
