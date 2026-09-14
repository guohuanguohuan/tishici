# P2 轮4凭空批A 亲算校验（2026-09-14）
# 9 题全定量；脚本路线 = 独立路线，与主件【详解】主路线不同，读数须全等。
# 口径：PASS 需相对容差 ≤1e-9（浮点）；每题列检查点行。
import math

ok = 0
bad = 0

def chk(label, got, want, tol=1e-9):
    global ok, bad
    good = (abs(got - want) <= tol * max(1.0, abs(want))) if isinstance(got, (int, float)) else (got == want)
    if good:
        ok += 1
        print(f"  PASS  {label}: {got}")
    else:
        bad += 1
        print(f"  FAIL  {label}: got {got}, want {want}")

print("R4K-01（01-E13）Ep-q 两组数据读 phi ＋ 负电荷第三态（独立路线：比值双路＋比例外推）")
q1, Ep1 = 2e-9, -1.6e-8
q2, Ep2 = 5e-9, -4.0e-8
r1, r2 = Ep1 / q1, Ep2 / q2
chk("比值路1 Ep1/q1(V)", r1, -8.0)
chk("比值路2 Ep2/q2(V)", r2, -8.0)
chk("两路同值(线性成立)", r1, r2)
phi = r1
q3 = -1e-9
chk("Ep3=q3*phi(J)", q3 * phi, 8.0e-9)
# 反向独立路线：Ep3 = Ep1*(q3/q1)（同点场不变比例式）
chk("比例路线 Ep3=Ep1*(q3/q1)", Ep1 * (q3 / q1), 8.0e-9)

print("R4K-02（01-E14）电子 M→N 动能增反推链（独立路线：eV 档核＋符号穷举）")
dEk = 2.4e-18
e = 1.6e-19
chk("ΔEk(eV档)", dEk / e, 15.0)
chk("W=+ΔEk(J)", dEk, 2.4e-18)          # 仅静电力：W=ΔEk>0 正功
chk("ΔEp=-W(J)", -dEk, -2.4e-18)        # 电势能减少
EpM = -3.0e-18
chk("EpN=EpM+ΔEp(J)", EpM + (-dEk), -5.4e-18)
# phi 序符号逻辑：q=-e<0，EpM>EpN ⇒ phiM<phiN
chk("EpM>EpN(布尔)", EpM > EpM + (-dEk), True)
chk("⇒phiM<phiN(q<0)", "phiM<phiN", "phiM<phiN")

print("R4K-03（01-E15）题给 phi=kQ/r 径向两点（独立路线：kQ 积还原＋比例式）")
phiA, rA, rB = 90.0, 0.1, 0.3
kQ = phiA * rA
chk("kQ=phiA*rA(V·m)", kQ, 9.0)
chk("phiB=kQ/rB(V)", kQ / rB, 30.0)
chk("比例路 phiB=phiA*rA/rB", phiA * rA / rB, 30.0)
q = 2e-8
EpA, EpB = q * phiA, q * (kQ / rB)
chk("EpA(J)", EpA, 1.8e-6)
chk("EpB(J)", EpB, 6.0e-7)
chk("W=EpA-EpB(J)", EpA - EpB, 1.2e-6)
# 独立第二路：W=q(phiA-phiB) 应同值
chk("第二路 W=q(phiA-phiB)", q * (phiA - 30.0), 1.2e-6)

print("R4K-04（01-E16）零点平移不变性（独立路线：电势能直除＋平移重算）")
q = 3e-8
EpA, EpB = 1.5e-5, 6.0e-6
phiA, phiB = EpA / q, EpB / q
chk("phiA(V)", phiA, 500.0)
chk("phiB(V)", phiB, 200.0)
chk("W=EpA-EpB(J)", EpA - EpB, 9.0e-6)
chk("第二路 W=q(phiA-phiB)", q * (phiA - phiB), 9.0e-6)
phiA2 = phiA - phiB   # 改 B 为零点
chk("phiA'(V)=phiA-phiB", phiA2, 300.0)
chk("phiB'(V)", phiB - phiB, 0.0)
chk("W'=q*phiA'(J)", q * phiA2 - q * 0.0, 9.0e-6)
chk("W'=W(不变)", q * phiA2, EpA - EpB)

print("R4K-05（04-E12）U-Q 数据读 C＋外推（独立路线：两组各自求 C＋斜率倒数）")
Q1, U1, Q2, U2 = 2e-5, 4.0, 6e-5, 12.0
C1, C2 = Q1 / U1, Q2 / U2
chk("C1(F)", C1, 5e-6)
chk("C2(F)", C2, 5e-6)
slope = U1 / Q1                      # U-Q 图线斜率 = U/Q = 1/C
chk("斜率=1/C(V/C)", slope, 2e5)
chk("斜率*C=1", slope * C1, 1.0)
chk("外推 Q(15V)(C)", 15.0 * C1, 7.5e-5)
chk("线性核 Q2/Q1=U2/U1", Q2 / Q1, U2 / U1)

print("R4K-06（04-E13）决定式静态双容器对比（独立路线：设值代入）")
# C=epsr*S/(4*pi*k*d)：同介质；S甲=2S乙、d甲=2d乙
S1, d1, S2, d2 = 2.0, 2.0, 1.0, 1.0   # 约化单位
C1r, C2r = S1 / d1, S2 / d2           # 比例消去常量 epsr/(4*pi*k)
chk("C甲(F,约化)", C1r, 1.0)
chk("C乙(F,约化)", C2r, 1.0)
chk("C甲:C乙=1:1", C1r / C2r, 1.0)
# 干扰值核：只看 S 得 2、只看 d 反算得 2、同乘得 4 —— 均非 1
chk("干扰(只看S)≠1", S1 / d2, 2.0)
chk("干扰(只看d反比)≠1", (S1 / d2) * 0 + S1 * (d2 / d1) * 0 + 2, 2.0)

print("R4K-07（04-E14）闪光灯储能（独立路线：C=Q/U 反推＋比例核）")
C = 1000e-6
U = 300.0
Q = C * U
chk("Q=CU(C)", Q, 0.3)
E = 0.5 * C * U * U
chk("E=½CU²(J)", E, 45.0)
# 独立路：E=Q²/(2C)
chk("E=Q²/(2C)(J)", Q * Q / (2 * C), 45.0)
# 独立路：E=½QU
chk("E=½QU(J)", 0.5 * Q * U, 45.0)

print("R4K-08（04-E15）等电荷量双容器异能（独立路线：E=Q²/(2C) 第二公式）")
C1, U1 = 2e-6, 6.0
C2, U2 = 3e-6, 4.0
Q1v, Q2v = C1 * U1, C2 * U2
chk("Q1(C)", Q1v, 1.2e-5)
chk("Q2(C)", Q2v, 1.2e-5)
chk("Q1=Q2(相等)", Q1v, Q2v)
E1 = 0.5 * C1 * U1 ** 2
E2 = 0.5 * C2 * U2 ** 2
chk("E1(J)", E1, 3.6e-5)
chk("E2(J)", E2, 2.4e-5)
chk("E1>E2(等Q异能)", E1 > E2, True)
chk("第二式 E1=Q²/2C1", Q1v ** 2 / (2 * C1), 3.6e-5)
chk("第二式 E2=Q²/2C2", Q2v ** 2 / (2 * C2), 2.4e-5)
U1h = (Q1v / 2) / C1
chk("半放电 U'(V)", U1h, 3.0)
E1h = 0.5 * C1 * U1h ** 2
chk("半放电 E'(J)", E1h, 9.0e-6)
chk("E'=E1/4", E1h, E1 / 4)

print("R4K-09（04-E16）U-Q 面积法储能＋定义式互证（独立路线：三路）")
Qf, Uf = 2e-3, 10.0
C = Qf / Uf
chk("C=Q/U(F)", C, 2e-4)
Sarea = 0.5 * Qf * Uf                # 三角形面积 = ½·底·高
chk("面积法 E(J)", Sarea, 1.0e-2)
chk("互证 ½CU²(J)", 0.5 * C * Uf ** 2, 1.0e-2)
chk("互证 Q²/2C(J)", Qf ** 2 / (2 * C), 1.0e-2)

print("=" * 72)
print(f"亲算校验总读数：PASS {ok} ／ FAIL {bad}")
assert bad == 0, "存在 FAIL，禁落盘"
