# -*- coding: utf-8 -*-
"""B代理·册目录页目录树提取＋内容件start/节标题/统计段核对（三向同源）。
只读。输出目录树逐行＋内容件节标题与统计段实测。"""
import io, re, sys, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SYNC = r'C:\提示词\高中数学\高中数学同步'
CONTENT = {
    'X1': '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    'I1': '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    'B':  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'C':  '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    'X2': '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
    'I2': '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    'E':  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    'F':  '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    'G':  '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    'H':  '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}
SEC_RE = re.compile(r'^(\d+\.\d+(?:\.\d+)?)[\s\u3000]+(.+?)'
                    r'(?:（第(\d+)[—–\-](\d+)题）)?(?:[\s\u3000]+本节(\d+)题[：:]([^：]*?))?[\s\u3000]*$')
STATS_RE = re.compile(r'[\s\u3000]本节\d+题')

def runs_text(p):
    return ''.join(re.findall(r'<w:t(?:\s[^>]*)?>([^<]*)</w:t>', p))

print('########## 一、册目录页目录树逐行提取 ##########')
z = zipfile.ZipFile(SYNC + r'\人教B版选必1·册目录页.docx')
doc = z.read('word/document.xml').decode('utf-8')
paras = re.findall(r'<w:p\b[^>]*>.*?</w:p>', doc, re.S)
toc_rows = []
for i, p in enumerate(paras):
    txt = runs_text(p)
    if not txt.strip():
        continue
    ind = re.search(r'<w:ind\b([^>]*)/>', p)
    indv = dict(re.findall(r'w:(\w+)="(-?\d+)"', ind.group(1))) if ind else {}
    shd = re.search(r'<w:shd\b[^>]*/>', p)
    fill = re.search(r'w:fill="([0-9A-Fa-f]{6})"', shd.group(0)) if shd else None
    bold = '<w:b/>' in p or '<w:b ' in p
    tabs = re.findall(r'<w:tab w:val="([^"]+)"(?:[^>]*)/>', p)
    leader = re.findall(r'w:leader="([^"]+)"', p)
    szs = set(re.findall(r'<w:sz w:val="(\d+)"/>', p))
    print(f'p{i:02d} ind_left={indv.get("left","-"):>5} ind_firstLine={indv.get("firstLine","-"):>5} fill={fill.group(1) if fill else "-":>6} bold={int(bold)} sz={sorted(szs)} tab={tabs} lead={leader}')
    print(f'     文字：{txt}')
    # 页码=行尾数字
    m = re.search(r'(\d+)\s*$', txt)
    toc_rows.append({'idx': i, 'text': txt, 'page': int(m.group(1)) if m else None,
                     'ind': int(indv.get('left', 0)) or int(indv.get('firstLine', 0)),
                     'fill': fill.group(1) if fill else None, 'bold': bold})
z.close()

print()
print('########## 二、内容件实测：start/pgSz/节标题/统计段 ##########')
measured = {}
for tag, fn in CONTENT.items():
    path = SYNC + '\\' + fn
    zz = zipfile.ZipFile(path)
    d = zz.read('word/document.xml').decode('utf-8')
    starts = re.findall(r'<w:pgNumType w:start="(\d+)"\s*/>', d)
    if not starts:
        starts = re.findall(r'<w:pgNumType\s+w:start="(\d+)"', d)
    hdr_ref = len(re.findall(r'<w:headerReference\b', d))
    ftr_ref = len(re.findall(r'<w:footerReference\b', d))
    # 段落级扫描（跳过表格内段落——按<w:tbl>剔除）
    body = re.sub(r'<w:tbl>.*?</w:tbl>', '', d, flags=re.S)
    pps = re.findall(r'<w:p\b[^>]*>.*?</w:p>', body, re.S)
    secs, stat_line = [], None
    for p in pps:
        t = runs_text(p).strip()
        if not t:
            continue
        m = SEC_RE.match(t)
        if m and (m.group(3) or STATS_RE.search(t)):
            shdp = re.search(r'<w:shd[^>]*w:fill="([0-9A-Fa-f]{6})"', p)
            secs.append((m.group(1), t[:60], shdp.group(1) if shdp else None))
        if t.startswith('全件') and '题' in t:
            stat_line = t
    measured[tag] = {'file': fn, 'start': starts[0] if starts else None,
                     'hdr_ref': hdr_ref, 'ftr_ref': ftr_ref, 'secs': secs, 'stat': stat_line}
    print(f'【{tag}】{fn}')
    print(f'  pgNumType start={starts} headerReference={hdr_ref} footerReference={ftr_ref}')
    print(f'  全件统计行：{stat_line}')
    print(f'  节标题（双签名，表外，同节号首现）共{len(secs)}个：')
    for no, t, fill in secs:
        print(f'    {no:8} 底纹={fill or "-"}  {t}')
    zz.close()

import json
with open(r'C:\提示词\工作区\同步-数学选必1-0903\B_册目录核对_数据.json', 'w', encoding='utf-8') as f:
    json.dump({'toc': toc_rows, 'measured': {k: {kk: vv for kk, vv in v.items()} for k, v in measured.items()}},
              f, ensure_ascii=False, indent=1)
print()
print('数据已落盘 B_册目录核对_数据.json')
