"""物理骨架渲染链（0911）：pdf → png 目验出图。

用法（件目录内）：
    python ../render.py                # 本目录 main.pdf → png/pageN.png @300dpi
    python C:/提示词/工作区/物理样张0911/骨架/render.py 件目录   # 指件目录
    python .../render.py 件目录 名称 300  # 名称=pdf 基名（默认 main）；dpi 默认 300
先清 png/ 再出图（沿数学 L1 render.py 纪律）；dpi 参数化——L1 各件默认 150，物理样张线
按任务书出 300dpi 目验档。
"""
import os
import sys
import glob
import pymupdf

here = os.path.dirname(os.path.abspath(__file__))
casedir = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else here
base = sys.argv[2] if len(sys.argv) > 2 else "main"
dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 300

pdf = os.path.join(casedir, base + ".pdf")
png = os.path.join(casedir, "png")
os.makedirs(png, exist_ok=True)
for f in glob.glob(os.path.join(png, "*.png")):
    os.remove(f)

doc = pymupdf.open(pdf)
for i, page in enumerate(doc, 1):
    out = os.path.join(png, "page%d.png" % i)
    page.get_pixmap(dpi=dpi).save(out)
    print("wrote", out)
