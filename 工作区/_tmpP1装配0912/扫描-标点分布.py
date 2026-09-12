# -*- coding: utf-8 -*-
# 装配轮·义6-2 前期扫描：各件正文（去注释行）句号「。」与半角句末「. 」分布计数
import io, sys, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = r"C:\提示词\工作区\P1-必修3第9章量产0912\成卷"
FILES = [
    ("导学9.1", "导学件/9.1电荷/main.tex"), ("导学9.2", "导学件/9.2库仑定律/main.tex"),
    ("导学9.3", "导学件/9.3电场电场强度/main.tex"), ("导学9.4", "导学件/9.4静电的防止与利用/main.tex"),
    ("练习9.1", "练习件/9.1电荷/main.tex"), ("练习9.2", "练习件/9.2库仑定律/main.tex"),
    ("练习9.3", "练习件/9.3电场电场强度/main.tex"), ("练习9.4", "练习件/9.4静电的防止与利用/main.tex"),
    ("章末", "章末-本章易错过关/main.tex"), ("拓展册", "拓展册/main.tex"),
    ("测评卷", "测评卷/main.tex"), ("学史切片", "学史切片/第9章静电学史/main.tex"),
    ("答案册body", "答案册/body.tex"),
]
CLS = "[" + "\u4e00-\u9fff）】》”" + "]"
re_half = re.compile(CLS + r"\.(?![a-zA-Z0-9])")
for name, f in FILES:
    t = open(os.path.join(ROOT, f), encoding="utf-8").read()
    lines = [re.sub(r"(?<!\\)%.*$", "", l) for l in t.splitlines()]
    body = "\n".join(lines)
    full = body.count("\u3002")
    half = len(re_half.findall(body))
    print(f"{name}\t「。」={full}\tCJK后半角「.」={half}")
