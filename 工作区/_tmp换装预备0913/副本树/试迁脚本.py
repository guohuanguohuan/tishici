# -*- coding: utf-8 -*-
"""M2 导学本课时01 锚点迁移试迁脚本（换装预备轮·副本树内作业）。

依据：工作区/_tmp换装预备0913/换装方案草案.md §1（锚点迁移法＋成组 \\ansline 键级拆分＋三件型插入规则）。
红线：答案册 body.tex 与 M2 成卷正件只读（本脚本仅 open('r')）；一切写入限本副本树。
断言：课时01 键数＝19（义务总表：预习填空1＋判5＋探例变8＋评价5）；拆分重组恒等原值；
      任一锚点未命中/多命中即停；拆分不出→整组迁组首题＋余键发射同值＋记「共键」（禁猜）。
"""
import io, os, re

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "导学件", "课时01")  # 副本树/导学件/课时01
ANSBODY = r"C:/提示词/工作区/M2-第1章量产0911/成卷/答案册/body.tex"  # 只读迁移源
KS = "导-课时01"

def read(p):
    with io.open(p, "r", encoding="utf-8") as f:
        return f.read()

# ---------- 1. 键内容提取（机器步）：% pair:<键> 切块 → 成组键→label/value ----------
body = read(ANSBODY)
groups, cur = [], None
for ln in body.split("\n"):
    m = re.match(r"^% pair:(\S+)$", ln.strip())
    if m:
        if cur is None:
            cur = {"keys": [], "value": None, "label": ""}
        cur["keys"].append(m.group(1))
    elif cur is not None:
        if ln.strip() == "" or ln.strip().startswith(("\\qufen", "\\jietitle", "\\vskip")):
            groups.append(cur); cur = None
            m2 = re.match(r"^\\ansline\{(.+?)\}\{(.+)\}\s*$", ln)
        else:
            m2 = re.match(r"^\\ansline\{(.+?)\}\{(.+)\}\s*$", ln)
        if cur is not None and m2:
            cur["label"], cur["value"] = m2.group(1), m2.group(2)
            groups.append(cur); cur = None
if cur: groups.append(cur)
kmap = {}
for g in groups:
    for k in g["keys"]:
        kmap[k] = {"label": g["label"], "value": g["value"], "group": list(g["keys"])}

WANT = ([KS + "-预习填空"] + [KS + "-判%d" % i for i in range(1, 6)]
        + [KS + "-探%d-%s" % (i, j) for i in range(1, 5) for j in ("例1", "变式1")]
        + [KS + "-评%d" % i for i in range(1, 6)])
missing = [k for k in WANT if k not in kmap]
assert not missing, "缺键即停：%s" % missing
novalue = [k for k in WANT if not kmap[k]["value"]]
assert not novalue, "组值缺失即停：%s" % novalue
extra = [k for k in kmap if k.startswith(KS + "-") and k not in WANT]
assert not extra, "多键即停：%s" % extra

# ---------- 2. 键级拆分（成组 \ansline → 单键值；拆分不出→共键，禁猜） ----------
uncertain = []
def split_group(key):
    grp = kmap[key]["group"]; val = kmap[key]["value"]
    if len(grp) == 1:
        return {grp[0]: val}
    if all(re.match(r"^%s-判\d$" % re.escape(KS), k) for k in grp):
        valn = re.sub(r"^\((\d+)\)", r"\\quad (\1)", val.strip())   # 首项 (N) 归一为可切分形
        parts = re.split(r"\\quad\s*\((\d+)\)", " " + valn)         # (N) 序拆单值
        nums = parts[1::2]; vals = [p.strip() for p in parts[2::2]]
        if len(nums) == len(grp) and all(vals):
            reasm = "(%s)%s" % (nums[0], vals[0])
            for n, v in zip(nums[1:], vals[1:]): reasm += "\\quad (%s)%s" % (n, v)
            assert reasm == val, "判组重组不等原值"
            return dict(zip(grp, vals))
    if all(re.match(r"^%s-评\d$" % re.escape(KS), k) for k in grp):
        parts = re.split(r"(\d+)．", " " + val)                 # N．序拆单值
        nums = parts[1::2]; vals = [p.rstrip("；").strip() for p in parts[2::2]]
        if len(nums) == len(grp) and all(vals):
            reasm = "%s．%s" % (nums[0], vals[0])
            for n, v in zip(nums[1:], vals[1:]): reasm += "；%s．%s" % (n, v)
            assert reasm == val, "评组重组不等原值"
            return dict(zip(grp, vals))
    if all(re.match(r"^%s-探\d-(例1|变式1)$" % re.escape(KS), k) for k in grp):
        m = re.match(r"^例1 (.+)；变式1 (.+)$", val)             # 「例1 X；变式1 Y」分隔符拆
        if m:
            return {grp[0]: m.group(1), grp[1]: m.group(2)}
    uncertain.append({"group": grp, "value": val,
                      "处置": "整组迁组首题 %s，余键共键发射同值（禁猜）" % grp[0]})
    return {grp[0]: val}                                         # 拆分不出：整组迁组首题

plan = {}
for k in WANT:
    if k not in plan:
        plan.update(split_group(k))

# ---------- 3. 件内插入（机器＋规则）：预迁移源＝副本树 main.src.tex ----------
tex = read(os.path.join(HERE, "main.src.tex"))

def sub_once(old, new, tag):
    global tex
    n = tex.count(old)
    assert n == 1, "锚点[%s]命中 %d 次（须恰 1）" % (tag, n)
    tex = tex.replace(old, new, 1)

def block(key, label, value, inner):
    b = "\\begin{ansblock}[%s]\n%% ans:%s\n" % (key, key)
    b += ("\\ansitem{%s}{%s}" % (label, value)) if inner == "ansitem" \
         else ("\\ansnote{%s}{%s}" % (label, value))
    return b + "\n\\end{ansblock}"

log = []

# 3.1 导言：六宏 \input → qp-m3 单包；补 \qpceming 回钉；删件内已收编局部宏
sub_once("""\\documentclass[fontset=none]{ctexart}
\\input{qp-fonts.tex}
\\input{qp-layout.tex}
\\input{qp-parts.tex}
\\input{qp-headfoot.tex}
\\input{qp-titles.tex}
\\input{qp-blocks.tex}""",
"\\documentclass[fontset=none]{ctexart}\n\\usepackage{qp-m3}", "导言六宏→qp-m3")

sub_once("\\renewcommand{\\qpjianming}{导学件}",
         "\\renewcommand{\\qpjianming}{导学件}\n"
         "\\renewcommand{\\qpceming}{高中数学\\quad 选择性必修第一册(人教B版)}"
         " % 换装回钉：qp-m3 默认册名＝选必二，原件 qp-headfoot 默认＝选必一，防页脚漂移", "册名回钉")

m = re.search(r"% =+ 局部宏.*?\\newcommand\{\\xjtk\}\[2\]\{[^\n]*\}\n", tex, re.S)
assert m, "局部宏块未定位"
tex = tex[:m.start()] + ("% 局部宏 \\pingtou/\\liubai/\\zhankong/\\xjtk 已由 qp-m3 收编（等值定义），"
                         "件内 \\newcommand 依换装方案§1.4 删除防撞名\n") + tex[m.end():]

# 3.2 课堂评价回流：\vbox 整体装栏 → ketang 顺排（先开箱，评价锚后插）
sub_once("\\vbox{\n\n\\huaxing{课}{堂}{评}{价}{知识评价\\quad 素养形成}\n\n"
         "\\pingtou{本组共5题，1—3为单选，4—5为填空．}",
         "\\begin{ketang}{本组共5题，1—3为单选，4—5为填空．}", "ketang 开")
KETANG_CLOSE = "}\n\n\\end{multicols}\n\\end{document}"

# 3.3 预习填空（1 键整迁，锚＝预习区末条知识点后、知识点三判断组头前）
key = KS + "-预习填空"
sub_once("\\zhenhead{判断正误(正确的打\\gou{},错误的打\\cha{})}\n\n"
         "\\zhentib{(1)}{若\\(\\overrightarrow{a}\\)，\\(\\overrightarrow{b}\\)不共线",
         block(key, "预习填空", plan[key], "ansnote") + "\n\n"
         "\\zhenhead{判断正误(正确的打\\gou{},错误的打\\cha{})}\n\n"
         "\\zhentib{(1)}{若\\(\\overrightarrow{a}\\)，\\(\\overrightarrow{b}\\)不共线", "预习填空锚")
log.append((key, "\\zsd三 知识点条末（知识点三判断组头前）", kmap[key]["group"], plan[key], "\\ansnote"))

# 3.4 判1–5（锚＝各 \zhentib 行后；标签用答案册连号 (1)–(5)）
PANDUAN = [
    ("判1", "(1)", "\\zhentib{(1)}{单位向量都相等．}", "(1)"),
    ("判2", "(2)", "\\zhentib{(2)}{向量\\(\\overrightarrow{a}\\)与\\(-\\overrightarrow{a}\\)互为相反向量，它们的模相等．}", "(2)"),
    ("判3", "(3)", "\\zhentib{(1)}{对任意实数\\(\\lambda\\)和空间向量", "(3)"),
    ("判4", "(4)", "\\zhentib{(2)}{若\\(\\overrightarrow{AB}=\\overrightarrow{CD}\\)", "(4)"),
    ("判5", "(5)", "\\zhentib{(1)}{若\\(\\overrightarrow{a}\\)，\\(\\overrightarrow{b}\\)不共线", "(5)"),
]
for name, lab, anchor, disamb in PANDUAN:
    key = "%s-%s" % (KS, name)
    idx = tex.find(anchor); assert idx >= 0, "判锚未命中 %s" % name
    eol = tex.index("\n", idx) + 1
    tex = tex[:eol] + "\n" + block(key, lab, plan[key], "ansitem") + "\n" + tex[eol:]
    log.append((key, "\\zhentib %s 行后" % disamb, kmap[key]["group"], plan[key], "\\ansitem"))

# 3.5 探1–4 例/变式（锚＝块终结符：例块→次 \liB 前；变式块→次 \xiaojie 前）
cur = 0
for i in range(1, 5):
    for j, stopmark in (("例1", "\\liB{变式"), ("变式1", "\\xiaojie{")):
        key = "%s-探%d-%s" % (KS, i, j)
        idx = tex.find(stopmark, cur); assert idx >= 0, "探锚未命中 %s" % key
        inner = "ansitem" if plan[key][:1].isdigit() else "ansnote"  # 中文号标签防 \ansitem 悬挂叠印（册93 同病灶）
        b = block(key, j, plan[key], inner)
        tex = tex[:idx] + b + "\n\n" + tex[idx:]
        cur = idx + len(b) + 2
        log.append((key, "%s 前（%s 块尾）" % (stopmark, j), kmap[key]["group"], plan[key], "\\" + inner))

# 3.6 评价 1–5（锚＝评价区各题块尾：次 \jiancestem 前；末题→ketang 闭箱前）
for i in range(1, 6):
    key = "%s-评%d" % (KS, i)
    stopmark = "\\jiancestem{" if i < 5 else KETANG_CLOSE
    pos = 0
    for _ in range(i):
        pos = tex.find("\\jiancestem{", pos); assert pos >= 0, "评价锚未命中 %d" % i
        pos += 1
    idx = tex.find(stopmark, pos); assert idx >= 0, "评价块尾未命中 %d" % i
    b = block(key, str(i), plan[key], "ansitem")
    tex = tex[:idx] + b + "\n\n" + tex[idx:]
    log.append((key, "次 \\jiancestem 前" if i < 5 else "ketang 闭箱前", kmap[key]["group"], plan[key], "\\ansitem"))

# 3.7 ketang 闭箱＋尾块（\tailfill 于 \end{document} 前，方案§1.3）
sub_once(KETANG_CLOSE,
         "\\end{ketang}\n\n\\end{multicols}\n\n\\tailfill\n\\end{document}", "ketang 闭＋尾块")

with io.open(os.path.join(HERE, "main.tex"), "w", encoding="utf-8", newline="\n") as f:
    f.write(tex)

# ---------- 4. 迁移日志 ----------
with io.open(os.path.join(HERE, "_试迁迁移日志.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write("# 课时01 试迁迁移日志（机器生成·拆分重组断言全过）\n\n"
            "| 键 | 锚点 | 拆分组 | 值 | 内件宏 |\n|---|---|---|---|---|\n")
    for k, a, g, v, inner in log:
        f.write("| %s | %s | %s | %s | %s |\n" % (k, a, "＋".join(g), v.replace("|", "\\|"), inner))
    f.write("\n拆分不确定点（禁猜登记）：%s\n" % ("无" if not uncertain else uncertain))

assert len(log) == 19, "迁移键数 %d ≠ 19" % len(log)
assert tex.count("\\begin{ansblock}") == 19 and tex.count("\\end{ansblock}") == 19
print("迁移键数:", len(log), "| 拆分不确定点:", len(uncertain))
print("ansblock:", tex.count("\\begin{ansblock}"), "| ketang:", tex.count("\\begin{ketang}"),
      "| tailfill:", tex.count("\\tailfill"), "| \\input残留:", tex.count("\\input{qp-"))
