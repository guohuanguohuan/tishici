# -*- coding: utf-8 -*-
"""T3·N20版本预检＋⑥COM开卷实测页数（一次性，工作区子文件夹内）
自建Word实例→只读开卷→ComputeStatistics(wdStatisticPages=2)→Close→Quit（用完即退）"""
import sys, io, os, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32com.client
import pythoncom

WD = os.path.dirname(os.path.abspath(__file__))
FILES = [
    ('小件X2基线', os.path.join(WD, '小件X2.docx')),
    ('小件X2改版', os.path.join(WD, '改版X2.docx')),
    ('大件B讲上基线', os.path.join(WD, '大件B讲上.docx')),
    ('大件B讲上改版', os.path.join(WD, '改版B讲上.docx')),
]

pythoncom.CoInitialize()
app = None
result = {'Word版本': None, '开卷冒烟': None, '页数': {}}
try:
    app = win32com.client.DispatchEx('Word.Application')
    app.Visible = False
    app.DisplayAlerts = 0
    result['Word版本'] = {'Version': app.Version, 'Build': app.Build}
    for tag, path in FILES:
        t0 = time.time()
        doc = app.Documents.Open(path, ReadOnly=True, AddToRecentFiles=False)
        pages = doc.ComputeStatistics(2)   # wdStatisticPages
        words = doc.ComputeStatistics(0)   # wdStatisticWords（冒烟旁证：文字量不变）
        doc.Close(False)
        result['页数'][tag] = {'页数': pages, '字数统计': words, '耗时秒': round(time.time() - t0, 1)}
        if '基线' in tag:
            result['开卷冒烟'] = 'OK：%s 开卷成功，%d页' % (tag, pages)
        print(tag, '→', pages, '页', words, '字')
finally:
    if app is not None:
        app.Quit()
    pythoncom.CoUninitialize()

base = {t.split('基线')[0]: v for t, v in result['页数'].items() if '基线' in t}
for t, v in result['页数'].items():
    if '改版' in t:
        k = t.split('改版')[0]
        if k in base:
            result['页数'][t]['增幅'] = v['页数'] - base[k]['页数']
            result['页数'][t]['字数差'] = v['字数统计'] - base[k]['字数统计']

out = os.path.join(WD, 'COM实测.json')
json.dump(result, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(result, ensure_ascii=False, indent=1))
