# -*- coding: utf-8 -*-
"""msprint_test.py — Microsoft Print to PDF 导出实验（问答触发，产物仅存tmp）。
用法: python msprint_test.py <docx> <out_pdf> [timeout_sec]
方法: Word COM→ActivePrinter='Microsoft Print to PDF'→PrintOut(PrintToFile=True, OutputFileName=)
防护: 只杀本实验拉起的新WINWORD进程；结束后恢复系统默认打印机。
"""
import sys, io, os, time, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client, pythoncom, win32print

def word_pids():
    r = subprocess.run(['wmic', 'process', 'where', "name='WINWORD.EXE'", 'get', 'ProcessId'],
                       capture_output=True, text=True)
    return {int(x) for x in r.stdout.split() if x.isdigit()}

def main(docx, out_pdf, timeout_sec=600):
    docx, out_pdf = os.path.abspath(docx), os.path.abspath(out_pdf)
    if os.path.exists(out_pdf):
        os.remove(out_pdf)
    pre_pids = word_pids()
    default_printer = win32print.GetDefaultPrinter()
    t0 = time.time()
    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        d = word.Documents.Open(docx, ReadOnly=True, AddToRecentFiles=False)
        word.ActivePrinter = 'Microsoft Print to PDF'
        d.PrintOut(Background=False, PrintToFile=True, OutputFileName=out_pdf,
                   Item=0, Copies=1, PageType=0)
        d.Close(False)
        elapsed = time.time() - t0
        # 等文件写稳
        s0 = -1
        for _ in range(30):
            if os.path.exists(out_pdf):
                s1 = os.path.getsize(out_pdf)
                if s1 == s0 and s1 > 0:
                    break
                s0 = s1
            time.sleep(1)
        ok = False
        if os.path.exists(out_pdf):
            with open(out_pdf, 'rb') as f:
                ok = f.read(5) == b'%PDF-'
        print('PrintOut耗时=%.1fs 产物存在=%s 是PDF=%s 大小=%.2fMB' % (
            elapsed, os.path.exists(out_pdf), ok,
            os.path.getsize(out_pdf) / 1048576 if os.path.exists(out_pdf) else 0))
        return 0 if ok else 2
    finally:
        try:
            word.Quit()
        except Exception:
            pass
        win32print.SetDefaultPrinter(default_printer)
        # 只清理本实验新拉起且仍存活的WINWORD
        for pid in word_pids() - pre_pids:
            subprocess.run(['taskkill', '/f', '/pid', str(pid)], capture_output=True)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 600))
