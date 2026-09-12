# -*- coding: utf-8 -*-
# P1 装配轮·终验：五本 PDF 全页页脚连续性断言（跨本连续 1~48）＋学史薄本自页码复核
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf

ASM = r"C:\提示词\工作区\P1-必修3第9章量产0912\成卷\装配"
BOOKS = [("导学本.pdf", 1), ("练习本.pdf", 17), ("拓展本.pdf", 31), ("测评本.pdf", 41), ("答案本.pdf", 44)]
ok_all = True
chain = 1
for fn, start in BOOKS:
    d = pymupdf.open(os.path.join(ASM, fn))
    assert start == chain, (fn, start, chain)
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
    chain = start + n
    d.close()
d = pymupdf.open(os.path.join(ASM, "学史切片.pdf"))
foot = d[0].get_text(clip=pymupdf.Rect(0, d[0].rect.height - 60, d[0].rect.width, d[0].rect.height))
has1 = "1" in re.findall(r"\d+", foot)
print(f"学史切片.pdf   {len(d)}页 独立页码制·页脚含1＝{'✓' if has1 else '✗ ' + repr(foot)}")
d.close()
print(f"断言：五本页脚 1-{chain-1} 连续无断点＝{'✓' if ok_all else '✗ 存在断点'}；合计 {chain-1} 页")
