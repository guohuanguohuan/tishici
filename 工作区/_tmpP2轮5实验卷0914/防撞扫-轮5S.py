# P2 轮5实验卷扩写 防撞机械对扫（2026-09-14）
# 扫描面：本批 R5S-01~03 ×（pool69＋R4A12＋R4B13＋R4M10＋R4K9＋R4L9）＝122 指纹库＝366 对；另批内互撞 3 对
# 指纹来源（按轮5派单令）：
#   pool69/newA12/newM10/两 new9 dict＝命制脚本 ast 逐字拷（不执行其代码；微专题〔防撞记〕行仅记键名照抄、无指纹串，
#     其脚本 new10 dict 为唯一逐字源——凭空批A/复核臂同口径先例）；
#   R4B13/R4K9/R4L9＝各命制件〔防撞记｜指纹＝「…」〕行正则提取全量面（轮5派单令指定源）。
# 交叉断言：①两凭空脚本共享 dict 逐字相等；②行提取 vs 脚本 dict 逐字相等（零转录）；③库内无 R5S 前缀（键名零撞）。
# 方法：字符4-gram Dice（批A/批B/微专题/复核同口径）；阈值 ≥0.40 全量召回人工判，top-3 逐题列读数。
import ast, re, os

BASE = r"C:/提示词/工作区"

def extract_dicts(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
            try:
                d = ast.literal_eval(node.value)
            except Exception:
                continue
            if d and all(isinstance(k, str) and isinstance(v, str) for k, v in d.items()):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        out[t.id] = d
    return out

A = extract_dicts(os.path.join(BASE, "_tmpP2轮4凭空0914", "防撞扫-批A.py"))
B = extract_dicts(os.path.join(BASE, "_tmpP2轮4凭空0914", "防撞扫批B.py"))

def norm(d):  # 两脚本键名格式异（一键带槽位后缀、一不带），去括号后按指纹串逐字比对
    return {re.sub(r"\(.*\)", "", k): v for k, v in d.items()}

for k in ("pool", "newA12", "newB13", "newM10"):
    assert norm(A.get(k, {})) == norm(B.get(k, {})), f"{k} 两凭空脚本不一致"
# new9 两脚本系两套（A＝凭空批A 01/04域即 R4K；B＝凭空批B 03域，勘定键名 R4L）——非共享，不比对

pool   = A["pool"];   assert len(pool) == 69,   f"pool 应69实{len(pool)}"
newA12 = A["newA12"]; assert len(newA12) == 12
newM10 = A["newM10"]; assert len(newM10) == 10
newB13_script = A["newB13"]; assert len(newB13_script) == 13
newK_script   = A["new9"];   assert len(newK_script) == 9
newL_script   = B["new9"];   assert len(newL_script) == 9

def fp_from_file(path):
    txt = open(path, encoding="utf-8").read()
    return re.findall(r"〔防撞记｜指纹＝「([^」]+)」", txt)

mz = os.path.join(BASE, "P2-第10章量产0914", "命制")
r4b_inline = fp_from_file(os.path.join(mz, "轮4改编批B-0914.md"))
r4k_inline = fp_from_file(os.path.join(mz, "轮4凭空批A-0914.md"))
r4l_inline = fp_from_file(os.path.join(mz, "轮4凭空批B-0914.md"))
assert len(r4b_inline) == 13, f"批B行提取{len(r4b_inline)}≠13"
assert len(r4k_inline) == 9,  f"凭空批A行提取{len(r4k_inline)}≠9"
assert len(r4l_inline) == 9,  f"凭空批B行提取{len(r4l_inline)}≠9"

# 行提取 vs 脚本 dict 逐字断言（按序映射；L 系勘定键名 R4L ≡ 脚本03域 new9）
mismatch = []
for i, s in enumerate(r4b_inline, 1):
    if s != list(newB13_script.values())[i - 1]: mismatch.append(f"R4B-{i:02d}")
for i, s in enumerate(r4k_inline, 1):
    if s != list(newK_script.values())[i - 1]: mismatch.append(f"R4K-{i:02d}")
for i, s in enumerate(r4l_inline, 1):
    if s != list(newL_script.values())[i - 1]: mismatch.append(f"R4L-{i:02d}")
print(f"行提取×脚本dict 逐字断言：{'全合（零转录）' if not mismatch else '不符→' + str(mismatch)}")

library = {}
library.update(pool)
library.update(newA12)
library.update({f"R4B-{i:02d}": s for i, s in enumerate(r4b_inline, 1)})
library.update(newM10)
library.update({f"R4K-{i:02d}": s for i, s in enumerate(r4k_inline, 1)})
library.update({f"R4L-{i:02d}": s for i, s in enumerate(r4l_inline, 1)})
assert len(library) == 122, f"库应122实{len(library)}"
assert not any(k.startswith("R5S") for k in library), "键名 R5S 与库相撞"

new3 = {
"R5S-01": "单刀双掷充放电实验扩写：充电电压表稳定6.0V、通过电流表电荷量1.2×10⁻⁴C=极板电荷量守恒求C=2.0×10⁻⁵F、断开电源电荷保存、放电电流反向渐减归零、场能经电流做功转内能——实验解答三问",
"R5S-02": "静电计测已充电平行板电容器U：断电Q不变、S减半偏角增、d倍增偏角增、插介质偏角减、U₁=12V变U₂=4.0V求C₁:C₂=1:3、归纳增S减d插介质增大C、控制变量法——实验解答三问",
"R5S-03": "传感器I-t数格测C：I₀=8.0mA约0.8s衰减尽、每格0.5mA×0.1s、约32格Q=1.6×10⁻³C、狭长矩形面积=ΔQ、充电8.0V测C=2.0×10⁻⁴F、释放电荷量=原带电荷量——实验解答三问",
}

def ngrams(s, n=4):
    s = "".join(ch for ch in s if not ch.isspace())
    return set(s[i:i + n] for i in range(len(s) - n + 1))

def dice(a, b):
    Ga, Gb = ngrams(a), ngrams(b)
    return 2 * len(Ga & Gb) / (len(Ga) + len(Gb)) if Ga and Gb else 0.0

print("P2轮5实验卷扩写 R5S-01~03 × 122指纹库 机械对扫（4-gram Dice）")
print("=" * 72)
hits40, tops = [], {}
for rk, rf in new3.items():
    scored = sorted(((dice(rf, pf), pk) for pk, pf in library.items()), reverse=True)
    tops[rk] = scored[:3]
    for s, pk in scored:
        if s >= 0.40:
            hits40.append((rk, pk, s))
for rk in new3:
    print(f"{rk:<8} top3：  " + "  ".join(f"{pk}={s:.2f}" for s, pk in tops[rk]))
print("-" * 72)
print(f"≥0.40 召回 {len(hits40)} 对：")
for rk, pk, s in hits40:
    print(f"  {rk}  ×  {pk}  = {s:.3f}")
    print(f"      新：{new3[rk]}")
    print(f"      旧：{library[pk]}")
# 全表 max 与批内 3 对
flat = [(dice(rf, pf), rk, pk) for rk, rf in new3.items() for pk, pf in library.items()]
flat.sort(reverse=True)
print(f"库面全表 max＝{flat[0][0]:.3f}（{flat[0][1]}×{flat[0][2]}）")
print("批内 3 对：")
for (k1, k2) in [("R5S-01", "R5S-02"), ("R5S-01", "R5S-03"), ("R5S-02", "R5S-03")]:
    print(f"  {k1}×{k2}＝{dice(new3[k1], new3[k2]):.3f}")
inb = [dice(new3[a], new3[b]) for a, b in [("R5S-01","R5S-02"),("R5S-01","R5S-03"),("R5S-02","R5S-03")]]
print(f"批内 max＝{max(inb):.3f}")
print("=" * 72)
print(f"扫描面：新3 × 旧122＝366 对＋批内 3 对；库构成：pool69＋R4A12＋R4B13＋R4M10＋R4K9＋R4L9；键名断言：库内零 R5S 前缀 ✓")
