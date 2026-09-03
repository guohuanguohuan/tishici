# -*- coding: utf-8 -*-
"""B代理·补充：docDefaults语义级比对（属性序无关）＋二级节标题证据＋错题残留扫描＋装订单恒等式复算。只读。"""
import io, re, sys, zipfile, os, xml.etree.ElementTree as ET
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SYNC = r'C:\提示词\高中数学\高中数学同步'
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
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

def sem(xmlelem):
    """元素→语义元组（tag+属性字典+子元素递归，属性序无关）。"""
    if xmlelem is None:
        return None
    return (xmlelem.tag.split('}')[1],
            {k.split('}')[1]: v for k, v in xmlelem.attrib.items()},
            [sem(c) for c in xmlelem])

print('########## A、docDefaults 语义级比对 ##########')
base = None
for tag, fn in CONTENT:
    z = zipfile.ZipFile(SYNC + '\\' + fn)
    styles = z.read('word/styles.xml').decode('utf-8')
    z.close()
    root = ET.fromstring(styles.encode('utf-8'))
    dd = root.find(f'{W}docDefaults')
    rpr = sem(dd.find(f'{W}rPrDefault')) if dd is not None else None
    ppr = sem(dd.find(f'{W}pPrDefault')) if dd is not None else None
    if base is None:
        base = (rpr, ppr)
        print(f'基准[{tag}] rPrDefault语义：{rpr}')
        print(f'        pPrDefault语义：{ppr}')
    else:
        rs, ps = (rpr == base[0]), (ppr == base[1])
        mark = 'PASS' if (rs and ps) else '差异'
        print(f'{tag}: rPrDefault同基准={rs} pPrDefault同基准={ps} → {mark}')
        if not rs:
            print(f'   实测rPrDefault：{rpr}')
        if not ps:
            print(f'   实测pPrDefault：{ppr}')

print()
print('########## B、二级节标题证据（标题3/ADC2DA、无统计段要求） ##########')
for tag, fn in CONTENT:
    z = zipfile.ZipFile(SYNC + '\\' + fn)
    doc = z.read('word/document.xml').decode('utf-8')
    z.close()
    body = re.sub(r'<w:tbl>.*?</w:tbl>', '', doc, flags=re.S)
    pps = re.findall(r'<w:p\b[^>]*>.*?</w:p>', body, re.S)
    hits = []
    for pi, p in enumerate(pps):
        t = ''.join(re.findall(r'<w:t(?:\s[^>]*)?>([^<]*)</w:t>', p)).strip()
        m = re.match(r'^(\d+\.\d+)(?:\.\d+)?\s', t)
        if not m:
            continue
        sty3 = ('标题3' in p or 'Heading3' in p or 'w:val="3"' in p)
        fill = re.search(r'w:fill="ADC2DA"', p)
        if sty3 or fill:
            hits.append((m.group(1) if '.' in m.group(1) else t[:12], t[:46], int(bool(fill))))
    print(f'[{tag}] 节标题（标题3/ADC2DA）共{len(hits)}：')
    for no, t, f in hits:
        print(f'    {no:8} ADC2DA={f} {t}')

print()
print('########## C、错题残留扫描 ##########')
print('① 主目录文件名含「错题」：')
found = 0
for fn in os.listdir(SYNC):
    if '错题' in fn:
        print(f'   红旗：{fn}')
        found += 1
print(f'   计数={found}' + ('（PASS：零残留）' if found == 0 else ''))
print('② 旧体系存档内含「错题」（存档件不属残留、仅登记）：')
old = os.path.join(SYNC, '旧体系存档')
if os.path.isdir(old):
    hits = [fn for fn in os.listdir(old) if '错题' in fn]
    print(f'   计数={len(hits)}：{hits}')
print('③ 全同步文件夹递归搜「错题」（文件名级）：')
for root_dir, dirs, files in os.walk(SYNC):
    for fn in files:
        if '错题' in fn:
            print(f'   {os.path.join(root_dir, fn)}')
print('④ 装订单.md「错题」句grep：')
with open(SYNC + r'\人教B版选必1·装订单.md', encoding='utf-8') as f:
    for ln in f:
        if '错题' in ln:
            print(f'   |{ln.strip()}')
print('⑤ 使用说明.docx「错题」句grep：')
z = zipfile.ZipFile(SYNC + r'\人教B版选必1·使用说明.docx')
doc = z.read('word/document.xml').decode('utf-8')
z.close()
for p in re.findall(r'<w:p\b[^>]*>.*?</w:p>', doc, re.S):
    t = ''.join(re.findall(r'<w:t(?:\s[^>]*)?>([^<]*)</w:t>', p))
    if '错题' in t:
        print(f'   |{t}')
print('⑥ 封面/册目录页/部分封面×6「错题」grep：')
for fn in ['人教B版选必1·封面.docx', '人教B版选必1·册目录页.docx'] + \
          [f for f in os.listdir(SYNC) if '部分封面' in f]:
    z = zipfile.ZipFile(SYNC + '\\' + fn)
    d = z.read('word/document.xml').decode('utf-8')
    z.close()
    if '错题' in d:
        print(f'   红旗：{fn} 含「错题」')
print('   （未列出＝不含）')

print()
print('########## D、装订单恒等式复算 ##########')
pages = {'X1': 16, 'I1': 14, 'B': 53, 'C': 61, 'X2': 6, 'I2': 28, 'E': 49, 'F': 53, 'G': 39, 'H': 64}
starts = {'X1': 1, 'I1': 1, 'B': 1, 'C': 54, 'X2': 1, 'I2': 1, 'E': 1, 'F': 50, 'G': 103, 'H': 142}
ben = {'本1': ['X1'], '本2': ['I1'], '本3': ['B', 'C'], '本4': ['X2'], '本5': ['I2'], '本6': ['E', 'F', 'G', 'H']}
total = 0
for b, tags in ben.items():
    s = sum(pages[t] for t in tags)
    total += s
    # 区间闭合：start[i] = start[i-1]+pages[i-1]（同部分内）
    ok_chain = True
    for i in range(1, len(tags)):
        if starts[tags[i]] != starts[tags[i-1]] + pages[tags[i-1]]:
            ok_chain = False
    # 区间末=Σpages
    end = starts[tags[-1]] + pages[tags[-1]] - 1
    print(f'{b}：{"+".join(str(pages[t]) for t in tags)}={s}页 {"≤400 PASS" if s <= 400 else "红旗"} 首件start={starts[tags[0]]} 末页={end} 链闭合={ok_chain}')
print(f'合计={total}（期望383：{"PASS" if total == 383 else "红旗"}）')
print(f'N值复核：P3={pages["B"]+pages["C"]}(期望114) P6={pages["E"]+pages["F"]+pages["G"]+pages["H"]}(期望205)')
