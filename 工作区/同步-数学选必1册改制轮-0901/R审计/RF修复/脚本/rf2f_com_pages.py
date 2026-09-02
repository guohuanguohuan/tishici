# -*- coding: utf-8 -*-
"""RF2 COM页数终测：I2/F/G/H四件 ComputeStatistics。"""
import os, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')
import win32com.client as wc
R = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复'
word = wc.DispatchEx('Word.Application'); word.Visible = False; word.DisplayAlerts = 0
try:
    for code in ['I2', 'F', 'G', 'H']:
        local = os.path.join(R, 'PDF', code + '_local.docx')
        shutil.copy2(os.path.join(R, '基线', code + '.docx'), local)
        doc = word.Documents.Open(local, ReadOnly=True, AddToRecentFiles=False)
        try:
            print('%s COM页数=%d' % (code, doc.ComputeStatistics(2)), flush=True)
        finally:
            doc.Close(False)
        os.remove(local)
finally:
    word.Quit()
print('DONE')
