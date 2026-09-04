# -*- coding: utf-8 -*-
"""单件COM页数实测（子步7驱动器的子进程体）：开卷(ReadOnly)→ComputeStatistics(2)→Close→Quit。
用法：python -u measure_one_子步7.py <代号> <docx路径> <out.json路径>"""
import sys, os, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import pythoncom, win32com.client

def main():
    code, path, outp = sys.argv[1], sys.argv[2], sys.argv[3]
    pythoncom.CoInitialize()
    t0 = time.time()
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        doc = word.Documents.Open(os.path.abspath(path), ReadOnly=True, AddToRecentFiles=False)
        try:
            pages = doc.ComputeStatistics(2)
        finally:
            doc.Close(False)
    finally:
        word.Quit()
    with open(outp, 'w', encoding='utf-8') as f:
        json.dump({'code': code, 'pages': pages, 'sec': round(time.time() - t0, 1)}, f)
    print('%s=%d (%.1fs)' % (code, pages, time.time() - t0))

if __name__ == '__main__':
    main()
