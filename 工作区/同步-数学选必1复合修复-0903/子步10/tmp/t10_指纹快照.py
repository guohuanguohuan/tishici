# -*- coding: utf-8 -*-
"""零改动自证指纹快照：高中数学同步目录全部文件＋关键体系/工具件 sha256+mtime。
用法：t10_指纹快照.py <out.json>；收尾重跑比对。"""
import hashlib, json, os, sys

ROOTS_FILE = [
    r"C:\提示词\高中数学\高中数学同步",
]
EXTRA = [
    r"C:\提示词\公共规则.md",
    r"C:\提示词\高中同步总控.md",
    r"C:\提示词\进度看板.md",
    r"C:\提示词\工具\本厚复核.py",
    r"C:\提示词\工具\册级连续页码.py",
    r"C:\提示词\工具\节页码定位.py",
    r"C:\提示词\工具\COM页数实测.py",
    r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步7\写回sha_子步7.json",
    r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步7\盖章记录_子步7.md",
    r"C:\提示词\工作区\同步-数学选必1复合修复-0903\报告-子步7.md",
    r"C:\提示词\工作区\同步-数学选必1复合修复-0903\报告-子步9.md",
]

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

snap = {}
for root in ROOTS_FILE:
    for dirpath, _dirs, files in os.walk(root):
        for n in files:
            p = os.path.join(dirpath, n)
            snap[p] = {"sha256": sha(p), "mtime": os.path.getmtime(p),
                       "size": os.path.getsize(p)}
for p in EXTRA:
    if os.path.exists(p):
        snap[p] = {"sha256": sha(p), "mtime": os.path.getmtime(p),
                   "size": os.path.getsize(p)}
    else:
        snap[p] = {"缺失": True}
with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(snap, f, ensure_ascii=False, indent=1)
print(f"快照文件数={len(snap)}")
