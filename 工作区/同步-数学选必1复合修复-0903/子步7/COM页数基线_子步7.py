# -*- coding: utf-8 -*-
"""子步7(a)：COM实测十件页数基线＋「共N页」字段口径登记（opencode M6列集）。
逐件：XML侧 sectPr分节数/各分节start/分节类型/pgSz/pgMar/footer距/titlePg/当前（共N页）值/PAGE域缓存值；
COM侧 ComputeStatistics(2) 实测页数。自建实例用完Quit。只读，不改任何文件。"""
import zipfile, re, os, sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client, pythoncom

BASE = r'C:\提示词\高中数学\高中数学同步'
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
# A''旧记（规格书v1表，383链路）与中间轮登记值（报告-子步5 §六导出记录）
A_OLD = {'X1':16,'I1':14,'B':53,'C':61,'X2':6,'I2':28,'E':49,'F':53,'G':39,'H':64}
S3 = {'X1':16,'I1':14,'B':62,'C':61,'X2':6,'I2':28,'E':55,'F':56,'G':45,'H':70}   # 子步3后
S5 = {'X1':14,'I1':13,'B':61,'C':60,'X2':5,'I2':28,'E':55,'F':56,'G':44,'H':70}   # 子步5后（导出记录）

def xml_side(path):
    with zipfile.ZipFile(path) as z:
        doc = z.read('word/document.xml').decode('utf-8')
        settings = z.read('word/settings.xml').decode('utf-8')
        names = z.namelist()
        foot = [n for n in names if re.fullmatch(r'word/footer\d+\.xml', n)]
        head = [n for n in names if re.fullmatch(r'word/header\d+\.xml', n)]
        fxml = z.read(foot[0]).decode('utf-8') if foot else ''
        hxml = z.read(head[0]).decode('utf-8') if head else ''
    sects = re.findall(r'<w:sectPr.*?</w:sectPr>', doc, re.S)
    sect_info = []
    for s in sects:
        st = re.search(r'<w:pgNumType w:start="(\d+)"/>', s)
        typ = re.search(r'<w:type w:val="(\w+)"/>', s)
        cols = re.search(r'<w:cols [^/]*w:num="(\d+)"', s)
        sect_info.append({'start': int(st.group(1)) if st else None,
                          'type': typ.group(1) if typ else 'nextPage(默认)',
                          'cols': cols.group(1) if cols else '1'})
    pgsz = re.findall(r'<w:pgSz w:w="(\d+)" w:h="(\d+)"/>', doc)
    pgmar = re.findall(r'<w:pgMar [^/]*/>', doc)
    footers850 = ['w:footer="850"' in m for m in pgmar]
    n_old = re.search(r'（共(\d+)页）', fxml or hxml)
    bookseg = re.search(r'·本(\d+)/共(\d+)本', fxml or '')
    page_cache = None
    m = re.search(r'<w:instrText[^>]*>[^<]*\bPAGE\b[^<]*</w:instrText>', fxml)
    if m:
        i_sep = fxml.index('w:fldCharType="separate"', m.end())
        j = fxml.index('<w:t', i_sep); gt = fxml.index('>', j); k = fxml.index('</w:t>', j)
        page_cache = fxml[gt+1:k]
    return {
        'n_sect': len(sects), 'sects': sect_info,
        'pgSz': sorted(set('%sx%s' % t for t in pgsz)),
        'footer850_all': all(footers850) if footers850 else None,
        'titlePg': doc.count('<w:titlePg'),
        'updateFields': '<w:updateFields' in settings,
        'n_old': int(n_old.group(1)) if n_old else None,
        'bookseg': '本%s/共%s本' % bookseg.groups() if bookseg else None,
        'page_cache': page_cache,
        'size_bytes': os.path.getsize(path),
    }

def main():
    out = {}
    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False; word.DisplayAlerts = 0
    try:
        for code, fn in FILES:
            p = os.path.join(BASE, fn)
            t0 = time.time()
            doc = word.Documents.Open(p, ReadOnly=True, AddToRecentFiles=False)
            try:
                pages = doc.ComputeStatistics(2)
            finally:
                doc.Close(False)
            rec = xml_side(p)
            rec['pages_com'] = pages
            rec['open_s'] = round(time.time()-t0, 1)
            out[code] = rec
            print('%-3s COM=%3d  A''=%3d  sect=%d starts=%s N旧=%s PAGE缓存=%s %s' %
                  (code, pages, A_OLD[code], rec['n_sect'],
                   [s['start'] for s in rec['sects']], rec['n_old'], rec['page_cache'], fn[:30]))
    finally:
        word.Quit()
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'baseline_子步7.json'), 'w', encoding='utf-8') as f:
        json.dump({'A_old': A_OLD, 'S3': S3, 'S5': S5, 'files': {c: fn for c, fn in FILES}, 'measure': out},
                  f, ensure_ascii=False, indent=1)
    print('baseline_子步7.json 落盘')

if __name__ == '__main__':
    main()
