import zipfile, re, os, fitz, json, time

BASE = r'C:\提示词\工作区\同步-数学选必1复合修复-0903'
SYNC = r'C:\提示词\高中数学\高中数学同步'
ITEMS = [  # 代号, 文件, 期望页数, 期望start, 期望footer缇, 本n
 ('X1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', 14, 1, '850', 1),
 ('I1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', 13, 1, '850', 2),
 ('B',  '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', 61, 1, '850', 3),
 ('C',  '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', 60, 62, '567', 3),
 ('X2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', 5, 1, '850', 4),
 ('I2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', 28, 1, '850', 5),
 ('E',  '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', 55, 1, '850', 6),
 ('F',  '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', 56, 56, '850', 6),
 ('G',  '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', 44, 112, '850', 6),
 ('H',  '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', 70, 156, '567', 6),
]
fails = []
def chk(cond, msg):
    print(('  ✓ ' if cond else '  ✗ ') + msg)
    if not cond: fails.append(msg)

for code, fn, pages, start, ftw, bn in ITEMS:
    p = os.path.join(SYNC, fn)
    with zipfile.ZipFile(p) as z:
        doc = z.read('word/document.xml').decode('utf-8')
        st = z.read('word/settings.xml').decode('utf-8')
        names = z.namelist()
        hname = [n for n in names if re.fullmatch(r'word/header\d+\.xml', n)]
        fname = [n for n in names if re.fullmatch(r'word/footer\d+\.xml', n)]
        hxml = z.read(hname[0]).decode('utf-8') if hname else ''
        fxml = z.read(fname[0]).decode('utf-8') if fname else ''
    print(f'== {code} ==')
    m = re.search(r'<w:pgMar ([^/]*)/>', doc)
    a = dict(re.findall(r'w:(\w+)="(-?\d+)"', m.group(1)))
    chk(a.get('top') == a.get('right') == a.get('bottom') == a.get('left') == '850', f'四边850缇: {a}')
    chk(a.get('header') == '283', f'页眉距283: {a.get("header")}')
    chk(a.get('footer') == ftw, f'页脚距{ftw}缇: {a.get("footer")}')
    starts = re.findall(r'<w:pgNumType w:start="(\d+)"/>', doc)
    chk(starts == [str(start)], f'pgNumType start={start} 唯一: {starts}')
    chk('<w:titlePg' not in doc, '无titlePg')
    chk('<w:updateFields' in st, 'settings updateFields在')
    chk(len(hname) == 1 and len(fname) == 1, f'页眉页脚部件各1: {hname}{fname}')
    for nm, xml in (('header', hxml), ('footer', fxml)):
        vis = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', xml))
        mm = re.fullmatch(r'(.+)（共(\d+)页）·本(\d+)/共(\d+)本　(.+)　第(\d+)页', vis)
        chk(bool(mm) and int(mm.group(3)) == bn and int(mm.group(6)) == start,
            f'{nm} 同串形态+本{bn}+start{start}: {vis[:50]!r}')
        chk(xml.count('fldCharType="begin"') == 2 and 'fldSimple' not in xml and 'NUMPAGES' not in xml,
            f'{nm} 域形态（2复杂域/无fldSimple/无NUMPAGES）')
    # PDF 侧：页数＋逐页页眉＋页脚页码链
    pdf = fitz.open(rf'{BASE}\pages_406\pdf\{code}.pdf')
    chk(len(pdf) == pages, f'PDF页数={pages}: 实{len(pdf)}')
    npg = 0
    chain_ok = True
    for i, pg in enumerate(pdf):
        t = re.sub(r'\s', '', pg.get_text())  # PyMuPDF 提取页眉带空格，先去空白再匹配
        if '羿郭工作室' in t or '人教B版' in t: npg += 1
        m2 = re.search(r'第(\d+)页', t)
        if not m2 or int(m2.group(1)) != start + i:
            chain_ok = False
    chk(npg == pages, f'页眉逐页在: {npg}/{pages}')
    chk(chain_ok, f'页脚页码链 {start}..{start+pages-1} 逐页+1')
    pdf.close()
    # mtime 链：仅对本轮重导的 6 件强制 docx ≤ pdf；
    # X1/X2/E/G 系盖章回拷重打包（内容零变动），改断言现行 XML 哈希 == 章码重盖前快照
    REEXPORT = {'B', 'I1', 'C', 'H', 'F', 'I2'}
    if code in REEXPORT:
        mt_d = os.path.getmtime(p)
        mt_p = os.path.getmtime(rf'{BASE}\pages_406\pdf\{code}.pdf')
        chk(mt_d <= mt_p, f'mtime: docx({time.strftime("%H:%M", time.localtime(mt_d))}) ≤ pdf({time.strftime("%H:%M", time.localtime(mt_p))})')
    else:
        snap = json.load(open(rf'{BASE}\tmp\章码重盖前备份\_快照.json', encoding='utf-8'))[fn]
        import hashlib
        now = {}
        with zipfile.ZipFile(p) as z:
            for n in z.namelist():
                if n == 'word/document.xml' or re.fullmatch(r'word/(header|footer)\d+\.xml', n) or n == 'word/settings.xml':
                    now[n] = hashlib.sha1(z.read(n)).hexdigest()[:12]
        diff = sorted(k for k in now if now[k] != snap.get(k))
        chk(not diff and set(now) == set(snap), f'XML哈希==重盖前快照（内容零变动，旧PDF仍有效）: 差异{diff}')

print('\n==== P2/P3脚本项总判:', '全绿' if not fails else f'{len(fails)} 红', '====')
