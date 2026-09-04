# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import pythoncom, win32com.client
pythoncom.CoInitialize()
try:
    word = win32com.client.GetObject(None, 'Word.Application')
    docs = [d.Name + ' | ' + d.FullName for d in word.Documents]
    print('user Word documents:', len(docs))
    for d in docs:
        print('  ', d)
except Exception as e:
    print('GetObject failed:', e)
