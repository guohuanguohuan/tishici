# -*- coding: utf-8 -*-
import hashlib, os, json, sys
ROOT = r"C:\提示词"
SYNC = ROOT + r"\高中数学\高中数学同步"
WS = ROOT + r"\工作区\同步-数学选必1复合修复-0903"
DOCX = {
 "X1": r"人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx",
 "I1": r"人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx",
 "B":  r"人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx",
 "C":  r"人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx",
 "X2": r"人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx",
 "I2": r"人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx",
 "E":  r"人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx",
 "F":  r"人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx",
 "G":  r"人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx",
 "H":  r"人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx",
}
PDFS = ["X1","I1","B","C","X2","I2","E","F","G","H","FM","SM","ML","FQ1","FQ2","FQ3","FQ4","FQ5","FQ6"]
paths = []
for k,v in DOCX.items(): paths.append((k, SYNC+"\\"+v))
for k in PDFS: paths.append(("pdf_"+k, WS+r"\pages_406\pdf\\"+k+".pdf"))
paths += [
 ("P2P3脚本门", WS+r"\子步11\P2P3脚本门_结果.txt"),
 ("P3配页前检查", WS+r"\子步11\P3配页前检查_结果.md"),
 ("盖章记录", WS+r"\子步11\盖章记录_子步11.md"),
 ("parts_json", WS+r"\子步11\parts_选必1_现行.json"),
 ("tool_册级连续页码", ROOT+r"\工具\册级连续页码.py"),
 ("tool_本厚复核", ROOT+r"\工具\本厚复核.py"),
 ("附则_页脚零占位例外", ROOT+r"\附则\页脚零占位例外.md"),
 ("快照json", WS+r"\tmp\章码重盖前备份\_快照.json"),
]
out = {}
for tag, p in paths:
    if not os.path.exists(p):
        out[tag] = {"path": p, "ERROR": "MISSING"}; continue
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""): h.update(chunk)
    st = os.stat(p)
    out[tag] = {"path": p, "sha256": h.hexdigest(), "size": st.st_size,
                "mtime": st.st_mtime, "mtime_iso": __import__("datetime").datetime.fromtimestamp(st.st_mtime).isoformat()}
with open(sys.argv[1] if len(sys.argv)>1 else "基线_guard.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(len(out), "files guarded")
for k,v in out.items():
    print(k, v.get("size"), v.get("mtime_iso",""), v.get("sha256","")[:16], v.get("ERROR",""))
