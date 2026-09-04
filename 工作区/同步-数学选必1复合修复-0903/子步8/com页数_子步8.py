# -*- coding: utf-8 -*-
"""子步8：COM实测配页件页数（册目录页/使用说明），断言=1页。"""
import os, sys, io, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import pythoncom, win32com.client as wc

BASE = r'C:\提示词\高中数学\高中数学同步'
targets = {
    '册目录页': os.path.join(BASE, '人教B版选必1·册目录页.docx'),
    '使用说明': os.path.join(BASE, '人教B版选必1·使用说明.docx'),
}
out = {}
pythoncom.CoInitialize()
app = wc.DispatchEx('Word.Application')
app.Visible = False
try:
    for k, p in targets.items():
        doc = None
        for attempt in range(3):
            try:
                doc = app.Documents.Open(p, ReadOnly=True)
                break
            except Exception as e:
                print('[%s] 第%d次打开失败: %s' % (k, attempt + 1, e))
                time.sleep(2)
        assert doc is not None, k + ' 三次打开均失败'
        doc.Repaginate()
        time.sleep(0.5)
        pages = doc.ComputeStatistics(2)  # wdStatisticPages
        print('%s: %d页' % (k, pages))
        out[k] = pages
        doc.Close(False)
finally:
    app.Quit()
    pythoncom.CoUninitialize()
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'com页数_子步8.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('com页数_子步8.json 落盘')
