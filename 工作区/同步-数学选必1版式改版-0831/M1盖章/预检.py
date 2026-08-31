# -*- coding: utf-8 -*-
"""M1盖章轮·预检（N20）：Python/pywin32/Word COM版本＋开卷冒烟落盘。"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '预检输出.txt')
PROD = r'C:\Users\28120\Desktop\提示词\高中数学\高中数学同步'
SMOKE = os.path.join(PROD, '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx')  # 最小件冒烟

lines = []
lines.append('== M1预检（N20） %s ==' % __import__('datetime').datetime.now().isoformat(timespec='seconds'))
lines.append('Python: %s (%s)' % (sys.version.split()[0], sys.executable))
try:
    import win32com.client
    import pywintypes
    lines.append('pywin32: %s' % (getattr(win32com.client, '__version__', '?') or '?'))
except ImportError as e:
    lines.append('pywin32缺失: %r' % e)
    open(OUT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    sys.exit(3)

word = None
try:
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    lines.append('Word COM: %s (Build %s)' % (word.Version, word.Build))
    assert os.path.isfile(SMOKE), '冒烟件不存在: %s' % SMOKE
    doc = word.Documents.Open(SMOKE, ReadOnly=True, AddToRecentFiles=False)
    try:
        pages = doc.ComputeStatistics(2)
        lines.append('开卷冒烟: %s -> %d页 OK' % (os.path.basename(SMOKE), pages))
    finally:
        doc.Close(False)
finally:
    if word is not None:
        word.Quit()
lines.append('预检结论: 全部通过')
open(OUT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
