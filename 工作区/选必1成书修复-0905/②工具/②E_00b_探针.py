# -*- coding: utf-8 -*-
"""②E_00b_探针.py — ②-D 事故面最小件实验梯（FX-2）：定位「同步盘位置 Word COM 开卷挂死」环节。
用法: python ②E_00b_探针.py <mode> <docx路径>
  open    —— 仅测 Documents.Open 返回耗时（ReadOnly）
  repag   —— Open→Repaginate→ComputeStatistics(2)→Close
带内部节拍打印（flush），外部以 timeout 杀（挂死时可见走到哪一步）。
"""
import sys, io, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import win32com.client, pythoncom

mode, path = sys.argv[1], os.path.abspath(sys.argv[2])
t0 = time.time()
print('T+0.0 启动 CoInitialize')
pythoncom.CoInitialize()
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
print('T+%.1f Word 实例就绪' % (time.time() - t0))
d = word.Documents.Open(path, ReadOnly=True, AddToRecentFiles=False)
print('T+%.1f Open 返回' % (time.time() - t0))
if mode == 'repag':
    d.Repaginate()
    print('T+%.1f Repaginate 返回' % (time.time() - t0))
    n = d.ComputeStatistics(2)
    print('T+%.1f 页数=%d' % (time.time() - t0, n))
d.Close(False)
print('T+%.1f Close 返回' % (time.time() - t0))
word.Quit()
pythoncom.CoUninitialize()
print('PROBE_OK')
