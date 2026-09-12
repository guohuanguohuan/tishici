# -*- coding: utf-8 -*-
# 装配轮·义6-2 前期扫描 v2：测评卷半角句末点位＋速查表区＋各件「。」明细行
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
CLS = "[一-鿿（）】《》“”、；：，！？·×∼～”]"
re_half = re.compile(CLS + r"\.(?!\d)(?![a-zA-Z])")

def code_only(l):
    return re.sub(r"(?<!\\)%.*$", "", l)

ROOT = r"C:\提示词\工作区\P1-必修3第9章量产0912\成卷"
import os
targets = [("测评卷", "测评卷/main.tex"), ("练习9.1", "练习件/9.1电荷/main.tex"),
           ("练习9.2", "练习件/9.2库仑定律/main.tex"), ("练习9.4", "练习件/9.4静电的防止与利用/main.tex"),
           ("章末", "章末-本章易错过关/main.tex"), ("学史", "学史切片/第9章静电学史/main.tex"),
           ("答案body", "答案册/body.tex"), ("答案main", "答案册/main.tex"),
           ("拓展册", "拓展册/main.tex"), ("导学9.1", "导学件/9.1电荷/main.tex")]
for name, f in targets:
    lines = open(os.path.join(ROOT, f), encoding="utf-8").read().splitlines()
    print(f"======== {name} ========")
    for i, l in enumerate(lines, 1):
        c = code_only(l)
        n_full = c.count("。")
        hits = list(re_half.finditer(c))
        if n_full or hits:
            tag = f"。x{n_full}" if n_full else ""
            if hits:
                tag += " HALF:" + "；".join(c[max(0, m.start()-14):m.end()+4] for m in hits)
            print(f"  L{i} {tag[:150]}")
