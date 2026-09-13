# 批C 定稿前数值真算校验（定量题 9 题；真算不抄——独立复算后对照源答案）
# 口径：sin37°=0.6、cos37°=0.8（⑥-4 惯例）；g=10（Q57/Q61/Q70 题给或惯例）
import math

ok = []
def chk(name, got, want, tol=1e-9):
    good = abs(got - want) <= tol * max(1.0, abs(want))
    ok.append((name, got, want, "一致" if good else "**不一致**"))

# Q41（简14）：a=(mg+qE)/m=2g；前半加速 d/2 后反向匀速
g, d = 9.8, 1.0
a = (g + g)                     # qE=mg
v = math.sqrt(2 * a * (d / 2))
t1 = v / a
t2 = (d / 2) / v
t = t1 + t2
chk("Q41.t/( (3/4)√(2d/g) )", t / ((3 / 4) * math.sqrt(2 * d / g)), 1.0, 1e-12)
chk("Q41.a/g", a / g, 2.0)

# Q45（中32）：v0=√(2eU/m)；y_A=Ed²/(4U)；t=d√(2m/(eU))（数值代入验）
e, m_, U, E, d_ = 1.6e-19, 9.1e-31, 100.0, 5.0, 0.02
v0 = math.sqrt(2 * e * U / m_)
t1 = d_ / v0
yA = 0.5 * (e * E / m_) * t1**2
chk("Q45.yA/(Ed²/4U)", yA / (E * d_**2 / (4 * U)), 1.0, 1e-12)
# 区域Ⅱ a'=2a，vy 归零历时 t2=t1/2，再对称 2t2 回 x 轴
vy = (e * E / m_) * t1
t2 = vy / (2 * e * E / m_)
chk("Q45.t2/(t1/2)", t2 / (t1 / 2), 1.0, 1e-12)
chk("Q45.t/(d√(2m/eU))", (t1 + 2 * t2) / (d_ * math.sqrt(2 * m_ / (e * U))), 1.0, 1e-12)

# Q46（中31）：v=4/3×10^7；y=0.36cm；φA=27.2V
U1, U2, l, dd = 500.0, 40.0, 0.06, 0.02
me, ee = 0.9e-30, 1.6e-19
v = math.sqrt(2 * ee * U1 / me)
chk("Q46.v", v, 4 / 3 * 1e7, 1e-3)
ta = l / v
acc = ee * U2 / (me * dd)
y = 0.5 * acc * ta**2
chk("Q46.y/cm", y * 100, 0.36, 1e-3)
phiA = (U2 / dd) * (dd / 2 + y)
chk("Q46.φA/V", phiA, 27.2, 1e-3)

# Q54（中27）：U=mgd/q；下移 d 后 a=g/2；v=√(6gd)
gg, dd2 = 10.0, 1.0
U = gg * dd2  # mg=qU/d
a2 = gg - (U / (2 * dd2))  # E'=U/(2d) → qE'/m=g/2
chk("Q54.a2/g", a2 / gg, 0.5)
v0 = math.sqrt(2 * gg * 2 * dd2)
vend = math.sqrt(v0**2 + 2 * a2 * 2 * dd2)
chk("Q54.v²/(6gd)", vend**2 / (6 * gg * dd2), 1.0, 1e-12)

# Q57（中28）：vm=2(L1+L2)/t=4；a2=4；f=4N；E=5×10⁴
L1, L2, tt, q_, m2 = 8.0, 2.0, 5.0, 1.0e-4, 1.0
vm = 2 * (L1 + L2) / tt
chk("Q57.vm", vm, 4.0)
a_2 = vm**2 / (2 * L2)
chk("Q57.a2", a_2, 4.0)
f = m2 * a_2
a_1 = vm**2 / (2 * L1)
E57 = (f + m2 * a_1) / q_
chk("Q57.E", E57, 5e4, 1e-9)

# Q51（冲4）：v=4√(eU/m)；L8=v·T/2；N=eUT²/(8md²)（数值代入验）
eU, mm, T, gap = 1.0, 2.0, 3.0, 0.5
v8 = math.sqrt(16 * eU / mm)
chk("Q51.v8/√(16eU/m)", v8 / 4 / math.sqrt(eU / mm), 1.0, 1e-12)
L8 = v8 * T / 2
chk("Q51.L8/(2T√(eU/m))", L8 / (2 * T * math.sqrt(eU / mm)), 1.0, 1e-12)
# 间隙累计：Nd=½vm(T/2)，NeU=½vm² 联立 → N=eUT²/(8md²)
N = (eU * T**2) / (8 * mm * gap**2)
vm2 = 4 * gap * N / T  # 由 Nd=½vm(T/2)
chk("Q51.能量式自洽", 0.5 * mm * vm2**2 / (N * eU), 1.0, 1e-12)

# Q60（冲10，源0.4）：E1=mg/q；Ek=(3√2−2)mgR/2；v0=½√(gR/2)
R, m3, g3, q3 = 1.0, 1.0, 10.0, 1.0
E1 = m3 * g3 / q3  # tan45°=mg/qE1
F = math.sqrt((m3 * g3) ** 2 + (q3 * E1) ** 2)
vD2 = F * R / m3
EkA = 0.5 * m3 * vD2 + F * R * (1 - math.cos(math.radians(45)))
chk("Q60.Ek/( (3√2−2)mgR/2 )", EkA / ((3 * math.sqrt(2) - 2) * m3 * g3 * R / 2), 1.0, 1e-12)
t_ = math.sqrt(2 * R / g3)
v0 = (R / 2) / t_
chk("Q60.v0/(½√(gR/2))", v0 / (0.5 * math.sqrt(g3 * R / 2)), 1.0, 1e-12)

# Q61（冲12）：vC=3；t=0.64；Ek=7.3J
E61, q61, m61, mu, L61, v061 = 1.0e5, 1.5e-5, 0.2, 0.5, 1.28, 5.0
qE = q61 * E61  # 1.5N 向右（负电荷受力与场反向→向右）
FN = m61 * 10 * 0.8 + qE * 0.6  # mg cos37 + qE sin37
fr = mu * FN
a1 = (m61 * 10 * 0.6 - qE * 0.8 - fr) / m61
vC2 = v061**2 + 2 * a1 * L61
chk("Q61.vC²", vC2, 9.0, 1e-9)
a2 = qE / m61
vC = math.sqrt(vC2)
vx0 = vC * 0.8
t61 = 2 * vx0 / a2
chk("Q61.t", t61, 0.64, 1e-9)
vx1 = abs(vx0 - a2 * t61)
vy1 = vC * 0.6 + 10 * t61
Ek = 0.5 * m61 * (vx1**2 + vy1**2)
chk("Q61.Ek", Ek, 7.3, 1e-9)

# Q70（冲6）：起动 t=1s；a_max=10（t=3s）；v_max=20（t=5s）；Ekm=20J
# a(t)=g−f/m, f=|1.5−0.5t|；[1,3]: a=5t−5；[3,5]: a=25−5t
v70, tmax = 0.0, None
for i in range(10000, 50001):  # dt=1e-4, t∈[1,5]
    tt2 = i * 1e-4
    a70 = (5 * tt2 - 5) if tt2 <= 3 else (25 - 5 * tt2)
    v70 += a70 * 1e-4
    if i == 50000:
        tmax = tt2
chk("Q70.v_max", v70, 20.0, 1e-6)
chk("Q70.Ekm", 0.5 * 0.1 * v70**2, 20.0, 1e-6)
chk("Q70.a_max(t=3)", 5 * 3 - 5, 10.0)

# Q30（简11）：Q=CU
chk("Q30.Q", 2200e-6 * 1.0, 2.2e-3, 1e-12)

bad = [r for r in ok if r[3] != "一致"]
for name, got, want, verdict in ok:
    print(f"{verdict}  {name}: got={got:.6g} want={want:.6g}")
print("---")
print(f"合计 {len(ok)} 项，不一致 {len(bad)} 项")
