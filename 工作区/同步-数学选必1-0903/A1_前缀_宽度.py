# -*- coding: utf-8 -*-
"""A1额外任务：品牌前缀行宽实测（ctypes GDI GetTextExtentPoint32）
串式＝羿郭工作室·＋现页眉串前段＋　＋该件最宽节名锚＋　＋第{最大页码}页
全角/非ASCII用SimSun 9pt、ASCII用Times New Roman 9pt 分段测量求和；
交叉验证：SimSun 9pt下全角字符恰9pt宽；等宽法（全角×9pt＋ASCII逐字符GDI）对照。"""
import os, re, sys, io, ctypes
from ctypes import wintypes
from lxml import etree
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
PARTS = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\A1_parts"

gdi32 = ctypes.windll.gdi32
user32 = ctypes.windll.user32
FW_NORMAL = 400
DEFAULT_CHARSET = 1  # 但用 GB2312_CHARSET=134 保证宋体中文字形
GB2312 = 134

hdc = user32.GetDC(0)
LOGPIXELSX = 88
LOGPIXELSY = 90
dpi_x = gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
dpi_y = gdi32.GetDeviceCaps(hdc, LOGPIXELSY)
print(f"设备DPI: x={dpi_x} y={dpi_y}")

def make_font(face, pt):
    h = -ctypes.windll.kernel32.MulDiv(pt, dpi_y, 72)
    f = gdi32.CreateFontW(h, 0, 0, 0, FW_NORMAL, 0, 0, 0, GB2312, 0, 0, 0, 0, face)
    return f

def measure(font, s):
    old = gdi32.SelectObject(hdc, font)
    size = wintypes.SIZE()
    gdi32.GetTextExtentPoint32W(hdc, s, len(s), ctypes.byref(size))
    gdi32.SelectObject(hdc, old)
    return size.cx  # px

def px2pt(px): return px * 72.0 / dpi_x

F_SONG = make_font("SimSun", 9)
F_TNR  = make_font("Times New Roman", 9)

# 全角字符宽度自检
test_cjk = "空"
w1 = measure(F_SONG, test_cjk)
print(f"自检：SimSun 9pt『空』宽 = {w1}px = {px2pt(w1):.3f}pt（应=9pt/12px@96dpi）")
w2 = measure(F_TNR, "0")
print(f"自检：TNR 9pt『0』宽 = {w2}px = {px2pt(w2):.3f}pt")

def width_pt(s):
    """分段测量：ASCII→TNR，其余→SimSun；返回pt"""
    total_px = 0
    segments = re.findall(r'[\x20-\x7e]+|[^\x20-\x7e]+', s)
    detail = []
    for seg in segments:
        f = F_TNR if seg[0] < '\x80' else F_SONG
        px = measure(f, seg)
        total_px += px
        detail.append((('TNR' if f is F_TNR else 'SIM'), seg[:8], round(px2pt(px),2)))
    return px2pt(total_px), detail

def width_equilibrium(s):
    """等宽法：全角×9pt＋ASCII逐字符GDI(TNR)求和"""
    tot = 0.0
    for ch in s:
        if ch < '\x80':
            tot += px2pt(measure(F_TNR, ch))
        else:
            tot += 9.0
    return tot

def anchors_of(tag):
    doc = etree.parse(os.path.join(PARTS, tag, 'word', 'document.xml'))
    res = []
    for p in doc.getroot().iter(q('p')):
        pPr = p.find(q('pPr'))
        if pPr is None: continue
        st = pPr.find(q('pStyle'))
        if st is None or st.get(q('val')) != 'JieMingMao': continue
        t = ''.join(x.text or '' for x in p.findall('.//'+q('t')))
        if t.strip(): res.append(t)
    return res

def header_text(tag):
    x = open(os.path.join(PARTS, tag, 'word', 'header1.xml'), encoding='utf-8').read()
    # 取缓存外的固定段：直接拼 w:t，把两个域缓存（节名、页码）剥掉——改为手工组装
    return None

# 各件参数：件型段（实测页眉前段去前缀）＋最大页码
CONF = {
    "X1": ("羿郭工作室·人教B版选必1 第1章 空间向量与立体几何·衔接（共16页）·本1/共6本", 16),
    "I1": ("羿郭工作室·人教B版选必1 第1章 空间向量与立体几何·清单（共14页）·本2/共6本", 14),
    "B":  ("羿郭工作室·人教B版选必1 第1章 空间向量与立体几何·讲练（共114页）·本3/共6本", 53),
    "C":  ("羿郭工作室·人教B版选必1 第1章 空间向量与立体几何·讲练（共114页）·本3/共6本", 114),
    "E":  ("羿郭工作室·人教B版选必1 第2章 平面解析几何·讲练（共205页）·本6/共6本", 49),
}
LIMIT = 510.0  # 版心18cm=510pt
rows = []
for tag, (front, maxpage) in CONF.items():
    anc = anchors_of(tag)
    if not anc:
        print(f"{tag}: 无节名锚！"); continue
    # 逐锚测宽取最宽
    best = max(anc, key=lambda a: width_equilibrium(a))
    bw = width_equilibrium(best)
    s = front + "\u3000" + best + "\u3000" + f"第{maxpage}页"
    w_pt, detail = width_pt(s)
    w_eq = width_equilibrium(s)
    fit = "放得下" if w_pt <= LIMIT else "放不下"
    rows.append((tag, best, s, w_pt, w_eq, fit))
    print(f"\n== {tag}")
    print(f"  节名锚数={len(anc)} 最宽锚={best!r}（等宽法{bw:.1f}pt）")
    print(f"  串全文={s!r}")
    print(f"  分段GDI实测={w_pt:.2f}pt = {w_pt/28.3465:.2f}cm ｜等宽法={w_eq:.2f}pt")
    print(f"  ≤510pt？{fit}（余量{LIMIT-w_pt:+.1f}pt）")

# 各件全部锚宽度明细（供复核）
print("\n== 各件全部节名锚等宽（pt）")
for tag in CONF:
    anc = anchors_of(tag)
    print(f"{tag}: " + " | ".join(f"{a}({width_equilibrium(a):.0f})" for a in anc))

user32.ReleaseDC(0, hdc)
rep = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\A1_reports\前缀宽度实测.txt"
with open(rep, 'w', encoding='utf-8') as f:
    for tag, best, s, w_pt, w_eq, fit in rows:
        f.write(f"{tag}\t最宽节名={best}\t实测={w_pt:.2f}pt({w_pt/28.3465:.2f}cm)\t等宽法={w_eq:.2f}pt\t{fit}\n")
print("\n落盘:", rep)
