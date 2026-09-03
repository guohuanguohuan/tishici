# -*- coding: utf-8 -*-
"""FX6 主编辑脚本（断言驱动：任一断言失败即中止不写回）
H件：人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx
E1删段[0]+节折叠 | E2选项分隔归一 | E3 sz21剥除 | E4 1F4E79去色
E5编注5段转oMath | E7灰底(p#617拆run+p#319/976移/3) | E8空格卫生
"""
import copy, re, sys, io
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
BASE = r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX6_H"
DOC = BASE + r"\word\document.xml"

parser = etree.XMLParser(remove_blank_text=False)
tree = etree.parse(DOC, parser)
root = tree.getroot()
body = root.find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")
LOG = []

def chk(cond, msg):
    if not cond:
        print("ASSERT-FAIL:", msg)
        sys.exit(1)
    LOG.append("OK " + msg)

def para_text(p):
    return "".join(p.itertext())

def wt_text(p):
    return "".join(t.text or "" for t in p.iter(f"{{{W}}}t"))

def rpr_of(r):
    return r.find(f"{{{W}}}rPr")

# ============ E1. 删段[0] + 节折叠 ============
chk(para_text(paras[0]) == "人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）", "E1 段[0]文本=文内标题")
p0 = paras[0]
sect0 = p0.find(f"{{{W}}}pPr").find(f"{{{W}}}sectPr")
chk(sect0 is not None, "E1 头部sectPr嵌段[0]")
hr = sect0.find(f"{{{W}}}headerReference")
fr = sect0.find(f"{{{W}}}footerReference")
pn = sect0.find(f"{{{W}}}pgNumType")
chk(hr is not None and hr.get(f"{{{R}}}id") == "rId374", "E1 headerReference rId374")
chk(fr is not None and fr.get(f"{{{R}}}id") == "rId9", "E1 footerReference rId9")
chk(pn is not None and pn.get(f"{{{W}}}start") == "142", "E1 pgNumType start=142")

body_sect = body.find(f"{{{W}}}sectPr")
chk(body_sect is not None, "E1 body级sectPr在位")
# 折叠：refs+pgNumType并入body sectPr，按schema序重建
cols_el = body_sect.find(f"{{{W}}}cols")
chk(cols_el is not None and cols_el.get(f"{{{W}}}num") == "2" and cols_el.get(f"{{{W}}}space") == "425" and cols_el.get(f"{{{W}}}sep") == "1", "E1 折叠前cols=2/425/1")
old_children = list(body_sect)
order = [hr, fr] + [c for c in old_children if etree.QName(c).localname in ("pgSz", "pgMar")] + [pn] + [c for c in old_children if etree.QName(c).localname in ("cols", "docGrid")]
chk(len(order) == len(old_children) + 3, "E1 折叠元素数=原+3")
for c in old_children:
    body_sect.remove(c)
for c in order:
    body_sect.append(c)
body.remove(p0)
LOG.append("E1 段[0]已删、refs+start142并入body sectPr（schema序）")

# ============ E2. 选项分隔归一 ============
# 注意：继续使用原paras引用（lxml删除p0后旧引用有效，索引不变）
OPTION_PARAS = {6, 12, 149, 166, 229, 498, 554, 568, 578, 626, 692}
NBSP_PARAS = {184, 286, 417, 488}

def linear_marks(p):
    """段直接子元素标记序列"""
    seq = []
    for ch in p:
        ln = etree.QName(ch).localname
        if ln == "r":
            for sub in ch:
                s = etree.QName(sub).localname
                if s == "t":
                    seq.append(("t", sub, ch))
                elif s == "tab":
                    seq.append(("TAB", sub, ch))
                elif s == "drawing":
                    seq.append(("IMG", sub, ch))
        elif ln == "oMath":
            seq.append(("M", ch, None))
    return seq

n_b = n_c = n_shift = n_glue = n_nbsp = 0
for idx in sorted(OPTION_PARAS):
    p = paras[idx]
    pPr = p.find(f"{{{W}}}pPr")
    if pPr is not None:
        tabs = pPr.find(f"{{{W}}}tabs")
        if tabs is not None:
            pPr.remove(tabs)
    # 错位「．；」→「．」（值前错位分号删除）
    for el, sub, run in linear_marks(p):
        if el == "t" and sub.text and "．；" in sub.text:
            n_shift += sub.text.count("．；")
            sub.text = sub.text.replace("．；", "．")
    # run级tab处置
    seq = linear_marks(p)
    for i, (el, sub, run) in enumerate(seq):
        if el != "TAB":
            continue
        # 后随内容首字符
        nxt = None
        if i + 1 < len(seq):
            e2, s2, r2 = seq[i + 1]
            if e2 == "t":
                nxt = (s2.text or "")[:1]
            else:
                nxt = e2  # M / IMG
        if nxt == "；":
            run.remove(sub); n_b += 1
        elif nxt in ("B", "C", "D"):
            # tab→全角；文本
            run.remove(sub)
            t = etree.SubElement(run, f"{{{W}}}t")
            t.text = "；"
            # 保持 rPr 在首位
            rp = rpr_of(run)
            if rp is not None:
                run.remove(t); run.insert(list(run).index(rp) + 1, t)
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            n_c += 1
        else:
            chk(False, f"E2 p#{idx} tab后随未预期内容={nxt!r}")
# 粘连补；（B–C间）：p#229「[M:12]C．」、p#578「中点C．」
for idx, anchor in ((229, "C"), (578, "C")):
    p = paras[idx]
    for r in p.findall(f"{{{W}}}r"):
        ts = r.findall(f"{{{W}}}t")
        if len(ts) == 1 and ts[0].text == anchor:
            newr = copy.deepcopy(r)
            for t in newr.findall(f"{{{W}}}t"):
                t.text = "；"
            r.addprevious(newr)
            n_glue += 1
            break
# nbsp选项间隔→；
for idx in sorted(NBSP_PARAS):
    p = paras[idx]
    for t in p.iter(f"{{{W}}}t"):
        if t.text and len(t.text) >= 3 and set(t.text) == {"\xa0"}:
            t.text = "；"
            n_nbsp += 1
chk(n_b == 13, f"E2 B型删tab=13 实测{n_b}")
chk(n_c == 14, f"E2 C型tab→；=14 实测{n_c}")
chk(n_shift == 8, f"E2 错位．；删除=8 实测{n_shift}")
chk(n_glue == 2, f"E2 粘连补；=2 实测{n_glue}")
chk(n_nbsp == 12, f"E2 nbsp选项间隔→；=12 实测{n_nbsp}")

# ============ E3. sz21剥除 ============
n21 = 0
for r in root.iter(f"{{{W}}}r"):
    rp = rpr_of(r)
    if rp is None:
        continue
    for tag in ("sz", "szCs"):
        e = rp.find(f"{{{W}}}{tag}")
        if e is not None and e.get(f"{{{W}}}val") == "21":
            rp.remove(e); n21 += 1
chk(n21 == 138, f"E3 sz/szCs21剥除=138 实测{n21}")

# ============ E4. 1F4E79去色 ============
nblue = 0
for r in root.iter(f"{{{W}}}r"):
    rp = rpr_of(r)
    if rp is None:
        continue
    c = rp.find(f"{{{W}}}color")
    if c is not None and (c.get(f"{{{W}}}val") or "").upper() == "1F4E79":
        rp.remove(c); nblue += 1
chk(nblue == 1, f"E4 1F4E79去色=1 实测{nblue}")

# ============ E5. 编注5段转oMath ============
RPR_TMPL = ('<w:rPr xmlns:w="%s"><w:rFonts w:ascii="Times New Roman" w:eastAsia="宋体" '
            'w:hAnsi="Times New Roman" w:cs="Cambria Math"/></w:rPr>') % W

def make_math_el(text):
    om = etree.fromstring(
        f'<m:oMath xmlns:m="{M}" xmlns:w="{W}">'
        f'<m:r>{RPR_TMPL}<m:t xml:space="preserve"></m:t></m:r></m:oMath>')
    om.find(f".//{{{M}}}t").text = text
    return om

def make_text_el(rpr_src, text):
    r = etree.SubElement(etree.Element(f"{{{W}}}p"), f"{{{W}}}r")  # 临时父
    if rpr_src is not None:
        r.append(copy.deepcopy(rpr_src))
    t = etree.SubElement(r, f"{{{W}}}t")
    t.text = text
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return r

SPLITS = {
 186: [("t","双曲线上点P处切线与OP斜率之积为定值"),("m","b²/a²"),("t","：由切线方程"),
       ("m","xx₀/a²−yy₀/b²＝1"),("t","得"),("m","k切＝b²x₀/(a²y₀)"),("t","，与"),
       ("m","kOP＝y₀/x₀"),("t","相乘得"),("m","b²/a²＝2/5"),("t","，"),
       ("m","e＝√(1＋2/5)＝√35/5"),("t","；易错点：双曲线取正、椭圆取负，符号勿混。")],
 275: [("t","抛物线两切线垂直的阿基米德三角形面积最值：两切线垂直⟺交点M在准线上，设"),
       ("m","M(x₀,−1/2)"),("t","，由切点弦、弦长与距离公式得"),("m","S＝(x₀²＋1)^(3/2)"),
       ("t","，最小值为1；易错点：最小值在"),("m","x₀＝0"),("t","（M为"),("m","(0,−1/2)"),("t","）时取得。")],
 419: [("t","过椭圆右焦点定斜率弦长：由"),("m","a²＝4"),("t","、"),("m","b²＝1"),("t","得"),
       ("m","c＝√3"),("t","与直线"),("m","y＝x−√3"),("t","，联立后"),("m","Δ＝32"),("t","，弦长"),
       ("m","|AB|＝√2·√Δ/5＝8/5"),("t","；易错点：硬解定理只宜草稿验算，大题须写联立与韦达过程。")],
 490: [("t","过焦点弦定比加距离相等求椭圆方程：设"),("m","F₂B＝t"),("t","，则"),("m","AF₂＝2t"),
       ("t","、"),("m","AB＝BF₁＝3t"),("t","，由两组焦半径和"),("m","2a"),("t","及F₂在A、B之间联立解得"),
       ("m","t＝√3/2"),("t","，"),("m","a²＝3"),("t","、"),("m","b²＝2"),("t","；易错点："),
       ("m","AB＝AF₂＋F₂B"),("t","勿漏。")],
 852: [("t","过定点直线的斜率和定值（非对称设线）：直线不过"),("m","A(0,−1)"),("t","时可设"),
       ("m","m·x＋n(y＋1)＝1"),("t","，配凑"),("m","x²/2＋[(y＋1)−1]²＝1"),("t","齐次化，韦达代入得"),
       ("m","kAP＋kAQ＝2"),("t","；易错点：直线过A时左端为0，此设线失效。")],
}
n_math = 0
for idx, seq in SPLITS.items():
    p = paras[idx]
    kids = [c for c in p if etree.QName(c).localname != "pPr"]
    chk(len(kids) == 3, f"E5 p#{idx} 段结构=2标签+1复合run 实测{len(kids)}")
    old_full = "".join(kids[2].itertext())
    joined = "".join(s for _, s in seq)
    chk(old_full == joined, f"E5 p#{idx} 切分拼接恒等（len={len(old_full)}）")
    rp = kids[2].find(f"{{{W}}}rPr")  # 正文run的rPr（无shd）
    pos = list(p).index(kids[1]) + 1
    p.remove(kids[2])
    for k2, (kind, s) in enumerate(seq):
        if kind == "t":
            el = make_text_el(rp, s)
        else:
            el = make_math_el(s)
            n_math += 1
        p.insert(pos + k2, el)
    after = "".join(p.itertext())
    chk(after == "【编注】【分析】" + old_full, f"E5 p#{idx} round-trip字符流恒等")
chk(n_math == 28, f"E5 新增oMath=28 实测{n_math}")

# ============ E7. 灰底 ============
# p#617 拆三run（值各标各的，「或」保持灰＝库内既有连接词形态）
p = paras[617]
done = False
for r in p.findall(f"{{{W}}}r"):
    for t in r.findall(f"{{{W}}}t"):
        if t.text == "4x−3y+20=0或4x+3y+20=0":
            r2 = copy.deepcopy(r); r3 = copy.deepcopy(r)
            r.find(f"{{{W}}}t").text = "4x−3y+20=0"
            r2.find(f"{{{W}}}t").text = "或"
            r3.find(f"{{{W}}}t").text = "4x+3y+20=0"
            r.addnext(r3); r.addnext(r2)
            done = True
chk(done, "E7 p#617 两值粘连run拆分")
# p#319/p#976 「/3」错位：oMath嵌在'/3'run内部（w:t后）——提升oMath至段级并置于run前
# 修复后读序：【答案】 (1)y=(4x²−x+2)/3；  （原错序：【答案】 /3(1)y=…）
for idx, frag in ((319, "/3"), (976, "/3=1")):
    p = paras[idx]
    hit = None
    for r in p.findall(f"{{{W}}}r"):
        if "".join(t.text or "" for t in r.findall(f"{{{W}}}t")) == frag:
            hit = r; break
    chk(hit is not None, f"E7 p#{idx} 找到{frag!r}run")
    om = hit.find(f"{{{M}}}oMath")
    chk(om is not None, f"E7 p#{idx} {frag!r}run内嵌oMath")
    hit.remove(om)
    hit.addprevious(om)
    chk(hit.getprevious() is om, f"E7 p#{idx} oMath已前置于{frag!r}run")
    LOG.append(f"E7 p#{idx} {frag!r}错位修复（oMath前置）")

# ============ E8. 空格卫生 ============
# p#345: 「（设」前的空格（跨run连续空格链）删除——定位'（设'run向前收集
p = paras[345]
removed = 0
for r in p.findall(f"{{{W}}}r"):
    ts = r.findall(f"{{{W}}}t")
    if len(ts) == 1 and (ts[0].text or "").startswith("（设"):
        cur = r.getprevious()
        while cur is not None:
            cts = cur.findall(f"{{{W}}}t")
            ctxt = "".join(t.text or "" for t in cts)
            if len(cts) >= 1 and ctxt != "" and set(ctxt) == {" "}:
                prev = cur.getprevious()
                removed += len(ctxt)
                p.remove(cur)
                cur = prev
            else:
                break
        break
chk(removed == 2, f"E8 p#345 删（设）前空格数=2 实测{removed}")
# 段尾空格 p#232/630/631
for idx in (232, 630, 631):
    p = paras[idx]
    ts = [t for t in p.iter(f"{{{W}}}t")]
    last = ts[-1]
    old = last.text or ""
    new = old.rstrip(" ")
    chk(old != new, f"E8 p#{idx} 段尾空格在位")
    last.text = new
# 纯nbsp段清空 p#363/596/865/869
for idx in (363, 596, 865, 869):
    p = paras[idx]
    full = "".join(t.text or "" for t in p.iter(f"{{{W}}}t"))
    chk(full != "" and set(full) == {"\xa0"}, f"E8 p#{idx} 纯nbsp段")
    for r in list(p.findall(f"{{{W}}}r")):
        rt = "".join(t.text or "" for t in r.findall(f"{{{W}}}t"))
        if rt != "" and set(rt) == {"\xa0"}:
            p.remove(r)
    chk(wt_text(p) == "", f"E8 p#{idx} 清后空段")

# ============ 全局终检断言 ============
paras2 = body.findall(f"{{{W}}}p")
chk(len(paras2) == 1261, f"终检 段数=1261 实测{len(paras2)}")
# sectPr
n_sect = len(root.findall(f".//{{{W}}}sectPr"))
chk(n_sect == 1, f"终检 sectPr=1 实测{n_sect}")
bs = body.find(f"{{{W}}}sectPr")
names = [etree.QName(c).localname for c in bs]
chk(names == ["headerReference", "footerReference", "pgSz", "pgMar", "pgNumType", "cols", "docGrid"], f"终检 sectPr子序={names}")
chk(bs.find(f"{{{W}}}pgNumType").get(f"{{{W}}}start") == "142", "终检 start=142")
c2 = bs.find(f"{{{W}}}cols")
chk(c2.get(f"{{{W}}}num") == "2" and c2.get(f"{{{W}}}space") == "425" and c2.get(f"{{{W}}}sep") == "1", "终检 cols=2/425/1")
chk(len(root.findall(f".//{{{W}}}tabs")) == 0, "终检 w:tabs=0")
n_rtab = len(root.findall(f".//{{{W}}}r/{{{W}}}tab"))
chk(n_rtab == 0, f"终检 run级tab=0 实测{n_rtab}")
# sz21
n21b = 0
for e in root.iter(f"{{{W}}}sz"):
    if e.get(f"{{{W}}}val") == "21": n21b += 1
for e in root.iter(f"{{{W}}}szCs"):
    if e.get(f"{{{W}}}val") == "21": n21b += 1
chk(n21b == 0, f"终检 sz21=0 实测{n21b}")
# 题号块89
ti = [r for p2 in paras2 for r in p2.findall(f"{{{W}}}r")
      if (rpr_of(r) is not None and rpr_of(r).find(f"{{{W}}}shd") is not None
          and rpr_of(r).find(f"{{{W}}}shd").get(f"{{{W}}}fill") == "C9C9C9"
          and rpr_of(r).find(f"{{{W}}}b") is not None
          and re.fullmatch(r"\d+(?:\.\d+)*-\d+．", "".join(t.text or "" for t in r.findall(f"{{{W}}}t"))))]
chk(len(ti) == 89, f"终检 题号块=89 实测{len(ti)}")
# 新首段=节名锚
chk("2.8 直线与圆锥曲线的位置关系" in para_text(paras2[0]), "终检 新首段=节名锚")
# 段级底纹恒等（ADC2DA 2→1）
adc = sum(1 for p2 in paras2 if (pp := p2.find(f"{{{W}}}pPr")) is not None
          and (s := pp.find(f"{{{W}}}shd")) is not None and s.get(f"{{{W}}}fill") == "ADC2DA")
chk(adc == 1, f"终检 ADC2DA段=1 实测{adc}")
c6 = sum(1 for p2 in paras2 if (pp := p2.find(f"{{{W}}}pPr")) is not None
         and (s := pp.find(f"{{{W}}}shd")) is not None and s.get(f"{{{W}}}fill") == "C6D4E3")
chk(c6 == 73, f"终检 C6D4E3段=73 实测{c6}")
e0 = sum(1 for p2 in paras2 if (pp := p2.find(f"{{{W}}}pPr")) is not None
         and (s := pp.find(f"{{{W}}}shd")) is not None and s.get(f"{{{W}}}fill") == "E0E0E0")
chk(e0 == 138, f"终检 E0E0E0题干底纹段=138 实测{e0}")
# 写回
tree.write(DOC, xml_declaration=True, encoding="UTF-8", standalone=True)
print("\n".join(LOG))
print("\nALL-ASSERT-PASS; document.xml written:", DOC)
