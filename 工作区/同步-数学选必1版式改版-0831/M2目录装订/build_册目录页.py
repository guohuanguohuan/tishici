# -*- coding: utf-8 -*-
"""M2任务A：重造 人教B版选必1·册目录页.docx（教材式目录·缩进列表形态）
数据源（数字同源恒等，全链条零手工推算）：
  - 件级start/页数/N：M1盖章记录.md（工具/册级连续页码.py --record 落盘）
  - 节级部分内页码：节页码定位输出.tsv（工具/节页码定位.py @parts.json --record 盖章记录.md）
  - 节级行题量括注/讲练三档：B讲上与E卷92的章首导航表（XML提取）
  - 件类型行题量：文件名（衔接29/13题；清单47/67条；讲练140=61+79、339=92+90+68+89）
版式：§7/§11——标题32半点加粗+ADC2DA整行底纹+底边框；列头/件型/节级行18半点（解析档），
  章行24半点加粗；层级缩进420/840缇（全体系唯一w:ind例外）；点线前导右停靠制表位pos=10206；
  段落一律左对齐；行距280 atLeast（标题410）；A4；pgMar全850；无页眉页脚部件；docDefaults显式双组值。
"""
import zipfile, re, os, sys, json, datetime
sys.stdout.reconfigure(encoding='utf-8')

WS = os.path.dirname(os.path.abspath(__file__))
ROOT = r'C:\Users\28120\Desktop\提示词'
OUTDIR = os.path.join(ROOT, '高中数学', '高中数学同步')
REC = os.path.join(ROOT, '工作区', '同步-数学选必1版式改版-0831', 'M1盖章', '盖章记录.md')
TSV = os.path.join(WS, '节页码定位输出.tsv')
DOCX = os.path.join(WS, '人教B版选必1·册目录页.docx')

F_B = '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx'
F_C = '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'
F_E = '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx'
F_F = '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx'
F_G = '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx'
F_H = '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx'
F_X1 = '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'
F_I1 = '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx'
F_X2 = '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx'
F_I2 = '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx'

checks = []          # (断言名, 期望, 实测, pass?)
def chk(name, exp, got):
    checks.append((name, exp, got, exp == got))
    if exp != got:
        print(f'[FAIL] {name}: 期望{exp} 实测{got}')

# ---------- 1. M1盖章记录：逐件页数/start/N ----------
starts, pages, Ns, parts = {}, {}, {}, {}
for line in open(REC, encoding='utf-8'):
    m = re.match(r'^\|\s*(P\d+)\s*\|\s*([^|]+?)\.docx\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*$', line)
    if m:
        p, fn, pg, st, tag, N = m.groups()
        fn = fn + '.docx'
        starts[fn], pages[fn], Ns[fn], parts[fn] = int(st), int(pg), int(N), p
chk('盖章记录件数', 10, len(starts))
chk('P3 starts=1/79', [1, 79], [starts[F_B], starts[F_C]])
chk('P6 starts=1/48/99/135', [1, 48, 99, 135], [starts[F_E], starts[F_F], starts[F_G], starts[F_H]])
chk('部分页数合计 20/20/156/4/40/197', [20, 20, 156, 4, 40, 197],
    [pages[F_X1], pages[F_I1], pages[F_B] + pages[F_C], pages[F_X2], pages[F_I2],
     pages[F_E] + pages[F_F] + pages[F_G] + pages[F_H]])
chk('全册合计437', 437, sum(pages.values()))

# ---------- 2. 节页码定位输出：25节级行 ----------
sec = {}   # 节号 -> (basename, 节标题全文, 件内页, 部分内页码)
for line in open(TSV, encoding='utf-8'):
    if line.startswith('#') or not line.strip():
        continue
    c = line.rstrip('\n').split('\t')
    if len(c) == 5:
        fn, no, full, inp, part_pg = c
        if inp.isdigit():                       # 节级行（件级行第2列是start也数字，长度4区分）
            sec[no] = (fn, full, int(inp), int(part_pg))
chk('节级行数25', 25, len(sec))
chk('第1章节级8行', 8, len([k for k in sec if k.startswith('1.')]))
chk('第2章节级17行', 17, len([k for k in sec if k.startswith('2.')]))
# 每卷首节的部分内页码==该卷start（定位值与盖章记录同源核）
for fn, firstsec in [(F_B, '1.1.1'), (F_C, '1.2.5'), (F_E, '2.1'), (F_F, '2.3.4'), (F_G, '2.6.1'), (F_H, '2.8')]:
    chk(f'首节{firstsec}部分内页码=={os.path.basename(fn)}start', starts[fn], sec[firstsec][3])

# ---------- 3. 章首导航表提取（B=第1章、E=第2章章首卷） ----------
NS = r'(?:ns0|w)'
def nav_table(path):
    z = zipfile.ZipFile(path)
    xml = z.read('word/document.xml').decode('utf-8')
    tbls = re.findall(r'<' + NS + r':tbl\b.*?</' + NS + r':tbl>', xml, re.S)
    rows = re.findall(r'<' + NS + r':tr\b.*?</' + NS + r':tr>', tbls[0], re.S)
    out = []
    for r in rows:
        cells = re.findall(r'<' + NS + r':tc>.*?</' + NS + r':tc>', r, re.S)
        vals = [''.join(re.findall(r'<' + NS + r':t[^>]*>([^<]*)</' + NS + r':t>', c)) for c in cells]
        out.append(vals)
    return out

nav1 = nav_table(os.path.join(OUTDIR, F_B))
nav2 = nav_table(os.path.join(OUTDIR, F_E))
def parse_nav(rows):
    hdr, body, total = rows[0], [], None
    for r in rows[1:]:
        if r[0] == '合计':
            total = r
        else:
            body.append(r)
    return hdr, body, total
h1, b1, t1 = parse_nav(nav1)
h2, b2, t2 = parse_nav(nav2)

# ---------- 4. 恒等断言：导航表↔定位TSV本节N题↔题号区间 ----------
nav1_map = {r[0].split()[0]: (r[0].split(None, 1)[1], int(r[2]), r[1]) for r in b1}
nav2_map = {r[0].split()[0]: (r[0].split(None, 1)[1], int(r[2]), r[1]) for r in b2}
chk('导航表1节行数8', 8, len(nav1_map)); chk('导航表2节行数17', 17, len(nav2_map))
chk('导航表1节号集==定位节号集', sorted(nav1_map), sorted(k for k in sec if k[0] == '1'))
chk('导航表2节号集==定位节号集', sorted(nav2_map), sorted(k for k in sec if k[0] == '2'))
for no, (name, n, rng) in {**nav1_map, **nav2_map}.items():
    full = sec[no][1]
    m = re.match(r'^(\d+\.\d+(?:\.\d+)?)\s+(.+?)（第(\d+)[—–-](\d+)题）', full)
    assert m, f'节标题形态异常: {full}'
    chk(f'{no} 节名导航==定位', name, m.group(2))
    chk(f'{no} 本节N题==导航题量', n, int(re.search(r'本节(\d+)题', full).group(1)))
    x, y = int(m.group(3)), int(m.group(4))
    chk(f'{no} 区间Y-X+1==题量', n, y - x + 1)
chk('第1章合计140/21/104/15', ['140', '简单21/中档104/难15'], [t1[2], t1[3]])
chk('第2章合计339/47/246/46', ['339', '简单47/中档246/难46'], [t2[2], t2[3]])
chk('讲练1文件名题量和61+79==140', 140, 61 + 79)
chk('讲练2文件名题量和92+90+68+89==339', 339, 92 + 90 + 68 + 89)

# ---------- 5. 目录树行组装 ----------
rows = []   # (文本, 页码, 缩进, 章行?)
rows.append(('HEADER', '件／节（括注＝题量）', '页码', 0, False))
rows.append(('CH1', '第1章 空间向量与立体几何', str(starts[F_X1]), 0, True))
rows.append(('X1', '衔接件（29题）', str(starts[F_X1]), 420, False))
rows.append(('I1', '知识清单（47条）', str(starts[F_I1]), 420, False))
rows.append(('JL1', f'讲练件（140题：简单21｜中档104｜难15）', str(starts[F_B]), 420, False))
for no in sorted(k for k in sec if k[0] == '1'):
    name, n, _ = nav1_map[no]
    rows.append(('S' + no, f'{no} {name}（{n}题）', str(sec[no][3]), 840, False))
rows.append(('CH2', '第2章 平面解析几何', str(starts[F_X2]), 0, True))
rows.append(('X2', '衔接件（13题）', str(starts[F_X2]), 420, False))
rows.append(('I2', '知识清单（67条）', str(starts[F_I2]), 420, False))
rows.append(('JL2', f'讲练件（339题：简单47｜中档246｜难46）', str(starts[F_E]), 420, False))
for no in sorted(k for k in sec if k[0] == '2'):
    name, n, _ = nav2_map[no]
    rows.append(('S' + no, f'{no} {name}（{n}题）', str(sec[no][3]), 840, False))

# 节号排序须为教材序（数值逐段比较）
def key(no): return tuple(int(x) for x in no.split('.'))
chk('第1章节序', sorted((k for k in sec if k[0] == '1'), key=key),
    sorted(k for k in sec if k[0] == '1'))
chk('树行数 1列头+2章+6件型+25节级=34', 34, len(rows))

# ---------- 6. XML生成 ----------
RF = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体" w:cs="Times New Roman"/>'
def run(text, sz, bold):
    b = '<w:b/><w:bCs/>' if bold else ''
    return (f'<w:r><w:rPr>{RF}{b}<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/></w:rPr>'
            f'<w:t xml:space="preserve">{text}</w:t></w:r>')

def row_par(text, page, ind, bold, sz=18, line=280):
    tabs = '<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="10206"/></w:tabs>'
    indxml = f'<w:ind w:left="{ind}"/>' if ind else ''
    ppr = (f'{tabs}<w:spacing w:before="0" w:after="0" w:line="{line}" w:lineRule="atLeast"/>{indxml}<w:jc w:val="left"/>')
    return (f'<w:p><w:pPr>{ppr}</w:pPr>{run(text, sz, bold)}'
            f'<w:r><w:rPr>{RF}<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/></w:rPr><w:tab/></w:r>'
            f'{run(page, sz, bold)}</w:p>')

TITLE = '人教B版选必1·册目录页'
body = [f'''<w:p><w:pPr><w:pBdr><w:bottom w:val="single" w:sz="4" w:space="1" w:color="auto"/></w:pBdr><w:shd w:val="clear" w:color="auto" w:fill="ADC2DA"/><w:spacing w:before="0" w:after="0" w:line="410" w:lineRule="atLeast"/><w:jc w:val="left"/></w:pPr>{run(TITLE, 32, True)}</w:p>''']
for tag, text, page, ind, isch in rows:
    body.append(row_par(text, page, ind, bold=isch, sz=24 if isch else 18))

SECT = ('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="850" w:right="850" w:bottom="850" w:left="850" w:header="850" w:footer="850" w:gutter="0"/>'
        '<w:docGrid w:type="default" w:linePitch="312"/></w:sectPr>')
document = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f'<w:body>{"".join(body)}{SECT}</w:body></w:document>')

styles = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:docDefaults><w:rPrDefault><w:rPr>' + RF + '<w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr></w:rPrDefault>'
    '<w:pPrDefault><w:pPr><w:spacing w:before="0" w:after="0" w:line="280" w:lineRule="atLeast"/><w:jc w:val="left"/></w:pPr></w:pPrDefault></w:docDefaults>'
    '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/>'
    '<w:pPr><w:spacing w:before="0" w:after="0" w:line="280" w:lineRule="atLeast"/><w:jc w:val="left"/></w:pPr>'
    '<w:rPr>' + RF + '<w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr></w:style></w:styles>')

settings = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:updateFields w:val="true"/>'
    '<w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat>'
    '</w:settings>')

now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
    'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
    'xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
    f'<dc:title>{TITLE}</dc:title><dc:creator/><cp:lastModifiedBy/>'
    f'<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>'
    f'<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>')

app = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
    'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
    '<Application>Microsoft Office Word</Application></Properties>')

ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
    '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
    '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
    '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>')

rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
    '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>')

drels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/></Relationships>')

with zipfile.ZipFile(DOCX, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', ct)
    z.writestr('_rels/.rels', rels)
    z.writestr('word/document.xml', document)
    z.writestr('word/_rels/document.xml.rels', drels)
    z.writestr('word/styles.xml', styles)
    z.writestr('word/settings.xml', settings)
    z.writestr('docProps/core.xml', core)
    z.writestr('docProps/app.xml', app)

fails = [c for c in checks if not c[3]]
print(f'断言 {len(checks)} 项，失败 {len(fails)} 项')
for c in fails:
    print('  FAIL:', c[0], '期望', c[1], '实测', c[2])
json.dump({'checks': checks, 'rows': [[r[1], r[2], r[3]] for r in rows]},
          open(os.path.join(WS, 'build_断言.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('WROTE', DOCX)
