# -*- coding: utf-8 -*-
"""SA任务3：C零联动核验——产出C（fix7落盘态、未重盖）开卷断言：
①COM页数=77；②sectPr start=78（全sectPr）；③页眉页脚两处 X域缓存=78、N=154、域形态、可见串；
④footer850/无titlePg/updateFields；⑤（前置已证）页眉页脚部件与fix6产出逐字节一致（sa2落成品md5链）。
另：页眉页脚/settings与RF修复基线C逐字节相等再证。"""
import io, os, re, sys, zipfile, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client

DOCX = r'C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx'
BASE = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复\基线\C.docx'
HERE = os.path.dirname(os.path.abspath(__file__))
START, N, PAGES = 78, 154, 77
INSTR_PAGE = re.compile(r'<w:instrText[^>]*>[^<]*\bPAGE\b[^<]*</w:instrText>')

def page_cache(xml):
    m = INSTR_PAGE.search(xml)
    i_sep = xml.index('w:fldCharType="separate"', m.end())
    j = xml.index('<w:t', i_sep)
    gt = xml.index('>', j)
    k = xml.index('</w:t>', j)
    return xml[gt + 1:k]

ok = []
with zipfile.ZipFile(DOCX) as z:
    names = z.namelist()
    hfs = [n for n in names if re.fullmatch(r'word/header\d+\.xml', n)] + \
          [n for n in names if re.fullmatch(r'word/footer\d+\.xml', n)]
    assert len(hfs) == 2, '页眉页脚部件数=%d' % len(hfs)
    for nm in hfs:
        xml = z.read(nm).decode('utf-8')
        w = os.path.basename(nm)
        ok.append(('%s X缓存=start78' % w, page_cache(xml) == str(START), page_cache(xml)))
        ns = re.findall(r'（共(\d+)页）', xml)
        ok.append(('%s N写死=154' % w, ns == [str(N)], repr(ns)))
        ok.append(('%s 域形态' % w, xml.count('fldCharType="begin"') == 2
                   and 'fldSimple' not in xml and 'NUMPAGES' not in xml
                   and 'STYLEREF "节名锚"' in xml, ''))
        vis = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', xml))
        m = re.fullmatch(r'(.+)（共(\d+)页）　(.+)　第(\d+)页', vis)
        ok.append(('%s 可见串' % w, bool(m) and int(m.group(2)) == N
                   and int(m.group(4)) == START and m.group(1).endswith('讲练'), vis[:60]))
    d = z.read('word/document.xml').decode('utf-8')
    starts = [int(x) for x in re.findall(r'<w:pgNumType w:start="(\d+)"/>', d)]
    ok.append(('sectPr start=78', starts and all(x == START for x in starts), repr(starts)))
    ok.append(('footer=850缇', 'w:footer="850"' in d, ''))
    ok.append(('无titlePg', '<w:titlePg' not in d, ''))
    s = z.read('word/settings.xml').decode('utf-8')
    ok.append(('updateFields且无evenAndOdd', '<w:updateFields' in s and 'evenAndOddHeaders' not in s, ''))
    # 与RF基线（fix7源）页眉/页脚/settings逐字节相等
    with zipfile.ZipFile(BASE) as zb:
        eq_hf = all(z.read(n) == zb.read(n) for n in hfs + ['word/settings.xml'])
    ok.append(('页眉页脚+settings=基线fix7逐字节', eq_hf, ''))

bad = [(k, v, e) for k, v, e in ok if not v]
for k, v, e in bad:
    print('  ✗ %s %s' % (k, e))
print('C XML断言 %d项 %s' % (len(ok), '全绿✓' if not bad else '失败%d' % len(bad)))

word = win32com.client.DispatchEx('Word.Application')
word.Visible = False; word.DisplayAlerts = 0
try:
    doc = word.Documents.Open(DOCX, ReadOnly=True, AddToRecentFiles=False)
    try:
        npg = doc.ComputeStatistics(2)
    finally:
        doc.Close(False)
finally:
    word.Quit()
print('C COM页数=%d %s' % (npg, '✓' if npg == PAGES else '✗ 期望77'))

allg = not bad and npg == PAGES
json.dump({'xml_asserts': len(ok), 'xml_fail': len(bad), 'com_pages': npg},
          open(os.path.join(HERE, 'C零联动核验.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('=== C零联动核验：%s ===' % ('全绿（页数77/start=78/N=154维持，页脚未触碰）' if allg else '存在失败项'))
sys.exit(0 if allg else 1)
