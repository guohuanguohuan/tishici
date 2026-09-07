# -*- coding: utf-8 -*-
"""
项目成品件排版参数实测（python-docx + 底层 XML）
对象：高中数学/高中数学同步/ 下 5 个选必一成品件
输出：stdout 报告，同时存 排版参数-实测输出.txt 备查
只读，不修改任何 docx。
"""
import io
import os
import re
import sys
from collections import Counter

from docx import Document
from docx.oxml.ns import qn

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = r"C:\提示词\高中数学\高中数学同步"
FILES = {
    "讲练件(上61)": "人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx",
    "讲练件(2.8)": "人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx",
    "知识清单": "人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx",
    "衔接件": "人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx",
    "使用说明": "人教B版选必1·使用说明.docx",
}

RE_QNUM = re.compile(r"^\d+(?:\.\d+)*-\d+．")          # 题号行 1.1.1-1．
RE_COL = re.compile(r"^\d+(?:\.\d+)+\s+\S+｜")          # 栏目行 1.1.1.1 知识讲解｜…
WJ = "\u2060"  # word joiner（标签内隐字符）
RE_LABEL = re.compile(r"^【([^】]{1,8})】")
EMU_PER_MM = 36000.0
TW_PER_MM = 56.6929  # 1mm = 56.6929 twips


def mm_from_emu(v):
    return None if v is None else round(int(v) / EMU_PER_MM, 1)


def tw_to_mm(v):
    return None if v is None else round(int(v) / TW_PER_MM, 1)


def tw_to_pt(v):
    return None if v is None else round(int(v) / 20.0, 2)


def halfpt_to_pt(v):
    return None if v is None else round(int(v) / 2.0, 1)


def el_attr(el, tag, attr):
    sub = el.find(qn(tag))
    return None if sub is None else sub.get(qn(attr))


def spacing_desc(sp):
    """w:spacing 元素 → (before_pt, after_pt, line, lineRule)"""
    if sp is None:
        return None
    before = sp.get(qn("w:before"))
    after = sp.get(qn("w:after"))
    line = sp.get(qn("w:line"))
    rule = sp.get(qn("w:lineRule"))
    return (
        tw_to_pt(before), tw_to_pt(after),
        None if line is None else (round(int(line) / 240.0, 2) if rule in (None, "auto") else tw_to_pt(line)),
        rule or "auto",
    )


def para_font_info(p):
    """段落显式 run 级字号/中文字体的众数来源"""
    szs, eas, fonts = [], [], []
    for r in p.runs:
        rpr = r._element.find(qn("w:rPr"))
        if rpr is None:
            continue
        szel = rpr.find(qn("w:sz"))
        if szel is not None:
            szs.append(halfpt_to_pt(szel.get(qn("w:val"))))
        rf = rpr.find(qn("w:rFonts"))
        if rf is not None:
            eas.append(rf.get(qn("w:eastAsia")))
            if rf.get(qn("w:ascii")):
                fonts.append(rf.get(qn("w:ascii")))
    return Counter(szs), Counter(eas), Counter(fonts)


def para_ppr_flags(p):
    ppr = p._p.find(qn("w:pPr"))
    d = {}
    if ppr is None:
        return d
    sp = ppr.find(qn("w:spacing"))
    if sp is not None:
        d["spacing"] = spacing_desc(sp)
    ind = ppr.find(qn("w:ind"))
    if ind is not None:
        d["ind"] = {
            "left": tw_to_mm(ind.get(qn("w:left")) or ind.get(qn("w:start"))),
            "hanging": tw_to_mm(ind.get(qn("w:hanging"))),
            "firstLine": tw_to_mm(ind.get(qn("w:firstLine"))),
        }
    shd = ppr.find(qn("w:shd"))
    if shd is not None:
        d["shd"] = shd.get(qn("w:fill"))
    jc = ppr.find(qn("w:jc"))
    if jc is not None:
        d["jc"] = jc.get(qn("w:val"))
    return d


def style_info(st):
    if st is None:
        return None
    el = st.element
    rpr = el.find(qn("w:rPr"))
    ppr = el.find(qn("w:pPr"))
    out = {}
    if rpr is not None:
        sz = rpr.find(qn("w:sz"))
        out["sz_pt"] = halfpt_to_pt(sz.get(qn("w:val"))) if sz is not None else None
        rf = rpr.find(qn("w:rFonts"))
        if rf is not None:
            out["eastAsia"] = rf.get(qn("w:eastAsia"))
            out["ascii"] = rf.get(qn("w:ascii"))
        out["bold"] = rpr.find(qn("w:b")) is not None and rpr.find(qn("w:b")).get(qn("w:val")) != "0"
        out["vanish"] = rpr.find(qn("w:vanish")) is not None
    if ppr is not None:
        sp = ppr.find(qn("w:spacing"))
        out["spacing"] = spacing_desc(sp) if sp is not None else None
        shd = ppr.find(qn("w:shd"))
        out["shd"] = shd.get(qn("w:fill")) if shd is not None else None
        ind = ppr.find(qn("w:ind"))
        if ind is not None:
            out["ind"] = {k: tw_to_mm(ind.get(qn("w:" + k))) for k in ("left", "hanging", "firstLine") if ind.get(qn("w:" + k))}
    return out


def sect_report(doc):
    out = []
    for i, s in enumerate(doc.sections):
        sp = s._sectPr
        cols = sp.find(qn("w:cols"))
        cd = {}
        if cols is not None:
            num = cols.get(qn("w:num"))
            space = cols.get(qn("w:space"))
            cd = {
                "num": int(num) if num else 1,
                "space_mm": tw_to_mm(space) if space else None,
                "sep": cols.get(qn("w:sep")),
                "equalWidth": cols.get(qn("w:equalWidth")),
            }
        tw = mm_from_emu(s.page_width) - mm_from_emu(s.left_margin) - mm_from_emu(s.right_margin)
        if cd.get("num", 1) > 1:
            n = cd["num"]
            gaps = cd["space_mm"] or 0.0
            cd["col_w_mm"] = round((tw - gaps * (n - 1)) / n, 1)
        hdrs = []
        for kind, hf in (("页眉", s.header), ("页脚", s.footer)):
            txt = ""
            szs = Counter()
            fields = []
            if hf is not None and not hf.is_linked_to_previous:
                txt = " ".join(p.text.strip() for p in hf.paragraphs if p.text.strip())
                for p in hf.paragraphs:
                    szs += para_font_info(p)[0]
                    for fi in p._p.findall(".//" + qn("w:fldSimple")):
                        fields.append(fi.get(qn("w:instr")))
                    for ic in p._p.findall(".//" + qn("w:instrText")):
                        fields.append(ic.text)
            hdrs.append(f"{kind}:linked={hf.is_linked_to_previous if hf is not None else '?'} sz={dict(szs)} 域={fields} 文本={txt[:70]!r}")
        out.append({
            "idx": i,
            "pgSz_mm": (mm_from_emu(s.page_width), mm_from_emu(s.page_height)),
            "mar_mm_TBR L": (mm_from_emu(s.top_margin), mm_from_emu(s.bottom_margin),
                             mm_from_emu(s.header_distance), mm_from_emu(s.footer_distance),
                             mm_from_emu(s.left_margin), mm_from_emu(s.right_margin)),
            "cols": cd,
            "text_w_mm": round(tw, 1),
            "header_footer": hdrs,
            "titlePg": sp.find(qn("w:titlePg")) is not None,
        })
    return out


def doc_defaults(doc):
    el = doc.styles.element
    dd = el.find(qn("w:docDefaults"))
    out = {}
    if dd is not None:
        rpr = dd.find(qn("w:rPrDefault") + "/" + qn("w:rPr"))
        if rpr is not None:
            sz = rpr.find(qn("w:sz"))
            out["sz_pt"] = halfpt_to_pt(sz.get(qn("w:val"))) if sz is not None else None
            rf = rpr.find(qn("w:rFonts"))
            if rf is not None:
                out["eastAsia"] = rf.get(qn("w:eastAsia"))
                out["ascii"] = rf.get(qn("w:ascii"))
                out["hAnsi"] = rf.get(qn("w:hAnsi"))
        ppr = dd.find(qn("w:pPrDefault") + "/" + qn("w:pPr"))
        if ppr is not None:
            sp = ppr.find(qn("w:spacing"))
            out["pPr_spacing"] = spacing_desc(sp) if sp is not None else None
    return out


def classify(p):
    t = p.text.strip().replace(WJ, "")
    st = p.style.name
    if st == "Heading 3":
        return "H3节标题"
    if st == "节名锚":
        return "节名锚"
    if RE_COL.match(t):
        return "栏目行"
    if RE_QNUM.match(t):
        return "题号行"
    if RE_LABEL.match(t):
        return "标签行:" + RE_LABEL.match(t).group(1)
    return None


def report_file(key, path):
    doc = Document(path)
    print("\n" + "=" * 30)
    print(f"### {key}  ({os.path.basename(path)})")
    print("docDefaults:", doc_defaults(doc))
    for sn in ("Normal", "Heading 3", "节名锚"):
        try:
            print(f"style[{sn}]:", style_info(doc.styles[sn]))
        except KeyError:
            print(f"style[{sn}]: (无)")
    for s in sect_report(doc):
        print("section:", s)
    # 分节符位置与类型
    idx = 0
    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:p"):
            ppr = child.find(qn("w:pPr"))
            if ppr is not None and ppr.find(qn("w:sectPr")) is not None:
                spx = ppr.find(qn("w:sectPr"))
                typ = spx.find(qn("w:type"))
                t = "".join(x.text or "" for x in child.findall(".//" + qn("w:t")))
                print(f"  分节符@第{idx}段: type={typ.get(qn('w:val')) if typ is not None else 'nextPage(默认)'} 断点段文本={t[:30]!r}")
            idx += 1

    groups = {}
    shd_counter = Counter()
    run_shd_counter = Counter()
    blank_lens = Counter()
    underline_runs = []
    chip_samples = Counter()
    auto_shd_samples = []
    img_inline = img_anchor = 0
    anchor_wrap = Counter()
    anchor_dist = Counter()
    inline_jc = Counter()
    inline_w = Counter()
    img_para_texts = []

    for p in doc.paragraphs:
        ppr = p._p.find(qn("w:pPr"))
        shd = ppr.find(qn("w:shd")) if ppr is not None else None
        if shd is not None:
            fill = shd.get(qn("w:fill"))
            shd_counter[fill] += 1
        cls = classify(p)
        if cls:
            groups.setdefault(cls, []).append(p)
        # run 级底纹与挖空
        for r in p.runs:
            rpr = r._element.find(qn("w:rPr"))
            if rpr is not None:
                rs = rpr.find(qn("w:shd"))
                if rs is not None:
                    run_shd_counter[rs.get(qn("w:fill"))] += 1
                    if rs.get(qn("w:fill")) == "C7C7C7" and r.text.strip():
                        chip_samples[r.text.strip().replace(WJ, "")[:12]] += 1
                if rpr.find(qn("w:u")) is not None:
                    underline_runs.append(r.text[:20])
            for m in re.finditer(r"_+", r.text):
                blank_lens[len(m.group())] += 1
        # 图
        el = p._p
        for inl in el.findall(".//" + qn("wp:inline")):
            img_inline += 1
            ext = inl.find(qn("wp:extent"))
            if ext is not None:
                inline_w[round(int(ext.get("cx")) / EMU_PER_MM, 1)] += 1
            pp = ppr.find(qn("w:jc")) if ppr is not None else None
            inline_jc[pp.get(qn("w:val")) if pp is not None else "(默认左)"] += 1
        if shd is not None and shd.get(qn("w:fill")) == "auto" and len(auto_shd_samples) < 3:
            auto_shd_samples.append((p.style.name, p.text.strip().replace(WJ, "")[:24]))
        for an in el.findall(".//" + qn("wp:anchor")):
            img_anchor += 1
            for child in an:
                tag = child.tag.split("}")[1]
                if tag.startswith("wrap"):
                    anchor_wrap[tag] += 1
            for a in ("distT", "distB", "distL", "distR"):
                if an.get(a):
                    anchor_dist[a] += 1
            if len(img_para_texts) < 3:
                img_para_texts.append(("anchor", p.text.strip()[:30]))

    def agg(name):
        ps = groups.get(name, [])
        if not ps:
            return
        sp_desc, ind_desc, shd_desc, sz_c, ea_c = Counter(), Counter(), Counter(), Counter(), Counter()
        samples = []
        for p in ps:
            d = para_ppr_flags(p)
            if "spacing" in d:
                sp_desc[d["spacing"]] += 1
            if "ind" in d:
                ind_desc[tuple(sorted(d["ind"].items()))] += 1
            else:
                ind_desc[("无显式缩进",)] += 1
            if "shd" in d:
                shd_desc[d["shd"]] += 1
            szs, eas, _ = para_font_info(p)
            sz_c += szs
            ea_c += eas
            if len(samples) < 2 and p.text.strip():
                samples.append(p.text.strip().replace(WJ, "")[:36])
        print(f"  [{name}] n={len(ps)}")
        if sp_desc:
            print("    spacing:", sp_desc.most_common(3))
        print("    ind:", ind_desc.most_common(3))
        if shd_desc:
            print("    段级shd:", shd_desc.most_common(3))
        if sz_c:
            print("    run_sz:", sz_c.most_common(3), " eastAsia:", ea_c.most_common(2))
        if samples:
            print("    例:", samples)

    print("-- 段落分组实测 --")
    for name in list(groups):
        agg(name)
    # 章标题：正文前两段中含“人教B版选必1”的段
    for p in doc.paragraphs[:3]:
        if p.text.strip().startswith("人教B版选必1"):
            d = para_ppr_flags(p)
            szs, eas, _ = para_font_info(p)
            print("  [章标题]", p.text.strip()[:30], d, "run_sz:", szs.most_common(2), "eastAsia:", eas.most_common(1))
            break
    print("-- 底纹 --")
    print("  段级shd fill 分布:", shd_counter.most_common(8))
    print("  run级shd fill 分布:", run_shd_counter.most_common(5))
    if chip_samples:
        print("  C7C7C7 run 文本样例:", chip_samples.most_common(6))
    if auto_shd_samples:
        print("  fill=auto 段样例:", auto_shd_samples)
    if shd_counter:
        # F2F2F2 段落的归属抽样
        hits = [p for p in doc.paragraphs if (p._p.find(qn("w:pPr")) is not None
                and p._p.find(qn("w:pPr")).find(qn("w:shd")) is not None
                and p._p.find(qn("w:pPr")).find(qn("w:shd")).get(qn("w:fill")) in ("F2F2F2", "E0E0E0"))]
        lab = Counter()
        for p in hits:
            t = p.text.strip()
            if RE_QNUM.match(t):
                lab["题号行"] += 1
            elif RE_LABEL.match(t):
                lab["标签行:" + RE_LABEL.match(t).group(1)] += 1
            elif t:
                lab["题干/其他"] += 1
            else:
                lab["空段"] += 1
        print(f"  F2F2F2/E0E0E0 段落共 {len(hits)} 段，构成:", lab.most_common(8))
        tail = [p.text.strip()[:24] for p in hits[-2:]]
        print("    末尾样例:", tail)
    print("-- 挖空 --")
    print("  '_' 连字符长度分布:", blank_lens.most_common(10), " 合计", sum(blank_lens.values()))
    print("  w:u 下划线run数:", len(underline_runs), underline_runs[:5])
    wus = doc.element.body.findall(".//" + qn("w:u"))
    if wus:
        uval = Counter(w.get(qn("w:val")) for w in wus)
        print(f"  全文XML w:u 共{len(wus)}个, val分布: {dict(uval)}")
    print("-- 图 --")
    print(f"  inline={img_inline} (jc分布{dict(inline_jc)}, 宽mm众数{inline_w.most_common(3)})")
    print(f"  anchor={img_anchor} (wrap分布{dict(anchor_wrap)}, dist{dict(anchor_dist)})")
    if img_para_texts:
        print("  anchor所在段:", img_para_texts)


def main():
    out = io.StringIO()
    old = sys.stdout
    sys.stdout = out
    for k, f in FILES.items():
        report_file(k, os.path.join(BASE, f))
    sys.stdout = old
    text = out.getvalue()
    print(text)
    with open(os.path.join(os.path.dirname(__file__), "排版参数-实测输出.txt"), "w", encoding="utf-8") as fh:
        fh.write(text)


if __name__ == "__main__":
    main()
