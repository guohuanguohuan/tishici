# -*- coding: utf-8 -*-
"""v2样张六项自查：页数/底纹/悬挂/图档/页眉页脚/文字对账 + OMML 不动证明"""
import re, json, zipfile
from collections import Counter
from lxml import etree as ET
from docx import Document
from docx.oxml.ns import qn
import pymupdf

BASE = r"工作区/全品结构提取/数学选必一/样张v2"
SRC = r"高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx"
OUT = BASE + r"/人教B版选必1-1.1.1-v2样张.docx"
PDF = BASE + r"/人教B版选必1-1.1.1-v2样张.pdf"
reg = json.load(open(BASE + "/_构建登记.json", encoding="utf-8"))
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ok = []; bad = []

def chk(name, cond, detail=""):
    (ok if cond else bad).append(f"{name} {detail}")

# ---------- ① 页数 ----------
doc_pdf = pymupdf.open(PDF)
pngs = sorted(__import__("glob").glob(BASE + "/png/p*.png"))
chk("① PDF页数", doc_pdf.page_count == len(pngs), f"PDF={doc_pdf.page_count} PNG={len(pngs)}（预期4~6）")
chk("① 页数在预期区间", 4 <= doc_pdf.page_count <= 6, f"{doc_pdf.page_count}页")

# ---------- ② 底纹 ----------
d_out = Document(OUT); body = d_out.element.body
p_shd = Counter(); r_shd = Counter()
for shd in body.iter(qn("w:shd")):
    par = shd.getparent()
    fill = shd.get(qn("w:fill"))
    if par.tag == qn("w:pPr"): p_shd[fill] += 1
    elif par.tag == qn("w:rPr"): r_shd[fill] += 1
    elif par.tag == qn("w:tcPr"): pass  # 表头单元格底纹（表格结构不动，允许）
chk("② 段落级无 ADC2DA", p_shd["ADC2DA"] == 0, f"计数={p_shd['ADC2DA']}")
chk("② 段落级无 F2F2F2", p_shd["F2F2F2"] == 0, f"计数={p_shd['F2F2F2']}")
chk("② 段落级无 C7C7C7", p_shd["C7C7C7"] == 0, f"计数={p_shd['C7C7C7']}")

def png_pixel_stats(path, targets, tol=3):
    pm = pymupdf.Pixmap(path)
    n = pm.width * pm.height
    step = 3
    cnt = {k: 0 for k in targets}
    for y in range(0, pm.height, step):
        for x in range(0, pm.width, step):
            r, g, b = pm.pixel(x, y)[:3]
            for k, (tr, tg, tb) in targets.items():
                if abs(r-tr) <= tol and abs(g-tg) <= tol and abs(b-tb) <= tol:
                    cnt[k] += 1
    return {k: v * step * step for k, v in cnt.items()}, n

tgt = {"ADC2DA": (0xAD, 0xC2, 0xDA), "F2F2F2": (0xF2, 0xF2, 0xF2),
       "C7C7C7": (0xC7, 0xC7, 0xC7), "DDDDDD": (0xDD, 0xDD, 0xDD)}
for pg in (0, 3):
    st, total = png_pixel_stats(BASE + f"/png/p{pg+1:02d}.png", tgt)
    # 仅 ADC2DA（淡紫，抗锯齿不可能由黑白文字产生）做像素级断言；
    # F2F2F2/C7C7C7 属灰阶，文字抗锯齿必然产生同值灰像素，像素断言无效，以 XML 断言为准
    chk(f"② p{pg+1} 无ADC2DA像素", st["ADC2DA"] == 0, f"采样计数={st['ADC2DA']}")
    chk(f"② p{pg+1} 页脚页码框DDDDDD存在", st["DDDDDD"] > 0, f"采样计数={st['DDDDDD']}")
    print(f"  p{pg+1} 像素统计(步长3, 仅信息): {st}")

# ---------- ③ 悬挂缩进抽测 ----------
RE_TK = re.compile(r"^\d+\.\d+\.\d+\.\d+-\d+．")
def ptext(p): return "".join(t.text or "" for t in p.iter(qn("w:t")))
def norm(s): return s.replace("\u2060", "")
hang = []; follow = []; tiao = []
kids = [k for k in body.iterchildren() if k is not body.find(qn("w:sectPr"))]
state = False
for el in kids:
    if el.tag != qn("w:p"):
        state = False; continue
    t = norm(ptext(el)).strip()
    ppr = el.find(qn("w:pPr"))
    ind = ppr.find(qn("w:ind")) if ppr is not None else None
    g = (lambda a: ind.get(qn(a)) if ind is not None else None)
    sty = ""
    if ppr is not None:
        ps = ppr.find(qn("w:pStyle"))
        sty = ps.get(qn("w:val")) if ps is not None else ""
    pb = ppr.find(qn("w:pBdr")) if ppr is not None else None
    is_group_head = (pb is not None and pb.find(qn("w:left")) is not None
                     and pb.find(qn("w:left")).get(qn("w:sz")) == "18")
    if sty in ("JieMingMao", "Heading3") or is_group_head:
        state = False; continue
    if RE_TK.match(t):
        hang.append((t[:24], g("w:left"), g("w:hanging"))); state = True; continue
    if re.match(r"^\d+\.\d+\.\d+-\d+．", t):
        tiao.append((t[:24], g("w:left"), g("w:hanging"))); state = True; continue
    if state: follow.append((t[:24], g("w:left"), g("w:hanging")))
chk("③ 题号段全部 left=400/hanging=400",
    all(a == "400" and b == "400" for _, a, b in hang) and len(hang) == 10,
    f"{len(hang)}段；抽3: {hang[:3]}")
chk("③ 讲部条目段 left=400 无悬挂",
    all(a == "400" and b is None for _, a, b in tiao) and len(tiao) == 9,
    f"{len(tiao)}段；抽3: {tiao[:3]}")
chk("③ 题组后续段 left=400 无悬挂",
    all(a == "400" and b is None for _, a, b in follow) and len(follow) >= 60,
    f"{len(follow)}段；抽3: {follow[:3]}")

# ---------- ④ 图片宽度三档 ----------
EMU = 36000
tbl_ext = []; solo_ext = []
def in_tbl(el):
    p = el.getparent()
    while p is not None:
        if p.tag == qn("w:tbl"): return True
        p = p.getparent()
    return False
for ext in body.iter(qn("wp:extent")):
    wmm = int(ext.get("cx")) / EMU
    (tbl_ext if in_tbl(ext) else solo_ext).append(round(wmm, 1))
chk("④ 独立题图宽度⊆{30,45,86}", set(solo_ext) <= {30.0, 45.0, 86.0}, f"{sorted(Counter(solo_ext).items())}")
print("  表内小图（未动）:", sorted(Counter(tbl_ext).items()))

# ---------- ⑤ 页眉页脚 ----------
z = zipfile.ZipFile(OUT)
hdr = ET.fromstring(z.read("word/header1.xml"))
ftr = ET.fromstring(z.read("word/footer1.xml"))
htxts = ["".join(t.text or "" for t in p.iter(qn("w:t"))) for p in hdr.iter(qn("w:p"))]
htxts = [t for t in htxts if t]
hr = hdr.find(f".//{{{W}}}r"); hrpr = hr.find(qn("w:rPr"))
hsz = hrpr.find(qn("w:sz")).get(qn("w:val")); hcol = hrpr.find(qn("w:color")).get(qn("w:val"))
hjc = hdr.find(f"{{{W}}}p/{{{W}}}pPr/{{{W}}}jc").get(qn("w:val"))
chk("⑤ 页眉文本", htxts == ["1.1 空间向量及其运算"], f"{htxts}")
chk("⑤ 页眉 9pt/灰595959/居中", hsz == "18" and hcol == "595959" and hjc == "center",
    f"sz={hsz} color={hcol} jc={hjc}")
ftxts = ["".join(t.text or "" for t in p.iter(qn("w:t"))) for p in ftr.iter(qn("w:p"))]
chk("⑤ 页脚小字行", ftxts[0] == "第1章 空间向量与立体几何 · 讲练件（上）", f"{ftxts[0]!r}")
fp1 = ftr.find(f"{{{W}}}p")
fp1pr = fp1.find(qn("w:r") + "/" + qn("w:rPr"))
fsz = fp1pr.find(qn("w:sz")).get(qn("w:val")); fcol = fp1pr.find(qn("w:color")).get(qn("w:val"))
chk("⑤ 页脚小字 6.5pt/灰595959", fsz == "13" and fcol == "595959", f"sz={fsz} color={fcol}")
tbl = ftr.find(qn("w:tbl"))
shd = tbl.find(f".//{{{W}}}shd"); trh = tbl.find(f".//{{{W}}}trHeight")
tw = tbl.find(f"{{{W}}}tblPr/{{{W}}}tblW"); tjc = tbl.find(f"{{{W}}}tblPr/{{{W}}}jc")
instr = [e.text for e in tbl.iter(qn("w:instrText"))]
fld = [e.get(qn("w:fldCharType")) for e in tbl.iter(qn("w:fldChar"))]
pgsz = tbl.find(f".//{{{W}}}sz").get(qn("w:val"))
pgb = tbl.find(f".//{{{W}}}b") is not None
chk("⑤ 页码表格 31mm宽/居中/DDDDDD/高≈7.8mm",
    tbl is not None and tw.get(qn("w:w")) == "1757" and tjc.get(qn("w:val")) == "center"
    and shd.get(qn("w:fill")) == "DDDDDD" and trh.get(qn("w:val")) == "442",
    f"w={tw.get(qn('w:w'))} jc={tjc.get(qn('w:val'))} fill={shd.get(qn('w:fill'))} h={trh.get(qn('w:val'))}")
chk("⑤ PAGE 复杂域齐全/粗体10.5pt",
    instr and "PAGE" in instr[0] and fld == ["begin", "separate", "end"] and pgsz == "21" and pgb,
    f"instr={instr} fldChar={fld} sz={pgsz} b={pgb}")
sectPr = body.find(qn("w:sectPr"))
refs = [(e.tag.split('}')[1], e.get(qn("w:type"))) for e in sectPr
        if e.tag in (qn("w:headerReference"), qn("w:footerReference"))]
chk("⑤ sectPr 引用 header+footer(default)", refs == [("headerReference", "default"), ("footerReference", "default")], f"{refs}")
chk("⑤ 无 titlePg / 无奇偶页", sectPr.find(qn("w:titlePg")) is None
    and d_out.settings.element.find(qn("w:evenAndOddHeaders")) is None)
# 页眉页脚同串删除证明：源 header1/footer1 的旧串不再出现
old = "人教B版选必1 第1章 空间向量与立体几何·讲练"
chk("⑤ 源页眉页脚同串已删除", all(old not in (z.read(n).decode("utf-8")) for n in ("word/header1.xml", "word/footer1.xml")))

# ---------- ⑥ 文字对账 ----------
d_src = Document(SRC)
ksrc = list(d_src.element.body.iterchildren())
cut = reg["明细"]["cut_index"] if "cut_index" in reg.get("明细", {}) else None
if cut is None:
    for i, el in enumerate(ksrc):
        if el.tag == qn("w:p"):
            ppr = el.find(qn("w:pPr"))
            ps = ppr.find(qn("w:pStyle")) if ppr is not None else None
            if ps is not None and ps.get(qn("w:val")) == "Heading3" and norm("".join(t.text or "" for t in el.iter(qn("w:t")))).strip().startswith("1.1.2"):
                cut = i; break

def stream(elems):
    out = []
    for el in elems:
        if el.tag == qn("w:p"): out.append(ptext(el))
        elif el.tag == qn("w:tbl"):
            for p in el.iter(qn("w:p")): out.append(ptext(p))
    return out

src_stream = stream(ksrc[:cut])
out_stream = stream(kids)
# 依同一规则在源流上重演合并
lbl = lambda s: norm(s).strip()
i = 0; merged_stream = []
while i < len(src_stream):
    t = src_stream[i]
    if lbl(t).startswith("【答案】"):
        j = i + 1; ans = [t]
        while j < len(src_stream) and not lbl(src_stream[j]).startswith("【知识点】"):
            if lbl(src_stream[j]).startswith("【") or RE_TK.match(lbl(src_stream[j])): break
            ans.append(src_stream[j]); j += 1
        if j < len(src_stream) and lbl(src_stream[j]).startswith("【知识点】"):
            kn = [src_stream[j]]; k = j + 1
            while k < len(src_stream) and not lbl(src_stream[k]).startswith("【") and not RE_TK.match(lbl(src_stream[k])):
                kn.append(src_stream[k]); k += 1
            merged_stream.append("".join(ans) + " " + "".join(kn))
            i = k; continue
    merged_stream.append(t); i += 1
merged_stream = [re.sub(r"_+", "　　　　　　", t) for t in merged_stream]
diffs = [(a, b) for a, b in zip(merged_stream, out_stream) if a != b]
same_len = len(merged_stream) == len(out_stream)
chk("⑥ 对账段落条数一致", same_len, f"预期流={len(merged_stream)} 输出流={len(out_stream)}")
chk("⑥ 对账逐段零差异", same_len and not diffs, f"差异数={len(diffs)}")
if diffs:
    for a, b in diffs[:5]:
        print("   差异:\n    预期:", repr(a[:80]), "\n    输出:", repr(b[:80]))

# ---------- OMML 不动 ----------
n_math_src = sum(1 for el in ksrc[:cut] for _ in el.iter(qn("m:oMath")))
n_math_out = sum(1 for el in kids for _ in el.iter(qn("m:oMath")))
chk("⑦ OMML 公式数量不变", n_math_src == n_math_out, f"源={n_math_src} 出={n_math_out}")

# ---------- 汇总 ----------
print("\n===== 自查结果 =====")
for s in ok: print("  [PASS]", s)
for s in bad: print("  [FAIL]", s)
print(f"\nPASS {len(ok)} / FAIL {len(bad)}")
print("run级C7C7C7（关键词芯片+表格芯片，规格未令删）:", dict(r_shd))
