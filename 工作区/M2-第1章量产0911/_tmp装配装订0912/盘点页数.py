# -*- coding: utf-8 -*-
# M2 轮4 装配轮 · 页数盘点＋G7 跨本连续页码链计算
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pypdf import PdfReader

ROOT = r"C:\提示词\工作区\M2-第1章量产0911\成卷"
BOOKS = [
    ("导学本", [
        "导学件/课时01", "导学件/课时02", "导学件/课时03", "导学件/课时04", "导学件/课时05",
        "导学件/衔接节-1.2.1前",
        "导学件/课时06", "导学件/课时07", "导学件/课时08", "导学件/课时09", "导学件/课时10",
        "导学件/章末-本章总结提升",
    ]),
    ("练习本", [
        "练习件/课时01", "练习件/课时02", "练习件/课时03", "练习件/课时04", "练习件/课时05",
        "练习件/课时06", "练习件/课时07", "练习件/课时08", "练习件/课时09", "练习件/课时10",
        "拓展册/上册", "拓展册/下册",
    ]),
    ("测评本", ["测评卷", "滚动卷/滚A", "滚动卷/滚B"]),
    ("答案本", ["答案册"]),
]

page = 1
total = 0
for book, pieces in BOOKS:
    print(f"■ {book}")
    for p in pieces:
        pdf = os.path.join(ROOT, p, "main.pdf")
        n = len(PdfReader(pdf).pages)
        end = page + n - 1
        print(f"  {p:<28s} {n:>3d}页  起始={page:>4d}  区间={page}-{end}")
        page = end + 1
        total += n
print(f"合计 {total} 页（连续页码 1-{total}）")
