# -*- coding: utf-8 -*-
"""试迁脚本-P1（副本树-P1 内；写入仅限本目录）
P1 导学本首件 9.1电荷 overlay 换装试迁：
  ① 答案册 body.tex（只读迁移源）→ 导-课时91 键账提取＋成组拆分（草案 §1.1）
  ② 件内锚点插入 ansblock（19 键）＋overlay 挂接＋\\tailfill（草案 §1.2/§1.3）
  ③ 断言：键数＝19、锚唯一、原件行零删改（纯插入 diff）
产物：导学件/9.1电荷/main-换装.tex ＋ 双壳 true/false ＋ 试迁键账-9.1.json
红线：零 git；P1 成卷正件/骨架/答案册只读。
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = os.path.join(HERE, "导学件", "9.1电荷")
SRC_MAIN = os.path.join(PIECE, "main.tex")
BODY = r"C:/提示词/工作区/P1-必修3第9章量产0912/成卷/答案册/body.tex"

# ---------- ① 键账提取（body.tex 课时91 段） ----------
EXPECT_KEYS = (
    ["导-课时91-预习填空"]
    + ["导-课时91-判%d" % i for i in range(1, 7)]
    + ["导-课时91-探%d-%s" % (i, k) for i in (1, 2, 3) for k in ("例1", "变式1")]
    + ["导-课时91-拓展"]
    + ["导-课时91-评%d" % i for i in range(1, 6)]
)

body = open(BODY, encoding="utf-8").read()
seg = body.split("% ---- 课时91", 1)[1].split("\\jietitle{9.2", 1)[0]

keys, pending, detail_last, ansval = {}, [], None, {}
last_group_first = None
for line in seg.splitlines():
    s = line.strip()
    m = re.match(r"^% pair:(.+)$", s)
    if m:
        pending.append(m.group(1).strip())
        continue
    m = re.match(r"^\\ansline\{(.+?)\}\{(.*)\}\s*$", s)
    if m:
        label, val = m.group(1), m.group(2)
        if pending:
            for k in pending:
                ansval[k] = (label, val)
            last_group_first = pending[0]
            pending = []
        elif label == "解析" and last_group_first:
            detail_last = (last_group_first, val)   # 悬空解析→随前组首键
        continue
    m = re.match(r"^\\ansitem\{(.+?)\}\{(.*)\}\s*$", s)
    if m and pending:
        k = pending.pop(0)
        ansval[k] = (m.group(1), m.group(2))
        last_group_first = k

assert not pending, "缺值键（悬空）: %s" % pending
got = list(ansval.keys())
assert got == EXPECT_KEYS, "键账不齐：got=%d want=%d\n%s" % (len(got), len(EXPECT_KEYS), set(EXPECT_KEYS) ^ set(got))

# ---------- 成组拆分（草案 §1.1.2；拆不出→共键停机） ----------
def split_judge(val):
    parts = re.split(r"\((\d)\)", val)   # ['', '1', '×', '2', '√', ...]
    it = iter(parts[1:])
    return {int(n): re.sub(r"\\quad\s*$", "", v).strip() for n, v in zip(it, it)}

def split_libian(val):
    m = re.match(r"^例1\s*(.*?)；变式1\s*(.*)$", val, re.S)
    assert m, "例变拆分失败: %r" % val
    return m.group(1).strip(), m.group(2).strip()

def split_ping(val):
    parts = re.split(r"(\d)．", val)
    it = iter(parts[1:])
    return {int(n): v.strip().rstrip("；。") for n, v in zip(it, it)}

K = {}
K["导-课时91-预习填空"] = ansval["导-课时91-预习填空"][1]
jud = split_judge(ansval["导-课时91-判1"][1])
for i in range(1, 7):
    K["导-课时91-判%d" % i] = jud[i]
for i in (1, 2, 3):
    a, b = split_libian(ansval["导-课时91-探%d-例1" % i][1])
    K["导-课时91-探%d-例1" % i] = a
    K["导-课时91-探%d-变式1" % i] = b
K["导-课时91-拓展"] = ansval["导-课时91-拓展"][1]
ping = split_ping(ansval["导-课时91-评1"][1])
for i in range(1, 6):
    K["导-课时91-评%d" % i] = ping[i]

DETAIL = {}
if detail_last:
    DETAIL[detail_last[0]] = detail_last[1]
# 悬空解析补全：段内解析行按序随探2-例1／探3-例1（与 body.tex 册面解析位一一对应）
xj = [m.group(1) for m in re.finditer(r"\\ansline\{解析\}\{(.*?)\}\s*$", seg, re.M)]
assert len(xj) == 2, "解析行数异常: %d" % len(xj)
DETAIL["导-课时91-探2-例1"] = xj[0]
DETAIL["导-课时91-探3-例1"] = xj[1]

assert len(K) == 19, "拆分后键数≠19: %d" % len(K)

# ---------- ② 件内插入 ----------
def ansblock(key, label, val, detail=None):
    body = "%% ans:%s\n\\ansitem{%s}{%s}" % (key, label, val)
    if detail:
        body += "\\ansnote{详解}{%s}" % detail
    return "\\begin{ansblock}[%s]\n%s\n\\end{ansblock}\n" % (key, body)

# (键, 锚子串, 题号标签)——锚须全件唯一；插入＝锚行之后
INSERTS = [
    ("导-课时91-判1",      r"用丝绸摩擦过的玻璃棒带正电", "(1)"),
    ("导-课时91-判2",      r"得到电子的物体带负电", "(2)"),
    ("导-课时91-判3",      r"自由电子发生了定向移动", "(1)"),
    ("导-课时91-判4",      r"感应电荷一定立即全部消失", "(2)"),
    ("导-课时91-判5",      r"都等于元电荷 $e$ 的整数倍", "(1)"),
    ("导-课时91-判6",      r"某带电体的电荷量可能是", "(2)"),
    ("导-课时91-预习填空", r"\liubai[9mm]{此处书写}", "预习填空"),
    ("导-课时91-探1-例1",  r"甲、丙之间没有力的作用", "例1"),
    ("导-课时91-探1-变式1", r"丙可能不带电", "变式1"),
    ("导-课时91-探2-例1",  r"将导体B接地后移走小球C", "例1"),
    ("导-课时91-探2-变式1", r"若先移走橡胶棒，再分开A、B", "变式1"),
    ("导-课时91-探3-例1",  r"\guifanbiao{6}", "例1"),
    ("导-课时91-拓展",     r"$+q$ 和 $-3q$", "拓展延伸"),
    ("导-课时91-探3-变式1", r"$-1.0\times10^{-9}\,\unit{C}$．使两球接触后再分开", "变式1"),
    ("导-课时91-评1",      r"质子从头发转移到梳子上", "1"),
    ("导-课时91-评2",      r"B球的电荷量因感应而变大了", "2"),
    ("导-课时91-评3",      r"$8.0\times10^{-19}", "3"),
    ("导-课时91-评4",      r"先让甲、乙接触后再分开，再让甲、丙接触后再分开", "4"),
    ("导-课时91-评5",      r"结果保留两位有效数字", "5"),
]

src = open(SRC_MAIN, encoding="utf-8").read()
lines = src.splitlines(keepends=True)

# overlay 挂接（七模块 \input 之后、件型层参数之前）
figs_i = next(i for i, l in enumerate(lines) if "qp-figs.tex" in l)
lines.insert(figs_i + 1, "\n% —— 换装 overlay 挂接（副本树试迁；七模块后、\\begin{document} 前，承 sty 头用法）——\n"
                         "\\usepackage{qp-m3p-overlay}\n")

out = "".join(lines)
for key, anchor, label in INSERTS:
    hits = out.count(anchor)
    assert hits == 1, "锚不唯一(%d): %s // %s" % (hits, key, anchor)
    block = ansblock(key, label, K[key], DETAIL.get(key))
    i = out.index(anchor)
    j = out.index("\n", i) + 1          # 锚行行尾
    out = out[:j] + block + out[j:]

# 尾页填充块（\end{multicols} 前）
assert out.count("\\end{multicols}") == 1
out = out.replace("\\end{multicols}", "\\tailfill\n\n\\end{multicols}")

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
added = len(new_lines) - len(orig)
assert added == 3 + len(INSERTS) * 4 + 2, "插入行数异常: %d" % added

with open(os.path.join(PIECE, "main-换装.tex"), "w", encoding="utf-8", newline="\n") as f:
    f.write("% —— 副本树-P1 试迁件（由 main.tex 机器迁移生成；正件 main.tex 只读对照）——\n" + out)

with open(os.path.join(PIECE, "main-换装-true.tex"), "w", encoding="utf-8", newline="\n") as f:
    f.write("% 试迁双壳·含详解印本档（\\showans true＝默认）→ main-换装-true.pdf\n\\def\\mthreepure{0}\n\\input{main-换装.tex}\n")
with open(os.path.join(PIECE, "main-换装-false.tex"), "w", encoding="utf-8", newline="\n") as f:
    f.write("% 试迁双壳·纯题档（\\mthreepure=1 → \\showansfalse）→ main-换装-false.pdf\n\\def\\mthreepure{1}\n\\input{main-换装.tex}\n")

man = {"件": "导学件/9.1电荷", "键数": len(K), "键值": K, "详解随键": DETAIL,
       "插入锚": {k: a for k, a, _ in INSERTS}}
with open(os.path.join(HERE, "试迁键账-9.1.json"), "w", encoding="utf-8") as f:
    json.dump(man, f, ensure_ascii=False, indent=1)

print("OK 迁移键数=%d（含详解随键 %d 处）＋\\tailfill 1 处＋overlay 挂接 1 处" % (len(K), len(DETAIL)))
for k in EXPECT_KEYS:
    print("  %s = %s" % (k, K[k][:48]))
