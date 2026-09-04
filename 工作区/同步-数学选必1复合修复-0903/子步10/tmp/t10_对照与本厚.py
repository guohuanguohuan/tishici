# -*- coding: utf-8 -*-
"""T1三方对照＋T2实测轨本厚＋T3 §12三上限（全部读已落盘实测件，零COM）。
数据源：实测_逐件.jsonl／t10_start采集.json／t10_sha比对.json／t10_册目录dump.json
       ＋装订单md／盖章记录md 原文解析（禁转抄在案dump数值）。"""
import json, os, re, sys

TMP = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步10\tmp"
ZD = r"C:\提示词\高中数学\高中数学同步\人教B版选必1·装订单.md"
GS = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步7\盖章记录_子步7.md"
OUT = os.path.join(TMP, "t10_对照与本厚.json")

# 短名→实名（报告-子步7 §一表）＋装订单序键（§五映射）
KEYS = [
    ("X1", "人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx", 5, 29),
    ("I1", "人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx", 7, 47),
    ("B", "人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx", 9, 61),
    ("C", "人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx", 10, 79),
    ("X2", "人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx", 12, 13),
    ("I2", "人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx", 14, 67),
    ("E", "人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx", 16, 92),
    ("F", "人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx", 17, 90),
    ("G", "人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx", 18, 68),
    ("H", "人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx", 19, 89),
]

def load(name):
    with open(os.path.join(TMP, name), encoding="utf-8") as f:
        return json.load(f)

_jl = [json.loads(ln) for ln in open(os.path.join(TMP, "实测_逐件.jsonl"), encoding="utf-8") if ln.strip()]
pages_com = {r["件名"]: r["页数"] for r in _jl}
forms = {r["件名"]: r["路径形态"] for r in _jl}
starts = {r["件"]: r["首节start"] for r in load("t10_start采集.json")}
sizes = {r["件"]: r["体积字节"] for r in load("t10_sha比对.json")["逐件"]}

# 装订单§一表解析：序→(页数, 区间左端, 本)
zd = open(ZD, encoding="utf-8").read()
zd_rows = {}
for m in re.finditer(r"\|\s*(\d+)\s*\|([^|]+)\|\s*(\d+)\s*\|\s*P\d+\s+(\d+)[–-]\d+\s*\|[^|]+\|\s*(本\d+)\s*\|", zd):
    zd_rows[int(m.group(1))] = {"件": m.group(2).strip(), "页数": int(m.group(3)),
                                "左端": int(m.group(4)), "本": m.group(5)}
# 盖章记录解析：实名→(页数,start)
gs_rows = {}
for m in re.finditer(r"\|\s*P\d+\s*\|\s*本\d+\s*\|\s*(人教B版选必1[^|]+\.docx)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", open(GS, encoding="utf-8").read()):
    gs_rows[m.group(1).strip()] = {"页数": int(m.group(2)), "start": int(m.group(3))}
# 册目录页件级行：·本N页
cd = load("t10_册目录dump.json")["锚定件级行"]
cd_ben = {i: int(re.search(r"·本(\d+)页", cd[str(i)]["text"]).group(1)) for i in (3, 4, 5, 9, 10, 11)}

rows, red = [], []
for key, name, xu, tishu in KEYS:
    mp = pages_com.get(name)
    zr, gr = zd_rows[xu], gs_rows[name]
    rows.append({"短名": key, "实名": name, "装订单序": xu, "本": zr["本"],
                 "题数": tishu, "题数口径": "非文件名口径（装订单§一↔册目录页同源）" if "知识清单" in name else "文件名口径",
                 "页数实测": mp, "装订单页数": zr["页数"], "盖章记录页数": gr["页数"],
                 "页数①等": mp == zr["页数"],
                 "start实测": starts[name], "盖章start": gr["start"], "装订单左端": zr["左端"],
                 "start③等": starts[name] == gr["start"] == zr["左端"],
                 "体积字节": sizes[name], "路径形态": forms.get(name)})
    if mp != zr["页数"]:
        red.append(f"页数①差异 {key}: 实测{mp} vs 装订单{zr['页数']}")
    if not (starts[name] == gr["start"] == zr["左端"]):
        red.append(f"start③差异 {key}: 实测{starts[name]} 盖章{gr['start']} 装订单{zr['左端']}")

# ② 册目录页六行对照
cmp2 = {
    "X1": (pages_com[KEYS[0][1]], cd_ben[3]), "I1": (pages_com[KEYS[1][1]], cd_ben[4]),
    "B+C": (pages_com[KEYS[2][1]] + pages_com[KEYS[3][1]], cd_ben[5]),
    "X2": (pages_com[KEYS[4][1]], cd_ben[9]), "I2": (pages_com[KEYS[5][1]], cd_ben[10]),
    "E+F+G+H": (sum(pages_com[k[1]] for k in KEYS[6:]), cd_ben[11]),
}
for k, (a, b) in cmp2.items():
    if a != b:
        red.append(f"页数②差异 {k}: 实测{a} vs 册目录页{b}")

# T2(a) 本厚实测轨
bens = {"本1": ["X1"], "本2": ["I1"], "本3": ["B", "C"], "本4": ["X2"], "本5": ["I2"],
        "本6": ["E", "F", "G", "H"]}
name_of = {k: n for k, n, _x, _t in KEYS}
ben_vals = {b: sum(pages_com[name_of[k]] for k in ks) for b, ks in bens.items()}
total = sum(ben_vals.values())
ben_flag = {b: (v <= 400) for b, v in ben_vals.items()}
if not all(ben_flag.values()):
    red.append("本厚>400停报：" + json.dumps({b: v for b, v in ben_vals.items() if v > 400}))

# T3 §12三上限
t3 = []
for r in rows:
    mb = r["体积字节"] / 1048576
    t3.append({"短名": r["短名"], "题数": r["题数"], "题≤100": r["题数"] <= 100,
               "页数": r["页数实测"], "页≤80": r["页数实测"] <= 80,
               "体积MB": round(mb, 2), "≤80MB": mb <= 80, ">50MB需媒体审计": mb > 50})
    if not (r["题数"] <= 100 and r["页数实测"] <= 80 and mb <= 80):
        red.append(f"§12超限 {r['短名']}: 题{r['题数']} 页{r['页数实测']} {mb:.1f}MB")

out = {"三方对照": rows, "册目录六行对照": cmp2, "T2a本厚": ben_vals,
       "全册合计": total, "本数": len(ben_vals), "逐本≤400": ben_flag,
       "册数复评": "M＝6 维持（最大本6={}页≤400，最小本4={}页，无合并/拆分必要）".format(ben_vals["本6"], ben_vals["本4"]),
       "T3": t3, "红旗": red}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ("册目录六行对照", "T2a本厚", "全册合计", "本数", "逐本≤400", "红旗")}, ensure_ascii=False, indent=1))
for r in rows:
    print(f"{r['短名']:>3} 序{r['装订单序']:>2} {r['本']} 页:测{r['页数实测']}/单{r['装订单页数']} start:测{r['start实测']}/章{r['盖章start']}/单{r['装订单左端']} ①{r['页数①等']} ③{r['start③等']} {r['体积字节']}B [{r['路径形态']}]")
sys.exit(1 if red else 0)
