# -*- coding: utf-8 -*-
"""PDF合册.py — 网上打印成书路线·装订单驱动 PDF 拼合（CB-7 / CB-11③ / CB-12）

读装订单取件序，按三种粒度拼合各件同名 PDF：
  ① whole 整册一册；② type 按件型跨册大分本（衔接本/清单本/讲练本，口径=装订单§三方案B，
     配页三件不入大分本）；③ six 原 6 分本（按装订单§二本划分区间）。
特性：
  · 件间自动补白页凑偶数页（每件从新纸起始，CB-11③），逐件页数与补白数落补白登记；
  · 书签：每件一个顶层书签（件名），源 PDF 已有书签保留并挂到件节点下（CB-12）；
  · 页码不重排、各件原页码原样拼接（CB-7），本工具只拼合不改页面内容；
  · --no-xianjie 选印「不含衔接件」版（剔除衔接件及其部分封面，即整个衔接部分）。

用法：
  python 工具/PDF合册.py [--order 装订单.md] [--input-dir DIR] [--output-dir DIR]
      [--granularity all|whole|type|six] [--no-xianjie] [--book-prefix 人教B版选必1]
"""
import sys, io, os, re, json, argparse, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from pypdf import PdfReader, PdfWriter

DEFAULT_ORDER = r"高中数学\高中数学同步\人教B版选必1·装订单.md"
DEFAULT_INPUT = r"高中数学\高中数学同步"
TYPE_ORDER = ["衔接", "清单", "讲练"]  # 大分本件型次序（方案B）


# ---------- 装订单解析 ----------
def parse_order(md_path):
    """解析取件序表（| 序 | 件 | 页数 | 部分内页码区间 | 部分 | 本 |）与§二本划分区间。"""
    text = open(md_path, encoding="utf-8").read()
    pieces = []
    for m in re.finditer(r"^\|\s*(\d+)\s*\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|",
                         text, re.M):
        xu, name, pages, _span, part, ben = [s.strip() for s in m.groups()]
        pieces.append({
            "xu": int(xu), "name": name,
            "order_pages": pages,  # 装订单登记页数（配页=「配页」字样）
            "part": part, "ben": ben,
        })
    if not pieces:
        raise SystemExit(f"ERROR: 装订单取件序表解析为空：{md_path}")
    ben_ranges = []  # (本号, 起序, 止序)
    for m in re.finditer(r"^-\s*\*\*本(\d+)\*\*＝序(\d+)\s*[–—-]\s*(\d+)", text, re.M):
        ben_ranges.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
    return pieces, ben_ranges


def jianxing(piece):
    """件型判定：衔接/清单/讲练/配页。部分封面取其括号内·后缀；配页三件按名。"""
    name, part = piece["name"], piece["part"]
    m = re.search(r"·(衔接|清单|讲练)）", name)
    if m:
        return m.group(1)
    if "衔接" in name:
        return "衔接"
    if "清单" in name:
        return "清单"
    if "讲练" in name:
        return "讲练"
    m = re.search(r"·(衔接|清单|讲练)\b", part)
    if m:
        return m.group(1)
    return "配页"


# ---------- 件名→PDF 文件解析 ----------
def resolve_path(piece, pdf_files):
    """按装订单行在输入目录唯一锁定同名 PDF；0 或多于 1 命中即报错。"""
    name = piece["name"]
    if name.startswith("部分封面"):
        cands = [f for f in pdf_files if name in f]
    elif name in ("封面", "使用说明", "册目录页"):
        cands = [f for f in pdf_files
                 if f.endswith("·" + name + ".pdf") and "部分封面" not in f]
    else:
        chap = re.search(r"第\d+章", piece["part"]) or re.search(r"第\d+章", name)
        ti = re.search(r"(\d+)题", name)
        if "衔接" in name:
            key = "·衔接件"
        elif "清单" in name:
            key = "·知识清单"
        elif "讲练" in name:
            key = "·讲练件"
        else:
            raise SystemExit(f"ERROR: 无法识别件型：序{piece['xu']} {name}")
        cands = [f for f in pdf_files
                 if (not chap or chap.group() in f) and key in f
                 and (not ti or f"（{ti.group(1)}题）" in f)]
    if len(cands) != 1:
        raise SystemExit(
            f"ERROR: 序{piece['xu']}「{name}」命中 {len(cands)} 个 PDF：{cands or '无'}")
    return cands[0]


# ---------- 拼合 ----------
def merge_pieces(rows, out_path):
    """rows=[(piece, pdf_path)]；件间补白凑偶；件名顶层书签+源书签挂载。返回登记行。"""
    writer = PdfWriter()
    reg = []
    for piece, path in rows:
        n_src = len(PdfReader(str(path)).pages)
        start = len(writer.pages)
        writer.append(str(path), outline_item=f"序{piece['xu']} {piece['name']}")
        n = len(writer.pages) - start
        blanks = 0
        if n % 2 == 1:
            mb = writer.pages[-1].mediabox
            writer.add_blank_page(width=float(mb.width), height=float(mb.height))
            blanks = 1
        reg.append({
            "xu": piece["xu"], "name": piece["name"],
            "file": os.path.basename(str(path)),
            "order_pages": piece["order_pages"],
            "src_pages": n_src, "blanks": blanks,
            "merged_range": f"{start + 1}–{len(writer.pages)}",
        })
        if piece["order_pages"].isdigit() and int(piece["order_pages"]) != n_src:
            print(f"  WARN: 序{piece['xu']} {piece['name']} 装订单登记 "
                  f"{piece['order_pages']} 页 ≠ 实测 {n_src} 页")
    with open(out_path, "wb") as f:
        writer.write(f)
    return reg, len(writer.pages)


def run_granularity(tag, rows, out_dir, book, registry):
    if not rows:
        print(f"  跳过（空组）：{tag}")
        return
    out = os.path.join(out_dir, f"{book}·{tag}.pdf")
    reg, total = merge_pieces(rows, out)
    print(f"  产出 {os.path.basename(out)}：{total} 页（{len(rows)} 件，补白 "
          f"{sum(r['blanks'] for r in reg)} 页）")
    registry[tag] = {"file": os.path.basename(out), "total_pages": total, "pieces": reg}


def main():
    ap = argparse.ArgumentParser(description="装订单驱动 PDF 合册（CB-7/CB-11③/CB-12）")
    ap.add_argument("--order", default=DEFAULT_ORDER, help="装订单 md 路径（只读）")
    ap.add_argument("--input-dir", default=DEFAULT_INPUT, help="各件同名 PDF 所在目录")
    ap.add_argument("--output-dir", default=".", help="输出目录")
    ap.add_argument("--granularity", default="all",
                    choices=["all", "whole", "type", "six"], help="拼合粒度")
    ap.add_argument("--no-xianjie", action="store_true",
                    help="选印不含衔接件版（剔除整个衔接部分：衔接件＋其部分封面）")
    ap.add_argument("--book-prefix", default="人教B版选必1", help="输出文件名前缀")
    args = ap.parse_args()

    pieces, ben_ranges = parse_order(args.order)
    pdf_files = sorted(f for f in os.listdir(args.input_dir) if f.lower().endswith(".pdf"))
    if not pdf_files:
        raise SystemExit(f"ERROR: 输入目录无 PDF：{args.input_dir}")

    dropped = [p for p in pieces if args.no_xianjie and jianxing(p) == "衔接"]
    pieces = [p for p in pieces if p not in dropped]
    for p in dropped:
        print(f"--no-xianjie 剔除：序{p['xu']} {p['name']}")

    rows = [(p, os.path.join(args.input_dir, resolve_path(p, pdf_files))) for p in pieces]
    os.makedirs(args.output_dir, exist_ok=True)
    suffix = "·无衔接件" if args.no_xianjie else ""
    registry = {"order": os.path.abspath(args.order),
                "input_dir": os.path.abspath(args.input_dir),
                "generated": datetime.datetime.now().isoformat(timespec="seconds"),
                "no_xianjie": args.no_xianjie, "outputs": {}}
    g = args.granularity
    if g in ("all", "whole"):
        run_granularity("整册" + suffix, rows, args.output_dir, args.book_prefix,
                        registry["outputs"])
    if g in ("all", "type"):
        for t in TYPE_ORDER:
            sub = [(p, path) for p, path in rows if jianxing(p) == t]
            run_granularity(f"大分本-{t}本" + suffix, sub, args.output_dir,
                            args.book_prefix, registry["outputs"])
    if g in ("all", "six"):
        if not ben_ranges:
            print("  WARN: 装订单§二本划分未解析到「本N＝序X–Y」行，跳过 6 分本粒度")
        for ben, a, b in ben_ranges:
            sub = [(p, path) for p, path in rows if a <= p["xu"] <= b]
            run_granularity(f"本{ben}" + suffix, sub, args.output_dir,
                            args.book_prefix, registry["outputs"])

    reg_json = os.path.join(args.output_dir, f"{args.book_prefix}·合册补白登记{suffix}.json")
    with open(reg_json, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=1)
    reg_md = reg_json[:-5] + ".md"
    with open(reg_md, "w", encoding="utf-8") as f:
        f.write(f"# {args.book_prefix}·合册补白登记{suffix}\n\n")
        f.write(f"装订单：{registry['order']}\n\n生成：{registry['generated']}"
                f"　no-xianjie={args.no_xianjie}\n\n")
        f.write("口径：件间自动补白页凑偶数页（CB-11③每件从新纸起始）；"
                "页码原样拼接不重排（CB-7）；书签＝件名顶层＋源书签挂载（CB-12）。\n")
        for tag, out in registry["outputs"].items():
            f.write(f"\n## {out['file']}（总 {out['total_pages']} 页）\n\n")
            f.write("| 序 | 件 | 源PDF | 装订单页数 | 实测页数 | 补白 | 合册页区间 |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for r in out["pieces"]:
                f.write(f"| {r['xu']} | {r['name']} | {r['file']} | "
                        f"{r['order_pages']} | {r['src_pages']} | {r['blanks']} | "
                        f"{r['merged_range']} |\n")
    print(f"补白登记：{os.path.basename(reg_md)} / .json")


if __name__ == "__main__":
    main()
