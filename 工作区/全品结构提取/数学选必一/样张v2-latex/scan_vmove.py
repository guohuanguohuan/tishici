# -*- coding: utf-8 -*-
"""vmove 扫描：对 MROW_VMOVE 各取值，编译并实测 sub3_B_1/sub3_B_2 图顶是否越过其所在表的顶线。"""
import re, subprocess, sys
import pymupdf

BASE = r"C:\提示词\工作区\全品结构提取\数学选必一\样张v2-latex"
PPP = BASE + r"\postproc_v2.py"

def set_vmove(v):
    s = open(PPP, encoding='utf-8').read()
    s = re.sub(r"MROW_VMOVE = '[^']*'", f"MROW_VMOVE = '{v}'", s)
    open(PPP, 'w', encoding='utf-8').write(s)

def measure():
    doc = pymupdf.open(BASE + r"\main_v2.pdf")
    out = []
    for pno in range(len(doc)):
        page = doc[pno]
        # 水平规则（表格横线）
        hlines = []
        for d in page.get_drawings():
            for item in d['items']:
                if item[0] == 're':
                    r = item[1]
                    if r.height < 2 and r.width > 100:
                        hlines.append((r.y0, r.x0, r.x1))
                elif item[0] == 'l':
                    p1, p2 = item[1], item[2]
                    if abs(p1.y - p2.y) < 0.6 and abs(p1.x - p2.x) > 100:
                        hlines.append((p1.y, min(p1.x, p2.x), max(p1.x, p2.x)))
        # 图片位置
        for info in page.get_image_info():
            name = info.get('digest', '?')
            r = pymupdf.Rect(info['bbox'])
            if not (60 < r.width < 130):  # 30mm≈85pt/45mm≈128pt 宽的表内图
                continue
            # 找与图水平范围重叠的横线
            near = [y for (y, x0, x1) in hlines if x0 < r.x0 + 5 and x1 > r.x1 - 5]
            above = [y for y in near if y <= r.y0 + 1]
            top_rule = max(above) if above else None
            poke = (r.y0 - top_rule) if top_rule is not None else None
            out.append((pno + 1, round(r.width, 1), round(r.y0, 1), None if top_rule is None else round(top_rule, 1),
                        None if poke is None else round(poke, 1)))
    doc.close()
    return out

def overfull():
    txt = open(BASE + r'\main_v2.log', encoding='utf-8', errors='ignore').read()
    hv = re.findall(r'^Overfull \\hbox \(([\d.]+)pt', txt, re.M)
    vv = re.findall(r'^Overfull \\vbox \(([\d.]+)pt', txt, re.M)
    return len(hv), len(vv), [float(x) for x in vv]

for v in sys.argv[1:]:
    set_vmove(v)
    subprocess.run([sys.executable, PPP], capture_output=True, cwd=BASE)
    subprocess.run(['xelatex', '-interaction=nonstopmode', 'main_v2.tex'], capture_output=True, cwd=BASE)
    res = measure()
    nh, nv, vvals = overfull()
    print(f'vmove={v}: overfull hbox={nh} vbox={nv} {vvals}')
    for pno, w, iy, ry, poke in res:
        poke_s = f'poke={"OK" if poke >= 0 else poke}' if poke is not None else 'no-rule'
        print(f'   p{pno} img_w={w} img_top={iy} rule_top={ry} {poke_s}')
