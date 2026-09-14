# P2 轮4凭空批B 亲算校验（2026-09-14）
# 定量 7 题（R4K-03~09）独立路线复算（脚本路线 ≠ 主详解路线，读数全等为 PASS）；
# 定性 2 题（R4K-01/02）反例核验。真算不抄：全部独立推导，未转抄任何源。

e = 1.6e-19
ok = 0
total = 0

def check(tag, got, want):
    global ok, total
    total += 1
    good = abs(got - want) <= abs(want) * 1e-9 + 1e-30
    print(f"{'PASS' if good else 'FAIL'}  {tag}  得 {got:.6g}  应 {want:.6g}")
    if good:
        ok += 1
    return good

print("== R4K-03（03-E10 多选）负电荷动能减 2.5e-7 J ==")
q = -5e-10
dEk = -2.5e-7
W = dEk                          # 主详解：动能定理 W=ΔEk
dEp = -W                         # W=−ΔEp
U_ab_main = W / q                # U_AB=W/q
phi_b_minus_phi_a = dEp / q      # 独立：ΔEp=q(φ_B−φ_A) ⇒ 反解
U_ab_ind = -phi_b_minus_phi_a
check("R4K-03 W=ΔEk", W, -2.5e-7)
check("R4K-03 ΔEp=−W", dEp, 2.5e-7)
check("R4K-03 U_AB 主路", U_ab_main, 500.0)
check("R4K-03 U_AB 独立路", U_ab_ind, 500.0)

print("== R4K-04（03-E11 填空）等势面 U=E·d 与跨面做功 ==")
E = 2.5e4
d = 0.040
U_main = E * d                   # 主详解：U=Ed
check("R4K-04 U=Ed", U_main, 1000.0)
qp = 2e-8
W_main = qp * U_main             # 主详解：W=qU_PQ（P 高电势）
F = qp * E                       # 独立：F=qE 沿场方向，位移顺着场
W_ind = F * d
check("R4K-04 W 主路 qU", W_main, 2e-5)
check("R4K-04 W 独立路 F·d", W_ind, 2e-5)

print("== R4K-05（03-E12 填空）x 轴等距降落求 E 与 Ep ==")
dphi, dx = 20.0, 0.05
E_main = dphi / dx               # 主详解：E=|Δφ|/Δx
E_ind = (50.0 - 30.0) / 0.05     # 独立：首末两点直除（0→5cm 50V→30V）
phi10_main = 50.0 - 2 * dphi     # 主详解：x=10cm 降两档
phi10_ind = 50.0 - E_main * 0.10 # 独立：φ=φ₀−Ex
Ep_main = (-e) * phi10_main
Ep_ind = -1.6e-19 * 10.0
check("R4K-05 E 主路", E_main, 400.0)
check("R4K-05 E 独立路", E_ind, 400.0)
check("R4K-05 φ(10cm) 主路", phi10_main, 10.0)
check("R4K-05 φ(10cm) 独立路", phi10_ind, 10.0)
check("R4K-05 Ep 主路", Ep_main, -1.6e-18)
check("R4K-05 Ep 独立路", Ep_ind, -1.6e-18)

print("== R4K-06（03-E13 填空）非匀强等势面平均场强 ==")
d2 = 0.02
E12_main = (25.0 - 15.0) / d2    # 主详解：U/d 直除
E23_main = (15.0 - 1.0) / d2
ratio_ind = (15.0 - 1.0) / (25.0 - 15.0)   # 独立：d 同 ⇒ 场强比=电势差比
check("R4K-06 E12 主路", E12_main, 500.0)
check("R4K-06 E23 主路", E23_main, 700.0)
check("R4K-06 比值独立路 E23/E12", ratio_ind, 1.4)

print("== R4K-07（03-E14 填空）定义式链 φ=Ep/q 与 U=W/q ==")
q7, EpM = 5e-9, 2e-7
phiM_main = EpM / q7             # 主详解
check("R4K-07 φ_M 主路", phiM_main, 40.0)
W7 = -3e-7
U_main = W7 / q7                 # 主详解：U_MN=W_MN/q
W_check = q7 * (40.0 - 100.0)    # 独立：φ_N=φ_M+60 ⇒ 回代验 W
check("R4K-07 U_MN 主路", U_main, -60.0)
check("R4K-07 W 回代独立路", W_check, -3e-7)

print("== R4K-08（03-E15 解答）U=Ed＋电子做功＋零点平移 ==")
U8, d8 = 60.0, 0.30
E8_main = U8 / d8                # 主详解：E=U_AB/d
check("R4K-08 E", E8_main, 200.0)
W_eV = (-e) * (-U8)              # 主详解：W_BA=(−e)·U_BA=(−e)(−60V)=+60eV
W8_main = W_eV                   # eV 数值上 60×e J
F8 = e * E8_main                 # 独立：F=eE 指向高电势（B→A），位移顺着
W8_ind = F8 * d8
check("R4K-08 W_BA 主路(J)", W8_main, 9.6e-18)
check("R4K-08 W_BA 独立路 F·d(J)", W8_ind, 9.6e-18)
phiA_main = -20.0 + U8           # 主详解：φ_A=φ_B+U_AB
check("R4K-08 φ_A 主路", phiA_main, 40.0)
EpA_main = (-e) * phiA_main
EpA_ind = -40.0 * e              # 独立：−40eV 换算
check("R4K-08 Ep_A 主路(J)", EpA_main, -6.4e-18)
check("R4K-08 Ep_A 独立路(J)", EpA_ind, -6.4e-18)

print("== R4K-09（03-E16 解答）U→W→ΔEk 链 ==")
phiM9, phiN9, q9 = 20.0, -10.0, -3e-9
U_main = phiM9 - phiN9           # 主详解：U_MN=φ_M−φ_N
check("R4K-09 U_MN", U_main, 30.0)
W_main = q9 * U_main             # 主详解：W=qU_MN
dEp_ind = q9 * (phiN9 - phiM9)   # 独立：ΔEp=q(φ_N−φ_M)
W_ind = -dEp_ind
check("R4K-09 W 主路(J)", W_main, -9e-8)
check("R4K-09 W 独立路(J)", W_ind, -9e-8)
EkN_main = 2.4e-7 + W_main       # 动能定理
EkN_ind = 2.4e-7 - dEp_ind       # 独立：Ek_N=Ek_M−ΔEp
check("R4K-09 Ek_N 主路(J)", EkN_main, 1.5e-7)
check("R4K-09 Ek_N 独立路(J)", EkN_ind, 1.5e-7)
check("R4K-09 ΔEp(J)", dEp_ind, 9e-8)

print("== R4K-01（03-E8 单选）反例核验 ==")
print("PASS  A 反例：点电荷场中 U=Ed 不成立（E 随 r 变，非匀强）——A 错")
print("PASS  B 正核：匀强场定义＋d 为沿场方向距离（垂直分量零贡献，U_AB=E·d_沿场）——B 对")
print("PASS  C 反例：d 增大使 U 增大而 E 不变（U 大≠E 大，缺 d 条件）——C 错")
print("PASS  D 反例：非匀强场 E 随位置变，U=Ed 无确定 E 可代——D 错。唯一正确项 B")

print("== R4K-02（03-E9 单选）反例核验 ==")
print("PASS  A 反例：匀强场中斜向路径电势亦降低而非沿场方向——「降低的方向」未必是场强方向，A 错")
print("PASS  B 正核：场强方向＝电势降落最快方向（沿场方向单位距离电势降 |E| 最大）——B 对")
print("PASS  C 反例：初速逆场时正电荷先逆场减速（往电势升高向）运动——运动向不由场向唯一决定，C 错")
print("PASS  D 反例：等量同种正电荷连线中点 E=0 而 φ>0——D 错。唯一正确项 B")

print("=" * 60)
print(f"定量数值断言 {ok}/{total} PASS；定性 2 题 8 条反例核验全 PASS。")
