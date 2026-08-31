# -*- coding: utf-8 -*-
"""阶段4子进程：COM实测页数为源＋缓存值抽查3页（调整页码=件内页+start−1）。
结果写 阶段4结果.json（Quit前落盘，COM拆解噪音不损结果）。独立短生命周期进程，用完即退。"""
import sys, os, io, json, gc
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import win32com.client, pythoncom

BASE = os.path.dirname(os.path.abspath(__file__))
EXPECT = {  # (收敛后页数, start)
    'P3/B.docx': (78, 1), 'P3/C.docx': (76, 79), 'P6/E.docx': (50, 1),
    'P6/F.docx': (53, 51), 'P6/G.docx': (38, 104), 'P6/H.docx': (64, 142),
}
samples = {'P3/B.docx': [1, 40, 78], 'P3/C.docx': [1, 38, 76], 'P6/E.docx': [1, 25, 50],
           'P6/F.docx': [1, 27, 53], 'P6/G.docx': [1, 19, 38], 'P6/H.docx': [1, 32, 64]}
res = {}
pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    for rel, pages3 in samples.items():
        base_pages, start = EXPECT[rel]
        doc = word.Documents.Open(os.path.join(BASE, rel), ReadOnly=True, AddToRecentFiles=False)
        try:
            pages = doc.ComputeStatistics(2)
            assert pages == base_pages, '%s COM页数=%d 预期%d' % (rel, pages, base_pages)
            got = []
            for k in pages3:
                rng = doc.GoTo(1, 1, k)                 # wdGoToPage→物理第k页
                got.append(rng.Information(1))          # wdActiveEndAdjustedPageNumber（含pgNumType）
            expect3 = [k - 1 + start for k in pages3]
            assert got == expect3, '%s 调整页码%s 预期%s' % (rel, got, expect3)
            res[rel] = {'pages': pages, 'sampled_physical': pages3, 'adjusted': got, 'expected': expect3}
            print('  %s: COM页数=%d(源) 3页调整页码%s==start+件内页−1 %s ✓' % (rel, pages, got, expect3))
        finally:
            doc.Close(False)
            doc = None
finally:
    json.dump(res, open(os.path.join(BASE, '阶段4结果.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    gc.collect()
    try:
        word.Quit()
    except Exception as e:
        print('Quit告警(容忍):', e)
    word = None
    gc.collect()
    try:
        pythoncom.CoUninitialize()
    except Exception:
        pass
print('阶段4完成：6件×(页数源+3页抽查) 全过')
