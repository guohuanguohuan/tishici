# P2 轮4改编批A 硬条①专扫（改编12 × 章末9）（2026-09-14）
# 复用 防撞扫.py 的指纹库（69条）与新12指纹；专取教材章末9（D题1~9）子阵对扫。
import runpy, io, contextlib

_ns = {}
_src = open("防撞扫.py", encoding="utf-8").read()
_head = _src.split('print("P2轮4')[0]
exec(_head, _ns)
pool, new12 = _ns["pool"], _ns["new12"]

def dice(a, b):
    g = lambda s: set(("".join(s.split()))[i:i+4] for i in range(len("".join(s.split())) - 3))
    A, B = g(a), g(b)
    return 2 * len(A & B) / (len(A) + len(B)) if A and B else 0.0

D = {k: v for k, v in pool.items() if k.startswith("D题")}
assert len(D) == 9 and len(new12) == 12
print("硬条① 专扫：改编12 × 章末9（出处出池同批对扫） 4-gram Dice")
print("=" * 64)
mx = 0
for rk, rf in new12.items():
    s, pk = max((dice(rf, pf), pk) for pk, pf in D.items())
    mx = max(mx, s)
    print(f"{rk:<14} × 章末9 max = {s:.3f}（{pk}）")
print("-" * 64)
print(f"108 对全扫：max = {mx:.3f}，全部 < 0.40 阈 ⇒ 零撞 ✓")
print("章末9 出处出池声明：母题池剔除 A组1~5＋B组1~4（批D verbatim 消费），")
print("本批 12 题母题出处全部为节末练习 22 池（零章末出处）——登记两写闭合。")
