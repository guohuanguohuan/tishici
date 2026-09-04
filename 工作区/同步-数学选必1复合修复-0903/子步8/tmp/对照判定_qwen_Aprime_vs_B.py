# -*- coding: utf-8 -*-
# qwen臂 对照判定：A′(tmp副本输入) vs B(codex已登记10件43条) 逐件逐字段对照
import json, sys

APRIME = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步8\tmp\复测_配置Aprime.json"
B = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步8\复测_补签_codex\复测_配置B.json"
FIELDS = ["no", "title", "in_page", "part_page"]

with open(APRIME, "r", encoding="utf-8") as f:
    a = json.load(f)
with open(B, "r", encoding="utf-8") as f:
    b = json.load(f)

af, bf = a["files"], b["files"]
na = sum(len(x["sections"]) for x in af)
nb = sum(len(x["sections"]) for x in bf)
print("件数 A'=%d B=%d | 记录数 A'=%d B=%d" % (len(af), len(bf), na, nb))

alive = sum(1 for x in af if x["sections"] and not x.get("zero_hit", False))
print("A'出数件数=%d/10（C4证伪条款触发条件=0/10）" % alive)

# 任务书§5对照面＝sections的no/title/in_page/part_page逐字段全等＋件数/记录数一致；
# 件级name/start/tag/path为输入配置回声字段，不在对照面内（A′沿模板短名，B跑全称），仅按位配对。
diffs = []
if len(af) != len(bf):
    diffs.append("件数不等")
for i in range(min(len(af), len(bf))):
    x, y = af[i], bf[i]
    if len(x["sections"]) != len(y["sections"]):
        diffs.append("件%d(%s~%s) sections数不等: %d vs %d" % (i + 1, x["name"], y["name"], len(x["sections"]), len(y["sections"])))
        continue
    for j, (sx, sy) in enumerate(zip(x["sections"], y["sections"]), 1):
        for k in FIELDS:
            if sx.get(k) != sy.get(k):
                diffs.append("件%d(%s) 节%s 字段%s不等: %r vs %r" % (i + 1, x["name"], sx.get("no", j), k, sx.get(k), sy.get(k)))
    if x.get("zero_hit") != y.get("zero_hit"):
        diffs.append("件%d(%s) zero_hit不等: %r vs %r" % (i + 1, x["name"], x.get("zero_hit"), y.get("zero_hit")))
    if x.get("in_file_pages") != y.get("in_file_pages"):
        diffs.append("件%d(%s) in_file_pages不等: %r vs %r" % (i + 1, x["name"], x.get("in_file_pages"), y.get("in_file_pages")))

if diffs:
    print("DIFFS %d" % len(diffs))
    for d in diffs[:40]:
        print("  " + d)
    print("VERDICT=FAIL")
    sys.exit(1)
print("逐件逐节四字段(no/title/in_page/part_page)全等 + 件数/记录数一致")
print("VERDICT=PASS")
