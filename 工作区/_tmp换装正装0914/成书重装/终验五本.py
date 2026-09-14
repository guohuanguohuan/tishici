# -*- coding: utf-8 -*-
# 换装成书重装·工装 终验五本.py ——验收②③④断言机（承 M3 成卷/装配/工装/终验页脚.py 先例）
#   ② 页数链实测逐件连续：D1 页脚页码逐页断言（<100 容差±1／≥100 三位精确）＋D2 页脚链 recto 形制
#     （recto＝章名＋件标识＋页码；verso＝页码＋丛书名，奇偶随连续页码自动交替＝书本文行为）
#     ＋D3 书签逐件复核（读数 json 件数 vs 合并 PDF outline）；
#   ③ 键账恒等：逐件件面双腿（% ans: 源锚 ↔ \begin{ansblock}[键] 编译锚）集合相等，
#     再对丁册切丁（迁前册键）逐件集合相等——豁免仅 导-课时01-衔接填空 1 键（键账对平案§三 挂哨在案）；
#     总账读数：册丁 769＝M2 580＋P1 189（839 全账去卷件 51＋19）｜件面 770＝册丁＋补键 1；
#   ④ pure 档零泄答抽 6 页：true 档含答案印面页定位→pure 同物理页断言 [答案]/[详解]/[解析] 全零。
# 用法：python 终验五本.py（先跑 装配五本.py，读 成书重装/装配读数.json 为唯一真源）
import io, sys, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pymupdf
from pypdf import PdfReader

ASM  = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ASM)                          # _tmp换装正装0914（只读键表）
with open(os.path.join(ASM, "装配读数.json"), encoding="utf-8") as fh:
    data = json.load(fh)

ZHANG  = {"M2": "空间向量与立体几何", "P1": "静电场及其应用"}          # recto 章名域
CONGSHU = {"M2": "选择性必修第一册", "P1": "必修第三册"}               # verso 丛书名域
MARK   = {("M2导学本", None): "导学件", ("P1导学本", None): "导学件",
          ("M2练习本", None): "练习件",
          ("M2练习本", "上册"): "拓展册（上）", ("M2练习本", "下册"): "拓展册（下）",
          ("P1拓展本", None): "拓展册", ("P1练习本", None): "练习"}
LEDGER = {  # 件 → 迁前册切丁键表（丁册 txt，一key一行）
    ("M2导学本", "衔接节-1.2.1前"):   "_键表/丁册-导-衔接.txt",
    ("M2导学本", "章末-本章总结提升"): "_键表/丁册-导-章末.txt",
    ("M2练习本", "上册"):            "_键表/丁册-拓上.txt",
    ("M2练习本", "下册"):            "_键表/丁册-拓下.txt",
    ("P1拓展本", "拓展册"):          "P1练习拓展/_键表/丁册-拓.txt",
}
for k in range(1, 10):
    LEDGER[("M2导学本", f"课时0{k}")] = f"_键表/丁册-导-课时0{k}.txt"
    LEDGER[("M2练习本", f"课时0{k}")] = f"_键表/丁册-练-课时0{k}.txt"
LEDGER[("M2导学本", "课时10")] = "_键表/丁册-导-课时10.txt"
LEDGER[("M2练习本", "课时10")] = "_键表/丁册-练-课时10.txt"
for rel in ("9.1电荷", "9.2库仑定律", "9.3电场电场强度", "9.4静电的防止与利用", "章末-本章易错过关"):
    LEDGER[("P1导学本", rel)] = f"P1导学本/_键表/丁册-件-{rel}.txt"
for i, rel in enumerate(("9.1电荷", "9.2库仑定律", "9.3电场电场强度", "9.4静电的防止与利用"), 1):
    LEDGER[("P1练习本", rel)] = f"P1练习拓展/_键表/丁册-练-课时9{i}.txt"
WAIVE = {"导-课时01-衔接填空"}                        # 键账对平案§三 件面补键（值有册源·挂哨放行）

def mark_of(book, rel):
    if (book, rel) in MARK:
        return MARK[(book, rel)]
    return MARK[(book, None)]

def band_text(page, h=60):
    r = page.rect
    return page.get_text(clip=pymupdf.Rect(0, r.height - h, r.width, r.height))

# ---- 验收② D1+D2：页脚页码链连续＋recto/verso 形制 ----
ok_all = True
foot_report = []
for mode in ("true", "false"):
    for book in data["modes"][mode]["books"]:
        d = pymupdf.open(os.path.join(ASM, book["pdf"].replace("/", os.sep)))
        n = len(d)
        segs, p0 = [], 0
        for pc in book["pieces"]:
            segs.append((pc, p0)); p0 += pc["pages"]
        assert p0 == n, f"{book['pdf']} 页数 {n} ≠ 件页数合计 {p0}"
        bad_cont, bad_form = [], []
        for pc, base in segs:
            chain = book["chain"]
            mk, zhang, cs = mark_of(book["book"], pc["rel"]), ZHANG[chain], CONGSHU[chain]
            for j in range(pc["pages"]):
                want = pc["start"] + j
                band = band_text(d[base + j])
                nums = [int(x) for x in re.findall(r"\d{1,3}", band.replace(",", ""))]
                hit = (want in nums) if want >= 100 else any(abs(x - want) <= 1 for x in nums)
                if not hit:
                    bad_cont.append((base + j + 1, want, " ".join(band.split())[:60]))
                if want % 2 == 1:                      # recto 形＝章名＋件标识＋页码
                    if not (zhang in band and mk in band):
                        bad_form.append((base + j + 1, "recto", mk))
                else:                                  # verso 形＝页码＋丛书名
                    if cs not in band:
                        bad_form.append((base + j + 1, "verso", cs))
        span = f"{book['start']}~{book['start'] + n - 1}"
        c_stat = "页码全连续 ✓" if not bad_cont else f"页码断点{len(bad_cont)}"
        f_stat = "recto/verso 形制 ✓" if not bad_form else f"形制缺{len(bad_form)}页"
        print(f"[{mode}] {book['pdf']:<22s} {n:>3d}页 期望{span:<9s} {c_stat} {f_stat}")
        for b in bad_cont[:4]:
            print(f"   物理{b[0]} 期望{b[1]} | 带: {b[2]}")
        for b in bad_form[:4]:
            print(f"   物理{b[0]} {b[1]} 缺「{b[2]}」")
        ok_all &= not bad_cont and not bad_form
        d.close()

# ---- 验收② D3：书签逐件复核 ----
for mode in ("true", "false"):
    for book in data["modes"][mode]["books"]:
        n_bm = len(PdfReader(os.path.join(ASM, book["pdf"].replace("/", os.sep))).outline)
        exp = len(book["pieces"])
        flag = "✓" if n_bm == exp else "**FAIL**"
        print(f"[{mode}] 书签 {book['book']}: {n_bm}/{exp} {flag}")
        ok_all &= (n_bm == exp)

# ---- 验收③ 键账恒等：件面双腿 ↔ 丁册切丁（迁前）逐件集合相等 ----
def anchors_of(path):
    with open(path, encoding="utf-8") as fh:
        t = fh.read()
    src = set(re.findall(r"^% ans:(\S+)", t, re.M))
    comp = set(re.findall(r"\\begin\{ansblock\}\[([^\]]+)\]", t))
    return src, comp

book_of = {b["book"]: b for m in ("true", "false") for b in data["modes"][m]["books"]}
tot_ledger, tot_face, key_rows = 0, 0, []
for mode in ("true", "false"):
    for book in data["modes"][mode]["books"]:
        for pc in book["pieces"]:
            path = os.path.join(ASM, mode, book["book"], pc["rel"], "main.tex")
            src, comp = anchors_of(path)
            if src != comp:
                print(f"**FAIL** 双腿不等 {mode}/{book['book']}/{pc['rel']}: "
                      f"源锚−编译锚={sorted(src-comp)} 编译锚−源锚={sorted(comp-src)}")
                ok_all = False
            if mode == "true":                     # 键账逐件一条（对 true 档取面）
                led = set(open(os.path.join(ROOT, LEDGER[(book["book"], pc["rel"])]),
                               encoding="utf-8").read().split())
                extra = src - led
                miss = led - src
                ok = not miss and extra <= WAIVE
                if not ok:
                    print(f"**FAIL** 键账 {book['book']}/{pc['rel']}: 缺{sorted(miss)} 溢{sorted(extra)}")
                    ok_all = False
                tot_ledger += len(led); tot_face += len(src)
                key_rows.append((book["book"], pc["rel"], len(led), len(src),
                                 "PASS" if ok else "**FAIL**",
                                 ("+" + "、".join(sorted(extra)) if extra else "")))
print(f"—— 键账逐件 {len(key_rows)} 件：{'全 PASS ✓' if all(r[4]=='PASS' for r in key_rows) else '有 FAIL'}；"
      f"册丁合计 {tot_ledger}（期望 769＝839 全账−卷件 70）｜件面合计 {tot_face}（期望 770＝册丁＋补键 1）")
ok_all &= (tot_ledger == 769 and tot_face == 770)

# ---- 验收④ pure 档零泄答抽 6 页（true 答案印面页定位→pure 同物理页断言） ----
def ans_pages(book):
    d = pymupdf.open(os.path.join(ASM, "true", book["book"] + ".pdf"))
    hits = [i for i in range(len(d))
            if re.search(r"答案\]|详解\]", d[i].get_text())]
    d.close()
    return hits
sample, seen = [], set()
books_t = data["modes"]["true"]["books"]
for passno in (0, 1):                              # 先每本 1 页，再补第 6 页
    for b in books_t:
        if len(sample) >= 6:
            break
        hits = ans_pages(b)
        if len(hits) > passno and (b["book"], hits[passno]) not in seen:
            sample.append((b, hits[passno])); seen.add((b["book"], hits[passno]))
print(f"—— 验收④ 抽样 {len(sample)} 页：")
for b, pi in sample:
    dp = pymupdf.open(os.path.join(ASM, "false", b["book"] + ".pdf"))
    txt = dp[pi].get_text()
    leak = [m for m in ("答案]", "详解]", "解析]") if m in txt]
    stat = "零泄答 ✓" if not leak else f"**FAIL 泄答 {leak}**"
    print(f"   {b['book']} p{pi+1}（true 含答案印面）→ pure {stat}")
    ok_all &= not leak
    dp.close()

print(f"断言：{'终验全过 ✓' if ok_all else '存在异常，见上'}｜"
      f"true 双链 M2 1~{data['chains']['true']['M2']-1}／P1 1~{data['chains']['true']['P1']-1}｜"
      f"pure 双链 M2 1~{data['chains']['false']['M2']-1}／P1 1~{data['chains']['false']['P1']-1}")
sys.exit(0 if ok_all else 1)
