
import sys, os, win32com.client, pythoncom
f, out, mode = sys.argv[1], sys.argv[2], sys.argv[3]
pythoncom.CoInitialize()
w = win32com.client.DispatchEx('Word.Application'); w.Visible = False; w.DisplayAlerts = 0
try:
    d = w.Documents.Open(os.path.abspath(f), ReadOnly=True, AddToRecentFiles=False)
    if mode == '5':
        d.ExportAsFixedFormat(os.path.abspath(out), 17, Range=0, From=1, To=5)
    else:
        d.ExportAsFixedFormat(os.path.abspath(out), 17)
    d.Close(False)
    print('OK', os.path.getsize(out)//1024)
finally:
    w.Quit(); pythoncom.CoUninitialize()
