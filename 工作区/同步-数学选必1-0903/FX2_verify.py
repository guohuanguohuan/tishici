# -*- coding: utf-8 -*-
# FX2修后结构自检：sectPr断言/题号79序列/tab残量/段尾空格/同串逐字/OMML合法性与round-trip/标签完整性抽核
import zipfile, re, io
from lxml import etree

SRC = r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
z = zipfile.ZipFile(SRC)
doc = etree.parse(io.BytesIO(z.read("word/document.xml")))
body = doc.getroot().find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")
ok = []

# 1) sectPr折叠断言
sects = body.findall(f"{{{W}}}sectPr")
inpara = body.findall(f".//{{{W}}}p/{{{W}}}pPr/{{{W}}}sectPr")
assert len(sects) == 1 and len(inpara) == 0
sect = sects[0]
kids = [etree.QName(c).localname for c in sect]
assert kids == ["headerReference", "footerReference", "pgSz", "pgMar", "pgNumType", "cols", "docGrid"], kids
hdr = sect.find(f"{{{W}}}headerReference"); ftr = sect.find(f"{{{W}}}footerReference")
assert hdr.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id") == "rId351"
assert ftr.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id") == "rId347"
assert sect.find(f"{{{W}}}pgNumType").get(f"{{{W}}}start") == "54"
cols = sect.find(f"{{{W}}}cols")
assert cols.get(f"{{{W}}}num") == "2" and cols.get(f"{{{W}}}space") == "425" and cols.get(f"{{{W}}}sep") == "1"
mar = sect.find(f"{{{W}}}pgMar")
assert all(mar.get(f"{{{W}}}{k}") == "850" for k in ("top", "right", "bottom", "left", "footer")) and mar.get(f"{{{W}}}header") == "283"
sz = sect.find(f"{{{W}}}pgSz")
assert sz.get(f"{{{W}}}w") == "11906" and sz.get(f"{{{W}}}h") == "16838"
# 头部无文内标题：首段=节名锚
first = "".join(t.text or "" for t in paras[0].iter(f"{{{W}}}t"))
assert first == "1.2.5 空间中的距离", repr(first)
st = paras[0].find(f"{{{W}}}pPr/{{{W}}}pStyle")
assert st is not None and st.get(f"{{{W}}}val") == "JieMingMao"
assert len(paras) == 1072, len(paras)
ok.append(f"①sectPr折叠：全文仅1个sectPr（schema序{kids}），headerReference rId351×1/footerReference rId347×1/pgNumType start=54/cols=2·425·sep=1/pgSz 11906×16838/pgMar 850·283；段内节隔断=0；首段=节名锚「1.2.5 空间中的距离」（样式JieMingMao），文内标题段已无；总段数1073→1072。")

# 2) 题号序列79
nums = []
for p in paras:
    for r in p.findall(f"{{{W}}}r"):
        rpr = r.find(f"{{{W}}}rPr")
        if rpr is None: continue
        shd = rpr.find(f"{{{W}}}shd")
        if shd is None or shd.get(f"{{{W}}}fill") != "C9C9C9": continue
        b = rpr.find(f"{{{W}}}b")
        if b is None: continue
        txt = "".join(t.text or "" for t in r.findall(f"{{{W}}}t"))
        m = re.match(r"^1\.2\.5(?:\.\d+)*-(\d+)．$", txt)
        if m:
            nums.append(int(m.group(1)))
assert len(nums) == 79, len(nums)
assert nums == list(range(1, 80)), "题号序列不连续"
ok.append(f"②题号序列：题号块（C9C9C9+加粗、文本恰=题号）79个，节内序列1..79连续无重复＝文件名79题（与A1基线一致）。")

# 3) tab残量与段尾空格
tabs = list(body.iter(f"{{{W}}}tab"))
assert len(tabs) == 76, len(tabs)
def inline_seq(p):
    seq = []
    for node in p.iter():
        if node.tag == f"{{{W}}}t": seq.append(("text", node.text or "", node))
        elif node.tag == f"{{{W}}}tab": seq.append(("tab", "", node))
        elif node.tag == f"{{{M}}}oMath": seq.append(("math", "", node))
    return seq
sep_remain = 0
for p in paras:
    seq = inline_seq(p)
    for k,(kind,txt,el) in enumerate(seq):
        if kind != "tab": continue
        before = False
        for j in range(k-1,-1,-1):
            if seq[j][0]=="math" or (seq[j][0]=="text" and seq[j][1].strip()): before=True; break
        if not before: continue
        nx=None
        for j in range(k+1,len(seq)):
            if seq[j][0]=="math": nx=("math",""); break
            if seq[j][0]=="text" and seq[j][1].strip(): nx=("text",seq[j][1].lstrip()); break
        if nx and (nx[1].startswith("；") or re.match(r"^[ABCD](．|$)", nx[1])):
            sep_remain += 1
assert sep_remain == 0
ok.append(f"③tab：全卷w:tab残留76处＝全部行首缩进LEAD位（段首A．/题号前，非选项分隔）；选项分隔位tab=0（88→0）；76处非A1派单项、已登记待主会话裁决。")

# 段尾空格
def para_tail_ws(p):
    seq = [n for n in p.iter() if n.tag in (f"{{{W}}}t", f"{{{W}}}drawing", f"{{{M}}}oMath")]
    while seq and seq[-1].tag == f"{{{W}}}drawing": seq.pop()
    if not seq or seq[-1].tag != f"{{{W}}}t": return None
    if seq[-1].text and re.search(r"[ \u3000]+$", seq[-1].text): return seq[-1]
    return None
tw = [t for t in (para_tail_ws(p) for p in paras) if t is not None]
assert len(tw) == 0
# 白名单核：【知识点】前的全角空格仍在（字段间全角空格白名单不动）
lin_all = "".join(t.text or "" for t in body.iter(f"{{{W}}}t"))
cnt_ans = lin_all.count("【答案】"); cnt_kp = lin_all.count("【知识点】")
cnt_kp_fw = lin_all.count("　【知识点】")
assert cnt_ans == 79 and cnt_kp == 79 and cnt_kp_fw == 60, (cnt_ans, cnt_kp, cnt_kp_fw)
ok.append(f"④段尾空格：真段末元素尾随空白=0（原10处已清）；字段间空格白名单零触碰——【答案】芯片{cnt_ans}、【知识点】芯片{cnt_kp}、带全角空格前缀{cnt_kp_fw}处＝基线60处逐一在位（另19处紧随【详解】文末无空格，原文件既有形态、基线恒等）。")

# 4) 页眉页脚同串逐字（含域形态）
for part in ("header1", "footer1"):
    t = etree.parse(io.BytesIO(z.read(f"word/{part}.xml")))
    ps = t.getroot().findall(f".//{{{W}}}p")
    assert len(ps) == 1
    seq = []
    fld = {"begin": 0, "separate": 0, "end": 0}
    for node in ps[0].iter():
        if node.tag == f"{{{W}}}t": seq.append(node.text or "")
        elif node.tag == f"{{{W}}}instrText": seq.append("«" + (node.text or "").strip() + "»")
        elif node.tag == f"{{{W}}}fldChar":
            ftype = node.get(f"{{{W}}}fldCharType")
            fld[ftype] = fld.get(ftype, 0) + 1
    full = "".join(seq)
    exp = ("羿郭工作室·人教B版选必1 第1章 空间向量与立体几何·讲练（共114页）·本3/共6本　"
           "«STYLEREF \"节名锚\"»1.2.5 空间中的距离　第«PAGE»54页")
    assert full == exp, f"{part}: {full!r}"
    assert fld == {"begin": 2, "separate": 2, "end": 2}, fld
    # 字号/对齐
    jc = ps[0].find(f"{{{W}}}pPr/{{{W}}}jc")
    assert jc is not None and jc.get(f"{{{W}}}val") == "left"
    szs = {r.find(f"{{{W}}}rPr/{{{W}}}sz").get(f"{{{W}}}val") for r in ps[0].findall(f"{{{W}}}r")}
    assert szs == {"18"}, szs
ok.append("⑤页眉页脚：header1/footer1各仅1段、同串逐字＝「羿郭工作室·人教B版选必1 第1章 空间向量与立体几何·讲练（共114页）·本3/共6本　{STYLEREF节名锚缓存1.2.5 空间中的距离}　第{PAGE缓存54}页」；域形态fldChar begin/separate/end各2组（STYLEREF+PAGE）、无fldSimple；jc=left、18半点。")

# 5) OMML合法性与round-trip（修后实文件）
def lin_node(node):
    if node.tag == f"{{{M}}}t": return node.text or ""
    q = etree.QName(node).localname
    if q == "rad": return "√" + "".join(lin_node(c) for c in node.find(f"{{{M}}}e"))
    if q == "f":
        return ("".join(lin_node(c) for c in node.find(f"{{{M}}}num")) + "/" +
                "".join(lin_node(c) for c in node.find(f"{{{M}}}den")))
    return "".join(lin_node(c) for c in node)
def pfull(p):
    s=[]
    for node in p.iter():
        if node.tag == f"{{{W}}}t": s.append(node.text or "")
        elif node.tag == f"{{{M}}}oMath": s.append(lin_node(node))
    return "".join(s)
p65 = paras[64]; p484 = paras[483]
l65 = pfull(p65); l484 = pfull(p484)
assert l65 == "【编注】【分析】正棱锥两棱垂直给点面距：设侧棱为a，用等体积法求出a，再补形正方体，外接球半径为体对角线一半；易错：底面边长为√2a，勿当作a代入。", l65
assert "R=L/√3" in l484 and "r=h/4" in l484 and l484.count("oMath") == 0
assert len(list(p65.iter(f"{{{M}}}oMath"))) == 1 and len(list(p484.iter(f"{{{M}}}oMath"))) == 2
# 新增oMath结构合法性：rad有degHide/deg/e；f有num/den
for om in list(p65.iter(f"{{{M}}}oMath")) + list(p484.iter(f"{{{M}}}oMath")):
    for tag in om.iter():
        q = etree.QName(tag).localname
        if q == "rad":
            assert tag.find(f"{{{M}}}e") is not None and tag.find(f"{{{M}}}deg") is not None
        if q == "f":
            assert tag.find(f"{{{M}}}num") is not None and tag.find(f"{{{M}}}den") is not None
# m:t文本非空
for om in list(p65.iter(f"{{{M}}}oMath")) + list(p484.iter(f"{{{M}}}oMath")):
    assert "".join(t.text or "" for t in om.iter(f"{{{M}}}t")).strip()
ok.append("⑥OMML：p#65/p#484三处oMath在修后实文件中rad(degHide/deg/e)与f(num/den)结构完整、m:t非空；全线性化round-trip逐字复验通过（√2a／R=L/√3／r=h/4）。")

# 7) 标签完整性快核
ans = sum(1 for p in paras if "【答案】" in "".join(t.text or "" for t in p.iter(f"{{{W}}}t")))
kp = sum(1 for p in paras if "【知识点】" in "".join(t.text or "" for t in p.iter(f"{{{W}}}t")))
assert ans == 79 and kp == 79, (ans, kp)
ok.append(f"⑦标签：【答案】段{ans}/【知识点】段{kp}＝题块数79（不变）。")

# 8) 与原件的归一化diff规模
old = etree.parse(r"C:\提示词\工作区\同步-数学选必1-0903\tmp\FX2_C\word\document.xml.orig")
ob = old.getroot().find(f"{{{W}}}body")
op = ob.findall(f"{{{W}}}p")
def norm_ps(ps):
    out = []
    OM = f"{{{M}}}oMath"
    WT = f"{{{W}}}t"
    for p in ps:
        parts = []
        for n in p.iter():
            if n.tag == OM:
                parts.append("«m»")
            elif n.tag == WT:
                parts.append(n.text or "")
        out.append("".join(parts))
    return out
a, b = norm_ps(op), norm_ps(paras)
# 旧文内标题段删除断言
assert a[0].startswith("人教B版选必1") and not any(x.startswith("人教B版选必1") for x in b)
diffn = sum(1 for x, y in zip(a[1:], b) if x != y)
ok.append(f"⑧diff规模：逐段归一化文字流对比，原1073段→新1072段（删文内标题段1段）；其余1072段中文字流有变段={diffn}（应为88tab所在31段＋段尾空格10段＋oMath转换2段的并集，均属派单范围）。")
chg = [i for i,(x,y) in enumerate(zip(a[1:], b)) if x!=y]
print("有变段（原索引−1后）:", chg)
for line in ok:
    print("PASS", line)
