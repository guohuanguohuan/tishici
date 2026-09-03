# -*- coding: utf-8 -*-
"""FX6 独立验证：重解析部署后H件全量断言（不复用编辑内存）"""
import re, io, sys
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
DST = r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx"
import zipfile
with zipfile.ZipFile(DST) as z:
    data = z.read("word/document.xml")
tree = etree.parse(io.BytesIO(data))
root = tree.getroot()
body = root.find(f"{{{W}}}body")
paras = body.findall(f"{{{W}}}p")
OUT = []
def chk(cond, msg):
    OUT.append(("PASS" if cond else "FAIL") + " " + msg)
    if not cond:
        print("FAIL:", msg)

# 1) 题号89序列与三向恒等
tihao = []
for k, p in enumerate(paras):
    for r in p.findall(f"{{{W}}}r"):
        rPr = r.find(f"{{{W}}}rPr")
        if rPr is None: continue
        s = rPr.find(f"{{{W}}}shd")
        b = rPr.find(f"{{{W}}}b")
        if s is not None and s.get(f"{{{W}}}fill") == "C9C9C9" and b is not None:
            txt = "".join(t.text or "" for t in r.findall(f"{{{W}}}t"))
            if re.fullmatch(r"\d+(?:\.\d+)*-\d+．", txt):
                tihao.append((k, txt))
chk(len(tihao) == 89, f"题号块=89 实测{len(tihao)}")
seqs = [int(t.split("-")[1].rstrip("．")) for _, t in tihao]
chk(seqs == list(range(1, 90)), "节内序号1..89连续无重复（单节2.8）")
# 档位
def itext(k):
    return "".join(paras[k].itertext())
n_easy = sum(1 for k, _ in tihao if "简单" in itext(k))
n_mid = sum(1 for k, _ in tihao if "中档" in itext(k))
n_hard = sum(1 for k, _ in tihao if "难·冲" in itext(k))
chk(n_easy + n_mid + n_hard == 89, f"三档计数={n_easy}/{n_mid}/{n_hard} Σ=89")
# 节统计段
sec_txt = "".join(paras[1].itertext())
chk("本节89题：简单5｜中档75｜难9" in sec_txt, f"节统计段在位: {sec_txt[:50]!r}")
chk((n_easy, n_mid, n_hard) == (5, 75, 9), f"档位=5/75/9 实测{n_easy}/{n_mid}/{n_hard}")
# 题型统计段Σ
tot = 0; n_group = 0
for p in paras:
    t = "".join(p.itertext())
    m = re.search(r"　(\d+)题：", t)
    if m and re.match(r"^\d+(\.\d+)+", t):
        tot += int(m.group(1)); n_group += 1
chk(tot == 89, f"题型组统计段Σ=89 实测{tot}（组数{n_group}，登记61）")
chk(n_group == 61, f"题型组数=61 实测{n_group}")

# 2) 七类底纹（段级）
def pshd_count(fill):
    return sum(1 for p in paras if (pp := p.find(f"{{{W}}}pPr")) is not None
               and (s := pp.find(f"{{{W}}}shd")) is not None and s.get(f"{{{W}}}fill") == fill)
chk(pshd_count("ADC2DA") == 1, f"③ADC2DA段=1（1节标题，文内标题已删）实测{pshd_count('ADC2DA')}")
chk(pshd_count("C6D4E3") == 73, f"③C6D4E3段=73（讲部12+题型61）实测{pshd_count('C6D4E3')}")
chk(pshd_count("E0E0E0") == 138, f"⑦题干底纹段=138（段级真值）实测{pshd_count('E0E0E0')}")
doc_s = data.decode("utf-8")
chk(doc_s.count('w:fill="C9C9C9"') == 1222, f"C9C9C9全XML=1222（基线1220+p#617拆run+2）实测{doc_s.count(chr(119)+':fill='+chr(34)+'C9C9C9'+chr(34))}")

# 3) sectPr断言
chk(len(root.findall(f".//{{{W}}}sectPr")) == 1, "sectPr=1")
bs = body.find(f"{{{W}}}sectPr")
names = [etree.QName(c).localname for c in bs]
chk(names == ["headerReference", "footerReference", "pgSz", "pgMar", "pgNumType", "cols", "docGrid"], f"sectPr子序={names}")
chk(bs.find(f"{{{W}}}pgNumType").get(f"{{{W}}}start") == "142", "pgNumType start=142")
c = bs.find(f"{{{W}}}cols")
chk(c.get(f"{{{W}}}num") == "2" and c.get(f"{{{W}}}space") == "425" and c.get(f"{{{W}}}sep") == "1", "cols=2/425/sep1")
chk(len(root.findall(f".//{{{W}}}type")) == 0, "type=continuous随隔断段消亡")
chk("".join(paras[0].itertext()) == "2.8 直线与圆锥曲线的位置关系", f"新首段=节名锚 实测{''.join(paras[0].itertext())[:30]!r}")

# 4) 空格/tab/sz21/色
chk(len(root.findall(f".//{{{W}}}r/{{{W}}}tab")) == 0, "run级tab=0")
chk(len(root.findall(f".//{{{W}}}tabs")) == 0, "w:tabs=0")
n21 = sum(1 for e in root.iter(f"{{{W}}}sz") if e.get(f"{{{W}}}val") == "21") + \
      sum(1 for e in root.iter(f"{{{W}}}szCs") if e.get(f"{{{W}}}val") == "21")
chk(n21 == 0, f"sz21=0 实测{n21}")
ncolor = 0
for r in root.iter(f"{{{W}}}r"):
    rp = r.find(f"{{{W}}}rPr")
    if rp is None: continue
    ce = rp.find(f"{{{W}}}color")
    if ce is not None and (ce.get(f"{{{W}}}val") or "") not in ("auto", "FFFFFF"):
        ncolor += 1
chk(ncolor == 0, f"非auto/FFFFFF色run=0 实测{ncolor}")
# 双半空格（w:t层）
ndb = sum(1 for t in root.iter(f"{{{W}}}t") if t.text and "  " in t.text)
chk(ndb == 0, f"w:t内双半空格=0 实测{ndb}")
# 段尾空格
ntail = 0
for p in paras:
    ts = [t for t in p.iter(f"{{{W}}}t")]
    if ts and (ts[-1].text or "").endswith(" "):
        ntail += 1
chk(ntail == 0, f"段尾半空格=0 实测{ntail}")
# 选项行分隔唯一；抽查11段
for k in range(len(paras)):
    t = "".join(paras[k].itertext())
    if re.match(r"^\s*A．", t):
        assert "⇥" not in t
print("\n".join(OUT))
fails = [o for o in OUT if o.startswith("FAIL")]
print(f"\n{len(OUT)-len(fails)}/{len(OUT)} PASS")
