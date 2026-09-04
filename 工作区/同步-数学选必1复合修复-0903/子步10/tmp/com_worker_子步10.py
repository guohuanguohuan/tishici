# -*- coding: utf-8 -*-
"""COM页数实测worker（逐件一子进程形态）：DispatchEx自建不可见实例、ReadOnly、
Repaginate()后ComputeStatistics(2)（wdStatisticPages），用完Quit。
测完即append一行JSONL（九字段：件名｜路径形态｜原件sha256｜页数｜首节start｜分节数｜各节start清单｜开卷耗时｜时刻）。
用法：com_worker_子步10.py <待测路径> <件名> <路径形态> <原件sha256> <start采集json行> <jsonl路径>"""
import json, sys, time, datetime
import win32com.client

def main():
    path, name, form, sha, start_json, jsonl = sys.argv[1:7]
    sinfo = json.loads(start_json)
    app = win32com.client.DispatchEx("Word.Application")
    app.Visible = False
    app.DisplayAlerts = 0
    doc = None
    try:
        t0 = time.time()
        doc = app.Documents.Open(path, ReadOnly=True, AddToRecentFiles=False,
                                 Visible=False, OpenAndRepair=False)
        open_cost = round(time.time() - t0, 2)
        doc.Repaginate()
        pages = int(doc.ComputeStatistics(2))  # wdStatisticPages
        doc.Close(False)
        doc = None
        line = {"件名": name, "路径形态": form, "原件sha256": sha, "页数": pages,
                "首节start": sinfo["首节start"], "分节数": sinfo["分节数"],
                "各节start清单": sinfo["各节start清单"], "开卷耗时": open_cost,
                "时刻": datetime.datetime.now().isoformat(timespec="milliseconds")}
        with open(jsonl, "a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
        print("WORKER-OK " + json.dumps(line, ensure_ascii=False), flush=True)
    finally:
        if doc is not None:
            try:
                doc.Close(False)
            except Exception:
                pass
        app.Quit()

if __name__ == "__main__":
    main()
