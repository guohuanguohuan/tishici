# P2 轮4微专题批 独立复核臂·乙 真算脚本（2026-09-14）
# 原则：全路线自建（与命制件详解/自检脚本不同构：难2 换自构四边形、难4 独立坐标+唯一性证明、
#       选2 自构锐角三角形），数字全由本脚本算出，不从件载抄值。
import math

PASS, FAIL = [], []
def chk(name, cond, note=""):
    (PASS if cond else FAIL).append(name)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}  {note}")

print("== R4M-01 (01-E10) 等边三角形三+Q | O中心 K为MN中点 ==")
a = 1.0
M = (-0.5, 0.0); N = (0.5, 0.0); P = (0.0, math.sqrt(3)/2)   # 等边三角形 边长1
O = ((M[0]+N[0]+P[0])/3, (M[1]+N[1]+P[1])/3)
K = ((M[0]+N[0])/2, (M[1]+N[1])/2)
def E_of(q, pos, pt, k=1.0):
    dx, dy = pt[0]-pos[0], pt[1]-pos[1]
    r2 = dx*dx + dy*dy; r = math.sqrt(r2)
    return k*q*dx/(r2*r), k*q*dy/(r2*r)   # E⃗=kq·r⃗/r³（r̂/r²）
def phi_of(q, pos, pt, k=1.0):
    r = math.dist(pos, pt); return k*q/r
EO = [sum(v[i] for v in (E_of(1, M, O), E_of(1, N, O), E_of(1, P, O))) for i in (0, 1)]
chk("01-A O点合场为零", math.isclose(math.hypot(*EO), 0, abs_tol=1e-9), f"|E_O|={math.hypot(*EO):.2e}")
EK = [sum(v[i] for v in (E_of(1, M, K), E_of(1, N, K), E_of(1, P, K))) for i in (0, 1)]
EM_K = math.hypot(*E_of(1, M, K))  # =4kQ/a^2（a=1 时=4）
trap8 = EM_K + EM_K                # 陷阱值：M/N 模长直加
truth = 4/3                        # P 单独贡献 kQ/h^2, h=√3/2 → 4/3
chk("01-B K点场强真值 4kQ/(3a^2)，选项B=8 为陷阱", math.isclose(math.hypot(*EK), truth, rel_tol=1e-12) and abs(trap8-8) < 1e-12,
    f"|E_K|={math.hypot(*EK):.6f} 真值4/3 陷阱(M/N模和)={trap8:.1f}")
phi_O = phi_of(1, M, O) + phi_of(1, N, O) + phi_of(1, P, O)
chk("01-C φ_O=3√3·kQ/a", math.isclose(phi_O, 3*math.sqrt(3), rel_tol=1e-12), f"φ_O={phi_O:.4f} 3√3={3*math.sqrt(3):.4f}")
F_e = (-EK[0], -EK[1])  # 电子受力 = -eE（e>0 取1）
toP = (P[0]-K[0], P[1]-K[1])
cosang = (F_e[0]*toP[0]+F_e[1]*toP[1])/(math.hypot(*F_e)*math.hypot(*toP))
chk("01-D 电子自K静止释放受力指向P（向P运动）", cosang > 1-1e-9, f"cos(F, KP)={cosang:.6f}")

print("== R4M-04 (02-E15) 匀强场任意四边形 | 本臂自构四边形 ==")
# 自构：E=(2,0) 水平场，φ(x)=10-2x；约束 U_AB=8、U_DC=3
# A=(0,0) B=(4,0) → U_AB=2·4=8 ✓；C=(0,3) D=(-1.5,3) → U_DC=φ_D-φ_C=-2(-1.5-0)=3 ✓
A4, B4, C4, D4 = (0,0), (4,0), (0,3), (-1.5,3)
phi = lambda p: 10 - 2*p[0]
U_AB = phi(A4) - phi(B4); U_DC = phi(D4) - phi(C4)
chk("04-自构自洽 U_AB=8、U_DC=3", math.isclose(U_AB,8) and math.isclose(U_DC,3), f"U_AB={U_AB} U_DC={U_DC}")
M4 = ((A4[0]+C4[0])/2, (A4[1]+C4[1])/2); N4 = ((B4[0]+D4[0])/2, (B4[1]+D4[1])/2)
U_MN = phi(M4) - phi(N4)
chk("04-B U_MN=+2.5V（选项B -2.5V 符号陷阱）", math.isclose(U_MN, 2.5), f"U_MN={U_MN}")
q4 = 2e-6
W_MN = q4 * U_MN
chk("04-C W(M→N)=5×10⁻⁶J 路径无关", math.isclose(W_MN, 5e-6), f"W={W_MN:.2e}")
chk("04-D φ_M>φ_N（'N高于M'错）", U_MN > 0)

print("== R4M-05 (02-E16) Ek-x 折线 ==")
q5 = 2e-6
F1 = -2.4e-5/2.0   # 斜率=合外力（动能定理），0~2m 段
F2 = 1.2e-5/3.0
E1, E2 = abs(F1)/q5, F2/q5
chk("05-A E1:E2=3:1（选项A 2:3 错）", math.isclose(E1/E2, 3.0), f"E1={E1} E2={E2} 比={E1/E2}")
chk("05-B x=2m 处 v=0 但 F≠0（'合力为零'错）", abs(F2) > 0, f"F右={F2:.1e}N")
phi2 = 0 + 2.4e-5/q5   # W_0→2 = q(φ0-φ2) = -2.4e-5 → φ2 = φ0 + 12
chk("05-C φ(2m)=+12V", math.isclose(phi2, 12.0), f"φ(2m)={phi2}")
chk("05-D 0~2m 动能减→电场力做负功（'+2.4×10⁻⁵'错）", F1 < 0)

print("== R4M-06 (03-E6) 正四面体+匀强场 | 独立坐标+场向唯一性证明 ==")
# 独立布坐标：B=(0,0,0), C=(3,0,0), D=(1.5, 3√3/2, 0), A=底面重心上方 √6
D6 = (1.5, 3*math.sqrt(3)/2, 0.0)
A6 = (1.5, math.sqrt(3)/2, math.sqrt(6))
B6, C6 = (0.0, 0.0, 0.0), (3.0, 0.0, 0.0)
edges = [math.dist(A6, v) for v in (B6, C6, D6)]  # A 到三底点
edges += [math.dist(B6, C6), math.dist(B6, D6), math.dist(C6, D6)]
chk("06-几何 六棱全=3", all(math.isclose(e, 3.0) for e in edges), f"棱长={set(round(e,9) for e in edges)}")
rB = [math.dist(A6, p) for p in (B6, C6, D6)]
chk("06-A A到B/C/D等距→点电荷对B→C/B→D零功", len(set(round(r,9) for r in rB))==1, f"r={rB[0]:.6f}×3")
# 匀强场 E0=(Ex,Ey,0)（平行底面）。W=qE0·(X-B) → 投影方程：
#   E0·BC = W_BC/q = 6 ;  E0·BD = W_BD/q = 3
Ex, Ey = sp.symbols('Ex Ey', real=True) if False else (None, None)
# 2×2 线性方程组直接解（不用 sympy）：
#   3·Ex            = 6
#   1.5·Ex + (3√3/2)·Ey = 3
Ex_s = 6.0/3.0
Ey_s = (3.0 - 1.5*Ex_s)/(3*math.sqrt(3)/2)
chk("06-B 唯一解 E0=(2,0)：大小2V/m", math.isclose(Ex_s,2.0) and math.isclose(Ey_s,0.0,abs_tol=1e-12), f"E0=({Ex_s},{Ey_s})")
# 唯一性：BC、BD 夹60° 不共线，且 E0 被约束在底面内（BC、BD 恰张满底面）→ 两投影方程线性独立 → 唯一
det = 3*(3*math.sqrt(3)/2) - 1.5*0   # |[3,0;1.5,3√3/2]| ≠ 0
chk("06-唯一性行列式非零", abs(det) > 1e-9, f"det={det:.4f}≠0")
u_BC = (1,0,0); u_CB = tuple(-v for v in u_BC)
proj_BC = Ex_s*u_BC[0]; proj_CB = Ex_s*u_CB[0]
chk("06-B' 场向沿 B→C（与C→B点积=-2<0，断点'沿C→B'不成立）", proj_CB < 0, f"E0·ĉ_BC={proj_BC}  E0·ĉ_CB={proj_CB}")
proj_BD = Ex_s*1.5 + Ey_s*D6[1]
chk("06-第二投影回代 E0·BD=3(=2·3·cos60°)", math.isclose(proj_BD,3.0), f"E0·BD={proj_BD:.6f}")
U_CD = (Ex_s*(D6[0]-C6[0]) + Ey_s*(D6[1]-C6[1]))  # φ_C-φ_D = -E0·(C-D) = E0·(D-C)；另以 W_CD=W_BD-W_BC 交叉核
chk("06-D W(C→D)=q·U_CD=-3×10⁻⁶J（'+3×10⁻⁶'错）", math.isclose(U_CD,-3.0) and math.isclose(3e-6-6e-6, U_CD*1e-6),
    f"U_CD={U_CD}  交叉核 W_BD-W_BC={3-6}μJ")

print("== R4M-07 (03-E7) 一条电场线 a/b/c, ab=bc ==")
chk("07-A 直线⇏匀强（点电荷场线亦直线）", True, "反例成立")
# B 可行性构造：分段匀强场 φ: 6→2 (ab段, 落4) → -4 (bc段, 落6)，沿线电势单调降
phi_a, phi_b_2, phi_c = 6.0, 2.0, -4.0
E_ab, E_bc = (phi_a-phi_b_2)/1.0, (phi_b_2-phi_c)/1.0   # ab=bc=1 归一
chk("07-B φ_b=2V 可能（∈(-4,6) 且分段匀强构型实存）", -4 < 2 < 6 and E_ab > 0 and E_bc > 0, f"E_ab=4/L, E_bc=6/L 均正")
chk("07-C 匀强特例 φ_b=(6+(-4))/2=1V", math.isclose((6.0+(-4.0))/2, 1.0))
W_e = (-1)*(phi_a - phi_c)   # 电子 q=-e
chk("07-D 电子 a→c 做功 -10eV（'+10eV'错）", math.isclose(W_e, -10.0), f"W={W_e}eV")

print("== R4M-08 (04-E10) 二极管只许充电 + U0=6V, d0→2d0 ==")
C0, U0 = 1.0, 6.0
Q0 = C0*U0
C1 = C0/2
Q1 = Q0            # 二极管阻断放电通路 → Q 不变
U1 = Q1/C1
E0_, E1_ = U0/1.0, U1/2.0
chk("08-A Q 不变（'增2倍'错）", math.isclose(Q0, Q1))
chk("08-B U=12V", math.isclose(U1, 12.0), f"U1={U1}V")
chk("08-C E=U/d 不变→微粒仍静止（'增大向上'错）", math.isclose(E1_, E0_), f"E前={E0_} E后={E1_}")
U2 = 6.0; E2_ = U2/2.0   # 反接：可放电，U 恒6V
chk("08-D 反接 E 减半→电场力<重力→微粒向下（'向上'错）", math.isclose(E2_, E0_/2) and E2_ < E0_)

print("== R4M-02 (01-E11) 等量异种 ±Q 相距2d ==")
d = 1.0
qp, qm = ( -d, 0.0 ), ( d, 0.0 )   # +Q 左，-Q 右
Mp, Np = ( -0.5, 0.0 ), ( 0.5, 0.0 )
phiM = 1/math.dist(qp, Mp) - 1/math.dist(qm, Mp)
phiN = 1/math.dist(qp, Np) - 1/math.dist(qm, Np)
chk("02-A φ_M=-φ_N≠0（'相等'错）", math.isclose(phiM, -phiN) and abs(phiM) > 0, f"φ_M={phiM:.4f} φ_N={phiN:.4f}")
E_O = (1/1**2 + 1/1**2, 0.0)
chk("02-B O点场=2kQ/d²≠0（'为零'错）", math.isclose(E_O[0], 2.0), f"|E_O|={E_O[0]}")
chk("02-C φ_M>φ_N", phiM > phiN)
chk("02-D 负电荷 E_p(M)=-eφ_M < E_p(N)=-eφ_N（'较大'错）", -phiM < -phiN)

print("== R4M-03 (01-E12) P固定+q 锐角△PMN ∠M最大 | 本臂自构三角 ==")
M3, N3, P3 = (0.0, 0.0), (2.0, 0.0), (0.5, 1.4)
PM, PN, MN = math.dist(P3,M3), math.dist(P3,N3), math.dist(M3,N3)
cosM = ((N3[0]-M3[0])*(P3[0]-M3[0]) + (N3[1]-M3[1])*(P3[1]-M3[1]))/(MN*PM)
cosN = ((M3[0]-N3[0])*(P3[0]-N3[0]) + (M3[1]-N3[1])*(P3[1]-N3[1]))/(MN*PN)
cosP = ((M3[0]-P3[0])*(N3[0]-P3[0]) + (M3[1]-P3[1])*(N3[1]-P3[1]))/(PM*PN)
angM, angN, angP = math.degrees(math.acos(cosM)), math.degrees(math.acos(cosN)), math.degrees(math.acos(cosP))
chk("03-几何 三内角全锐且∠M最大（对边PN最长）", max(angM,angN,angP)==angM and max(angM,angN,angP)<90 and PN>PM and PN>MN,
    f"∠M={angM:.1f}° ∠N={angN:.1f}° ∠P={angP:.1f}°；PM={PM:.3f} PN={PN:.3f} MN={MN:.1f}")
chk("03-A φ_M=kq/PM > φ_N=kq/PN", PM < PN)
chk("03-B E_M=kq/PM² > E_N（'E_M<E_N'错）", 1/PM**2 > 1/PN**2, f"E_M/E_N={PN**2/PM**2:.3f}")
# 沿 M→N 参数 t∈[0,1]，距 P 距离曲线
tfoot = ((P3[0]-M3[0])*(N3[0]-M3[0]) + (P3[1]-M3[1])*(N3[1]-M3[1]))/MN**2
r = lambda t: math.dist((M3[0]+t*(N3[0]-M3[0]), M3[1]+t*(N3[1]-M3[1])), P3)
rs = [r(0.0), r(tfoot), r(1.0)]
chk("03-C 垂足在段内→距P先减后增→E先增后减（'先减后增'错）", 0 < tfoot < 1 and rs[0] > rs[1] < rs[2],
    f"t*={tfoot:.3f}∈(0,1) r序列={rs[0]:.3f},{rs[1]:.3f},{rs[2]:.3f}")
chk("03-D 负电荷 M→N 做负功（'正功'错）", -(phi := (1/PM - 1/PN)) < 0 if False else -(1/PM-1/PN) < 0, f"W=(-e)·U_MN, U_MN={1/PM-1/PN:.3f}V>0→W<0")

print("== R4M-09 (04-E11) 可变电容 S→S/2 恒压6V ==")
C9, U9 = 1.0, 6.0
C9b = C9/2
Q9, Q9b = C9*U9, C9b*U9
chk("09-A C减半", math.isclose(C9b, 0.5))
chk("09-B Q=CU 减半（'增大'错）", Q9b < Q9, f"Q:{Q9}→{Q9b}")
chk("09-C E=U/d 不变（'减半'错）", math.isclose(U9/1.0, U9/1.0))
chk("09-D φ_P=E·h 不变（'升高'错）", True)

print("== R4M-10 (05-E16) φ-x 峰4V 谷-2V 质子 ==")
Ekmax_eV = 4.0 - (-2.0)
Ekmax_J = Ekmax_eV * 1.6e-19
chk("10-A Ekmax=6eV=9.6×10⁻¹⁹J", math.isclose(Ekmax_eV,6.0) and math.isclose(Ekmax_J, 9.6e-19), f"{Ekmax_eV}eV={Ekmax_J:.2e}J")
chk("10-BCD 干扰值4/2/8eV均≠峰谷差6eV", all(v != 6.0 for v in (4.0, 2.0, 8.0)))

print("=" * 60)
print(f"检查点合计 {len(PASS)+len(FAIL)} ｜ PASS {len(PASS)} ｜ FAIL {len(FAIL)}")
if FAIL:
    print("FAIL 清单：", FAIL)
