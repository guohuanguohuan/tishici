# -*- coding: utf-8 -*-
"""试迁对勘-P1练习（9.1电荷 练习件）：原印面页级对勘＋键值零漂移＋印面读数＋像素比对＋目验出图。"""
import hashlib, json, os, re
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = os.path.join(HERE, "练习件9.1-换装")
BASE = os.path.join(HERE, "00原样基线")
ORIG = r"C:/提示词/工作区/P1-必修3第9章量产0912/成卷/练习件/9.1电荷/main.pdf"
PNGD = os.path.join(HERE, "png对照")

def pages_of(pdf):
    doc = pymupdf.open(pdf)
    return [p.get_text() for p in doc]

def norm(s):
    return re.sub(r"\s+", "", s)

po = pages_of(ORIG)
pb = pages_of(os.path.join(BASE, "main.pdf"))
pt = pages_of(os.path.join(PIECE, "main-换装-true.pdf"))
pf = pages_of(os.path.join(PIECE, "main-换装-false.pdf"))
py = pages_of(os.path.join(PIECE, "main-压测.pdf"))
print("页数: 正件=%d 基线=%d true=%d false=%d 压测=%d  (false≤true: %s)"
      % (len(po), len(pb), len(pt), len(pf), len(py), len(pf) <= len(pt)))

# ① 工具链基线：原样复编译 vs 成卷正件——逐页文本全等（对照面成立）
ok = len(po) == len(pb) and all(norm(a) == norm(b) for a, b in zip(po, pb))
print("① 工具链基线（原样复编译≡正件印面，逐页 %d/%d）: %s" % (len(po), len(po), "PASS" if ok else "FAIL"))
assert ok

# ② 题面锚序（题干/选项 distinctive 片段，件面序；四档全过＝题序/题面零漂移）
anchors = [
    "用金属箔做成一个不带电的圆环", "笔套的起电方式属于接触起电", "笔套接触圆环后，笔套所带的电荷全部被中和",
    "塑料带化身为“章鱼”在空中漂浮", "毛巾与塑料带带同种电荷", "受到了PVC管对它的吸引力",
    "关于电荷，下列说法正确的是", "最早是科学家卡文迪什测得", "物体所带的电荷量可以是任意的",
    "推断该数值不可能是下列哪一个", "关于电荷守恒定律，下列叙述不正确的是", "电荷守恒定律并不意味着带电系统",
    "贴在A、B下部的金属箔片都张开", "移去C，贴在A、B下部的金属箔片都将处于",
    "带正电的绝缘棒甲左端靠近", "金属球和金箔片均不带电", "用丝绸摩擦玻璃棒，玻璃棒带正电",
    "摩擦时玻璃棒上的一些电子转移到丝绸上", "把摩擦过的玻璃棒靠近悬挂的轻质铝箔小球",
    "元电荷", "电子的比荷（电子的电荷量与电子质量之比）", "两个完全相同的金属小球A和B",
    "A、B都带", "电荷全部抵消消失了", "三个相同的金属球A、B、C", "最后A所带的电荷量是多少",
    "有A、B、C三个完全相同的金属球", "现用相互接触的方法使它们都带电",
    "绝缘泡沫板上安装有一绝缘支架", "用不带绝缘手套的手触摸硬币", "把一个带电体P靠近甲球一侧",
    "求甲、乙分开瞬间各自所带的电荷量", "带电体P带什么电", "用丝绸摩擦过的玻璃棒靠近甲球一侧",
    "指出甲、乙分开瞬间各自的电性", "是否仍能唯一确定", "用毛皮摩擦过的橡胶棒靠近A球一侧",
    "求B球在两球分开瞬间所带的电荷量", "能否通过上述接触操作使A、B、C三球最后都带上同种电荷",
]
def order_idx(txt):
    idx, pos = [], 0
    for a in anchors:
        i = txt.find(norm(a), pos)
        assert i >= 0, "缺锚: %s" % a
        idx.append(i); pos = i
    return idx
o, u, f, y = norm("\n".join(po)), norm("\n".join(pt)), norm("\n".join(pf)), norm("\n".join(py))
io, iu, if_, iy = order_idx(o), order_idx(u), order_idx(f), order_idx(y)
def mono(v):
    return all(a <= b for a, b in zip(v, v[1:]))
print("② 题面锚 %d 条×四档（正件/true/false/压测）全中，沿件面序单调一致: %s"
      % (len(anchors), "PASS" if all(mono(v) for v in (io, iu, if_, iy)) else "FAIL"))
assert all(mono(v) for v in (io, iu, if_, iy))

# ③ tex 层键值零漂移（emitted \ansitem 体 vs 答案册逐字节；钉值门）
body = open(r"C:/提示词/工作区/P1-必修3第9章量产0912/成卷/答案册/body.tex", encoding="utf-8").read()
seg = body.split("\\jietitle{9.1\\quad 电荷(练习件答案)}", 1)[1].split("\\jietitle{9.2", 1)[0]
ref = {}
pending = []
for line in seg.splitlines():
    s = line.strip()
    m = re.match(r"^% pair:(.+)$", s)
    if m: pending.append(m.group(1).strip()); continue
    m = re.match(r"^\\ansitem\{(.+?)\}\{(.*)\}\s*$", s)
    if m and pending: ref[pending.pop(0)] = m.group(2)
em = open(os.path.join(PIECE, "main-换装.tex"), encoding="utf-8").read()
def read_group(s, i):
    # s[i] == '{'；按花括号计数取组体，返回（体, 结束位}
    assert s[i] == "{"
    d, j = 0, i
    while True:
        c = s[j]
        if c == "{": d += 1
        elif c == "}":
            d -= 1
            if d == 0: return s[i + 1:j], j + 1
        elif c == "\\": j += 1   # 跳过转义符防 \{ \} 干扰计数
        j += 1
got = {}
pos = 0
while True:
    i = em.find("% ans:练-课时91-", pos)
    if i < 0: break
    key = em[em.index(":", i) + 1:].split("\n", 1)[0].strip()
    j = em.index("\\ansitem{", i)
    label, j2 = read_group(em, j + len("\\ansitem"))
    while em[j2] != "{": j2 += 1
    val, j2 = read_group(em, j2)
    got[key] = val
    pos = j2
ok = set(got) == set(ref) and all(got[k] == ref[k] for k in ref)
print("③ 键值零漂移（tex 层 16 键逐字节 vs body.tex）: %s" % ("PASS" if ok else "FAIL"))
assert ok, [(k, got.get(k), ref.get(k)) for k in ref if got.get(k) != ref[k]]

# ④ 印面读数（[答案]/[详解]/尾块/难度标/花形）
def cnt(t, s): return t.count(norm(s))
rows = [
    ("[答案]",        16, 0, 16, "题后答案条"),
    ("[详解]",         6, 0, 6, "命制详解回嵌"),
    ("笔记与错题整理",  1, 1, 1, "尾页填充块（true/false/压测各1；正件0）"),
    ("基础巩固",        1, 1, 1, "花形三档名守恒"),
    ("综合提升",        1, 1, 1, ""), ("思维探索", 1, 1, 1, ""),
    ("时间：40分钟",    1, 1, 1, "限时总量行守恒"),
]
ok = True
for s, et, ef, ey, desc in rows:
    a, b, c, d = cnt(o, s), cnt(u, s), cnt(f, s), cnt(y, s)
    good = (b == et and c == ef and d == ey)
    ok = ok and good
    print("  %-10s 正件=%d true=%d(期%d) false=%d(期%d) 压测=%d(期%d) %s %s"
          % (s, a, b, et, c, ef, d, ey, "OK" if good else "漂!", desc))
assert ok

# ⑤ false 档页级：p1/p2 与正件同页文本全等（答案吞体零残留）；p3 差＝尾块
for i in (0, 1):
    same = norm(po[i]) == norm(pf[i])
    print("  false p%d vs 正件 p%d 文本全等: %s" % (i + 1, i + 1, "PASS" if same else "FAIL"))
    assert same
p3o, p3f = norm(po[2]), norm(pf[2])
print("  false p3: 尾块文本增印=%s，其余差=%s" % (cnt(p3f, "笔记与错题整理") == 1, p3o in p3f))

# ⑥ 对号：log M3-ANSKEY 键清单两档＋压测恒等，且＝键账
def keys_of(log):
    return sorted(re.findall(r"M3-ANSKEY: (.+)", open(os.path.join(PIECE, log), encoding="utf-8", errors="ignore").read()))
kt, kf, ky2 = keys_of("main-换装-true.log"), keys_of("main-换装-false.log"), keys_of("main-压测.log")
man = json.load(open(os.path.join(HERE, "试迁键账-9.1练习.json"), encoding="utf-8"))
ok = kt == kf == ky2 and set(kt) == set(man["键值"]) and len(kt) == 16
print("⑥ 对号: true=%d false=%d 压测=%d 清单diff=%s 与键账一致: %s"
      % (len(kt), len(kf), len(ky2), "零" if kt == kf == ky2 else "有", "PASS" if ok else "FAIL"))
assert ok

# ⑦ 像素级：false p1/p2 vs 正件 p1/p2 MD5（吞体零版面漂移的最强证）
os.makedirs(PNGD, exist_ok=True)
def render(pdf, tag):
    doc = pymupdf.open(pdf)
    for i, p in enumerate(doc, 1):
        out = os.path.join(PNGD, "%s-p%d.png" % (tag, i))
        p.get_pixmap(dpi=150).save(out)
    return len(doc)
n = {}
n["orig"] = render(ORIG, "orig"); n["true"] = render(os.path.join(PIECE, "main-换装-true.pdf"), "true")
n["false"] = render(os.path.join(PIECE, "main-换装-false.pdf"), "false")
n["压测"] = render(os.path.join(PIECE, "main-压测.pdf"), "yace")
def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()
pix = []
for i in (1, 2, 3):
    a = md5(os.path.join(PNGD, "orig-p%d.png" % i)); b = md5(os.path.join(PNGD, "false-p%d.png" % i))
    pix.append("p%d:%s" % (i, "≡(MD5同)" if a == b else "≠"))
print("⑦ 像素: false vs 正件 " + "  ".join(pix) + "  （p3≠＝尾块增印预期）")
print("出图: png对照/ orig×%d true×%d false×%d 压测×%d（150dpi）" % (n["orig"], n["true"], n["false"], n["压测"]))
print("对勘全部断言 PASS")
