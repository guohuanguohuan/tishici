# -*- coding: utf-8 -*-
"""word_repair_save.py — OpenAndRepair 开卷 + SaveAs 定稿（FileFormat=16）
用法: python word_repair_save.py <in.docx> <out.docx>  输出页数"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client, pythoncom

def repair_save(src, dst):
    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        d = word.Documents.Open(os.path.abspath(src), ReadOnly=False, AddToRecentFiles=False, OpenAndRepair=True)
        pages = d.ComputeStatistics(2)
        d.SaveAs2(os.path.abspath(dst), FileFormat=16)
        d.Close(False)
        return pages
    finally:
        word.Quit()
        pythoncom.CoUninitialize()

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    print('%s -> %s : %s页' % (os.path.basename(src), os.path.basename(dst), repair_save(src, dst)))
