# -*- coding: utf-8 -*-
# 终验：四本 PDF 全页页脚连续性断言＋答案本复核
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf

ASM = r"C:\提示词\工作区\M2-第1章量产0911\成卷\装配"
BOOKS = [("导学本.pdf", 1), ("练习本.pdf", 45), ("测评本.pdf", 83), ("答案本.pdf", 90)]
ok_all = True
for fn, start in BOOKS:
    d = pymupdf.open(os.path.join(ASM, fn))
    bad = []
    for i in range(len(d)):
        r = d[i].rect
        foot = d[i].get_text(clip=pymupdf.Rect(0, r.height - 60, r.width, r.height))
        nums = re.findall(r"\d{1,3}", foot.replace(",", ""))
        want = start + i
        cands = {int(x) for x in nums if abs(int(x) - want) <= 1}
        if want not in cands:
            bad.append((i + 1, want, " ".join(foot.split())[:60]))
    n = len(d)
    stat = "全连续 ✓" if not bad else f"异常{len(bad)}处"
    print(f"{fn:<12s} {n:>3d}页 期望{start}~{start+n-1}  {stat}")
    for b in bad[:6]:
        print("   物理", b[0], "期望", b[1], "| 页脚:", b[2])
    ok_all &= not bad
    d.close()
print("断言：", "四本页脚 1-103 连续无断点" if ok_all else "存在断点，见上")
