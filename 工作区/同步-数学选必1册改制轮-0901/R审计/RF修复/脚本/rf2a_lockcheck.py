# -*- coding: utf-8 -*-
"""RF2残留归属：Restart Manager查 RF修复\PDF\{H_local.docx,msoA53E.tmp} 的持有PID。"""
import ctypes, ctypes.wintypes as wt, sys, os
sys.stdout.reconfigure(encoding='utf-8')

class RM_UNIQUE_PROCESS(ctypes.Structure):
    _fields_ = [('dwProcessId', ctypes.c_int), ('ProcessStartTime', wt.FILETIME)]

class RM_PROCESS_INFO(ctypes.Structure):
    _fields_ = [('Process', RM_UNIQUE_PROCESS),
                ('strAppName', ctypes.c_wchar * 256),
                ('strServiceShortName', ctypes.c_wchar * 64),
                ('ApplicationType', ctypes.c_uint), ('AppStatus', ctypes.c_uint),
                ('TSSessionId', ctypes.c_uint), ('bRestartable', wt.BOOL)]

rm = ctypes.WinDLL('rstrtmgr')
rm.RmStartSession.argtypes = [ctypes.POINTER(ctypes.c_uint), ctypes.c_uint, ctypes.c_wchar_p]
rm.RmRegisterResources.argtypes = [ctypes.c_uint, ctypes.c_uint,
    ctypes.POINTER(ctypes.c_wchar_p), ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p]
rm.RmGetList.argtypes = [ctypes.c_uint, ctypes.POINTER(ctypes.c_uint),
    ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(RM_PROCESS_INFO), ctypes.POINTER(ctypes.c_uint)]

base = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\RF修复\PDF'
for f in ('H_local.docx', 'msoA53E.tmp'):
    path = os.path.join(base, f)
    h = ctypes.c_uint(0)
    key = 'RF2_%d' % os.getpid()
    rc = rm.RmStartSession(ctypes.byref(h), 0, key)
    assert rc == 0, 'RmStartSession rc=%d' % rc
    try:
        arr = (ctypes.c_wchar_p * 1)(path)
        rc = rm.RmRegisterResources(h, 1, arr, 0, None, 0, None)
        assert rc == 0, 'RmRegisterResources rc=%d' % rc
        needed = ctypes.c_uint(0); cnt = ctypes.c_uint(16); reasons = ctypes.c_uint(0)
        infos = (RM_PROCESS_INFO * 16)()
        rc = rm.RmGetList(h, ctypes.byref(needed), ctypes.byref(cnt), infos, ctypes.byref(reasons))
        pids = [(infos[i].Process.dwProcessId, infos[i].strAppName) for i in range(cnt.value)] if rc == 0 else [('rc=%d' % rc, '')]
        print('%s -> %s' % (f, pids))
    finally:
        rm.RmEndSession(h)
