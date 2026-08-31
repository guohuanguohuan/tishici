# -*- coding: utf-8 -*-
"""任务A复核（重派轮）：6张部分封面在产出文件夹内的逐件复核。
件型检查修正：按T5产件设计（§11 N9＋T5报告§5），件型段落文本＝「衔接/清单/讲练」短形态。
检查项：A4、pgMar850、header/footer部件=0、全左对齐、w:ind=0、8要素、统计口径、inline主题图、core title。"""
import zipfile, re, json, os
from lxml import etree

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
DST = r"C:/Users/28120/Desktop/提示词/高中数学/高中数学同步"
SRC = r"C:/Users/28120/Desktop/提示词/工作区/同步-数学选必1版式改版-0831/T5图件生成/部分封面"

FILES = [
    "人教B版选必1·部分封面（第1章 空间向量与立体几何·衔接）.docx",
    "人教B版选必1·部分封面（第1章 空间向量与立体几何·清单）.docx",
    "人教B版选必1·部分封面（第1章 空间向量与立体几何·讲练）.docx",
    "人教B版选必1·部分封面（第2章 平面解析几何·衔接）.docx",
    "人教B版选必1·部分封面（第2章 平面解析几何·清单）.docx",
    "人教B版选必1·部分封面（第2章 平面解析几何·讲练）.docx",
]
# 统计口径台账（派发语给定）
STAT = {
    "第1章 空间向量与立体几何·衔接": ["29题", "必会"],
    "第1章 空间向量与立体几何·清单": ["47条", "33", "14"],
    "第1章 空间向量与立体几何·讲练": ["140题", "21", "104", "15"],
    "第2章 平面解析几何·衔接": ["13题", "必会"],
    "第2章 平面解析几何·清单": ["67条", "38", "29"],
    "第2章 平面解析几何·讲练": ["339题", "47", "246", "46"],
}
# 件型短形态（与T5产件、页脚件标识体系同源）
TYPE_SHORT = {"衔接": "衔接", "清单": "清单", "讲练": "讲练"}

results = {}
for fn in FILES:
    key = fn.split('·部分封面（')[1].rstrip('）.docx')
    parts = key.split('·')
    jianxing = parts[1]
    dst = os.path.join(DST, fn)
    with zipfile.ZipFile(dst) as z:
        names = z.namelist()
        docb = z.read('word/document.xml')
        docstr = docb.decode('utf-8')
    root = etree.fromstring(docb)
    body = root.find(W+'body')
    sect = body.find(W+'sectPr')
    pgsz = sect.find(W+'pgSz'); pgmar = sect.find(W+'pgMar')
    c = {}
    c['pgSz'] = [pgsz.get(W+'w'), pgsz.get(W+'h')]
    c['pgMar'] = {k.split('}')[-1]: v for k, v in pgmar.attrib.items()}
    hp = [n for n in names if re.match(r'word/header\d*\.xml', n)]
    fp = [n for n in names if re.match(r'word/footer\d*\.xml', n)]
    c['headerParts'] = len(hp); c['footerParts'] = len(fp)
    c['headerRefs'] = docstr.count('headerReference'); c['footerRefs'] = docstr.count('footerReference')
    paras = body.findall(W+'p')
    nonleft = inds = 0; texts = []
    for p in paras:
        s = etree.tostring(p, encoding='unicode')
        jc = re.search(r'<w:jc w:val="(\w+)"/>', s)
        if not jc or jc.group(1) != 'left': nonleft += 1
        if '<w:ind ' in s or '<w:ind/>' in s: inds += 1
        texts.append(''.join(t.text or '' for t in p.iter(W+'t')))
    c['paraCount'] = len(paras); c['nonLeftPara'] = nonleft; c['indParas'] = inds
    fulltext = '\n'.join(texts)
    els = {}
    els['羿郭工作室'] = '羿郭工作室' in fulltext
    els['册名'] = '人教B版选必1' in fulltext
    els['大章号数字'] = any(re.match(r'^\s*(1|2)\s*$', t) for t in texts)
    els['章名'] = ('空间向量与立体几何' in fulltext if '第1章' in key else '平面解析几何' in fulltext)
    # 件型：短形态独立段落（与文件名括注件型一致）
    els['件型'] = any(t.strip() == jianxing for t in texts)
    els['统计'] = any(re.search(r'\d+[题条]', t) for t in texts)
    els['编注导读'] = any(t.startswith('【编注】') for t in texts)
    c['inline'] = docstr.count('<wp:inline'); c['anchor'] = docstr.count('<wp:anchor')
    els['主题图inline'] = (c['inline'] >= 1 and c['anchor'] == 0)
    stat_texts = [t for t in texts if re.search(r'\d+[题条]', t) or '必会' in t]
    c['statLine'] = stat_texts
    c['statOK'] = all(any(k in t for t in stat_texts + [fulltext]) for k in STAT[key])
    with zipfile.ZipFile(dst) as z:
        core = z.read('docProps/core.xml').decode('utf-8') if 'docProps/core.xml' in names else ''
    m = re.search(r'<dc:title>([^<]*)</dc:title>', core)
    c['coreTitle'] = m.group(1) if m else None
    c['coreTitleOK'] = c['coreTitle'] == fn[:-5]
    # 汇总判定
    ok = (c['pgSz'] == ['11906', '16838']
          and all(c['pgMar'].get(k) == '850' for k in ('top', 'right', 'bottom', 'left'))
          and c['headerParts'] == 0 and c['footerParts'] == 0
          and c['headerRefs'] == 0 and c['footerRefs'] == 0
          and nonleft == 0 and inds == 0
          and all(els.values()) and c['statOK'] and c['coreTitleOK'])
    results[fn] = {'key': key, 'checks': c, 'elements': els, 'ALL_OK': ok}

print(json.dumps(results, ensure_ascii=False, indent=1))
