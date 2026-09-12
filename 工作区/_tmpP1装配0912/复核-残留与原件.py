# -*- coding: utf-8 -*-
# 装配轮·清扫残留复核：各副本正文（去注释·数学段除外）应零「。」零半角句末「.」；原件应零改动
import io, sys, re, os, glob, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = r"C:\提示词\工作区\P1-必修3第9章量产0912\成卷"
CLS = "\u4e00-\u9fff，、；：）】《》"
def resid(f):
    t = open(f, encoding="utf-8").read()
    code = "\n".join(re.sub(r"(?<!\\)%.*$", "", l) for l in t.splitlines())
    code_nomath = re.sub(r"\$[^$]*\$", "", code)
    return code_nomath.count("。"), len(re.findall("[" + CLS + r"]\.(?![0-9A-Za-z])", code_nomath))
print("--- 装配副本 ---")
for f in sorted(glob.glob(os.path.join(ROOT, "装配", "*", "main.tex")) + glob.glob(os.path.join(ROOT, "装配", "*", "*", "main.tex")) + glob.glob(os.path.join(ROOT, "装配", "答案本", "答案册", "body.tex"))):
    n, h = resid(f)
    flag = "OK" if n == 0 and h == 0 else "**残留**"
    print(os.path.relpath(f, ROOT), f"。={n} 半角={h}", flag)
print("--- 原件 md5 复核（应与收尾记录终态一致·零改动） ---")
for rel, want in [("拓展册/main.tex", "492e403cec2dfcdcc46c9821790ad4c6"),
                  ("测评卷/main.tex", "661a14b09428e4160ad56291fca279e6"),
                  ("答案册/body.tex", "67fba08a4ce34ab24a837b147b581fef"),
                  ("答案册/main.tex", "0e6b473614b8a74f6ade198f2ba7e427")]:
    d = hashlib.md5(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()
    print(rel, d, "OK" if d == want else "**CHANGED**")
