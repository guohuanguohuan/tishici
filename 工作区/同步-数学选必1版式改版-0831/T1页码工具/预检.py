# -*- coding: utf-8 -*-
"""T1版本预检（N20）：Python/pywin32/Word COM版本＋开卷冒烟实测值落盘。只读，不改任何docx。"""
import sys, os, io, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import win32com.client
import pythoncom
import win32com  # __file__ 可查pywin32安装路径

print('python     :', sys.version.replace('\n', ' '))
print('python路径 :', sys.executable)
try:
    import win32api
    pywin32_ver = win32api.GetFileVersionInfo(win32com.__file__.replace('win32com\\__init__.py', 'pythoncom32.dll'), '\\')
    print('pywin32 dll ver:', pywin32_ver.get('FileVersionLS'), pywin32_ver.get('FileVersionMS'))
except Exception as e:
    print('pywin32 dll ver: 查询失败(%s)，改报模块路径：%s' % (e, win32com.__file__))
import pywin32_system32  # noqa: F401  仅探测可导入

BASE = os.path.dirname(os.path.abspath(__file__))
targets = [os.path.join(BASE, 'P3', 'B.docx'), os.path.join(BASE, 'P3', 'C.docx')] + \
          [os.path.join(BASE, 'P6', x) for x in ('E.docx', 'F.docx', 'G.docx', 'H.docx')]

# 同步盘干扰防：落盘后重读校验（sha256两次）
for p in targets:
    h1 = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    h2 = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    assert h1 == h2, '副本读取不稳定: %s' % p
    print('sha256稳定 %s %s %d字节' % (os.path.basename(os.path.dirname(p)) + '/' + os.path.basename(p), h1[:16], os.path.getsize(p)))

pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    print('Word COM 版本:', word.Version, '| Build:', word.Build)
    for p in targets:
        doc = word.Documents.Open(p, ReadOnly=True, AddToRecentFiles=False)
        pages = doc.ComputeStatistics(2)  # wdStatisticPages
        sec = doc.Sections.Count
        footers = doc.Sections(1).Footers
        fcnt = sum(1 for i in (1, 2, 3) if footers(i).Exists)
        print('冒烟 %s/%s: COM实测页数=%d 节数=%d 首节页脚Exists数=%d'
              % (os.path.basename(os.path.dirname(p)), os.path.basename(p), pages, sec, fcnt))
        doc.Close(False)
finally:
    word.Quit()
    pythoncom.CoUninitialize()
print('预检完成')
