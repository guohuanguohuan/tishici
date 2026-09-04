# -*- coding: utf-8 -*-
import zipfile, os, json
BAK = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\tmp\章码重盖前备份"
SYNC = r"C:\提示词\高中数学\高中数学同步"
res = {}
for k, fn in [("C","人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx"),
              ("H","人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx")]:
    a = zipfile.ZipFile(os.path.join(BAK, fn)).read("word/document.xml").decode("utf-8")
    b = zipfile.ZipFile(os.path.join(SYNC, fn)).read("word/document.xml").decode("utf-8")
    # 公共前缀/后缀
    p = 0
    while p < min(len(a), len(b)) and a[p] == b[p]:
        p += 1
    s = 0
    while s < min(len(a) - p, len(b) - p) and a[len(a)-1-s] == b[len(b)-1-s]:
        s += 1
    old_mid = a[p:len(a)-s if s else len(a)]
    new_mid = b[p:len(b)-s if s else len(b)]
    res[k] = {"len_old": len(a), "len_new": len(b), "prefix": p, "suffix": s,
              "ctx_before": a[max(0,p-120):p], "old_mid": old_mid, "new_mid": new_mid,
              "ctx_after": a[len(a)-s:len(a)-s+120] if s else ""}
    print("====", k, "len", len(a), "->", len(b), " 前缀", p, "后缀", s)
    print("CTX前:", a[max(0,p-120):p])
    print("OLD差段:", old_mid)
    print("NEW差段:", new_mid)
    print("CTX后:", (a[len(a)-s:len(a)-s+120] if s else ""))
json.dump(res, open("项10_CH差异.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
