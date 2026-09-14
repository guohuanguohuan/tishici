# -*- coding: utf-8 -*-
"""巡检两项.py — 维护轮调研臂只读扫描器（2026-09-14）
  ①跨栏选项：选项行（A~D．）落栏顶且与同组/题干跨栏分离（承 M2 S7 §八-4 判据 y<66pt 细化）
  ②标题孤字：标题/加粗条目块末行仅落单字（承 M2 S7 §八-2 口径程序化重建）
输入全只读；输出（JSON＋命中裁片 PNG）仅写本目录。零 git。
用法: python 巡检两项.py
"""
import pymupdf, re, os, json, sys
sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))

def _m3_exercise():
    import glob
    out = []
    for d in sorted(glob.glob(r"C:\提示词\工作区\M3-第2章量产0913\成卷\练习件\*")):
        p = os.path.join(d, "main-true.pdf")
        if os.path.exists(p):
            out.append((os.path.basename(d), p))
    return out

BOOKS = [
    # (书名, glob)
    ("M2练习本-下册", r"C:\提示词\工作区\_tmp换装正装0914\M2练习本\下册\main.pdf"),
    ("M2练习本-上册", r"C:\提示词\工作区\_tmp换装正装0914\M2练习本\上册\main.pdf"),
] + [
    (f"M2练习本-课时{i:02d}", rf"C:\提示词\工作区\_tmp换装正装0914\M2练习本\课时{i:02d}\main.pdf")
    for i in range(1, 11)
] + [
    (f"M2导学本-{n}", rf"C:\提示词\工作区\_tmp换装正装0914\M2导学本\{n}\main.pdf")
    for n in (["衔接节-1.2.1前", "章末-本章总结提升"] + [f"课时{i:02d}" for i in range(1, 11)])
] + [
    ("M2测评卷", r"C:\提示词\工作区\_tmp换装正装0914\M2测评滚动\测评卷\main.pdf"),
    ("M2滚动卷A", r"C:\提示词\工作区\_tmp换装正装0914\M2测评滚动\滚动卷A\main.pdf"),
    ("M2滚动卷B", r"C:\提示词\工作区\_tmp换装正装0914\M2测评滚动\滚动卷B\main.pdf"),
    ("P1导学本-9.1电荷", r"C:\提示词\工作区\_tmp换装正装0914\P1导学本\9.1电荷\main.pdf"),
    ("P1导学本-9.2库仑定律", r"C:\提示词\工作区\_tmp换装正装0914\P1导学本\9.2库仑定律\main.pdf"),
    ("P1导学本-9.3电场电场强度", r"C:\提示词\工作区\_tmp换装正装0914\P1导学本\9.3电场电场强度\main.pdf"),
    ("P1导学本-9.4静电的防止与利用", r"C:\提示词\工作区\_tmp换装正装0914\P1导学本\9.4静电的防止与利用\main.pdf"),
    ("P1导学本-章末易错过关", r"C:\提示词\工作区\_tmp换装正装0914\P1导学本\章末-本章易错过关\main.pdf"),
    ("P1测评卷", r"C:\提示词\工作区\_tmp换装正装0914\P1测评本\测评卷\main.pdf"),
    ("P1练习拓展-9.1电荷", r"C:\提示词\工作区\_tmp换装正装0914\P1练习拓展\9.1电荷\main-true.pdf"),
    ("P1练习拓展-9.2库仑定律", r"C:\提示词\工作区\_tmp换装正装0914\P1练习拓展\9.2库仑定律\main-true.pdf"),
    ("P1练习拓展-9.3电场电场强度", r"C:\提示词\工作区\_tmp换装正装0914\P1练习拓展\9.3电场电场强度\main-true.pdf"),
    ("P1练习拓展-9.4静电的防止与利用", r"C:\提示词\工作区\_tmp换装正装0914\P1练习拓展\9.4静电的防止与利用\main-true.pdf"),
    ("P1练习拓展-拓展册", r"C:\提示词\工作区\_tmp换装正装0914\P1练习拓展\拓展册\main-true.pdf"),
    ("M3拓展册-上册", r"C:\提示词\工作区\M3-第2章量产0913\成卷\拓展册\上册\main-true.pdf"),
    ("M3拓展册-下册", r"C:\提示词\工作区\M3-第2章量产0913\成卷\拓展册\下册\main-true.pdf"),
    ("M3测评卷", r"C:\提示词\工作区\M3-第2章量产0913\成卷\测评卷\main.pdf"),
    ("M3滚动卷", r"C:\提示词\工作区\M3-第2章量产0913\成卷\滚动卷\main.pdf"),
] + [
    (f"M3练习件-{d}", p)
    for d, p in _m3_exercise()
]

OPT = re.compile(r"^([ABCD])[．.、]\s*")
QN = re.compile(r"^(\d{1,3})[．.、\s]")
BOLD_MARK = ("Bold", "Medium", "Hei", "bold")

def get_lines(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            t = "".join(s["text"] for s in l["spans"]).strip()
            if not t:
                continue
            x0, y0, x1, y1 = l["bbox"]
            bold = any(any(m in s["font"] for m in BOLD_MARK) for s in l["spans"])
            out.append(dict(t=t, x0=x0, y0=y0, x1=x1, y1=y1, bold=bold,
                            font=l["spans"][0]["font"], size=round(l["spans"][0]["size"], 1)))
    return out

def columns_of(page, lines):
    """按页宽中线分左右栏；返回 [(side, [lines sorted by y])]，阅读序 L→R。"""
    mid = page.rect.width / 2
    cols = {"L": [], "R": []}
    for ln in lines:
        cols["L" if ln["x0"] < mid else "R"].append(ln)
    for k in cols:
        cols[k].sort(key=lambda l: l["y0"])
    return [("L", cols["L"]), ("R", cols["R"])]

def scan_crosscol(pdf, book):
    hits = []
    doc = pymupdf.open(pdf)
    colseq = []  # 阅读序 (pno, side, lines)
    for pno in range(len(doc)):
        pg = doc[pno]
        ls = get_lines(pg)
        if not ls:
            colseq.append((pno, "L", [])); colseq.append((pno, "R", []))
            continue
        for side, col in columns_of(pg, ls):
            colseq.append((pno, side, col))
    for idx in range(len(colseq)):
        pno, side, col = colseq[idx]
        if not col:
            continue
        top = min(l["y0"] for l in col)
        heads = [l for l in col if l["y0"] - top < 14]  # 栏首行（含数学分片）
        first_opt = None
        for l in heads:
            m = OPT.match(l["t"])
            if m:
                first_opt = (m.group(1), l)
                break
        if not first_opt:
            continue
        letter, line = first_opt
        # 前栏（阅读序上一栏）
        prev = None
        for j in range(idx - 1, -1, -1):
            if colseq[j][2]:
                prev = colseq[j]
                break
        if prev is None:
            continue
        ppno, pside, pcol = prev
        ptail = [l for l in pcol if l["y0"] > max(x["y1"] for x in pcol) - 30]
        ptail_txt = [l["t"] for l in ptail]
        pm = [OPT.match(t) for t in ptail_txt]
        pletters = [m.group(1) for m in pm if m]
        # 前栏尾/全栏找题干号
        pqn = [QN.match(l["t"]).group(1) for l in pcol if QN.match(l["t"])]
        cls = None
        if letter in "CD" and pletters:
            cls = "组内跨栏断(前栏尾有同组前位选项)"
        elif letter == "A" and pqn:
            cls = "干组跨栏分离(前栏尾即题干)"
        elif letter in "CD" and pqn and letter == "C":
            # C 落栏顶且前栏尾无选项——可能 A/B 与题干俱在前栏（整组分离）
            cls = "干组跨栏分离(前栏尾题干,组整迁)"
        if cls:
            hits.append(dict(book=book, page=pno + 1, side=side, cls=cls,
                             letter=letter, text=line["t"][:40], y=round(line["y0"], 1),
                             prev=f"p{ppno+1}{pside}尾", ptail=ptail_txt[-3:], pqn=pqn[-2:]))
    doc.close()
    return hits

def scan_orphan(pdf, book):
    """双档孤字：
    A 标题族＝NotoSans* 标题行聚块，块末行仅落 1 个可见字符（真孤字：标题折行尾悬单字）；
    B 条目级＝正文任意行可见内容恰为 1 个 CJK 汉字（段末行孤字候选；数学分片为数字/符号天然排除）。
    """
    hits = []
    doc = pymupdf.open(pdf)
    for pno in range(len(doc)):
        pg = doc[pno]
        for side, col in columns_of(pg, get_lines(pg)):
            if not col:
                continue
            # A 标题族块
            ttl = [l for l in col if l["font"].startswith("NotoSans")]
            blocks, cur = [], []
            for l in ttl:
                if cur and (l["y0"] - cur[-1]["y1"] > 2.2 * max(8, cur[-1]["size"])):
                    blocks.append(cur); cur = []
                cur.append(l)
            if cur:
                blocks.append(cur)
            for blk in blocks:
                if len(blk) < 2:
                    continue
                last = blk[-1]
                vis = re.sub(r"[\s.．、;；:：,，()（）]", "", last["t"])
                if len(vis) == 1 and re.match(r"^[\u4e00-\u9fff]$", vis):  # 单汉字尾行＝真孤字（题号行 1. 天然排除）
                    hits.append(dict(book=book, page=pno + 1, side=side, tier="A标题族",
                                     block="∥".join(b["t"][:34] for b in blk),
                                     lastline=last["t"][:20], y=round(last["y0"], 1),
                                     font=last["font"], size=last["size"]))
            # B 条目级：单汉字行
            col_right = max(l["x1"] for l in col)
            for i, l in enumerate(col):
                vis = re.sub(r"[\s.．、;；:：,，()（）]", "", l["t"])
                if len(vis) != 1 or not re.match(r"^[\u4e00-\u9fff]+$", vis):
                    continue
                prev = col[i - 1] if i else None
                dense = bool(prev) and (col_right - prev["x1"] < 25)  # 前行近满行
                hits.append(dict(book=book, page=pno + 1, side=side, tier="B条目级",
                                 block=(prev["t"][-34:] if prev else ""),
                                 lastline=l["t"][:20], y=round(l["y0"], 1),
                                 font=l["font"], size=l["size"], dense=dense))
    doc.close()
    return hits

def crop(pdf, pno, side, out):
    doc = pymupdf.open(pdf)
    pg = doc[pno - 1]
    w, h = pg.rect.width, pg.rect.height
    x0 = 0 if side == "L" else w / 2
    clip = pymupdf.Rect(x0, 0, x0 + w / 2, h / 2)  # 命中栏上半（栏顶区）
    pg.get_pixmap(dpi=200, clip=clip).save(out)
    doc.close()

def main():
    xhits, ohits = [], []
    for book, pdf in BOOKS:
        if not os.path.exists(pdf):
            print("缺件:", book, pdf); continue
        xhits += scan_crosscol(pdf, book)
        ohits += scan_orphan(pdf, book)
    json.dump(dict(crosscol=xhits, orphan=ohits),
              open(os.path.join(HERE, "巡检两项-读数.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    # 命中裁片
    pdfmap = {b: p for b, p in BOOKS}
    for i, h in enumerate(xhits):
        crop(pdfmap[h["book"]], h["page"], h["side"],
             os.path.join(HERE, f"裁片-跨栏{i+1:02d}-{h['book']}-p{h['page']}{h['side']}.png"))
    for i, h in enumerate([x for x in ohits if x["tier"].startswith("A") or x.get("dense")]):
        crop(pdfmap[h["book"]], h["page"], h["side"],
             os.path.join(HERE, f"裁片-孤字{i+1:02d}-{h['book']}-p{h['page']}{h['side']}.png"))
    print("跨栏选项命中:", len(xhits), " 标题孤字A(标题族):", sum(1 for h in ohits if h["tier"].startswith("A")),
          " 条目孤字B:", sum(1 for h in ohits if h["tier"].startswith("B")),
          "（其中前行满行dense:", sum(1 for h in ohits if h["tier"].startswith("B") and h.get("dense")), "）")
    for h in xhits:
        print("  [跨栏]", h["book"], "p%d%s" % (h["page"], h["side"]), h["cls"], "|", h["text"])
    for h in ohits:
        if h["tier"].startswith("A"):
            print("  [孤A]", h["book"], "p%d%s" % (h["page"], h["side"]), "| 块:", h["block"][:70], "| 末行:", h["lastline"])
    for h in [x for x in ohits if x["tier"].startswith("B") and x.get("dense")][:40]:
        print("  [孤B]", h["book"], "p%d%s" % (h["page"], h["side"]), "y=%s" % h["y"], "| 前行:", h["block"][-30:], "| 孤字:", h["lastline"])

if __name__ == "__main__":
    main()
