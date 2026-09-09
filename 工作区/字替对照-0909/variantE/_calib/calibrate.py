# -*- coding: utf-8 -*-
# E版字重标定：实例化(可跳过) → 标定样张 → zoom5.0(14.17px/mm) 等密度测量 → 每档选 wght/FakeBold
# 注意：TeX 控制词只能含字母，族名一律用 NotoA..K / FangYa..c / TNRa..d / NotoKfbXX
import os, re, subprocess, json
import pymupdf, numpy as np

WORK = r"C:/提示词/工作区/字替对照-0909"
CAL = WORK + "/variantE/_calib"
VF = r"C:/Windows/Fonts/NotoSansSC-VF.ttf"
FY = WORK + "/fonts/候选字体/AlimamaFangYuanTi-VF.ttf"
os.makedirs(CAL + "/fonts", exist_ok=True)

THR = 128
SIZES = [20.67, 16.88, 15.1, 13.0, 12.03, 11.4, 10.09]
LIGHT = [250, 300, 315, 330, 350]             # 节 5px@16.88 卡在 w300=4 与 w350=6 之间
NW = LIGHT + [400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900]
FW = [400, 500, 600]
TNR_FB = ["10", "11", "12", "13"]             # T组：TNR Bold + FakeBold 0.10..0.13（实测无效档，留档）
RFB = {"0": ("TNRrA", None), "4": ("TNRrB", "0.04"),     # R组：TNR 常规 + 微FB（无效档，留档）
       "6": ("TNRrC", "0.06"), "8": ("TNRrD", "0.08")}
UFB = {"18": ("TNRbA", "0.18"), "25": ("TNRbB", "0.25"),  # U组：TNR Bold + 大FB（无效档，留档）
       "32": ("TNRbC", "0.32")}
SFB = {"6": ("TNRsA", "0.6"), "10": ("TNRsB", "1.0"),     # S组：TNR 常规 × FB 大档（检测题号 6px）
       "15": ("TNRsC", "1.5"), "20": ("TNRsD", "2.0")}
VFB = {"6": ("TNRtA", "0.6"), "10": ("TNRtB", "1.0"),     # V组：TNR Bold × FB 大档（条目号 8px）
       "15": ("TNRtC", "1.5"), "20": ("TNRtD", "2.0")}
KFB = {"20": ("NotoKfA", "0.2"), "35": ("NotoKfB", "0.35"),
       "50": ("NotoKfC", "0.5")}  # Noto w900 + FakeBold（章 12px 补强候选），族名单token纯字母

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return r.returncode, (r.stdout + r.stderr)[-500:]

# ---------- 1) 实例化（已有则跳过） ----------
noto_files = {}
for w in NW:
    out = f"{CAL}/fonts/NSC-w{w}.ttf"
    if not os.path.exists(out):
        rc, msg = run(f'python -m fontTools.varLib.instancer "{VF}" wght={w} -o "{out}"')
        if rc: print("instancer err", w, msg); raise SystemExit
    noto_files[w] = out
fy_files = {}
for w in FW:
    out = f"{CAL}/fonts/FY-w{w}.ttf"
    if not os.path.exists(out):
        rc, msg = run(f'python -m fontTools.varLib.instancer "{FY}" wght={w} -o "{out}"')
        if rc: print("instancer err FY", w, msg); raise SystemExit
    fy_files[w] = out
print("instanced:", len(noto_files), len(fy_files))

# ---------- 2) 标定 tex ----------
NL = ["Noto" + c for c in "ABCDEFGHIJKLMNOP"][:len(NW)]
name_of = {w: NL[i] for i, w in enumerate(NW)}
FYn = {400: "FangYa", 500: "FangYb", 600: "FangYc"}
TNRn = {"10": "TNRa", "11": "TNRb", "12": "TNRc", "13": "TNRd"}

lines = [r"""\documentclass[fontset=none]{ctexart}
\usepackage[a4paper,margin=15mm]{geometry}
\setmainfont{Times New Roman}
\xeCJKsetup{CheckSingle=false}
"""]
for w in NW:
    lines.append(r"\newCJKfontfamily\%s[Path=fonts/]{NSC-w%d.ttf}" % (name_of[w], w))
for w in FW:
    lines.append(r"\newCJKfontfamily\%s[Path=fonts/]{FY-w%d.ttf}" % (FYn[w], w))
for fb in TNR_FB:
    lines.append(r"\newfontfamily\%s[BoldFont={Times New Roman Bold},FakeBold=0.%s]{Times New Roman}" % (TNRn[fb], fb))
for k, (fam, f) in RFB.items():
    if f is None:
        lines.append(r"\newfontfamily\%s{Times New Roman}" % fam)
    else:
        lines.append(r"\newfontfamily\%s[FakeBold=%s]{Times New Roman}" % (fam, f))
for k, (fam, f) in UFB.items():
    lines.append(r"\newfontfamily\%s[BoldFont={Times New Roman Bold},FakeBold=%s]{Times New Roman}" % (fam, f))
for k, (fam, f) in SFB.items():
    lines.append(r"\newfontfamily\%s[FakeBold=%s]{Times New Roman}" % (fam, f))
for k, (fam, f) in VFB.items():
    lines.append(r"\newfontfamily\%s[BoldFont={Times New Roman Bold},FakeBold=%s]{Times New Roman}" % (fam, f))
for k, (fam, f) in KFB.items():
    lines.append(r"\newCJKfontfamily\%s[Path=fonts/,FakeBold=%s]{NSC-w900.ttf}" % (fam, f))
lines.append(r"\newcommand{\mk}[1]{{\fontsize{8pt}{9pt}\selectfont #1 }}")
lines.append(r"\begin{document}\fontsize{10pt}{16pt}\selectfont")

def esc(v): return ("%g" % v)
for w in NW:
    for s in SIZES:
        lines.append(r"\mk{N%d-%s}{\%s\fontsize{%spt}{%gpt}\selectfont 永国字探}\par"
                     % (w, esc(s), name_of[w], esc(s), s * 1.35))
for w in FW:
    lines.append(r"\mk{F%d-12.03}{\%s\fontsize{12.03pt}{16.24pt}\selectfont 永国字探}\par" % (w, FYn[w]))
for fb in TNR_FB:
    for s in (10.09, 11.4):
        lines.append(r"\mk{T%s-%s}{\%s\bfseries\fontsize{%spt}{%gpt}\selectfont 1234.}\par"
                     % (fb, esc(s), TNRn[fb], esc(s), s * 1.35))
for k, (fam, f) in RFB.items():
    for s in (10.09, 11.4):
        lines.append(r"\mk{R%s-%s}{\%s\fontsize{%spt}{%gpt}\selectfont 1234.}\par"
                     % (k, esc(s), fam, esc(s), s * 1.35))
for k, (fam, f) in UFB.items():
    for s in (10.09, 11.4):
        lines.append(r"\mk{U%s-%s}{\%s\bfseries\fontsize{%spt}{%gpt}\selectfont 1234.}\par"
                     % (k, esc(s), fam, esc(s), s * 1.35))
for k, (fam, f) in SFB.items():
    for s in (10.09, 11.4):
        lines.append(r"\mk{S%s-%s}{\%s\fontsize{%spt}{%gpt}\selectfont 1234.}\par"
                     % (k, esc(s), fam, esc(s), s * 1.35))
for k, (fam, f) in VFB.items():
    for s in (10.09, 11.4):
        lines.append(r"\mk{V%s-%s}{\%s\bfseries\fontsize{%spt}{%gpt}\selectfont 1234.}\par"
                     % (k, esc(s), fam, esc(s), s * 1.35))
for k, (fam, f) in KFB.items():
    lines.append(r"\mk{K%s-20.67}{\%s\fontsize{20.67pt}{27.9pt}\selectfont 永国字探}\par" % (k, fam))
lines.append(r"\end{document}")
open(CAL + "/calib.tex", "w", encoding="utf-8").write("\n".join(lines))

# ---------- 3) 编译 ----------
rc, msg = run(f'cd "{CAL}" && xelatex -interaction=nonstopmode -halt-on-error calib.tex')
print("compile rc=", rc)
if rc:
    print(msg)
    try:
        log = open(CAL + "/calib.log", encoding="utf-8", errors="ignore").read()
        print(log[-1200:])
    except OSError:
        pass
    raise SystemExit

# ---------- 4) 测量（zoom5.0=14.17px/mm，阈128，暗run中位=笔画px） ----------
MKRE = re.compile(r"^([A-Z])(\d+)-([\d.]+)$")
doc = pymupdf.open(CAL + "/calib.pdf")
Z = 5.0
pix = {}
def page_img(p):
    if p not in pix:
        pm = doc[p].get_pixmap(matrix=pymupdf.Matrix(Z, Z), colorspace=pymupdf.csGRAY)
        pix[p] = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width)
    return pix[p]
def metrics(arr):
    dark = arr < THR
    if not dark.any(): return None
    runs = []
    for row in dark:
        padded = np.zeros(len(row) + 2, dtype=np.int8)
        padded[1:-1] = row
        idx = np.flatnonzero(np.diff(padded))
        runs.extend((idx[1::2] - idx[0::2]).tolist())
    return float(np.median(runs)) if runs else 0.0

res = {}
nmiss = 0
for p in range(len(doc)):
    for b in doc[p].get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            spans = l["spans"]
            for i, sp in enumerate(spans):
                t = sp["text"].strip()
                if not MKRE.match(t):
                    continue
                if i + 1 >= len(spans):
                    nmiss += 1
                    continue
                sp2 = spans[i + 1]          # 同一 line 内 marker 的下一个 span 即样字
                x0, y0, x1, y1 = sp2["bbox"]
                img = page_img(p)
                X0, Y0 = int(max(0, (x0 - 1) * Z)), int(max(0, (y0 - 1) * Z))
                X1, Y1 = int(min(img.shape[1], (x1 + 1) * Z)), int(min(img.shape[0], (y1 + 1) * Z))
                res[t] = metrics(img[Y0:Y1, X0:X1])
doc.close()
if nmiss: print("warn: marker 无同行后继 span ×", nmiss)

def sortkey(kv):
    m = MKRE.match(kv[0])
    return (m.group(1), int(m.group(2)), float(m.group(3)))
out = dict(sorted(res.items(), key=sortkey))
print(json.dumps(out, ensure_ascii=False, indent=0))
json.dump(out, open(CAL + "/calib_result.json", "w"), indent=1)

# ---------- 5) 按岗位自动推荐（±0.5px 收敛优先最近值） ----------
roles = [
    ("章",     "N", [20.67], 12.0, True),   # 含 K（w900+FakeBold）候选
    ("节",     "N", [16.88], 5.0,  False),
    ("小节",   "N", [15.1],  10.0, False),
    ("课时",   "N", [13.0],  8.0,  False),
    ("◆·例N", "N", [12.03], 7.0,  False),
    ("条目号", "TUV", [10.09], 8.0, False),
    ("检测题号", "TRS", [11.4], 6.0, False),
    ("变式",   "F", [12.03], 4.0,  False),
]
print("\n==== 岗位推荐 ====")
for name, g, sizes, target, withK in roles:
    for s in sizes:
        cands = [(k, v) for k, v in res.items()
                 if k[0] in g and abs(float(k.split("-")[1]) - s) < 0.011 and v is not None]
        if withK:
            cands += [(k, v) for k, v in res.items() if k[0] == "K" and v is not None]
        if not cands:
            print(f"{name}@{s}pt 目标{target}px —— 无数据"); continue
        ranked = sorted(cands, key=lambda kv: abs(kv[1] - target))
        best = ranked[0]
        flag = "OK" if abs(best[1] - target) <= 0.5 else "超差"
        print(f"{name}@{s}pt 目标{target}px -> {best[0]} = {best[1]:.2f}px (Δ{best[1]-target:+.2f}) {flag}")
        for k, v in ranked[:5]:
            print(f"    {k}: {v:.2f}")
