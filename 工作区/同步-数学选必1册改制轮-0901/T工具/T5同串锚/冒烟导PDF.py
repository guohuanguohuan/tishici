# -*- coding: utf-8 -*-
# COM冒烟：开卷→页数/页眉页脚文本→导PDF→Quit（自建实例用完Quit）
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client

FILES = [('X2挂载.docx', 4), ('B挂载.docx', 78), ('C挂载.docx', 78)]
base = os.path.dirname(os.path.abspath(__file__))
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
ok = True
try:
    for f, expect_pages in FILES:
        p = os.path.join(base, f)
        doc = word.Documents.Open(p, ReadOnly=True, AddToRecentFiles=False)
        try:
            doc.Repaginate()
            pages = doc.ComputeStatistics(2)
            hdr = doc.Sections(1).Headers(1).Range.Text.strip()
            ftr = doc.Sections(1).Footers(1).Range.Text.strip()
            print('%s | COM开卷OK | 页数=%d（期望%d）| 页眉=%r' % (f, pages, expect_pages, hdr))
            print('    页脚=%r' % ftr)
            if pages != expect_pages:
                ok = False
                print('    [FAIL] 页数不符')
            pdf = os.path.join(base, f.replace('.docx', '.pdf'))
            doc.ExportAsFixedFormat(pdf, 17)   # 17 = wdExportFormatPDF
            print('    PDF -> %s（%dKB）' % (os.path.basename(pdf), os.path.getsize(pdf) // 1024))
        finally:
            doc.Close(False)
finally:
    word.Quit()
    print('Word Quit OK')
print('COM冒烟:', 'PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
