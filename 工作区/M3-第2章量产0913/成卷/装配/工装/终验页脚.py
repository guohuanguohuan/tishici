# -*- coding: utf-8 -*-
# M3 S6 工装① 终验页脚.py（三本版）——装配方案.md §三／§五 D1·D2·D3 断言机
# 先例：M2 _tmp装配装订0912/终验页脚.py。三本适配三要点：
#   ①BOOKS 三本参数化（本一导学本 1~／本二练习本 155~／本三测评拓展本 245~，true 档；
#     起页/页数/件制不再硬编码——读 装配三本.py 产出的 装配读数.json，同源防两表漂移）；
#   ②三位数页码域抽验（方案 §三.3）：页码 <100 沿 M2 容差 ±1；页码 ≥100 须页脚带含
#     完整三位数字精确匹配（防「155」印成两位/截位，M2 无此域先例，S6 新增检查点）；
#   ③册目录页不计页豁免：--tocpdf 传入册目录页 PDF，逐页断言页底 60pt 带无页码数字
#     （\pagestyle{empty} 机证），不参与连续链。
# 件制分流（沙箱实测 2026-09-14 修订）：
#   ke/juan 页脚数字均随 \setcounter{page} 注入走连续页码（juan 卷面自印序「卷NNN/NNN 卷」
#   系 \thepage 驱动，注入后自动连续——沙箱实证），故 D1 连续断言两件制统一；
#   D2 件标识链：页脚 RO/LE 随页码奇偶交替（recto 形＝章名＋件名；verso 形＝页码＋丛书名），
#   标识仅 recto 形（want 奇数页）断言，verso 形页由 D1 页码断言覆盖。
# 用法：python 终验页脚.py <装配输出目录> [--tocpdf <册目录页.pdf>]
#   <装配输出目录> 下须有 装配读数.json＋{true,false}/本X….pdf（先跑 装配三本.py）
import io, sys, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf
from pypdf import PdfReader

def band_text(page, h=60):
    r = page.rect
    return page.get_text(clip=pymupdf.Rect(0, r.height - h, r.width, r.height))

def check_cont(bands, start):
    """D1 连续页码断言（ke/juan 统一——juan 自印序随注入连续，沙箱实证）。
    <100 容差±1；≥100 三位数完整精确匹配（§三.3）。"""
    bad = []
    for i, txt in enumerate(bands):
        want = start + i
        nums = [int(x) for x in re.findall(r"\d{1,3}", txt.replace(",", ""))]
        if want >= 100:
            hit = want in nums                      # 三位数域：精确无容差
        else:
            hit = any(abs(n - want) <= 1 for n in nums)
        if not hit:
            bad.append((i + 1, want, " ".join(txt.split())[:60]))
    return bad

def pi_pages(pieces, i):
    return sum(p["pages"] for p in pieces[:i])

def marks_of(d, pieces, p0):
    """D2 件标识链：仅 recto 形页（want 奇）断言——ke 域「平面解析几何」＋件标识，
    juan 域件标识；verso 形页（want 偶）页脚＝页码＋丛书名，由 D1 覆盖。"""
    bad = []
    for idx, pc in enumerate(pieces):
        base = p0 + pi_pages(pieces, idx)
        for j in range(pc["pages"]):
            if (pc["start"] + j) % 2 == 0:
                continue
            txt = d[base + j].get_text()
            if pc["kind"] == "ke":
                ok = ("平面解析几何" in txt) and (pc["mark"] in txt)
            else:
                ok = pc["mark"] in txt
            if not ok:
                bad.append((base + j + 1, pc["mark"]))
    return bad

def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("--"):
        print("用法: python 终验页脚.py <装配输出目录> [--tocpdf <册目录页.pdf>]"); sys.exit(2)
    asm = args[0]
    tocpdf = None
    if "--tocpdf" in args:
        tocpdf = args[args.index("--tocpdf") + 1]
    jpath = os.path.join(asm, "装配读数.json")
    if not os.path.exists(jpath):
        print(f"[缺输入] {jpath} 不存在——先跑 装配三本.py（起页/件制以装配读数为唯一真源）"); sys.exit(2)
    with open(jpath, encoding="utf-8") as fh:
        data = json.load(fh)

    ok_all = True
    for mode in ("true", "false"):
        print(f"＝＝ {mode} 档 ＝＝")
        for book in data["modes"][mode]["books"]:
            pdf = os.path.join(asm, book["pdf"])
            d = pymupdf.open(pdf)
            n = len(d)
            # 物理页分段
            segs, p0 = [], 0
            for pc in book["pieces"]:
                segs.append((pc, p0)); p0 += pc["pages"]
            assert p0 == n, f"{pdf} 页数 {n} ≠ 件页数合计 {p0}"
            bad_cont, bad_mark, juan_pages, three_digit_n = [], [], 0, 0
            for pc, base in segs:
                bands = [band_text(d[base + j]) for j in range(pc["pages"])]
                bad_cont += [(base + b[0], b[1], b[2]) for b in check_cont(bands, pc["start"])]
                three_digit_n += sum(1 for j in range(pc["pages"]) if pc["start"] + j >= 100)
                if pc["kind"] == "juan":
                    juan_pages += pc["pages"]
                bad_mark += marks_of(d, [pc], base)
            span = f"{book['start']}~{book['start'] + n - 1}"
            stat = "全连续 ✓" if not bad_cont else f"断点{len(bad_cont)}处"
            markstat = "标识 ✓" if not bad_mark else f"标识缺{len(bad_mark)}页"
            print(f"[{mode}] {book['pdf']:<24s} {n:>3d}页 期望{span:<9s} {stat} {markstat}"
                  + (f"（卷件自序随注入连续{juan_pages}页；三位数域抽验{three_digit_n}页）" if juan_pages or three_digit_n else ""))
            for b in bad_cont[:6]:
                print(f"   物理{b[0]} 期望{b[1]} | 带: {b[2]}")
            for b in bad_mark[:6]:
                print(f"   物理{b[0]} 缺标识「{b[1]}」")
            ok_all &= not bad_cont and not bad_mark
            d.close()
        # D3 书签独立复核（合并后 PDF outline）
        for book in data["modes"][mode]["books"]:
            n_bm = len(PdfReader(os.path.join(asm, book["pdf"])).outline)
            exp = len(book["pieces"])
            flag = "✓" if n_bm == exp else f"**FAIL 期望{exp}**"
            print(f"[{mode}] 书签 {book['pdf']}: {n_bm}/{exp} {flag}")
            ok_all &= (n_bm == exp)

    if tocpdf:
        d = pymupdf.open(tocpdf)
        leak = []
        for i in range(len(d)):
            nums = re.findall(r"\d{1,4}", band_text(d[i]))
            if nums:
                leak.append((i + 1, " ".join(band_text(d[i]).split())[:50]))
        stat = f"{len(d)}页 页底无页码 ✓ 不计页" if not leak else f"页码泄漏{len(leak)}页"
        print(f"[豁免] 册目录页 {os.path.basename(tocpdf)}: {stat}")
        for b in leak[:6]:
            print(f"   物理{b[0]} | 带: {b[1]}")
        ok_all &= not leak
        d.close()

    t = data["modes"]["true"]["total_pages"]; f = data["modes"]["false"]["total_pages"]
    print(f"断言：{'双档全过 ✓' if ok_all else '存在异常，见上'}｜true 全册 1~{t} 连续（含卷件域）｜false 独立链 1~{f} 连续｜书签合计 true {data['modes']['true']['total_bookmarks']} 条/false {data['modes']['false']['total_bookmarks']} 条")
    sys.exit(0 if ok_all else 1)

if __name__ == "__main__":
    main()
