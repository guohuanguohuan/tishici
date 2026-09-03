# -*- coding: utf-8 -*-
"""A1审计：COM页数实测v2——逐件独立Word实例（开→测→关→Quit），flush实时日志"""
import os, sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)
import win32com.client as w32
import pythoncom

SRC = r"C:\提示词\高中数学\高中数学同步"
FILES = [
    ("X1", "人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx"),
    ("I1", "人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx"),
    ("B",  "人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx"),
    ("C",  "人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx"),
]
EXPECT = {"X1":16, "I1":14, "B":53, "C":61}
results = {}

pythoncom.CoInitialize()
for tag, name in FILES:
    print(f"[{time.strftime('%H:%M:%S')}] {tag} 开始…", flush=True)
    word = None
    try:
        word = w32.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        path = os.path.join(SRC, name)
        print(f"  打开 {name}", flush=True)
        doc = word.Documents.Open(path, ReadOnly=True, AddToRecentFiles=False,
                                  Visible=False, ConfirmConversions=False, OpenAndRepair=False)
        print("  已打开，测页数…", flush=True)
        pages = doc.ComputeStatistics(2)  # wdStatisticPages（自动分页）
        results[tag] = pages
        print(f"  [{tag}] COM实测页数={pages} 规格={EXPECT[tag]} {'一致' if pages==EXPECT[tag] else '!!不一致'}", flush=True)
        doc.Close(SaveChanges=0)
    except Exception as e:
        print(f"  [{tag}] 异常: {e}", flush=True)
        results[tag] = f"ERR:{e}"
    finally:
        if word is not None:
            try: word.Quit()
            except Exception: pass
        print(f"  [{tag}] Word已Quit", flush=True)
pythoncom.CoUninitialize()
print("RESULT:", results, flush=True)
rep = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\A1_reports\COM页数.txt"
os.makedirs(os.path.dirname(rep), exist_ok=True)
open(rep,'w',encoding='utf-8').write(repr(results))
