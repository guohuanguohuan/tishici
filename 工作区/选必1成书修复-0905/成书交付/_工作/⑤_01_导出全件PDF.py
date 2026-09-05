# -*- coding: utf-8 -*-
r"""⑤_01_导出全件PDF.py — 同步盘终态工作区复制件 → 全件 PDF（COM ExportAsFixedFormat 17，CB-12 书签 CreateBookmarks=1）。
用法: python ⑤_01_导出全件PDF.py [--smoke 衔接2]
输出: 成书交付\全件PDF\<同名>.pdf；日志 _工作\⑤_01_导出记录.json/.md
"""
import sys, io, os, json, datetime, time, argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import win32com.client, pythoncom

WORK = r"C:\提示词\工作区\选必1成书修复-0905\成书交付"
SRC_DIR = os.path.join(WORK, "_工作", "docx源")
OUT_DIR = os.path.join(WORK, "全件PDF")

ALL = [
    "人教B版选必1·封面.docx",
    "人教B版选必1·使用说明.docx",
    "人教B版选必1·册目录页.docx",
    "人教B版选必1·部分封面（第1章 空间向量与立体几何·衔接）.docx",
    "人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx",
    "人教B版选必1·部分封面（第1章 空间向量与立体几何·清单）.docx",
    "人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx",
    "人教B版选必1·部分封面（第1章 空间向量与立体几何·讲练）.docx",
    "人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx",
    "人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx",
    "人教B版选必1·部分封面（第2章 平面解析几何·衔接）.docx",
    "人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx",
    "人教B版选必1·部分封面（第2章 平面解析几何·清单）.docx",
    "人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx",
    "人教B版选必1·部分封面（第2章 平面解析几何·讲练）.docx",
    "人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx",
    "人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx",
    "人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx",
    "人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", default=None, help="冒烟模式：只导名称含此子串的第一件")
    args = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    targets = ALL
    if args.smoke:
        targets = [f for f in ALL if args.smoke in f][:1]
        if not targets:
            raise SystemExit(f"冒烟目标未命中：{args.smoke}")
    rows = []
    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        for name in targets:
            src = os.path.join(SRC_DIR, name)
            out = os.path.join(OUT_DIR, os.path.splitext(name)[0] + ".pdf")
            t0 = time.time()
            d = word.Documents.Open(os.path.abspath(src), ReadOnly=True, AddToRecentFiles=False)
            try:
                d.Repaginate()
                pages = d.ComputeStatistics(2)  # wdStatisticPages
                d.ExportAsFixedFormat(
                    OutputFileName=os.path.abspath(out), ExportFormat=17,
                    OpenAfterExport=False, OptimizeFor=0, Range=0, Item=0,
                    IncludeDocProps=True, KeepIRM=True, CreateBookmarks=1,
                    DocStructureTags=True, BitmapMissingFonts=True,
                    UseISO19005_1=False)
                dt = round(time.time() - t0, 1)
                rows.append({"file": name, "pages_com": pages, "kb": os.path.getsize(out) // 1024, "sec": dt})
                print(f"OK {pages:>4}页 {dt:>6}s {os.path.getsize(out)//1024:>6}KB  {name}")
            finally:
                d.Close(False)
    finally:
        word.Quit()
        pythoncom.CoUninitialize()
    tag = "冒烟" if args.smoke else "全件"
    with open(os.path.join(WORK, "_工作", f"⑤_01_导出记录_{tag}.json"), "w", encoding="utf-8") as f:
        json.dump({"time": datetime.datetime.now().isoformat(timespec="seconds"),
                   "src": SRC_DIR, "out": OUT_DIR, "rows": rows}, f, ensure_ascii=False, indent=1)
    print("DONE", len(rows), "件")


if __name__ == "__main__":
    main()
