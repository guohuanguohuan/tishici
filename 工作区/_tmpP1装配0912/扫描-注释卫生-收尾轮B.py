# -*- coding: utf-8 -*-
"""收尾轮B·注释卫生门自查扫描（成卷原件链，装配/ 除外——副本随装配重生后再扫）。
门规＝附则/内容质量闸.md 行128：注释/头注段禁止携带答案键值、选项判读结论、解法关键中间值。
探测口径承 处理轮 剥注-答案值.py 硬闸（答案+字母）并扩 ＝=/：/数字 与判读短语；命中仅报不改。"""
import io, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = sys.argv[1] if len(sys.argv) > 1 else r"C:\提示词\工作区\P1-必修3第9章量产0912\成卷"

PATS = [
    (re.compile(r"答案[\s　]*[＝=：:]?\s*[A-DＡ-Ｄ<＜]"), "答案+键字母"),
    (re.compile(r"答案[\s　]*[＝=：:]?\s*[0-9]"), "答案+数字"),
    (re.compile(r"印面答案[^｜\n]*[A-DＡ-Ｄ]"), "印面答案+键"),
    (re.compile(r"【答案】"), "【答案】段"),
    (re.compile(r"(正解|应选|故选|正确答案)[^\n]{0,8}[A-DＡ-Ｄ]{1,4}(?![A-Za-z])"), "判读短语+键"),
]

def comment_of(line):
    m = re.search(r"(?<!\\)%", line)
    return line[m.start():] if m else (line if line.lstrip().startswith("%") else "")

hits = []
for root, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in ("png", "__pycache__", "figs")]
    for fn in files:
        if not fn.endswith(".tex"):
            continue
        p = os.path.join(root, fn)
        with io.open(p, encoding="utf-8") as f:
            for i, ln in enumerate(f.read().split("\n"), 1):
                c = comment_of(ln)
                if not c:
                    continue
                for pat, tag in PATS:
                    if pat.search(c):
                        hits.append((os.path.relpath(p, ROOT), i, tag, c.strip()[:100]))
if hits:
    print("命中 %d 处（人工复核）：" % len(hits))
    for f, i, tag, c in hits:
        print("  %s:%d [%s] %s" % (f, i, tag, c))
else:
    print("注释卫生扫描（%s）：0 命中（口径＝答案+键字母/数字、印面答案、【答案】、判读短语+键）" % ROOT)
