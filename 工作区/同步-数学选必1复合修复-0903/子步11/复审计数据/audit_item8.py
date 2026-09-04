# -*- coding: utf-8 -*-
import re, os, json, zipfile
from lxml import etree
WS = r"C:\提示词\工作区\同步-数学选必1复合修复-0903"
r8 = {}
t = open(WS + r"\子步11\P2P3脚本门_结果.txt", encoding="utf-8").read()
lines = t.splitlines()
r8["P2P3"] = {"tail_line": lines[-1], "has_全绿": "全绿" in lines[-1],
              "count_✓": sum(1 for l in lines if "✓" in l),
              "count_✗": sum(1 for l in lines if "✗" in l)}
t3 = open(WS + r"\子步11\P3配页前检查_结果.md", encoding="utf-8").read()
r8["P3配页前检查"] = {"has_①": "①" in t3, "has_③": "③" in t3, "has_⑤": "⑤" in t3,
                      "has_⑥": "⑥" in t3, "has_PASS": "[PASS]" in t3}
tg = open(WS + r"\子步11\盖章记录_子步11.md", encoding="utf-8").read()
r8["盖章记录"] = {"has_修订3": "修订3" in tg, "has_时间戳字样": "时间戳" in tg,
                  "声明不含时间戳": "本记录不含时间戳" in tg, "n_lines": len(tg.splitlines())}
pj = json.load(open(WS + r"\子步11\parts_选必1_现行.json", encoding="utf-8"))
r8["parts_footer_twips_keys"] = sorted(pj.get("footer_twips", {}).keys())
import datetime
for tag, p in [("P2P3", WS+r"\子步11\P2P3脚本门_结果.txt"), ("P3", WS+r"\子步11\P3配页前检查_结果.md"),
               ("盖章", WS+r"\子步11\盖章记录_子步11.md"), ("parts", WS+r"\子步11\parts_选必1_现行.json")]:
    mt = os.stat(p).st_mtime
    r8.setdefault("mtime", {})[tag] = datetime.datetime.fromtimestamp(mt).isoformat()
r8["window"] = "2026-09-04T00:00:00 <= mtime <= 2026-09-05T23:59:59"
r8["mtime_in_window"] = {k: ("2026-09-04" <= v[:10] <= "2026-09-05") for k, v in r8["mtime"].items()}

# 项6补测：B件全文层 x=1z=-2 / x=1z=−2 缺席；解得x=-1z=2 在全文(w:t+m:t)层
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
z = zipfile.ZipFile(r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx")
root = etree.fromstring(z.read("word/document.xml"))
def nows(s): return re.sub(r"\s+", "", s)
allt = nows("".join(n.text or "" for n in root.iter() if n.tag in (W+"t", M+"t")))
allm = nows("".join(n.text or "" for n in root.iter() if n.tag == M+"t"))
r8["item6_extra"] = {
 "fulltext(w:t+m:t) 含解得x=-1z=2": "解得x=-1z=2" in allt,
 "fulltext 含解得x=−1z=2(U2212)": "解得x=−1z=2" in allt,
 "fulltext 含x=1z=-2": "x=1z=-2" in allt, "fulltext 含x=1z=−2": "x=1z=−2" in allt,
 "全件m:t 含解得x=-1z=2": "解得x=-1z=2" in allm,
 "全件m:t 含x=-1z=2": "x=-1z=2" in allm,
 "全件m:t 含x=1z=-2": "x=1z=-2" in allm, "全件m:t 含x=1z=−2": "x=1z=−2" in allm}
json.dump(r8, open("自测_item8_item6extra.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(r8, ensure_ascii=False, indent=1))
