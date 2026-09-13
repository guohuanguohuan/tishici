# -*- coding: utf-8 -*-
"""双档＋压测 log 机械读数（编译三零门＋对号门锚＋页数）。"""
import os, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = os.path.join(HERE, "拓展册")
man = json.load(open(os.path.join(HERE, "试迁键账-拓展.json"), encoding="utf-8"))
EXPECT = set(man["键值"])

TARGETS = ["main", "main-换装-true", "main-换装-false",
           "压测A-三栏灰底-true", "压测B-两栏括线-true", "压测C-三栏括线-true"]

allok = True
for base in TARGETS:
    log = open(os.path.join(PIECE, base + ".log"), encoding="utf-8", errors="ignore").read()
    err = len(re.findall(r"^!", log, re.M))
    ovf = len(re.findall(r"^Overfull", log, re.M))
    und = len(re.findall(r"^Underfull", log, re.M))
    mch = len(re.findall(r"Missing character", log))
    keys = re.findall(r"M3-ANSKEY: (.+)", log)
    m = re.search(r"Output written on .+ \((\d+) page", log)
    pages = m.group(1) if m else "?"
    uniq = sorted(set(keys))
    ok = (err == 0 and ovf == 0 and und == 0 and mch == 0)
    keyok = True
    if base not in ("main",):
        keyok = (len(uniq) == 46 and set(uniq) == EXPECT and len(keys) == len(uniq))
    if base == "main":
        keyok = (len(keys) == 0)
    allok &= (ok and keyok)
    print("%-22s 三零=%s 0/0/0/0=%d/%d/%d/%d 页数=%s ANSKEY=%d(uniq%d 对账=%s)" % (
        base, "PASS" if ok else "FAIL", err, ovf, und, mch, pages,
        len(keys), len(uniq), "—" if base == "main" else ("PASS" if keyok else "FAIL")))
print("ALL:", "PASS" if allok else "FAIL")
