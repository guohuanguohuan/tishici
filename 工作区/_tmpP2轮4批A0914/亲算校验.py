# P2 轮4改编批A 亲算独立复算（2026-09-14）
# 口径：与命制件主详解「不同计算路径」复推——主详解用符号式，本件用数值直代/比例式/能量链独立路线。
# 每题：independent() 为独立路线；expected 为命制件答案；一致则 PASS。
e = 1.6e-19
m_e = 9.1e-31      # 电子质量（题给量级 9×10⁻³¹ 亦验）
m_p = 1.67e-27

def near(a, b, rel=0.02):
    return abs(a - b) <= rel * max(abs(a), abs(b), 1e-300)

res = []

# ── R4A-01（01-E6 填空）改编·教材10.1-2：φ_M 与换电荷后的电势能 ──
# 独立路线：先由比例 Ep∝q（同一点场不变）定 φ，再以新电荷比例回推
Ep1, q1 = -1.2e-8, -3e-9
phi_M = Ep1 / q1
q2 = 5.0e-10
Ep2 = Ep1 * (q2 / q1)          # 比例路线
Ep2b = q2 * phi_M              # 定义式路线（互证）
res.append(("R4A-01 phi_M=4.0V", phi_M, 4.0))
res.append(("R4A-01 Ep2=2.0e-9J(比例)", Ep2, 2.0e-9))
res.append(("R4A-01 Ep2=2.0e-9J(定义式)", Ep2b, 2.0e-9))

# ── R4A-04（02-E9 单选）改编·教材10.2-1：U_AB=-50V，q=+4nC，A→B ──
# 独立路线：先判电势高低→电势能变化→反推功（不经 W=qU 直乘）
U_AB, q = -50.0, 4e-9
dEp = q * (-U_AB)              # φ_B−φ_A = −U_AB = 50V，电势能增
W = -dEp                       # 动能定理/W=qU_AB 互证
res.append(("R4A-04 ΔEp=+2.0e-7J", dEp, 2.0e-7))
res.append(("R4A-04 W=-2.0e-7J", W, -2.0e-7))

# ── R4A-07（04-E4 填空）改编·教材10.4-3：4.5V 充 9μC；改 3V ──
C = 9e-6 / 4.5
dQ = C * (4.5 - 3.0)           # 独立路线：ΔQ = C·ΔU
Q3 = C * 3.0
res.append(("R4A-07 C=2.0e-6F", C, 2.0e-6))
res.append(("R4A-07 Q(3V)=6.0e-6C", Q3, 6.0e-6))
res.append(("R4A-07 ΔQ=3.0e-6C", dQ, 3.0e-6))

# ── R4A-09（04-E6 填空）改编·教材10.4-4：20μF/3.5kV；放出一半 ──
Cc, Uc = 20e-6, 3.5e3
Q = Cc * Uc
Up = 0.5 * Uc                  # 独立路线：Q∝U ⇒ 放一半电荷即电压降一半
Up2 = (0.5 * Q) / Cc           # 定义式互证
res.append(("R4A-09 Q=7.0e-2C", Q, 7.0e-2))
res.append(("R4A-09 U'=1750V(比例)", Up, 1750.0))
res.append(("R4A-09 U'=1750V(定义式)", Up2, 1750.0))

# ── R4A-10（05-E7 单选）改编·教材10.5-1：二价氧离子 120V 加速 ──
q_ion = 2 * e
Ek_J = q_ion * 120.0
Ek_eV = Ek_J / e               # 独立路线：焦耳→eV 回除
res.append(("R4A-10 Ek=3.84e-17J", Ek_J, 3.84e-17))
res.append(("R4A-10 Ek=240eV", Ek_eV, 240.0))

# ── R4A-11（05-E8 填空）改编·教材10.5-5：1800V 加速→E=4.5e4 N/C、L=4cm 偏转 ──
# 独立路线：全数值分步（主详解用闭式 y=EL²/4U₁、tanθ=EL/2U₁）
U1, E2, L = 1800.0, 4.5e4, 0.04
v0 = (2 * e * U1 / m_e) ** 0.5
t = L / v0
a = e * E2 / m_e
y = 0.5 * a * t * t
tan_th = a * t / v0
# 闭式互证
y_c = E2 * L * L / (4 * U1)
tan_c = E2 * L / (2 * U1)
res.append(("R4A-11 v0≈2.52e7m/s", v0, 2.52e7))
res.append(("R4A-11 y=0.010m(分步)", y, 0.010))
res.append(("R4A-11 y=0.010m(闭式)", y_c, 0.010))
res.append(("R4A-11 tanθ=0.50(分步)", tan_th, 0.50))
res.append(("R4A-11 tanθ=0.50(闭式)", tan_c, 0.50))

# ── R4A-12（05-E9 填空）改编·教材10.5-6：电子 v=4e6 m/s 过 L=0.1m 加速段 ──
# 独立路线：动能定理求 U=e⁻¹·½mv²，再 E=U/L（主详解用 E=mv²/2eL 直式）
# 题给电子质量 9×10⁻³¹ kg（教材题惯给值，取整以便简翼口算复核）
m_give = 9.0e-31
v, L2 = 4.0e6, 0.10
Ek_need = 0.5 * m_give * v * v
U_need = Ek_need / e
E_need = U_need / L2
res.append(("R4A-12 Ek=7.2e-18J", Ek_need, 7.2e-18))
res.append(("R4A-12 U=45V", U_need, 45.0))
res.append(("R4A-12 E=450V/m", E_need, 450.0))

# ── R4A-03（01-E8 多选·定性）数值支撑：等量同种正电荷 φ_A＞φ_O＞φ_C ──
k = 9e9
Qc = 2e-6
import math
phi = lambda x, y: k * Qc * (1 / math.hypot(x + 0.1, y) + 1 / math.hypot(x - 0.1, y))
pA, pO, pC = phi(-0.05, 0), phi(0, 0), phi(0, 0.05)
res.append(("R4A-03 φ_A＞φ_O", 1.0 if pA > pO else 0.0, 1.0))
res.append(("R4A-03 φ_O＞φ_C", 1.0 if pO > pC else 0.0, 1.0))

# ── R4A-05（02-E10 单选·定性）数值支撑：U_MN=+60V 时电子 Ep 符号链 ──
phi_M_, phi_N_ = 60.0, 0.0
Ep_M, Ep_N = -e * phi_M_, -e * phi_N_
res.append(("R4A-05 Ep_N＞Ep_M", 1.0 if Ep_N > Ep_M else 0.0, 1.0))
res.append(("R4A-05 U_MN=+60V＞0", phi_M_ - phi_N_, 60.0))

# ── 输出 ──
print("P2轮4改编批A 亲算独立复算（独立路线 vs 命制件答案）")
print("=" * 64)
npass = 0
for name, got, exp in res:
    ok = near(got, exp)
    npass += ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name:<28} 复算={got:.6g}  命制件={exp:.6g}")
print("=" * 64)
print(f"合计 {npass}/{len(res)} 一致、{len(res)-npass} 不一致")
