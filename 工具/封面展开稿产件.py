# -*- coding: utf-8 -*-
"""封面展开稿产件.py — 封面＋封底＋书脊连体展开稿 PDF 直产（CB-6；PyMuPDF，不经 Word）

幅面＝(210×2＋书脊宽)mm × 297mm，四周 3mm 出血；书脊宽参数化（默认 20mm，
70g 纸 415 页≈208 张预估，以店家实测纸厚为准，--spine-mm 调）。
布局：展开稿外侧面——左＝封底，中＝书脊（文字竖排），右＝封面。
封面文字照抄既有封面件：高中同步讲练／人教B版选必1／数　学／版次：2026年08月／
内部资料·仅供教学使用；主视觉＝部分封面章主题图（图内零文字，默认自动从
--cover-docx 的 word/media/image1.png 提取），置封面中下部；封底留白，
仅置「内部资料·仅供教学使用」＋系列书目预留行占位一行。
字体默认系统宋体 simsun.ttc（嵌入 PDF）；安全边距默认 5mm（口径未定量，参数可调）。
辅助线（裁切线/书脊折线/区域标注）默认画在出血区，--no-guides 关闭。

用法：
  python 工具/封面展开稿产件.py [--spine-mm 20] [--bleed-mm 3] [--safety-mm 5]
      [--image 主题图.png] [--cover-docx 部分封面.docx] [--out out.pdf] [--png prev.png]
      [--dpi 110] [--no-guides]
"""
import sys, io, os, argparse, zipfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import pymupdf

MM = 72.0 / 25.4
DEFAULT_FONT = r"C:\Windows\Fonts\simsun.ttc"
DEFAULT_COVER_DOCX = (r"高中数学\高中数学同步"
                      r"\人教B版选必1·部分封面（第1章 空间向量与立体几何·清单）.docx")
DEFAULT_OUT = r"工作区\选必1成书修复-0905\阶段④\封面展开稿-预览.pdf"
DEFAULT_PNG = r"工作区\选必1成书修复-0905\阶段④\封面展开稿-预览.png"

COVER_LINES_TOP = [("高中同步讲练", 22.0, 28.0), ("人教B版选必1", 26.0, 46.0)]
COVER_TITLE = ("数　学", 54.0, 86.0)          # 封面主名（大字）
COVER_LINES_BOTTOM = [("版次：2026年08月", 12.0, 22.0),
                      ("内部资料·仅供教学使用", 12.0, 14.0)]  # 距裁切底边 mm
BACK_LINES_BOTTOM = [("内部资料·仅供教学使用", 12.0, 22.0),
                     ("系列书目：（预留）", 12.0, 14.0)]      # 新固定文案，待过目
SPINE_TEXT = "高中同步讲练 数学 人教B版选必1"  # 新固定文案（竖排），待过目
IMAGE_WIDTH_MM = 110.0
IMAGE_TOP_MM = 108.0


def put_center(page, font, fontfile, cx, baseline_y, text, size, color=(0, 0, 0)):
    w = font.text_length(text, fontsize=size)
    page.insert_text((cx - w / 2, baseline_y), text, fontname="F0",
                     fontfile=fontfile, fontsize=size, color=color)


def main():
    ap = argparse.ArgumentParser(description="封面＋封底＋书脊连体展开稿产件（CB-6）")
    ap.add_argument("--spine-mm", type=float, default=20.0, help="书脊宽 mm（默认20，以店家实测纸厚为准）")
    ap.add_argument("--bleed-mm", type=float, default=3.0, help="四周出血 mm（默认3）")
    ap.add_argument("--safety-mm", type=float, default=5.0, help="安全边距 mm（默认5，口径未定量）")
    ap.add_argument("--font", default=DEFAULT_FONT, help="中文字体文件（默认 simsun.ttc）")
    ap.add_argument("--image", default=None, help="主视觉 PNG；缺省则从 --cover-docx 提取 image1.png")
    ap.add_argument("--cover-docx", default=DEFAULT_COVER_DOCX, help="部分封面 docx（只读取图）")
    ap.add_argument("--out", default=DEFAULT_OUT, help="输出 PDF 路径")
    ap.add_argument("--png", default=DEFAULT_PNG, help="PNG 预览路径（空串不渲染）")
    ap.add_argument("--dpi", type=int, default=110, help="预览 PNG 分辨率")
    ap.add_argument("--no-guides", action="store_true", help="不画裁切/折线/区域标注辅助线")
    args = ap.parse_args()

    if not os.path.exists(args.font):
        raise SystemExit(f"ERROR: 字体不可用：{args.font}")
    font = pymupdf.Font(fontfile=args.font)
    print(f"字体：{font.name}（{args.font}，将嵌入）")

    spine, bleed = args.spine_mm * MM, args.bleed_mm * MM
    pw = (420 + args.spine_mm + 2 * args.bleed_mm) * MM   # 页面总宽（含出血）
    ph = (297 + 2 * args.bleed_mm) * MM
    trim = pymupdf.Rect(bleed, bleed, bleed + (420 + args.spine_mm) * MM, bleed + 297 * MM)
    x_back0, x_back1 = trim.x0, trim.x0 + 210 * MM        # 封底（左）
    x_sp0, x_sp1 = x_back1, x_back1 + spine               # 书脊（中）
    x_fr0, x_fr1 = x_sp1, trim.x1                         # 封面（右）
    cx_back, cx_sp, cx_fr = (x_back0 + x_back1) / 2, (x_sp0 + x_sp1) / 2, (x_fr0 + x_fr1) / 2

    doc = pymupdf.open()
    page = doc.new_page(width=pw, height=ph)

    # ---- 封面文字（照抄既有封面件） ----
    for text, size, top_mm in COVER_LINES_TOP:
        put_center(page, font, args.font, cx_fr, trim.y0 + top_mm * MM, text, size)
    text, size, top_mm = COVER_TITLE
    put_center(page, font, args.font, cx_fr, trim.y0 + top_mm * MM, text, size)
    for text, size, bot_mm in COVER_LINES_BOTTOM:
        put_center(page, font, args.font, cx_fr, trim.y1 - bot_mm * MM, text, size)

    # ---- 主视觉（章主题图，图内零文字）置封面中下部 ----
    img_stream = None
    if args.image:
        img_stream = open(args.image, "rb").read()
        img_src = args.image
    elif os.path.exists(args.cover_docx):
        with zipfile.ZipFile(args.cover_docx) as z:
            img_stream = z.read("word/media/image1.png")
        img_src = args.cover_docx + "#word/media/image1.png"
    if img_stream:
        pix = pymupdf.Pixmap(img_stream)
        iw = IMAGE_WIDTH_MM * MM
        ih = iw * pix.height / pix.width
        rect = pymupdf.Rect(cx_fr - iw / 2, trim.y0 + IMAGE_TOP_MM * MM,
                            cx_fr + iw / 2, trim.y0 + IMAGE_TOP_MM * MM + ih)
        page.insert_image(rect, stream=img_stream)
        print(f"主视觉：{img_src}（{pix.width}×{pix.height}px → "
              f"{IMAGE_WIDTH_MM:.0f}×{ih / MM:.0f}mm，封面中下部）")
    else:
        print("WARN: 无主视觉图（--image/--cover-docx 均不可用），封面图位留空")

    # ---- 书脊文字竖排（字宽超书脊净宽自动缩号，封顶 12pt、保底 6pt） ----
    pt = max(min(12.0, (args.spine_mm - 3.0) * 72 / 25.4), 6.0)
    y = trim.y0 + 30 * MM
    for ch in SPINE_TEXT:
        if ch == " ":
            y += pt * 0.9
            continue
        w = font.text_length(ch, fontsize=pt)
        page.insert_text((cx_sp - w / 2, y + pt), ch, fontname="F0",
                         fontfile=args.font, fontsize=pt)
        y += pt * 1.14
    print(f"书脊：宽 {args.spine_mm:g}mm，竖排「{SPINE_TEXT}」，字号 {pt:.1f}pt")

    # ---- 封底（留白，仅声明行＋系列书目预留行） ----
    for text, size, bot_mm in BACK_LINES_BOTTOM:
        put_center(page, font, args.font, cx_back, trim.y1 - bot_mm * MM, text, size)

    # ---- 辅助线（出血区内，供店家对位；--no-guides 关闭） ----
    if not args.no_guides:
        g = (0.55, 0.55, 0.55)
        page.draw_rect(trim, color=g, width=0.6)                       # 裁切线
        for x in (x_sp0, x_sp1):                                       # 书脊折线
            page.draw_line((x, trim.y0), (x, trim.y1), color=g, width=0.5,
                           dashes="[3 3] 0")
        for cx, label in ((cx_back, "封底"), (cx_fr, "封面")):
            put_center(page, font, args.font, cx, bleed * 0.8, label, 6.5, g)
            put_center(page, font, args.font, cx, ph - bleed * 0.2, label, 6.5, g)
        put_center(page, font, args.font, cx_sp, bleed * 0.8,
                   f"书脊 {args.spine_mm:g}mm", 6.5, g)
        page.insert_text((trim.x1 + 1 * MM, trim.y0 + 4 * MM),
                         f"出血{args.bleed_mm:g}mm", fontname="F0",
                         fontfile=args.font, fontsize=6.5, color=g)
        s = args.safety_mm * MM                                        # 安全边距（点线）
        for x0, x1 in ((x_back0, x_back1), (x_fr0, x_fr1)):
            page.draw_rect(pymupdf.Rect(x0 + s, trim.y0 + s, x1 - s, trim.y1 - s),
                           color=(0.75, 0.75, 0.75), width=0.4, dashes="[1 3] 0")

    doc.set_metadata({"title": f"封面展开稿（书脊{args.spine_mm:g}mm）",
                      "producer": "封面展开稿产件.py"})
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    doc.save(args.out, deflate=True)
    doc.close()
    print(f"幅面：{(420 + args.spine_mm + 2 * args.bleed_mm):g}mm × "
          f"{297 + 2 * args.bleed_mm:g}mm（含出血）→ {args.out}")

    if args.png:
        d = pymupdf.open(args.out)
        d[0].get_pixmap(dpi=args.dpi).save(args.png)
        d.close()
        print(f"预览 PNG：{args.png}（{args.dpi}dpi）")


if __name__ == "__main__":
    main()
