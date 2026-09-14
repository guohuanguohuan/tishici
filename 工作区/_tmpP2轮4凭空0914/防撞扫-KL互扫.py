# P2 轮4凭空批A(R4K-01~09) × 凭空批B(R4L-01~09) K×L 互扫补扫（2026-09-14，军师六案①放行条件补充）
# 全链缺口：K、L 各自×104 库（936 对各在 防撞扫-批A/批B 输出档）＋批内 36 对×2 均已扫，
#           唯 K×L 直扫 81 对从未跑过——本件补齐。
# 方法：字符4-gram Dice 相似度，ngrams/dice 逐字复用 `_tmpP2轮4批A0914/防撞扫.py`（轮1同族机械初筛口径）；
#       阈值 ≥0.40 全量召回人工判级，全表 81 对读数＋逐题 top-5 读数列。机械扫仅作初筛，判级以人工逐对为档。
# 指纹源（只读）：两命制件各题〔防撞记〕指纹＝「…」行——批A＝`P2-第10章量产0914/命制/轮4凭空批A-0914.md`（件内键 R4K），
#                批B＝`P2-第10章量产0914/命制/轮4凭空批B-0914.md`（件内键 R4L）；以件内现版指纹行为准（勘定见 键名勘定-R4K≡R4L.md）。
# 红线：零 git；命制件只读；写入域仅 `_tmpP2轮4凭空0914/`。
import re
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_A = os.path.normpath(os.path.join(HERE, "..", "P2-第10章量产0914", "命制", "轮4凭空批A-0914.md"))
SRC_B = os.path.normpath(os.path.join(HERE, "..", "P2-第10章量产0914", "命制", "轮4凭空批B-0914.md"))
OUT = os.path.join(HERE, "防撞扫-KL互扫-输出.txt")

# ---- Dice 实现：逐字复用 _tmpP2轮4批A0914/防撞扫.py ----
def ngrams(s, n=4):
    s = "".join(ch for ch in s if not ch.isspace())
    return set(s[i:i+n] for i in range(len(s)-n+1))

def dice(a, b):
    A, B = ngrams(a), ngrams(b)
    if not A or not B:
        return 0.0
    return 2 * len(A & B) / (len(A) + len(B))

# ---- 指纹提取：题头键＋槽位，〔防撞记｜指纹＝「…」首现行 ----
HEAD = re.compile(r"^\*\*(R4[KL]-\d\d)〔槽位：(\d{2}-E\d{1,2})")
FP = re.compile(r"〔防撞记｜指纹＝「(.*?)」")

def load(path, tag):
    fps, cur = {}, None
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = HEAD.match(line)
            if m:
                cur = m.group(1)
                assert cur not in fps, f"{tag} 键重复：{cur}"
                fps[cur] = {"slot": m.group(2), "fp": None}
                continue
            m = FP.search(line)
            if m and cur and fps[cur]["fp"] is None:
                fps[cur]["fp"] = m.group(1)
    assert len(fps) == 9, f"{tag} 应9题，实{len(fps)}"
    for k, v in fps.items():
        assert v["fp"], f"{tag} {k} 缺指纹"
    return fps

K = load(SRC_A, "批A(R4K)")
L = load(SRC_B, "批B(R4L)")
ks = sorted(K)
ls = sorted(L)
assert ks == [f"R4K-{i:02d}" for i in range(1, 10)], ks
assert ls == [f"R4L-{i:02d}" for i in range(1, 10)], ls

# ---- 81 对全扫 ----
score = {}
for a in ks:
    for b in ls:
        score[(a, b)] = dice(K[a]["fp"], L[b]["fp"])
assert len(score) == 81, f"应81对，实{len(score)}"

def key_of(d):
    return f"{d}({d['slot']})"

recalls = sorted(((s, a, b) for (a, b), s in score.items()), reverse=True)
recalls40 = [(s, a, b) for s, a, b in recalls if s >= 0.40]
maxs, maxa, maxb = recalls[0]

lines = []
lines.append("P2轮4凭空批A(R4K-01~09) × 凭空批B(R4L-01~09) K×L 互扫补扫 机械对扫（4-gram Dice）")
lines.append("=" * 88)
lines.append("全链缺口补扫：K、L 各自×104 库（936 对各）＋批内 36 对×2 均已在档（防撞扫-批A/批B 输出档），")
lines.append("唯 K×L 直扫 81 对从未跑过——本件补齐。方法：字符4-gram Dice（逐字复用 _tmpP2轮4批A0914/防撞扫.py）；")
lines.append("阈值 ≥0.40 全量召回人工判级，判级以人工逐对为档。")
lines.append("指纹源（只读）：两命制件各题〔防撞记〕指纹＝「…」行，以件内现版为准（键名勘定见 键名勘定-R4K≡R4L.md）。")
lines.append("=" * 88)
lines.append("九九全表（81 对读数；行=R4K 凭空批A，列=R4L 凭空批B）：")
lines.append("行槽位速查：" + "  ".join(f"{a}={K[a]['slot']}" for a in ks))
lines.append("列槽位速查：" + "  ".join(f"{b}={L[b]['slot']}" for b in ls))
head = " " * 16 + "".join(b.ljust(8) for b in ls)
lines.append(head.rstrip())
for a in ks:
    row = f"{a}({K[a]['slot']})".ljust(16)
    row += "".join(f"{score[(a, b)]:.2f}".ljust(8) for b in ls)
    lines.append(row)
lines.append("-" * 88)
lines.append("逐题 top-5 读数列：")
for a in ks:
    tops = sorted(((score[(a, b)], b) for b in ls), reverse=True)[:5]
    line = "  ".join(f"{b}={s:.2f}" for s, b in tops)
    lines.append(f"{a}({K[a]['slot']})  top5：{line}")
for b in ls:
    tops = sorted(((score[(a, b)], a) for a in ks), reverse=True)[:5]
    line = "  ".join(f"{a}={s:.2f}" for s, a in tops)
    lines.append(f"{b}({L[b]['slot']})  top5：{line}")
lines.append("-" * 88)
lines.append(f"≥0.40 召回 {len(recalls40)} 对（逐对人工判级——判级论证收拢于 KL补扫硬化报告.md §一）：")
if recalls40:
    for s, a, b in recalls40:
        lines.append(f"  {a}({K[a]['slot']})  ×  {b}({L[b]['slot']})  = {s:.3f}")
        lines.append(f"      K指纹：{K[a]['fp']}")
        lines.append(f"      L指纹：{L[b]['fp']}")
else:
    lines.append(f"  零召回——81 对全表最高 {maxs:.3f}（{maxa}({K[maxa]['slot']}) × {maxb}({L[maxb]['slot']})），低于阈值 0.40。")
lines.append("=" * 88)
avg = sum(score.values()) / 81
lines.append(f"统计：9×9＝81 对全扫；≥0.40 召回 {len(recalls40)} 对；全表 max {maxs:.3f}（{maxa}×{maxb}）；全表均值 {avg:.3f}。")
lines.append("机械扫仅作初筛；零撞断言以人工逐对判级为档（两命制件§防撞扫出口闸同口径）。")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
print(f"K×L 互扫补扫完成：81 对；≥0.40 召回 {len(recalls40)} 对；max {maxs:.3f}（{maxa}×{maxb}）")
print(f"输出：{OUT}")

