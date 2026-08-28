# -*- coding: utf-8 -*-
"""word_check.py — Word COM 开卷验证+页数实测（不保存）
用法: python word_check.py <docx...>  输出每件 页数/可开性"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client, pythoncom

def check(path):
    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        d = word.Documents.Open(os.path.abspath(path), ReadOnly=True, AddToRecentFiles=False, OpenAndRepair=False)
        pages = d.ComputeStatistics(2)  # wdStatisticPages
        d.Close(False)
        return pages
    finally:
        word.Quit()
        pythoncom.CoUninitialize()

if __name__ == '__main__':
    for p in sys.argv[1:]:
        try:
            print('%s\t%s页' % (os.path.basename(p), check(p)))
        except Exception as e:
            print('%s\tERROR %s' % (os.path.basename(p), e))
