# -*- coding: utf-8 -*-
# qwen臂 派生配置A′：以codex _输入_配置A.json为模板，十件path全部改指tmp全同副本；name/tag/start逐字段不动
import json, os

TPL = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步8\复测_补签_codex\_输入_配置A.json"
DST_DIR = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步8\tmp\原件全同副本"
OUT = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步8\tmp\_输入_配置A_全同副本.json"

with open(TPL, "r", encoding="utf-8") as f:
    items = json.load(f)

assert len(items) == 10, "模板件数!=10"
new = []
for it in items:
    p = it["path"]
    npath = os.path.join(DST_DIR, os.path.basename(p))
    assert os.path.isfile(npath), "副本缺失: " + npath
    assert it["start"] is None, "start非null: " + it["name"]
    new.append({"path": npath, "start": it["start"], "name": it["name"], "tag": it["tag"]})

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(new, f, ensure_ascii=False, indent=2)
    f.write("\n")

print("WROTE", OUT)
for it in new:
    print("%s\t%s" % (it["name"], it["path"]))
