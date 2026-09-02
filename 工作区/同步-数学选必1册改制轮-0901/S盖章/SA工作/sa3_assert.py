# -*- coding: utf-8 -*-
"""SA任务2断言包（X1重盖章后）：①XML独立断言（页眉页脚两处X缓存=start/N写死/域形态/可见串
＋sectPr start＋footer850＋无titlePg＋updateFields）；②COM页数=17；③PDF抽2页（p1/p17）页眉页脚
两区「第X页（共17页）」渲染；④幂等复跑（快照→重跑工具→全zip成员DIFF=0）。"""
import io, os, re, subprocess, sys, zipfile, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client
import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = r'C:\提示词\工具\册级连续页码.py'
CFG = os.path.join(HERE, 'parts_SA.json')
PDFDIR = os.path.join(HERE, 'PDF')
os.makedirs(PDFDIR, exist_ok=True)
DOCX = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx'
START, N = 1, 17
INSTR_PAGE = re.compile(r'<w:instrText[^>]*>[^<]*\bPAGE\b[^<]*</w:instrText>')

def page_cache(xml):
    m = INSTR_PAGE.search(xml)
    i_sep = xml.index('w:fldCharType="separate"', m.end())
    j = xml.index('<w:t', i_sep)
    gt = xml.index('>', j)
    k = xml.index('</w:t>', j)
    return xml[gt + 1:k]

def xml_asserts(stage):
    ok = []
    with zipfile.ZipFile(DOCX) as z:
        names = z.namelist()
        hfs = [n for n in names if re.fullmatch(r'word/header\d+\.xml', n)] + \
              [n for n in names if re.fullmatch(r'word/footer\d+\.xml', n)]
        assert len(hfs) == 2, '页眉页脚部件数=%d' % len(hfs)
        for nm in hfs:
            xml = z.read(nm).decode('utf-8')
            w = os.path.basename(nm)
            ok.append(('%s X缓存=start' % w, page_cache(xml) == str(START), page_cache(xml)))
            ns = re.findall(r'（共(\d+)页）', xml)
            ok.append(('%s N写死=17' % w, ns == [str(N)], repr(ns)))
            ok.append(('%s 域形态' % w, xml.count('fldCharType="begin"') == 2
                       and xml.count('fldCharType="end"') == 2 and 'fldSimple' not in xml
                       and 'NUMPAGES' not in xml and 'STYLEREF "节名锚"' in xml, ''))
            vis = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', xml))
            m = re.fullmatch(r'(.+)（共(\d+)页）　(.+)　第(\d+)页', vis)
            ok.append(('%s 可见串' % w, bool(m) and int(m.group(2)) == N
                       and int(m.group(4)) == START and m.group(1).endswith('衔接'), vis[:60]))
        d = z.read('word/document.xml').decode('utf-8')
        starts = [int(x) for x in re.findall(r'<w:pgNumType w:start="(\d+)"/>', d)]
        ok.append(('sectPr start=1', starts and all(x == START for x in starts), repr(starts)))
        ok.append(('footer=850缇', 'w:footer="850"' in d, ''))
        ok.append(('无titlePg', '<w:titlePg' not in d, ''))
        s = z.read('word/settings.xml').decode('utf-8')
        ok.append(('updateFields且无evenAndOdd', '<w:updateFields' in s and 'evenAndOddHeaders' not in s, ''))
    bad = [(k, v, e) for k, v, e in ok if not v]
    for k, v, e in bad:
        print('  ✗ [%s] %s %s' % (stage, k, e))
    print('[%s] XML断言 %d项 %s' % (stage, len(ok), '全绿✓' if not bad else '失败%d' % len(bad)))
    return not bad

def com_pages():
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False; word.DisplayAlerts = 0
    try:
        doc = word.Documents.Open(DOCX, ReadOnly=True, AddToRecentFiles=False)
        try:
            return doc.ComputeStatistics(2)
        finally:
            doc.Close(False)
    finally:
        word.Quit()

def pdf_check():
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False; word.DisplayAlerts = 0
    pdf = os.path.join(PDFDIR, 'X1_SA.pdf')
    try:
        doc = word.Documents.Open(DOCX, ReadOnly=True, AddToRecentFiles=False)
        try:
            doc.ExportAsFixedFormat(pdf, 17)
        finally:
            doc.Close(False)
    finally:
        word.Quit()
    d = fitz.open(pdf)
    n_pdf = d.page_count
    print('X1 PDF页数=%d（COM一致性待比对）' % n_pdf)
    allok = True
    for pno in (0, n_pdf - 1):
        page = d[pno]
        expect_x = START + pno
        for region, clip in (('页眉', fitz.Rect(0, 0, 595, 60)), ('页脚', fitz.Rect(0, 770, 595, 842))):
            txt = page.get_text(clip=clip)
            m = re.search(r'（共\s*(\d+)\s*页）', txt)
            mx = re.search(r'第\s*(\d+)\s*页', txt)
            v_ok = bool(m) and int(m.group(1)) == N
            x_ok = bool(mx) and int(mx.group(1)) == expect_x
            str_ok = ('衔接' in txt) and ('羿郭工作室' in txt.replace(' ', ''))
            print('  p%d %s: %s（期望 第%d页/共%d页）%s'
                  % (pno + 1, region, re.sub(r'\s+', '', txt)[:44], expect_x, N,
                     '✓' if v_ok and x_ok and str_ok else '✗ %r' % txt))
            allok = allok and v_ok and x_ok and str_ok
    d.close()
    return n_pdf, allok

def snapshot(path, dest):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        for n in names:
            with open(os.path.join(dest, n.replace('/', '__')), 'wb') as f:
                f.write(z.read(n))
    return names

# ── ① XML断言（run1态） ──
a1 = xml_asserts('run1')
# ── ② COM页数 ──
npages = com_pages()
print('[COM] 页数=%d %s' % (npages, '✓' if npages == N else '✗ 期望17'))
# ── ③ PDF抽验（p1/p17两页·页眉页脚两区） ──
n_pdf, pok = pdf_check()
# ── ④ 幂等复跑：快照→重跑→DIFF=0 ──
snap = os.path.join(HERE, 'snap_run1')
os.makedirs(snap, exist_ok=True)
names = snapshot(DOCX, snap)
r = subprocess.run([sys.executable, TOOL, '--parts', CFG, '--record',
                    os.path.join(HERE, '盖章记录_SA_run2.md')],
                   capture_output=True, text=True, encoding='utf-8')
print('[幂等复跑] rc=%d 输出尾行: %s' % (r.returncode, (r.stdout or r.stderr).strip().splitlines()[-1]))
assert r.returncode == 0, '幂等复跑失败'
with zipfile.ZipFile(DOCX) as z:
    diffs = [n for n in names if z.read(n) != open(os.path.join(snap, n.replace('/', '__')), 'rb').read()]
    order_same = z.namelist() == names
print('[幂等] 全zip成员（%d个）DIFF=%s | 成员序一致=%s' % (len(names), diffs if diffs else 0, order_same))
a2 = xml_asserts('run2')
# 记录run1==run2逐字
r1 = open(os.path.join(HERE, '盖章记录_SA.md'), encoding='utf-8').read()
r2 = open(os.path.join(HERE, '盖章记录_SA_run2.md'), encoding='utf-8').read()
print('[幂等] 盖章记录run1==run2逐字: %s' % ('✓' if r1 == r2 else '✗'))

ok_all = a1 and a2 and npages == N and n_pdf == N and pok and not diffs and order_same and r1 == r2
json.dump({'xml_run1': a1, 'xml_run2': a2, 'com_pages': npages, 'pdf_pages': n_pdf,
           'pdf_check': pok, 'idempotent_diff': diffs, 'record_equal': r1 == r2},
          open(os.path.join(HERE, 'X1盖章断言.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('=== X1重盖章断言汇总：%s ===' % ('全绿' if ok_all else '存在失败项'))
sys.exit(0 if ok_all else 1)
