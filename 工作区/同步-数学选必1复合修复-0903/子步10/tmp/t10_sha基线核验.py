# -*- coding: utf-8 -*-
"""T1.0 十件原件sha256 vs 子步7盖章态基线（写回sha_子步7.json new列）逐件比对。
另登记体积（§12体积判据用）。只读。"""
import hashlib, json, os, sys

BASE = r"C:\提示词\高中数学\高中数学同步"
BASELINE = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步7\写回sha_子步7.json"
OUT = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步10\tmp\t10_sha比对.json"

with open(BASELINE, encoding="utf-8") as f:
    base = json.load(f)

rows = []
all_eq = True
for name in base:
    p = os.path.join(BASE, name)
    if not os.path.exists(p):
        rows.append({"件": name, "存在": False})
        all_eq = False
        continue
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    sha = h.hexdigest()
    exp = base[name]["new"]
    eq = sha == exp
    all_eq = all_eq and eq
    rows.append({"件": name, "存在": True, "sha256": sha, "基线new": exp,
                 "全等": eq, "体积字节": os.path.getsize(p),
                 "mtime": os.path.getmtime(p)})

# 件集谓词核验：目录内docx总数 + 「人教B版选必1 第」开头件数
docs = [n for n in os.listdir(BASE) if n.lower().endswith(".docx")]
pred = [n for n in docs if n.startswith("人教B版选必1 第")]
result = {"十件全等": all_eq, "目录docx总数": len(docs),
          "谓词件数": len(pred), "谓词清单": sorted(pred), "逐件": rows}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
print(f"十件全等={all_eq} 目录docx={len(docs)} 谓词件数={len(pred)}")
for r in rows:
    if r.get("存在"):
        print(("EQ " if r["全等"] else "NE ") + r["件"][:44] + f"  {r['体积字节']}")
    else:
        print("MISS " + r["件"])
sys.exit(0 if all_eq and len(docs) == 26 and len(pred) == 10 else 1)
