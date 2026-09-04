# -*- coding: utf-8 -*-
"""COM worker（qwen复测）：DispatchEx 不可见单会话，顺开 argv 所列 docx（ReadOnly），ComputeStatistics(2) 写 JSONL 后 Quit。
用法: com_worker_复测_qwen.py status.jsonl file1 [file2...]"""
import sys, os, json, time

status_path = sys.argv[1]
files = sys.argv[2:]

def log(ev):
    ev['ts'] = time.time()
    with open(status_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(ev, ensure_ascii=False) + '\n')

word = None
pid = None
try:
    import win32com.client, pythoncom
    from win32process import GetWindowThreadProcessId
    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        _, pid = GetWindowThreadProcessId(word.Hwnd)
    except Exception:
        pid = None
    log({'ev': 'word_started', 'pid': pid})
    for fp in files:
        name = os.path.basename(fp)
        log({'ev': 'open_start', 'file': name})
        t0 = time.time()
        d = word.Documents.Open(fp, ReadOnly=True, AddToRecentFiles=False, Visible=False)
        pages = d.ComputeStatistics(2)
        secs = d.Sections.Count
        log({'ev': 'open_done', 'file': name, 'pages': pages, 'sections': secs, 'sec': round(time.time() - t0, 2)})
        d.Close(False)
    log({'ev': 'all_done'})
except Exception as e:
    log({'ev': 'error', 'msg': repr(e)[:300]})
finally:
    try:
        if word is not None:
            word.Quit()
    except Exception:
        pass
    log({'ev': 'quit'})
