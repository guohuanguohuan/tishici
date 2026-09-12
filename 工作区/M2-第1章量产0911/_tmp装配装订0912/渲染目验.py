# -*- coding: utf-8 -*-
# M2 轮4 装配轮 · 六件改动页渲染目验（150dpi）
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf

ROOT = r"C:\提示词\工作区\M2-第1章量产0911\成卷"
OUT = r"C:\提示词\工作区\M2-第1章量产0911\_tmp装配装订0912\目验"
os.makedirs(OUT, exist_ok=True)

JOBS = [
    ("拓展册/上册",  range(1, 6)),
    ("拓展册/下册",  range(12, 14)),
    ("练习件/课时06", range(1, 3)),
    ("练习件/课时07", [2]),
    ("练习件/课时08", [1]),
    ("练习件/课时10", [2]),
]
KEYS = {  # 页定位关键词（验证删语/图位落点）
    "拓展册/上册": ["D为原点", "如图"],
    "拓展册/下册": ["如图"],
    "练习件/课时06": ["如图"],
    "练习件/课时07": ["如图"],
    "练习件/课时08": ["如图"],
    "练习件/课时10": ["如图"],
}
for rel, pages in JOBS:
    doc = pymupdf.open(os.path.join(ROOT, rel, "main.pdf"))
    hits = {k: [] for k in KEYS.get(rel, [])}
    for i in range(len(doc)):
        txt = doc[i].get_text()
        for k in KEYS.get(rel, []):
            if k in txt:
                hits[k].append(i + 1)
    print(f"== {rel}（{len(doc)}页）关键词页分布: {hits}")
    tag = rel.replace("/", "_")
    for pno in pages:
        if pno <= len(doc):
            pg = doc[pno - 1]
            pix = pg.get_pixmap(dpi=150)
            fp = os.path.join(OUT, f"{tag}_p{pno}.png")
            pix.save(fp)
    doc.close()
print("渲染完成 →", OUT)
