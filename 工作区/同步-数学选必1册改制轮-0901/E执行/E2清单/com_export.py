# -*- coding: utf-8 -*-
"""E2一次性：Word COM 页数实测＋PDF导出（自建实例、用完Quit）。
用法: python com_export.py <docx> <pdf_out> [--pages N]"""
import sys, os
import win32com.client as wc

def main(docx, pdf, pages_only=False):
    docx = os.path.abspath(docx); pdf = os.path.abspath(pdf)
    app = wc.DispatchEx('Word.Application')
    app.Visible = False
    try:
        doc = app.Documents.Open(docx, ReadOnly=True, AddToRecentFiles=False)
        n = doc.ComputeStatistics(2)  # wdStatisticPages
        print('PAGES=%d' % n)
        if not pages_only:
            doc.ExportAsFixedFormat(pdf, 17)  # wdExportFormatPDF
            print('PDF=%s' % pdf)
        doc.Close(False)
    finally:
        app.Quit()

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '', '--pages-only' in sys.argv)
