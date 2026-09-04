# -*- coding: utf-8 -*-
"""子步7(a)驱动器：逐件子进程COM实测（隔离挂起；单件180s超时、至多3次重试；孤Word实例按启动时刻归属清理，
用户实例28012永不触碰）。结果写 measure_子步7.json，并输出口径登记表所需XML侧信息。"""
import subprocess, os, sys, io, json, time, zipfile, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = sys.argv[1] if len(sys.argv) > 1 else r'C:\提示词\高中数学\高中数学同步'
FILES = [
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
USER_WORD_PID = 28012
DRIVER_T0 = time.time()

def kill_orphan_words():
    """清理由本驱动批次拉起的孤儿WINWORD（启动时刻晚于驱动启动、且≠用户实例28012）。"""
    import datetime
    r = subprocess.run(['powershell', '-NoProfile', '-Command',
        "Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object Id,StartTime | ConvertTo-Json"],
        capture_output=True, text=True)
    try:
        data = json.loads(r.stdout or '{}')
    except Exception:
        return
    if isinstance(data, dict):
        data = [data]
    for p in data:
        pid = p.get('Id'); st = p.get('StartTime')
        if not pid or pid == USER_WORD_PID or not st:
            continue
        # StartTime JSON: "/Date(ms)/" 或 ISO
        m = re.search(r'Date\((\d+)', str(st))
        ts = int(m.group(1)) / 1000 if m else 0
        if ts and ts >= DRIVER_T0 - 5:
            print('  清孤儿WINWORD pid=%d start=%s' % (pid, st))
            subprocess.run(['taskkill', '/pid', str(pid), '/f'], capture_output=True)

def measure_one(code, fn):
    outp = os.path.join(HERE, 'm_%s.json' % code)
    if os.path.exists(outp):
        os.remove(outp)
    for attempt in (1, 2, 3):
        try:
            subprocess.run([sys.executable, '-u', os.path.join(HERE, 'measure_one_子步7.py'),
                            code, os.path.join(BASE, fn), outp], timeout=180, check=False)
            if os.path.exists(outp):
                d = json.load(open(outp, encoding='utf-8'))
                print('%-3s COM=%3d  %5.1fs (尝试%d)' % (code, d['pages'], d['sec'], attempt))
                return d['pages']
        except subprocess.TimeoutExpired:
            print('%-3s 尝试%d 超时180s——清孤儿实例后重试' % (code, attempt))
            kill_orphan_words()
    raise RuntimeError('%s 三次尝试均失败' % code)

def xml_side(path):
    with zipfile.ZipFile(path) as z:
        doc = z.read('word/document.xml').decode('utf-8')
        settings = z.read('word/settings.xml').decode('utf-8')
        names = z.namelist()
        foot = [n for n in names if re.fullmatch(r'word/footer\d+\.xml', n)]
        head = [n for n in names if re.fullmatch(r'word/header\d+\.xml', n)]
        fxml = z.read(foot[0]).decode('utf-8') if foot else ''
    sects = re.findall(r'<w:sectPr.*?</w:sectPr>', doc, re.S)
    sect_info = []
    for s in sects:
        st = re.search(r'<w:pgNumType w:start="(\d+)"/>', s)
        typ = re.search(r'<w:type w:val="(\w+)"/>', s)
        cols = re.search(r'<w:cols [^/]*w:num="(\d+)"', s)
        sect_info.append({'start': int(st.group(1)) if st else None,
                          'type': typ.group(1) if typ else 'nextPage(默认)',
                          'cols': cols.group(1) if cols else '1'})
    pgsz = sorted(set('%sx%s' % t for t in re.findall(r'<w:pgSz w:w="(\d+)" w:h="(\d+)"/>', doc)))
    pgmar = re.findall(r'<w:pgMar [^/]*/>', doc)
    n_old = re.search(r'（共(\d+)页）', fxml)
    bookseg = re.search(r'·本(\d+)/共(\d+)本', fxml)
    page_cache = None
    m = re.search(r'<w:instrText[^>]*>[^<]*\bPAGE\b[^<]*</w:instrText>', fxml)
    if m:
        i_sep = fxml.index('w:fldCharType="separate"', m.end())
        j = fxml.index('<w:t', i_sep); gt = fxml.index('>', j); k = fxml.index('</w:t>', j)
        page_cache = fxml[gt + 1:k]
    return {'n_sect': len(sects), 'sects': sect_info, 'pgSz': pgsz,
            'footer850_all': all('w:footer="850"' in x for x in pgmar),
            'titlePg': doc.count('<w:titlePg'),
            'updateFields': '<w:updateFields' in settings,
            'n_old': int(n_old.group(1)) if n_old else None,
            'bookseg': ('本%s/共%s本' % bookseg.groups()) if bookseg else None,
            'page_cache': page_cache, 'size_bytes': os.path.getsize(path)}

def main():
    res = {}
    for code, fn in FILES:
        pages = measure_one(code, fn)
        rec = xml_side(os.path.join(BASE, fn))
        rec['pages_com'] = pages
        res[code] = rec
    A_OLD = {'X1':16,'I1':14,'B':53,'C':61,'X2':6,'I2':28,'E':49,'F':53,'G':39,'H':64}
    S3 = {'X1':16,'I1':14,'B':62,'C':61,'X2':6,'I2':28,'E':55,'F':56,'G':45,'H':70}
    S5 = {'X1':14,'I1':13,'B':61,'C':60,'X2':5,'I2':28,'E':55,'F':56,'G':44,'H':70}
    out = {'A_old': A_OLD, 'S3': S3, 'S5': S5,
           'files': {c: fn for c, fn in FILES}, 'measure': res}
    with open(os.path.join(HERE, sys.argv[2] if len(sys.argv) > 2 else 'baseline_子步7.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('落盘；合计=%d' % sum(r['pages_com'] for r in res.values()))

if __name__ == '__main__':
    main()
