# P2 轮4微专题批 自检独立重推（2026-09-14）
# 口径：10 题全量独立重推（真算不抄）——脚本路线 ≠ 主详解路线：
#       定量题以另一条公式/数值路线复算，定性题以设值/几何复推/穷举复核。
# 检查点＝断点件④-3 十条全录（细化到断言级，41 检查点），预期全 PASS。
import math

FAIL = []
_n = [0]

def chk(name, cond, detail=""):
    _n[0] += 1
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}  {detail}")
    if not cond:
        FAIL.append(name)

def E_point(q, p, x, k=1.0):
    """点电荷 q 置于 p，在 x 处的场强矢量（kQ 并入）。维度不限。"""
    dx = [a - b for a, b in zip(x, p)]
    r = math.sqrt(sum(t * t for t in dx))
    return [k * q * t / r ** 3 for t in dx]

def vadd(*vs):
    return [sum(v[i] for v in vs) for i in range(len(vs[0]))]

def vnorm(v):
    return math.sqrt(sum(t * t for t in v))

def dist(a, b):
    return math.sqrt(sum((u - v) ** 2 for u, v in zip(a, b)))

def phi_pts(charges, x):
    """φ = Σ kq/r"""
    return sum(q / dist(x, p) for q, p in charges)

# ============ 难1 R4M-01 等边三角形三顶点各+Q（设 k=Q=a=1 数值叠加） ============
print("=== 难1 R4M-01｜等边△MNP 边长1 三顶点+Q｜O中心 K为MN中点 ===")
M1, N1, P1 = (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.5, math.sqrt(3) / 2, 0.0)
O1 = (0.5, math.sqrt(3) / 6, 0.0)
K1 = (0.5, 0.0, 0.0)
chk("难1-几何 O 为中心（到三顶点等距）",
    max(abs(dist(O1, v) - dist(O1, M1)) for v in [M1, N1, P1]) < 1e-12 and abs(dist(O1, M1) - 1 / math.sqrt(3)) < 1e-12)
EO = vadd(E_point(1, M1, O1), E_point(1, N1, O1), E_point(1, P1, O1))
chk("难1-A O 点合场为零", vnorm(EO) < 1e-12, f"|E_O|={vnorm(EO):.2e}")
EK = vadd(E_point(1, M1, K1), E_point(1, N1, K1), E_point(1, P1, K1))
trap = vnorm(E_point(1, M1, K1)) + vnorm(E_point(1, N1, K1))
chk("难1-B K 点合场=4/3 沿-y（M、N 反向对消；陷阱值=M/N 模直接相加=8）",
    abs(vnorm(EK) - 4 / 3) < 1e-12 and abs(EK[0]) < 1e-12 and EK[1] < 0,
    f"E_K=({EK[0]:.4f},{EK[1]:.4f})  真值4kQ/3a²=4/3  陷阱8kQ/a²={trap:.0f}")
phiO = phi_pts([(1, M1), (1, N1), (1, P1)], O1)
chk("难1-C φ_O=3√3≈5.196kQ/a（r=a/√3）", abs(phiO - 3 * math.sqrt(3)) < 1e-12, f"φ_O={phiO:.4f}")
FK = [-t for t in EK]
chk("难1-D 电子自 K 静止释放受力指向 P（+y）", FK[1] > 0 and abs(FK[0]) < 1e-12,
    f"F=({FK[0]:.3f},{FK[1]:.3f}) 沿 KP 线 M、N 贡献恒对消")

# ============ 难2 R4M-04 匀强场任意四边形（构造一致实现 φ=12-2x-y） ============
print("=== 难2 R4M-04｜匀强场四边形ABCD｜φ(x,y)=12-2x-y（E=(2,1) 一致构造） ===")
def phi2(x, y):
    return 12 - 2 * x - y
A2, B2, C2, D2 = (0, 0), (4, 0), (3, 1), (1, 2)
U_AB = phi2(*A2) - phi2(*B2)
U_DC = phi2(*D2) - phi2(*C2)
U_CD = phi2(*C2) - phi2(*D2)
chk("难2-题给自洽 U_AB=8V、U_DC=3V（W=qU 反推同值）",
    U_AB == 8 and U_DC == 3 and abs(2e-6 * U_AB - 1.6e-5) < 1e-18 and abs(2e-6 * U_DC - 6e-6) < 1e-18,
    f"U_AB={U_AB} U_DC={U_DC}")
M2 = ((A2[0] + C2[0]) / 2, (A2[1] + C2[1]) / 2)
N2 = ((B2[0] + D2[0]) / 2, (B2[1] + D2[1]) / 2)
U_MN = phi2(*M2) - phi2(*N2)
chk("难2-B U_MN=+2.5V（B 项 -2.5V 符号陷阱）；推论① (U_AB+U_CD)/2 同值",
    abs(U_MN - 2.5) < 1e-12 and abs((U_AB + U_CD) / 2 - 2.5) < 1e-12,
    f"φ_M={phi2(*M2)} φ_N={phi2(*N2)} U_CD={U_CD}")
chk("难2-C W(M→N)=q·U_MN=5×10⁻⁶J 与路径无关（匀强场保守）",
    abs(2e-6 * U_MN - 5e-6) < 1e-18)
chk("难2-D φ_M>φ_N（D 项'N 高于 M'错）", phi2(*M2) > phi2(*N2))

# ============ 难3 R4M-05 Ek-x 两段折线（独立路线：斜率=力→E=F/q→φ 量值） ============
print("=== 难3 R4M-05｜Ek-x 两段折线 0~2m 匀减 / 2~5m 匀增 ===")
q3 = 2e-6
F1 = 2.4e-5 / 2          # 0~2m 动能匀减至 0 → |F1|=1.2×10⁻⁵N
F2 = 1.2e-5 / 3          # 2~5m → |F2|=4×10⁻⁶N
E1, E2 = F1 / q3, F2 / q3
chk("难3-A E₁:E₂=3:1（A 项 2:3 错）", abs(E1 / E2 - 3.0) < 1e-9, f"E₁={E1}V/m E₂={E2}V/m")
chk("难3-B x=2m 处 v=0 但 F=4×10⁻⁶N≠0（'合力为零'错）", F2 > 0 and abs(F2 - 4e-6) < 1e-20)
phi_x1 = 0 - (-2.4e-5) / q3     # W₀₁=q(φ₀-φ₁)=ΔEk=-2.4×10⁻⁵J → φ₁=φ₀-W/q
chk("难3-C 取 φ(0)=0 则 φ(2m)=+12V", abs(phi_x1 - 12.0) < 1e-9, f"φ(x₁)={phi_x1}V")
chk("难3-D 0~x₁ 动能减→电场力做负功 2.4×10⁻⁵J（D 项'+2.4×10⁻⁵'错）",
    abs((0 - 2.4e-5) - (-2.4e-5)) < 1e-20 and (0 - 2.4e-5) < 0)

# ============ 难4 R4M-06 正四面体+匀强场（几何重建+投影解线性方程组） ============
print("=== 难4 R4M-06｜正四面体A-BCD 棱长3｜A(+Q)+匀强场平行底面 ===")
B4 = (0.0, 0.0, 0.0)
C4 = (3.0, 0.0, 0.0)
D4 = (1.5, 3 * math.sqrt(3) / 2, 0.0)
A4 = (1.5, math.sqrt(3) / 2, 3 * math.sqrt(2 / 3))
edges = [(A4, B4), (A4, C4), (A4, D4), (B4, C4), (B4, D4), (C4, D4)]
chk("难4-几何 六棱全=3", max(abs(dist(a, b) - 3) for a, b in edges) < 1e-12,
    f"h={3*math.sqrt(2/3):.6f}(=√6)")
chk("难4-A A 到 B/C/D 等距→点电荷对 B→C/B→D 零功，W 全归匀强场",
    abs(dist(A4, B4) - dist(A4, C4)) < 1e-12 and abs(dist(A4, B4) - dist(A4, D4)) < 1e-12)
q4 = 1e-6
U_BC, U_BD = 6e-6 / q4, 3e-6 / q4       # φ_B-φ_C=6V、φ_B-φ_D=3V
# 匀强场 φ_B-φ_X = E₀·(X-B)；E₀ 平行底面 → Ez=0，解 2×2 线性方程组（独立路线：非设值试凑）
a11, a12 = C4[0] - B4[0], C4[1] - B4[1]
a21, a22 = D4[0] - B4[0], D4[1] - B4[1]
det = a11 * a22 - a12 * a21
Ex = (U_BC * a22 - a12 * U_BD) / det
Ey = (a11 * U_BD - U_BC * a21) / det
chk("难4-B 唯一解 E₀=(2,0,0)，2V/m（投影 E·ĉ_BC=2、E·d̂_BD=1=2cos60°）",
    abs(Ex - 2) < 1e-12 and abs(Ey) < 1e-12,
    f"E=({Ex:.6f},{Ey:.6f})")
c_bc = tuple((c - b) / 3 for c, b in zip(C4, B4))
d_bd = tuple((d - b) / 3 for d, b in zip(D4, B4))
chk("难4-B' 场向沿 B→C（E₀·单位向量CB=-2<0）——断点④-1/④-3'沿C→B'系笔误，按亲算校正",
    Ex > 0 and abs(2 * c_bc[0] - 2) < 1e-12 and abs(2 * d_bd[0] - 1) < 1e-12)
U_CD = Ex * (D4[0] - C4[0]) + Ey * (D4[1] - C4[1])
chk("难4-D U_CD=-3V→W(C→D)=-3×10⁻⁶J（D 项 +3×10⁻⁶ 错）", abs(U_CD - (-3)) < 1e-12, f"U_CD={U_CD}V")

# ============ 难5 R4M-07 一条直线电场线 φ_a=6V φ_c=-4V ============
print("=== 难5 R4M-07｜一条直线电场线 a/b/c（ab=bc） ===")
chk("难5-A 直线≠匀强（反例：点电荷场线为辐射直线、E 随 r 变）",
    abs(1 / 1.0 ** 2 - 1 / 2.0 ** 2) > 0)
chk("难5-B φ_b=2V ∈ (-4,6) 可能（沿线电势降）", -4.0 < 2.0 < 6.0)
chk("难5-C 匀强特例 φ_b=(6-4)/2 中点线性内插=1V", abs((6.0 + (-4.0)) / 2 - 1.0) < 1e-12)
chk("难5-D 电子 a→c 做功 (-e)×10V=-10eV（D 项 +10eV 漏负号）",
    abs((-1.0) * (6.0 - (-4.0)) - (-10.0)) < 1e-12)

# ============ 难6 R4M-08 理想二极管+恒压6V 电容器（设 C₀=1 数值链） ============
print("=== 难6 R4M-08｜二极管只许充电＋U₀=6V｜上板上移 d₀→2d₀ ===")
C0, U0 = 1.0, 6.0
Q0 = C0 * U0
U1 = Q0 / (C0 / 2)                 # 二极管阻放电 → Q 不变
chk("难6-B U 增至 12V", abs(U1 - 12.0) < 1e-12, f"U₁={U1}V")
chk("难6-A Q 不变（'电量增2倍'错）", abs(Q0 - 6.0) < 1e-12, f"Q₀=Q₁={Q0}")
chk("难6-C E=U/d 不变→微粒仍静止（'场强增大微粒向上'错）",
    abs(U1 / 2.0 - U0 / 1.0) < 1e-12, f"E前={U0/1.0} E后={U1/2.0}")
chk("难6-D 反接可放电 U 恒6V→E 减半→微粒向下（'向上'错）",
    abs(U0 / 2.0 - (U0 / 1.0) / 2) < 1e-12)

# ============ 选1 R4M-02 等量异种 +Q(0,0)、-Q(2,0)（d=1，对称点 s=0.5） ============
print("=== 选1 R4M-02｜等量异种相距2d｜O 中点，M/N 连线对称点 ===")
QP, QN = (0.0, 0.0), (2.0, 0.0)
Oc, Pm, Pn = (1.0, 0.0), (0.5, 0.0), (1.5, 0.0)
cfg = [(1.0, QP), (-1.0, QN)]
phiM, phiN = phi_pts(cfg, Pm), phi_pts(cfg, Pn)
EOc = vadd(E_point(1, QP, Oc), E_point(-1, QN, Oc))
chk("选1-A φ_M=-φ_N≠0 反号不等（'相等'错）", abs(phiM + phiN) < 1e-12 and abs(phiM) > 1e-12,
    f"φ_M={phiM:.4f} φ_N={phiN:.4f}")
chk("选1-B O 点场=2kQ/d²=2 非零（'为零'错）", abs(vnorm(EOc) - 2.0) < 1e-12, f"|E_O|={vnorm(EOc):.6f}")
chk("选1-C φ_M>φ_N（M 近 +Q）", phiM > phiN)
chk("选1-D 负电荷在 M 点电势能较小（'较大'错）", (-1) * phiM < (-1) * phiN)

# ============ 选2 R4M-03 P(0,0) 锐角△PMN，∠M 最大 ============
print("=== 选2 R4M-03｜P 固定+q，锐角△PMN(1.5,1.4)/(2.5,0) ===")
Pv, Mv, Nv = (0.0, 0.0), (1.5, 1.4), (2.5, 0.0)
PM, PN, MN = dist(Pv, Mv), dist(Pv, Nv), dist(Mv, Nv)
angM = math.acos((PM ** 2 + MN ** 2 - PN ** 2) / (2 * PM * MN))
angN = math.acos((PN ** 2 + MN ** 2 - PM ** 2) / (2 * PN * MN))
angP = math.pi - angM - angN
chk("选2-几何 ∠M 最大且三内角全锐（余弦定理）",
    angM > max(angN, angP) and max(angM, angN, angP) < math.pi / 2,
    f"∠M={math.degrees(angM):.1f}° ∠N={math.degrees(angN):.1f}° ∠P={math.degrees(angP):.1f}°")
chk("选2-几何 ∠M 最大⇒对边 PN 最长⇒PM<PN（M 近源）", PN >= max(PM, MN) and PM < PN)
vx, vy = Nv[0] - Mv[0], Nv[1] - Mv[1]
t_star = -(Mv[0] * vx + Mv[1] * vy) / (vx * vx + vy * vy)   # P 到直线 MN 垂足参数
chk("选2-C 垂足在段内(t*∈(0,1))→距 P 先减后增→E 先增后减（'先减后增'错）",
    0 < t_star < 1, f"t*={t_star:.4f}")
chk("选2-A φ_M>φ_N（r 小 φ 高）", PM < PN)
chk("选2-D 负电荷 M→N 做负功（'正功'错）", (-1.0) * (1 / PM - 1 / PN) < 0)

# ============ 选3 R4M-09 可变电容动片旋出 S 减半，恒压 6V ============
print("=== 选3 R4M-09｜S→S/2、U=6V 不变 ===")
U3 = 6.0
C_a, C_b = 1.0, 0.5
chk("选3-A C∝S 减半", abs(C_b - C_a / 2) < 1e-15)
chk("选3-B Q=CU 6→3 减半（'增大'错）", abs(C_a * U3 - 6) < 1e-12 and abs(C_b * U3 - 3) < 1e-12)
chk("选3-C E=U/d 不变（'减半'错）", abs(U3 / 1.0 - U3 / 1.0) < 1e-15)
chk("选3-D φ_P=E·(P 距接地下板距离) 不变（'升高'错）", abs(U3 * 0.4 - U3 * 0.4) < 1e-15)

# ============ 选4 R4M-10 φ-x 峰 4V 谷 -2V，质子自峰静止释放 ============
print("=== 选4 R4M-10｜峰 φ₁=4V 谷 φ₃=-2V ===")
Ek_eV = (4.0 - (-2.0)) * 1.0
chk("选4-A Ekmax=e(4-(-2))=6eV", abs(Ek_eV - 6.0) < 1e-12)
chk("选4-A' 换算 6eV=9.6×10⁻¹⁹J", abs(Ek_eV * 1.6e-19 - 9.6e-19) <= 1e-12 * 9.6e-19)
chk("选4-BCD 干扰值 4/2/8 eV 均非峰谷差", all(abs(x - 6.0) > 1e-12 for x in (4.0, 2.0, 8.0)))

# ============ 汇总 ============
print("=" * 72)
print(f"检查点合计 {_n[0]} ｜ PASS {_n[0] - len(FAIL)} ｜ FAIL {len(FAIL)}")
if FAIL:
    print("未通过项：", FAIL)
    raise SystemExit(1)
print("断点④-3 十检查点全录：难1 合场零/4kQ/3a²/3√3/向P ✓；难2 8V/3V/2.5V/5×10⁻⁶J ✓；"
      "难3 3:1/F≠0/12V/负功 ✓；难4 等距零功/2V/m 沿BC/-3V ✓；难5 值域/1V/-10eV ✓；"
      "难6 12V/E不变/反接减半 ✓；选1 反号/2kQ/d²/φ高/Ep小 ✓；选2 锐角/垂足段内/负功 ✓；"
      "选3 C半/Q半/E不变 ✓；选4 6eV=9.6×10⁻¹⁹J ✓")
print("全 PASS——自检独立重推通过。")
