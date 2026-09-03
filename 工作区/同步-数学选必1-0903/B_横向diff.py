# -*- coding: utf-8 -*-
"""B代理·十内容件横向diff：页眉页脚域结构语义等价判据＋同串文字比对＋docDefaults＋件标识/标签体系＋序列化代际登记（C恢复后重测）。
只读。输出全量登记。"""
import io, re, sys, zipfile, hashlib, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SYNC = r'C:\提示词\高中数学\高中数学同步'
CONTENT = [
    ('X1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'),
    ('I1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx'),
    ('B',  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'),
    ('C',  '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'),
    ('X2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx'),
    ('I2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'),
    ('E',  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx'),
    ('F',  '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'),
    ('G',  '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx'),
    ('H',  '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'),
]
EXPECT_START = {'X1': 1, 'I1': 1, 'B': 1, 'C': 54, 'X2': 1, 'I2': 1, 'E': 1, 'F': 50, 'G': 103, 'H': 142}

def sh(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()[:16]

def analyze_hf(xml, label, tag, part):
    """页眉/页脚域结构与显示串分析。"""
    out = {}
    out['fld_begin'] = xml.count('w:fldCharType="begin"')
    out['fld_sep'] = xml.count('w:fldCharType="separate"')
    out['fld_end'] = xml.count('w:fldCharType="end"')
    out['fldSimple'] = len(re.findall(r'<w:fldSimple\b', xml))
    out['NUMPAGES'] = ('NUMPAGES' in xml)
    instrs = re.findall(r'<w:instrText(?:\s[^>]*)?>([^<]*)</w:instrText>', xml)
    out['instr_list'] = instrs
    out['instr_join'] = ''.join(instrs)
    # 域缓存值：separate 与 end 之间的 w:t
    segs = []
    pos = 0
    while True:
        b = xml.find('w:fldCharType="separate"', pos)
        if b < 0:
            break
        e = xml.find('w:fldCharType="end"', b)
        if e < 0:
            e = len(xml)
        segs.append(''.join(re.findall(r'<w:t(?:\s[^>]*)?>([^<]*)</w:t>', xml[b:e])))
        pos = e
    out['cached_vals'] = segs
    # 显示串（全部w:t拼接，含缓存）
    disp = ''.join(re.findall(r'<w:t(?:\s[^>]*)?>([^<]*)</w:t>', xml))
    out['display'] = disp
    # 域结构语义等价判据
    pair_ok = out['fld_begin'] == out['fld_sep'] == out['fld_end'] and out['fld_begin'] >= 1
    out['pair_ok'] = pair_ok
    # instr 拼接归一（去空白）
    out['instr_norm'] = re.sub(r'\s+', '', out['instr_join'])
    return out

results = {}
for tag, fn in CONTENT:
    path = SYNC + '\\' + fn
    z = zipfile.ZipFile(path)
    names = z.namelist()
    hf = sorted(n for n in names if re.search(r'word/(header|footer)\d+\.xml$', n))
    doc = z.read('word/document.xml').decode('utf-8')
    styles = z.read('word/styles.xml').decode('utf-8')
    d = {'file': fn, 'hf_parts': []}
    for h in hf:
        raw = z.read(h)
        xml = raw.decode('utf-8')
        kind = 'header' if 'header' in h else 'footer'
        a = analyze_hf(xml, fn, tag, h)
        a['bytes'] = len(raw)
        a['sha16'] = hashlib.sha256(raw).hexdigest()[:16]
        d['hf_parts'].append({'part': h, 'kind': kind, **a})
    # docDefaults
    dd = re.search(r'<w:docDefaults>.*?</w:docDefaults>', styles, re.S)
    d['docDefaults'] = dd.group(0) if dd else ''
    rpr = re.search(r'<w:rPrDefault>(.*?)</w:rPrDefault>', d['docDefaults'], re.S)
    ppr = re.search(r'<w:pPrDefault>(.*?)</w:pPrDefault>', d['docDefaults'], re.S)
    d['rPrDefault'] = re.sub(r'\s+', '', rpr.group(1)) if rpr else ''
    d['pPrDefault'] = re.sub(r'\s+', '', ppr.group(1)) if ppr else ''
    # sectPr概览
    d['sect_count'] = len(re.findall(r'<w:sectPr\b', doc))
    d['starts'] = re.findall(r'<w:pgNumType w:start="(\d+)"', doc)
    d['cols'] = re.findall(r'<w:cols\b[^>]*?/>', doc)
    d['pgMar'] = re.findall(r'<w:pgMar\b[^>]*?/>', doc)[:2]
    # 标签体系（【×】标签种数与计数）
    tags_c = {}
    for t in re.findall(r'【([^】]{1,12})】', doc):
        tags_c[t] = tags_c.get(t, 0) + 1
    d['label_tags'] = tags_c
    # settings
    st = z.read('word/settings.xml').decode('utf-8')
    d['updateFields'] = '<w:updateFields' in st
    d['evenOdd'] = 'evenAndOddHeaders' in st
    results[tag] = d
    z.close()

print('########## 一、页眉页脚部件清单与代际登记（字节数） ##########')
print(f'{"件":4} {"部件":22} {"字节":>7}  {"sha16":18} {"begin/sep/end":14} {"fldSimple":9} {"NUMPAGES":8} 域结构')
for tag, d in results.items():
    for p in d['hf_parts']:
        gen = '5.6K代' if p['bytes'] > 4500 else ('3.3K代' if p['bytes'] > 2500 else '其他')
        print(f"{tag:4} {p['part']:22} {p['bytes']:>7}  {p['sha16']:18} {p['fld_begin']}/{p['fld_sep']}/{p['fld_end']:<6} {p['fldSimple']:<9} {str(p['NUMPAGES']):<8} {'配对OK' if p['pair_ok'] else '配对异常'} {gen}")

print()
print('########## 二、域指令与缓存值（逐件） ##########')
for tag, d in results.items():
    for p in d['hf_parts']:
        print(f"[{tag}·{p['part']}]")
        print(f"  instrText段={p['instr_list']}")
        print(f"  instr拼接（归一）={p['instr_norm']}")
        print(f"  缓存值={p['cached_vals']}")
        print(f"  显示串={p['display']}")

print()
print('########## 三、同串文字结构比对（显示串骨架归一） ##########')
def skeleton(disp, tag):
    """归一：件型段/共N页/本n/共M/页码数字/节名段视为变量。"""
    s = disp
    s = re.sub(r'（共\d+页）', '（共N页）', s)
    s = re.sub(r'·本\d+/共\d+本', '·本n/共M本', s)
    s = re.sub(r'第\d+页', '第X页', s)
    return s
skels = {}
for tag, d in results.items():
    for p in d['hf_parts']:
        skels[(tag, p['part'], p['kind'])] = skeleton(p['display'], tag)
# 逐件列出，比较骨架（人工判读变量段外一致性）
for (tag, part, kind), s in skels.items():
    print(f'{tag} {part}: {s}')

print()
print('########## 四、docDefaults 十件比对 ##########')
ref = None
for tag, d in results.items():
    key = (d['rPrDefault'], d['pPrDefault'])
    if ref is None:
        ref = key
        print(f'基准（{tag}）：rPrDefault={d["rPrDefault"]}')
        print(f'          pPrDefault={d["pPrDefault"]}')
    else:
        same = key == ref
        print(f'{tag}: rPrDefault同基准={d["rPrDefault"]==ref[0]} pPrDefault同基准={d["pPrDefault"]==ref[1]}' + ('' if same else '  ←差异!'))

print()
print('########## 五、件标识与标签体系 ##########')
for tag, d in results.items():
    tags_c = d['label_tags']
    print(f'[{tag}] 标签种类={len(tags_c)} 标签计数={sum(tags_c.values())}')
    print(f'   标签集：{sorted(tags_c.keys())}')
print()
print('件标识（页眉显示串内「第X章·件型」段提取）：')
for tag, d in results.items():
    for p in d['hf_parts']:
        if p['kind'] == 'header':
            m = re.search(r'(第[12]章·[^（\s　]+)', p['display'])
            print(f'  {tag}: {m.group(1) if m else "(未提取到)"} | 完整串首段：{p["display"][:60]}')

print()
print('########## 六、sectPr/页码start/settings 复核 ##########')
for tag, d in results.items():
    ok = [int(s) for s in d['starts']] == [EXPECT_START[tag]] if len(d['starts']) == 1 else False
    print(f'{tag}: sectPr={d["sect_count"]} starts={d["starts"]} 期望={EXPECT_START[tag]} {"PASS" if ok else "红旗"} updateFields={d["updateFields"]} evenOdd={d["evenOdd"]} cols={len(d["cols"])}节')
    for m in d['cols']:
        print(f'    {m}')

with open(r'C:\提示词\工作区\同步-数学选必1-0903\B_横向diff_数据.json', 'w', encoding='utf-8') as f:
    json.dump({k: {kk: vv for kk, vv in v.items() if kk != 'docDefaults'} for k, v in results.items()},
              f, ensure_ascii=False, indent=1, default=str)
print()
print('数据已落盘 B_横向diff_数据.json')
