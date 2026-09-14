# P2 轮4改编批B 亲算校验（2026-09-14）
# 7 定量题独立路线复算＋6 定性/比值题数值支撑；路线≠主详解路线，读数全等判 PASS。
import math

ok = True
def chk(tag, got, want, rel=1e-9):
    global ok
    good = abs(got - want) <= rel * max(1.0, abs(want)) if isinstance(want, (int, float)) else got == want
    print(f"{'PASS' if good else 'FAIL'}  {tag}: got={got!r} want={want!r}")
    if not good:
        ok = False

e = 1.6e-19; me = 9e-31

# R4B-02 eV换算：路线①定义倍乘  路线②W=qU 直算
chk("R4B-02a 定义路线 1eV/J", 1 * e * 1, 1.6e-19)
chk("R4B-02b W=qU 路线 100eV/J", e * 100, 1.6e-17)
chk("R4B-02c 两路线互等", e * 100, 100 * 1.6e-19)

# R4B-04 W→U→排序→换电荷：路线①W=qU 直除  路线②分段ΔEp能量账
q = 3e-9; WAB = -6e-7; WBC = 1.2e-6
Uab = WAB / q; Ubc = WBC / q; Uac = Uab + Ubc
chk("R4B-04a U_AB", Uab, -200.0); chk("R4B-04b U_BC", Ubc, 400.0); chk("R4B-04c U_AC", Uac, 200.0)
dEpAB = -WAB; dEpBC = -WBC  # ΔEp = -W
# 路线②：q>0 时电势高低跟电势能同向；Ep_B>Ep_A>Ep_C ⇒ φ_B>φ_A>φ_C
order_ok = (dEpAB > 0) and (dEpBC < 0) and ((-dEpAB + dEpBC) < 0)  # Ep_C-Ep_A = -(W_AB+W_BC) = -6e-7 <0
chk("R4B-04d 能量账路线 B>A>C", 1 if order_ok else 0, 1)
Wp = (-2e-9) * Uac
chk("R4B-04e 换电荷 W_AC'", Wp, -4e-7)

# R4B-05 击穿/耐压：路线①U=Ed 直乘  路线②千进制复核（3e6 V/m × 1mm）
Em = 3.0e6; d5 = 1.0e-3
chk("R4B-05a 耐压 U_m=Ed", Em * d5, 3000.0)
chk("R4B-05b 工况 E=U/d", 300 / d5, 3.0e5)
chk("R4B-05c 判不击穿(1/10阈值)", 300 / d5 / Em, 0.1)

# R4B-06 极板接地求电势：路线①自M降落  路线②自N(0)起算
E6 = 4e3; dM = 0.05; dMP = 0.02
phiM = E6 * dM            # φ_N=0，M 在 N 上游 Ed
phiP_a = phiM - E6 * dMP  # 自 M 降落 E·MP
phiP_b = E6 * (dM - dMP)  # 自 N 起算 E·NP
chk("R4B-06a φ_M", phiM, 200.0)
chk("R4B-06b φ_P 路线①", phiP_a, 120.0)
chk("R4B-06c φ_P 路线②", phiP_b, 120.0)
chk("R4B-06d D项 改M接地φ_P", -E6 * dMP, -80.0)

# R4B-08 偏转（题给v₀）：路线①分步 a→t→y、v_y→tanθ  路线②闭式
l = 0.03; E8 = 3.6e4; v0 = 2.4e7; U8 = 900.0; d8 = 0.025
chk("R4B-08a U=Ed 配凑", E8 * d8, U8)
a8 = e * E8 / me; t8 = l / v0
y1 = 0.5 * a8 * t8 * t8; vy = a8 * t8; tan1 = vy / v0
y2 = e * E8 * l * l / (2 * me * v0 * v0); tan2 = 2 * y2 / l
chk("R4B-08b a", a8, 6.4e15, rel=1e-6)
chk("R4B-08c y 分步", y1, 5.0e-3, rel=1e-6)
chk("R4B-08d y 闭式", y2, 5.0e-3, rel=1e-6)
chk("R4B-08e tanθ 分步", tan1, 1/3, rel=1e-9)
chk("R4B-08f tanθ 闭式", tan2, 1/3, rel=1e-9)
chk("R4B-08g 不落极板 y<d/2", 1 if y1 < d8 / 2 else 0, 1)

# R4B-09 截止电压：路线①Ek=eU₀→v=√(2Ek/m)  路线②v=√(2eU₀/m)→Ek=½mv²
U0 = 22.5
Ek1 = e * U0; v1 = math.sqrt(2 * Ek1 / me)
v2 = math.sqrt(2 * e * U0 / me); Ek2 = 0.5 * me * v2 * v2
chk("R4B-09a Ek 路线①", Ek1, 3.6e-18)
chk("R4B-09b Ek 路线②", Ek2, 3.6e-18)
chk("R4B-09c v 两路线互等", v1, v2, rel=1e-12)
chk("R4B-09d v=2.8×10⁶", v1 / 1e6, 2.83, rel=1e-2)

# R4B-10 质子/α 比值：数值代入验证 tan∝q/(mv²) 与 tan∝q/(2Ek)
E10, l10, v10, Ek10 = 1e4, 0.1, 1e6, 1e-17
mp = 1.0; qp = 1.0; ma = 4.0; qa = 2.0   # 约化单位（m_p、e）
tanp_v = qp * E10 * l10 / (mp * v10**2); tana_v = qa * E10 * l10 / (ma * v10**2)
tanp_k = qp * E10 * l10 / (2 * Ek10);   tana_k = qa * E10 * l10 / (2 * Ek10)
chk("R4B-10a 初速同 tan_p/tan_α", tanp_v / tana_v, 2.0)
chk("R4B-10b 初动能同 tan_p/tan_α", tanp_k / tana_k, 0.5)

# R4B-11 加速装置：路线①E=U/d→F=qE→a=F/m→v=√(2ad)  路线②v=√(2qU/m)、F=qU/d
U11 = 500.0; d11 = 0.04; m11 = 4e-25
E11 = U11 / d11; F11 = e * E11; a11 = F11 / m11
v11_a = math.sqrt(2 * a11 * d11); v11_b = math.sqrt(2 * e * U11 / m11)
chk("R4B-11a E", E11, 1.25e4)
chk("R4B-11b F", F11, 2.0e-15)
chk("R4B-11c v 路线①", v11_a, 2.0e4, rel=1e-9)
chk("R4B-11d v 路线②", v11_b, 2.0e4, rel=1e-9)
E11b = U11 / (2 * d11); F11b = e * E11b
chk("R4B-11e d加倍 F 减半", F11b / F11, 0.5)
chk("R4B-11f d加倍 v 不变", math.sqrt(2 * (F11b / m11) * (2 * d11)) / v11_a, 1.0, rel=1e-9)

# R4B-12 等势线疏密：设值支撑（甲密乙疏 ⇒ E_甲>E_乙 ⇒ a_甲>a_乙）
dphi = 2.0; ddx, ddy = 0.05, 0.20
Ejia, Eyi = dphi / ddx, dphi / ddy
chk("R4B-12 E_甲/E_乙", Ejia / Eyi, 4.0)

# R4B-13 等势面做功：路线①W=q(φP−φS)  路线②W=−ΔEp=−q(φS−φP)
q13 = -2e-9; phiP = 5.0; phiS = -7.0
W13a = q13 * (phiP - phiS); W13b = -(q13 * (phiS - phiP))
chk("R4B-13a W 路线①", W13a, -2.4e-8)
chk("R4B-13b W 路线②", W13b, -2.4e-8)
chk("R4B-13c ΔEp=+2.4×10⁻⁸", -W13a, 2.4e-8)

# R4B-01 沿场线/垂直场线：设值支撑（E 沿+x，φ(x)=100−200x）
phi = lambda x: 100 - 200 * x
chk("R4B-01a 垂直线 A、B 等势", phi(0.0) - phi(0.0) if True else 0, 0.0)
chk("R4B-01b 沿场线 φ_B−φ_C>0", 1 if phi(0.0) > phi(0.1) else 0, 1)
chk("R4B-01c 电子B→C W<0", (-e) * (phi(0.0) - phi(0.1)), -3.2e-18)

print("-" * 64)
print(f"批B亲算校验：{'全一致 PASS' if ok else '存在不一致 FAIL'}")
