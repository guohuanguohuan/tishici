# 选必一各节元素密度普查：图/表/题块/挖空/公式 逐节计数，为 v2 样张选节
import glob, re
from docx import Document
from docx.oxml.ns import qn

FILES = [f for f in glob.glob(r"高中数学/高中数学同步/人教B版选必1*.docx")
         if "讲练件" in f or "知识清单" in f]

def para_style(p):
    st = p.find(qn("w:pPr") + "/" + qn("w:pStyle")) if False else None
    ppr = p.find(qn("w:pPr"))
    if ppr is None: return ""
    ps = ppr.find(qn("w:pStyle"))
    return ps.get(qn("w:val")) if ps is not None else ""

def para_text(p):
    return "".join(t.text or "" for t in p.iter(qn("w:t")))

for f in FILES:
    doc = Document(f)
    body = doc.element.body
    cur = "（章首）"
    sec = {}
    order = []
    for el in body.iterchildren():
        if el.tag == qn("w:tbl"):
            s = sec.setdefault(cur, dict(tbl=0, img=0, math=0, para=0, blank=0, tk=0))
            s["tbl"] += 1
            continue
        if el.tag != qn("w:p"):
            continue
        s = sec.setdefault(cur, dict(tbl=0, img=0, math=0, para=0, blank=0, tk=0))
        if cur not in order: order.append(cur)
        sty = para_style(el)
        txt = para_text(el).strip()
        # 节标题判定：标题3样式
        if sty in ("标题3", "Heading3", "3"):
            cur = txt[:40]
            sec.setdefault(cur, dict(tbl=0, img=0, math=0, para=0, blank=0, tk=0))
            if cur not in order: order.append(cur)
            continue
        s["para"] += 1
        s["img"] += len(el.findall(".//" + qn("wp:inline")))
        s["math"] += len(el.findall(".//" + qn("m:oMath")))
        s["blank"] += len(re.findall(r"_+", txt))
        if re.match(r"^\d[\d.]*-\d+．", txt): s["tk"] += 1
    print("=" * 100)
    print(f.split("/")[-1])
    for name in order:
        s = sec[name]
        print(f"  {name:<42} 图{s['img']:>3} 表{s['tbl']:>2} 题{s['tk']:>3} 挖空{s['blank']:>2} 公式{s['math']:>4} 段{s['para']:>4}")
