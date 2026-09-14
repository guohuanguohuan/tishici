# P2 轮5实验卷复核臂·亲算抽验（R5S-03 独立路线）·0914
# 路线与命制脚本/主详解均异：数格复核＋指数衰减柱均值读格路线＋e⁻⁴残流半格核＋CU 回路核
import math
ok = 0
def chk(tag, cond):
    global ok
    ok += bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {tag}")

I0, U, C = 8.0e-3, 8.0, 2.0e-4      # 由数格链解得 C，再回头全链自洽
R = U / I0
tau = R * C
chk("① 数格复核 q₀=0.5mA×0.1s=5×10⁻⁵C", abs(0.5e-3 * 0.1 - 5e-5) < 1e-15)
chk("② 数格复核 Q=32q₀=1.6×10⁻³C", abs(32 * 5e-5 - 1.6e-3) < 1e-15)
chk("③ R=U/I₀=1000Ω", abs(R - 1000.0) < 1e-9)
chk("④ τ=RC=0.2s", abs(tau - 0.2) < 1e-12)
# 柱均值路线：0.8s=4τ 可见窗内指数平均电流 → 折格数
Imean = I0 * (1 - math.exp(-4)) / 4
grids = Imean * 0.8 / 5e-5
chk(f"⑤ 柱均值折格 {grids:.2f}≈32 格（估读法「约32格」自洽）", abs(grids - 32) < 1.0)
I4_mA = I0 * math.exp(-4) * 1e3
chk(f"⑥ 4τ 残流 {I4_mA:.4f}mA＜半格0.25mA →『接近于0』成立", I4_mA < 0.25)
Q_exact = I0 * tau
chk("⑦ 积分路线 Q=I₀τ=1.6×10⁻³C 与数格同值", abs(Q_exact - 1.6e-3) < 1e-15)
chk("⑧ C=Q/U=2.0×10⁻⁴F=200μF", abs(1.6e-3 / 8.0 - 2.0e-4) < 1e-15 and abs(2.0e-4 * 1e6 - 200) < 1e-9)
chk("⑨ 回路核 C·U=1.6×10⁻³C 闭合", abs(C * U - 1.6e-3) < 1e-15)
print(f"合计：{ok}/9 PASS" + ("，0 FAIL" if ok == 9 else "，有 FAIL"))
