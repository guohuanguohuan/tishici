# -*- coding: utf-8 -*-
"""试迁脚本-P1拓展（副本树-P1拓展 内；写入仅限本目录）
P1 拓展本 overlay 换装试迁＋专项压测（三栏卡块/括线模长答块）：
  ① 答案册 body.tex 丙段（只读迁移源）→ 拓-001~046 键账提取（一对一 ansitem，无成组拆分）
  ② 件内锚点插入 ansblock（46 键）＋overlay 挂接＋\\tailfill（草案 §1.2/§1.3）
  ③ 模式判据（草案 §1.2.5）：45 短块灰底；拓-046 详解长块（~170字）括线模
  ④ 压测变体：A＝三栏全灰底（拓-046 强制灰卡，worst-case）；B＝两栏全括线；C＝三栏全括线
  ⑤ 断言：键数＝46、锚唯一、原件行零删改（纯插入 diff）
红线：零 git；P1 成卷正件/骨架/答案册/sty 原件只读。
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = os.path.join(HERE, "拓展册")
SRC_MAIN = os.path.join(PIECE, "main.tex")
BODY = r"C:/提示词/工作区/P1-必修3第9章量产0912/成卷/答案册/body.tex"

EXPECT_KEYS = ["拓-%03d" % i for i in range(1, 47)]

# ---------- ① 键账提取（body.tex 丙段【拓展册答案】） ----------
body = open(BODY, encoding="utf-8").read()
seg = body.split("\\jietitle{拓展册(答案)}", 1)[1].split("\\jietitle{单元素养测评卷", 1)[0]

K, DETAIL, pending, last_key = {}, {}, [], None
for line in seg.splitlines():
    s = line.strip()
    m = re.match(r"^% pair:(拓-\d+)$", s)
    if m:
        assert not pending, "成组 pair（预期一对一）: %s" % pending
        pending.append(m.group(1))
        continue
    m = re.match(r"^\\ansitem\{(\d+)\}\{(.*)\}\s*$", s)
    if m and pending:
        assert len(pending) == 1, "一对一破坏: %s" % pending
        k = pending.pop(0)
        assert int(k.split("-")[1]) == int(m.group(1)), "键号/题号错位: %s vs %s" % (k, m.group(1))
        K[k] = m.group(2)
        last_key = k
        continue
    m = re.match(r"^\\ansline\{解析\}\{(.*)\}\s*$", s)
    if m:
        assert last_key, "悬空解析无前键"
        DETAIL[last_key] = m.group(1)
        continue

assert not pending, "缺值键: %s" % pending
assert list(K.keys()) == EXPECT_KEYS, "键账不齐: got=%d" % len(K)
assert list(DETAIL.keys()) == ["拓-001", "拓-046"], "详解随键错位: %s" % list(DETAIL.keys())
print("键账提取: %d 键（一对一，共键 0）；详解随键 %d 处: %s" % (len(K), len(DETAIL), list(DETAIL.keys())))

# ---------- ② 件内插入（题块尾＝下一结构边界行前） ----------
src = open(SRC_MAIN, encoding="utf-8").read()
lines = src.splitlines(keepends=True)

# overlay 挂接（七模块 \input 之后）
figs_i = next(i for i, l in enumerate(lines) if "qp-figs.tex" in l)
lines.insert(figs_i + 1, "\n% —— 换装 overlay 挂接（副本树试迁；七模块后、\\begin{document} 前，承 sty 头用法）——\n"
                         "\\usepackage{qp-m3p-overlay}\n")

def block_of(key):
    label = str(int(key.split("-")[1]))
    inner = "%% ans:%s\n\\ansitem{%s}{%s}" % (key, label, K[key])
    if key in DETAIL:
        inner += "\\ansnote{详解}{%s}" % DETAIL[key]
    return "\\begin{ansblock}[%s]\n%s\n\\end{ansblock}\n" % (key, inner)

def line_starts_boundary(st):
    return st.startswith(("\\tihao{", "\\zu{", "\\columnbreak", "\\end{multicols}"))

out_lines = lines
for key in EXPECT_KEYS:                      # 顺序插入，边界随插随移
    tag = "\\tihao{%d}" % int(key.split("-")[1])
    hits = [i for i, l in enumerate(out_lines) if l.strip().startswith(tag)]
    assert len(hits) == 1, "题锚不唯一(%d): %s" % (len(hits), key)
    i = hits[0]
    b = next(j for j in range(i + 1, len(out_lines)) if line_starts_boundary(out_lines[j].strip()))
    blk = block_of(key)
    if key == "拓-046":                      # 判据 §1.2.5：长详解块括线模（组内局部开关）
        blk = "\\begingroup\\ansblockgrayfalse\n" + blk + "\\endgroup\n"
    out_lines = out_lines[:b] + blk.splitlines(keepends=True) + out_lines[b:]

out = "".join(out_lines)

# 尾页填充块（件尾＝最后一个 \end{multicols} 前；本件 4 处 multicols）
assert out.count("\\end{multicols}") == 4, "multicols 计数异常"
j = out.rfind("\\end{multicols}")
out = out[:j] + "\\tailfill\n\n" + out[j:]

# ---------- ③ 断言：原件行零删改（纯插入） ----------
new_lines = out.splitlines()
orig = [l.rstrip("\n") for l in src.splitlines()]
it = iter(new_lines)
for ol in orig:
    for nl in it:
        if nl == ol:
            break
    else:
        sys.exit("原件行被删改: %r" % ol[:60])
n_blocks = 46
added = len(new_lines) - len(orig)
assert added == 3 + n_blocks * 4 + 2 + 2, "插入行数异常: %d" % added   # 挂接3＋块4×46＋拓046壳2＋尾块2

with open(os.path.join(PIECE, "main-换装.tex"), "w", encoding="utf-8", newline="\n") as f:
    f.write("% —— 副本树-P1拓展 试迁件（由 main.tex 机器迁移生成；正件 main.tex 只读对照）——\n" + out)

with open(os.path.join(PIECE, "main-换装-true.tex"), "w", encoding="utf-8", newline="\n") as f:
    f.write("% 试迁双壳·含详解印本档（\\showans true＝默认；45灰底＋拓-046括线）→ main-换装-true.pdf\n\\def\\mthreepure{0}\n\\input{main-换装.tex}\n")
with open(os.path.join(PIECE, "main-换装-false.tex"), "w", encoding="utf-8", newline="\n") as f:
    f.write("% 试迁双壳·纯题档（\\mthreepure=1 → \\showansfalse）→ main-换装-false.pdf\n\\def\\mthreepure{1}\n\\input{main-换装.tex}\n")

# ---------- ④ 压测变体（专项：三栏卡块＋括线模长答块） ----------
def strip_t046_wrapper(t):
    t2 = t.replace("\\begingroup\\ansblockgrayfalse\n\\begin{ansblock}[拓-046]", "\\begin{ansblock}[拓-046]")
    t2 = t2.replace("\\end{ansblock}\n\\endgroup\n\\tailfill", "\\end{ansblock}\n\\tailfill")
    assert t2 != t and "\\ansblockgrayfalse" not in t2, "拓-046 括线壳剥离失败"
    return t2

def to3col(t):
    assert t.count("\\begin{multicols}{2}") == 4
    return t.replace("\\begin{multicols}{2}", "\\begin{multicols}{3}")

def add_global_rule(t):
    return t.replace("\\usepackage{qp-m3p-overlay}",
                     "\\usepackage{qp-m3p-overlay}\n\\ansblockgrayfalse   % 压测：全件括线模（三栏口径拟态）")

VAR = {
    "压测A-三栏灰底": to3col(strip_t046_wrapper(out)),          # worst-case：三栏＋46 灰卡（长详解强制灰卡）
    "压测B-两栏括线": add_global_rule(out),                      # 两栏全括线（46 hairline 对）
    "压测C-三栏括线": to3col(add_global_rule(out)),              # 三栏全括线（测评口径拟态）
}
for name, text in VAR.items():
    with open(os.path.join(PIECE, name + ".tex"), "w", encoding="utf-8", newline="\n") as f:
        f.write("%% —— 压测变体（试迁件派生；只作版面压测，不入重发清单）——\n" + text)
    with open(os.path.join(PIECE, name + "-true.tex"), "w", encoding="utf-8", newline="\n") as f:
        f.write("%% 压测双壳（\\mthreepure=0）→ %s-true.pdf\n\\def\\mthreepure{0}\n\\input{%s.tex}\n" % (name, name))

man = {"件": "拓展册", "键数": len(K), "键值": K, "详解随键": DETAIL,
       "模式": {"拓-046": "括线", "默认": "灰底（45 块）"},
       "压测变体": {k: v.replace("\n", " ")[:40] for k, v in VAR.items()}}
with open(os.path.join(HERE, "试迁键账-拓展.json"), "w", encoding="utf-8") as f:
    json.dump(man, f, ensure_ascii=False, indent=1)

print("OK 迁移键数=%d（详解随键 %d 处）＋\\tailfill 1 处＋overlay 挂接 1 处＋压测变体 3 件" % (len(K), len(DETAIL)))
print("拓-046 块长判据：详解 %d 字（全角计）＞8 行阈值 → 括线模" % len(DETAIL["拓-046"]))
