# -*- coding: utf-8 -*-
"""v2 全品式样张构建：抽取 1.1.1 节 → 按 v2 规格重排 → 输出样张 docx。
产出登记 JSON 供自查/对账使用。不触碰 样张v2-latex/ 目录。"""
import re, json, copy
from collections import Counter
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls

SRC = r"高中数学/高中数学同步/人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx"
OUT = r"工作区/全品结构提取/数学选必一/样张v2/人教B版选必1-1.1.1-v2样张.docx"
REG = r"工作区/全品结构提取/数学选必一/样张v2/_构建登记.json"

EMU_MM = 36000  # 1mm = 36000 EMU（此前误用 360000 导致全部尺寸读数×10）
reg = Counter(); detail = {}

doc = Document(SRC)
body = doc.element.body

def ptext(p):
    return "".join(t.text or "" for t in p.iter(qn("w:t")))

def norm(s):
    return s.replace("\u2060", "")

# ---------- 0. 定位截断点：第一个文本以 1.1.2 开头的 Heading3 段 ----------
kids = list(body.iterchildren())
cut = None
for i, el in enumerate(kids):
    if el.tag == qn("w:p"):
        ppr = el.find(qn("w:pPr"))
        if ppr is None: continue
        ps = ppr.find(qn("w:pStyle"))
        sty = ps.get(qn("w:val")) if ps is not None else ""
        if sty == "Heading3" and norm(ptext(el)).strip().startswith("1.1.2"):
            cut = i; break
assert cut is not None, "未找到 1.1.2 截断点"
sectPr = body.find(qn("w:sectPr"))
detail["cut_index"] = cut

# ---------- 1. 快照原文（对账基准），随后删除截断点之后内容（保留 sectPr） ----------
snap = {}   # id(el) -> text（含表格内段落）
for el in kids[:cut]:
    if el.tag == qn("w:p"):
        snap[id(el)] = ptext(el)
    elif el.tag == qn("w:tbl"):
        for p in el.iter(qn("w:p")):
            snap[id(p)] = ptext(p)

for el in kids[cut:]:
    if el is sectPr: continue
    body.remove(el)
reg["删除尾部元素数"] = len(kids) - cut - 1

kids = list(body.iterchildren())[:-1]  # 截断后的内容元素（不含 sectPr）

# ---------- 2. styles.xml：docDefaults / Normal / 样式底纹 ----------
styles = doc.styles.element
dd = styles.find(qn("w:docDefaults"))
rprd = dd.find(qn("w:rPrDefault") + "/" + qn("w:rPr"))
for tag in ("w:sz", "w:szCs"):
    e = rprd.find(qn(tag))
    if e is not None: e.set(qn("w:val"), "21")
pprd = dd.find(qn("w:pPrDefault") + "/" + qn("w:pPr"))
sp = pprd.find(qn("w:spacing"))
sp.set(qn("w:before"), "0"); sp.set(qn("w:after"), "0")
sp.set(qn("w:line"), "360"); sp.set(qn("w:lineRule"), "atLeast")
for st in styles.findall(qn("w:style")):
    if st.get(qn("w:styleId")) == "a":
        jc = st.find(qn("w:pPr") + "/" + qn("w:jc"))
        if jc is not None: jc.set(qn("w:val"), "left")

n_style_shd = 0
for shd in list(styles.iter(qn("w:shd"))):
    if shd.getparent().tag == qn("w:pPr") and shd.get(qn("w:fill")) in ("ADC2DA", "F2F2F2", "C7C7C7"):
        shd.getparent().remove(shd); n_style_shd += 1
reg["样式级pPr底纹移除"] = n_style_shd
# Heading3 样式 rPr 里的加粗撤掉（节/小节标题规格不加粗）
for st in styles.findall(qn("w:style")):
    if st.get(qn("w:styleId")) == "Heading3":
        srpr = st.find(qn("w:rPr"))
        if srpr is not None:
            for tag in ("w:b", "w:bCs"):
                e = srpr.find(qn(tag))
                if e is not None: srpr.remove(e)
# settings：不设奇偶页不同
stt = doc.settings.element
eo = stt.find(qn("w:evenAndOddHeaders"))
if eo is not None: stt.remove(eo); reg["evenAndOddHeaders移除"] = 1
else: reg["evenAndOddHeaders本无"] = 1

# ---------- 3. sectPr 挂页眉页脚引用（复用既有 header1/footer1 部件） ----------
hdr_rid = ftr_rid = None
for rid, rel in doc.part.rels.items():
    if rel.is_external: continue
    pn = str(rel.target_part.partname)
    if pn.endswith("header1.xml") and "header" in rel.reltype: hdr_rid = rid
    if pn.endswith("footer1.xml") and "footer" in rel.reltype: ftr_rid = rid
assert hdr_rid and ftr_rid, f"header/footer 关系未找到 {hdr_rid} {ftr_rid}"
for tag, rid in (("w:footerReference", ftr_rid), ("w:headerReference", hdr_rid)):
    e = OxmlElement(tag)
    e.set(qn("w:type"), "default"); e.set(qn("r:id"), rid)
    sectPr.insert(0, e)  # 先插 footer 再插 header → 最终顺序 header, footer（符合 CT_SectPr 序列）
# titlePg 不设（确认无）
assert sectPr.find(qn("w:titlePg")) is None, "sectPr 已有 titlePg"

RF_BODY = '<w:rFonts xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体" w:cs="Times New Roman"/>'
def rpr_xml(sz, color=None, bold=False, hei=False):
    fonts = ('<w:rFonts w:ascii="SimHei" w:hAnsi="SimHei" w:eastAsia="黑体" w:cs="SimHei"/>' if hei
             else RF_BODY)
    b = "<w:b/><w:bCs/>" if bold else ""
    c = f'<w:color w:val="{color}"/>' if color else ""
    return (f'<w:rPr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f"{fonts}{b}{c}<w:sz w:val=\"{sz}\"/><w:szCs w:val=\"{sz}\"/></w:rPr>")

hdr = doc.part.related_parts[hdr_rid]
for ch in list(hdr.element): hdr.element.remove(ch)
hdr.element.append(parse_xml(
    f'<w:p {nsdecls("w")}>'
    f'<w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="atLeast"/>'
    f'<w:jc w:val="center"/></w:pPr>'
    f'<w:r>{rpr_xml(18, "595959")}<w:t>1.1 空间向量及其运算</w:t></w:r>'
    f'</w:p>'))
reg["页眉段数"] = 1

ftr = doc.part.related_parts[ftr_rid]
for ch in list(ftr.element): ftr.element.remove(ch)
RPR_PG = rpr_xml(21, None, bold=True)
ftr.element.append(parse_xml(
    f'<w:p {nsdecls("w")}>'
    f'<w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="atLeast"/>'
    f'<w:jc w:val="center"/></w:pPr>'
    f'<w:r>{rpr_xml(13, "595959")}<w:t>第1章 空间向量与立体几何 · 讲练件（上）</w:t></w:r>'
    f'</w:p>'))
ftr.element.append(parse_xml(
    f'<w:tbl {nsdecls("w")}>'
    f'<w:tblPr><w:tblW w:w="1757" w:type="dxa"/><w:jc w:val="center"/>'
    f'<w:tblCellMar><w:left w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar></w:tblPr>'
    f'<w:tblGrid><w:gridCol w:w="1757"/></w:tblGrid>'
    f'<w:tr><w:trPr><w:trHeight w:val="442" w:hRule="atLeast"/></w:trPr>'
    f'<w:tc><w:tcPr><w:tcW w:w="1757" w:type="dxa"/>'
    f'<w:shd w:val="clear" w:color="auto" w:fill="DDDDDD"/><w:vAlign w:val="center"/></w:tcPr>'
    f'<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="atLeast"/>'
    f'<w:jc w:val="center"/></w:pPr>'
    f'<w:r>{RPR_PG}<w:fldChar w:fldCharType="begin"/></w:r>'
    f'<w:r>{RPR_PG}<w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
    f'<w:r>{RPR_PG}<w:fldChar w:fldCharType="separate"/></w:r>'
    f'<w:r>{RPR_PG}<w:t>1</w:t></w:r>'
    f'<w:r>{RPR_PG}<w:fldChar w:fldCharType="end"/></w:r>'
    f'</w:p></w:tc></w:tr></w:tbl>'))
ftr.element.append(parse_xml(
    f'<w:p {nsdecls("w")}>'
    f'<w:pPr><w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/>'
    f'<w:rPr><w:sz w:val="2"/><w:szCs w:val="2"/></w:rPr></w:pPr></w:p>'))
detail["页脚结构"] = "小字行 + 1x1表格(31mm/DDDDDD/高442twips/PAGE复杂域) + 护尾空段(1pt/20twips exact)"

# ---------- 4. 段落分类 ----------
RE_TK   = re.compile(r"^\d+\.\d+\.\d+\.\d+-\d+．")   # 练习题号 1.1.1.X-Y
RE_TIAO = re.compile(r"^\d+\.\d+\.\d+-\d+．")         # 讲部条目 1.1.1-Y
cls = {}
for el in kids:
    if el.tag != qn("w:p"):
        continue
    ppr = el.find(qn("w:pPr"))
    sty = ""
    if ppr is not None:
        ps = ppr.find(qn("w:pStyle"))
        sty = ps.get(qn("w:val")) if ps is not None else ""
    t = norm(ptext(el)).strip()
    pb = ppr.find(qn("w:pBdr")) if ppr is not None else None
    left18 = pb is not None and pb.find(qn("w:left")) is not None and pb.find(qn("w:left")).get(qn("w:sz")) == "18"
    if sty == "JieMingMao":
        cls[el] = "锚段"
    elif pb is not None and pb.find(qn("w:bottom")) is not None and not left18 and el is kids[0]:
        cls[el] = "章标题"
    elif sty == "Heading3" and re.match(r"^\d+\.\d+\.\d+\s", t):
        cls[el] = "小节标题"
    elif sty == "Heading3" and re.match(r"^\d+\.\d+\s", t):
        cls[el] = "节标题"
    elif left18:
        cls[el] = "组标题"
    elif RE_TK.match(t):
        cls[el] = "题号段"
    elif RE_TIAO.match(t):
        cls[el] = "条目段"
    else:
        cls[el] = "普通段"
detail["分类统计"] = dict(Counter(cls.values()))

# ---------- 5. 答案块+知识点块 合并（演示性，登记） ----------
merges = []
def is_label(p): 
    t = norm(ptext(p)).strip()
    return t.startswith("【") and "】" in t

paras = [el for el in kids if el.tag == qn("w:p")]
i = 0
while i < len(paras):
    p = paras[i]
    if norm(ptext(p)).strip().startswith("【答案】"):
        ans_block = [p]; j = i + 1
        while j < len(paras) and not norm(ptext(paras[j])).strip().startswith("【知识点】"):
            if is_label(paras[j]) or cls.get(paras[j]) in ("题号段", "组标题") or paras[j].tag == qn("w:tbl"):
                break
            ans_block.append(paras[j]); j += 1
        if j < len(paras) and norm(ptext(paras[j])).strip().startswith("【知识点】"):
            kn_block = [paras[j]]; k = j + 1
            while k < len(paras):
                q = paras[k]
                if is_label(q) or cls.get(q) in ("题号段", "组标题") or RE_TK.match(norm(ptext(q)).strip()):
                    break
                kn_block.append(q); k += 1
            host = ans_block[0]
            # 答案块后续段的内容搬到答案段
            for q in ans_block[1:]:
                for ch in list(q):
                    if ch.tag == qn("w:pPr"): continue
                    host.append(ch)
                q.getparent().remove(q)
            # 半角空格分隔 run
            spacer = OxmlElement("w:r")
            sp_rpr = parse_xml('<w:rPr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr>')
            spacer.append(sp_rpr)
            st = OxmlElement("w:t"); st.set(qn("xml:space"), "preserve"); st.text = " "
            spacer.append(st)
            host.append(spacer)
            # 知识点块内容搬到答案段
            for q in kn_block:
                for ch in list(q):
                    if ch.tag == qn("w:pPr"): continue
                    host.append(ch)
                q.getparent().remove(q)
            merges.append({"答案块": [snap[id(x)] for x in ans_block],
                           "知识点块": [snap[id(x)] for x in kn_block]})
            i = k
            continue
    i += 1
reg["答案知识点合并处数"] = len(merges)

# ---------- 5b. 剔除源排版遗留的分栏/分页符（w:br 不含文字字符，零字符增删） ----------
n_br = 0
for br in list(body.iter(qn("w:br"))):
    if br.get(qn("w:type")) in ("column", "page"):
        r = br.getparent()
        r.remove(br)
        if r.find(qn("w:t")) is None and len(r.findall(qn("w:br"))) == 0 and len(r) <= 2 and (
                r.find(qn("w:rPr")) is not None or len(r) == 0):
            pass  # 保留空 run（无字符影响）
        n_br += 1
reg["剔除分栏分页符"] = n_br

# ---------- 6. 挖空替换（演示性，登记） ----------
blanks = []
def fix_blanks_in_run(r, p):
    ts = r.findall(qn("w:t"))
    if len(ts) != 1: return False
    t = ts[0]; txt = t.text or ""
    if not re.search(r"_+", txt): return False
    parts = [x for x in re.split(r"(_+)", txt) if x != ""]
    rpr = r.find(qn("w:rPr"))
    parent, idx = r.getparent(), list(r.getparent()).index(r)
    new_runs = []
    for part in parts:
        nr = OxmlElement("w:r")
        if rpr is not None: nr.append(copy.deepcopy(rpr))
        if re.fullmatch(r"_+", part):
            rp = nr.find(qn("w:rPr"))
            if rp is None:
                rp = OxmlElement("w:rPr"); nr.insert(0, rp)
            u = OxmlElement("w:u"); u.set(qn("w:val"), "single")
            anchor = None
            for tag in ("w:shd", "w:bdr", "w:vertAlign", "w:rtl"):
                e = rp.find(qn(tag))
                if e is not None: anchor = e; break
            rp.insert(list(rp).index(anchor), u) if anchor is not None else rp.append(u)
            txt_new = "　　　　　　"
        else:
            txt_new = part
        nt = OxmlElement("w:t"); nt.set(qn("xml:space"), "preserve"); nt.text = txt_new
        nr.append(nt); new_runs.append(nr)
    for k, nr in enumerate(new_runs):
        parent.insert(idx + k, nr)
    parent.remove(r)
    blanks.append({"段": snap.get(id(p), ptext(p))[:60], "原文片段": txt[:60], "替换后": "".join(x.text or "" for x in [nr.find(qn("w:t")) for nr in new_runs])[:60]})
    return True

n_blank_runs = 0
for el in list(body.iterchildren()):
    if el.tag != qn("w:p") or cls.get(el) == "锚段": continue
    for r in list(el.iter(qn("w:r"))):
        if fix_blanks_in_run(r, el): n_blank_runs += 1
reg["挖空替换处数"] = len(blanks)

# ---------- 7. 题图三档定宽（跳过表内小图标） ----------
imgs = []
for el in list(body.iterchildren()):
    if el.tag != qn("w:p"): continue
    for host in el.iter():
        if host.tag not in (qn("wp:inline"), qn("wp:anchor")): continue
        ext = host.find(qn("wp:extent"))
        aext = host.find(".//" + qn("a:ext"))
        cx, cy = int(ext.get("cx")), int(ext.get("cy"))
        wmm = cx / EMU_MM
        nw = 30 if wmm <= 40 else (45 if wmm <= 60 else 86)
        scale = nw * EMU_MM / cx
        cy2 = round(cy * scale)
        ext.set("cx", str(nw * EMU_MM)); ext.set("cy", str(cy2))
        if aext is not None:
            aext.set("cx", str(nw * EMU_MM)); aext.set("cy", str(cy2))
        imgs.append({"段": (snap.get(id(el)) or "(图独立段)")[:30], "原mm": round(wmm, 1),
                     "新mm": nw, "新cy_mm": round(cy2 / EMU_MM, 1)})
reg["题图改宽张数"] = len(imgs)

# 表内小图标（不动，登记）
n_tbl_img = 0
for el in list(body.iterchildren()):
    if el.tag != qn("w:tbl"): continue
    n_tbl_img += len(list(el.iter(qn("wp:extent"))))
detail["表内小图标数(未动)"] = n_tbl_img

# ---------- 8. 段落统一版式 + 撤底纹 + 悬挂缩进 ----------
FONT_TAGS = ("w:rFonts", "w:sz", "w:szCs")
def set_run_pr(r, sz="21", hei=False, bold=None, color=None):
    rpr = r.find(qn("w:rPr"))
    if rpr is None:
        rpr = OxmlElement("w:rPr"); r.insert(0, rpr)
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    if hei:
        rf.set(qn("w:ascii"), "SimHei"); rf.set(qn("w:hAnsi"), "SimHei")
        rf.set(qn("w:eastAsia"), "黑体"); rf.set(qn("w:cs"), "SimHei")
    else:
        rf.set(qn("w:ascii"), "Times New Roman"); rf.set(qn("w:hAnsi"), "Times New Roman")
        rf.set(qn("w:eastAsia"), "宋体"); rf.set(qn("w:cs"), "Times New Roman")
    if bold is True:
        if rpr.find(qn("w:b")) is None: rpr.insert(1, OxmlElement("w:b"))
        if rpr.find(qn("w:bCs")) is None: rpr.append(OxmlElement("w:bCs"))
    szel = rpr.find(qn("w:sz"))
    if szel is None:
        szel = OxmlElement("w:sz"); rpr.append(szel)
    szel.set(qn("w:val"), sz)
    szcs = rpr.find(qn("w:szCs"))
    if szcs is None:
        szcs = OxmlElement("w:szCs"); rpr.append(szcs)
    szcs.set(qn("w:val"), sz)

def para_format(p, center=False):
    ppr = p.find(qn("w:pPr"))
    if ppr is None:
        ppr = OxmlElement("w:pPr"); p.insert(0, ppr)
    shd = ppr.find(qn("w:shd"))
    if shd is not None: ppr.remove(shd)
    sp = ppr.find(qn("w:spacing"))
    if sp is None:
        sp = OxmlElement("w:spacing"); ppr.insert(0, sp)
    for k, v in (("w:before", "0"), ("w:after", "0"), ("w:line", "360"), ("w:lineRule", "atLeast")):
        sp.set(qn(k), v)
    jc = ppr.find(qn("w:jc"))
    if jc is None:
        jc = OxmlElement("w:jc"); ppr.append(jc)
    jc.set(qn("w:val"), "center" if center else "left")
    mrpr = ppr.find(qn("w:rPr"))
    if mrpr is not None:
        for tag in ("w:sz", "w:szCs"):
            e = mrpr.find(qn(tag))
            if e is not None: e.set(qn("w:val"), "21")

n_pshd = 0
for el in list(body.iterchildren()):
    if el.tag == qn("w:p"):
        stack = [el]
    elif el.tag == qn("w:tbl"):
        stack = list(el.iter(qn("w:p")))
    else:
        continue
    for p in stack:
        ppr = p.find(qn("w:pPr"))
        if ppr is not None and ppr.find(qn("w:shd")) is not None:
            ppr.remove(ppr.find(qn("w:shd"))); n_pshd += 1
        if cls.get(p) == "锚段": continue
        para_format(p, center=(cls.get(p) in ("章标题", "节标题", "小节标题")))
reg["段落级底纹移除"] = n_pshd

# run 级：字体字号统一（跳过锚段与标题段）；条目段/题号段撤 run 底纹
n_run = 0; n_chip_del = 0
for el in list(body.iterchildren()):
    if el.tag == qn("w:p"):
        targets = [(el, cls.get(el))]
    elif el.tag == qn("w:tbl"):
        targets = [(p, "表格内") for p in el.iter(qn("w:p"))]
    else:
        continue
    for p, c in targets:
        if c == "锚段": continue
        title_cls = c in ("章标题", "节标题", "小节标题", "组标题")
        for r in p.iter(qn("w:r")):
            if c in ("条目段", "题号段"):
                rpr = r.find(qn("w:rPr"))
                if rpr is not None and rpr.find(qn("w:shd")) is not None:
                    rpr.remove(rpr.find(qn("w:shd"))); n_chip_del += 1
            if title_cls: continue
            set_run_pr(r); n_run += 1
reg["正文字体统一run数"] = n_run
reg["条目号牌灰底撤除"] = n_chip_del

# 标题段 styling
for el, c in cls.items():
    if c == "章标题":
        ppr = el.find(qn("w:pPr"))
        pb = ppr.find(qn("w:pBdr"))
        bt = pb.find(qn("w:bottom"))
        bt.set(qn("w:color"), "000000"); bt.set(qn("w:sz"), "4")
        for r in el.iter(qn("w:r")): set_run_pr(r, sz="44", hei=True, bold=True)
        mrpr = ppr.find(qn("w:rPr"))
        if mrpr is not None:
            for e in list(mrpr): mrpr.remove(e)
            set_run_pr(mrpr, sz="44", hei=True, bold=True) if False else None
    elif c in ("节标题", "小节标题"):
        sz = "36" if c == "节标题" else "30"
        for r in el.iter(qn("w:r")): set_run_pr(r, sz=sz, hei=True)
        ppr = el.find(qn("w:pPr"))
        ind = ppr.find(qn("w:ind"))
        if ind is not None: ppr.remove(ind)
    elif c == "组标题":
        ppr = el.find(qn("w:pPr"))
        pb = ppr.find(qn("w:pBdr")); lf = pb.find(qn("w:left"))
        lf.set(qn("w:color"), "000000"); lf.set(qn("w:sz"), "18")
        for r in el.iter(qn("w:r")): set_run_pr(r, sz="24", bold=True)

# 悬挂缩进
def set_ind(p, hanging):
    ppr = p.find(qn("w:pPr"))
    if ppr is None:
        ppr = OxmlElement("w:pPr"); p.insert(0, ppr)
    ind = ppr.find(qn("w:ind"))
    if ind is None:
        ind = OxmlElement("w:ind")
        jc = ppr.find(qn("w:jc"))
        ppr.insert(list(ppr).index(jc) if jc is not None else len(list(ppr)), ind)
    for a in ("w:left", "w:leftChars", "w:hanging", "w:hangingChars", "w:firstLine", "w:firstLineChars"):
        if ind.get(qn(a)) is not None: del ind.attrib[qn(a)]
    ind.set(qn("w:left"), "400")
    if hanging: ind.set(qn("w:hanging"), "400")

n_group = 0; n_hang = 0
state = False
for el in list(body.iterchildren()):
    if el.tag == qn("w:tbl"):
        state = False; continue
    if el.tag != qn("w:p"): continue
    c = cls.get(el)
    if c in ("章标题", "节标题", "小节标题", "组标题", "锚段"):
        state = False; continue
    t = norm(ptext(el)).strip()
    if RE_TK.match(t):
        state = True; set_ind(el, True); n_hang += 1; continue
    if RE_TIAO.match(t):
        state = True; set_ind(el, False); n_group += 1; continue
    if state:
        set_ind(el, False); n_group += 1
reg["悬挂题号段数"] = n_hang
reg["组内左缩进段数"] = n_group

# ---------- 9. 表头行黑体加粗（按证据） ----------
tbl_notes = []
for ti, el in enumerate([e for e in body.iterchildren() if e.tag == qn("w:tbl")]):
    rows = el.findall(qn("w:tr"))
    row0 = rows[0]
    ev = []
    if row0.find(qn("w:trPr") + "/" + qn("w:tblHeader")) is not None: ev.append("tblHeader")
    if any(tc.find(qn("w:tcPr") + "/" + qn("w:shd")) is not None for tc in row0.findall(qn("w:tc"))): ev.append("row0单元格shd")
    look = el.find(qn("w:tblPr") + "/" + qn("w:tblLook"))
    if look is not None and look.get(qn("w:firstRow")) == "1": ev.append("tblLook.firstRow")
    if ev:
        for r in row0.iter(qn("w:r")):
            set_run_pr(r, bold=True)
            rpr = r.find(qn("w:rPr")); rf = rpr.find(qn("w:rFonts"))
            rf.set(qn("w:eastAsia"), "黑体")
    tbl_notes.append({"表": ti, "行数": len(rows), "表头证据": ev, "已加粗": bool(ev)})
detail["表格"] = tbl_notes

# ---------- 10. 保存 + 登记 ----------
doc.save(OUT)
detail["合并明细"] = merges
detail["挖空明细"] = blanks
detail["图片明细"] = imgs
detail["页眉页脚引用"] = {"header": hdr_rid, "footer": ftr_rid}
with open(REG, "w", encoding="utf-8") as f:
    json.dump({"计数": dict(reg), "明细": detail}, f, ensure_ascii=False, indent=1)
print("登记计数:", dict(reg))
print("分类:", detail["分类统计"])
print("表格:", json.dumps(tbl_notes, ensure_ascii=False))
print("图片:", json.dumps(imgs, ensure_ascii=False))
print("挖空:", json.dumps(blanks, ensure_ascii=False)[:600])
print("OK ->", OUT)
