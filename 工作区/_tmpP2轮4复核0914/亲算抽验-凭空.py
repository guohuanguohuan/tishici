# 丙臂亲算抽验 4 题（凭空批A/B）·独立路线真算·0914
# 路线均≠命制件主详解：R4K-01 比例外推＋线性核；R4K-07 反推 C＋½QU 均值电压；R4L-05 首末全区间直除；R4L-09 ΔEp=qΔφ 直算取反
from fractions import Fraction as F

def chk(label, got, want, tol=1e-9):
    ok = abs(got - want) <= tol * max(1.0, abs(want))
    print(f"  {'PASS' if ok else 'FAIL'}  {label}: {got}")
    return ok

ok = 0
print("R4K-01（独立路线：同点线性核 E_p2·q1＝E_p1·q2 ＋ 比例外推 E_p3＝E_p1·(q3/q1)）")
q1, ep1, q2, ep2, q3 = F(2,10**9), F(-16,10**9), F(5,10**9), F(-40,10**9), F(-1,10**9)
ok += chk("线性核 ep2*q1−ep1*q2＝0", float(ep2*q1 - ep1*q2), 0.0)
phi = ep1/q1
ok += chk("φ_M＝E_p1/q1 (V)", float(phi), -8.0)
ep3 = ep1*(q3/q1)
ok += chk("E_p3 比例外推 (J)", float(ep3), 8e-9)
ok += chk("E_p3 定义式交叉 φ·q3 (J)", float(phi*q3), 8e-9)

print("R4K-07（独立路线：由(1)问 Q 反推 C 再以充电平均电压 ½U 计能 E＝Q·(U/2)）")
Q, U = F(3,10), F(300)
C = Q/U
ok += chk("反推 C＝Q/U (F)", float(C), 1e-3)
E = Q*(U/2)
ok += chk("E＝Q·U/2 (J)", float(E), 45.0)
ok += chk("第三式 Q²/(2C) 交叉 (J)", float(Q*Q/(2*C)), 45.0)

print("R4L-05（独立路线：首末全区间直除 E＝(φ0−φ10)/0.10 ＋ 线性式 φ(x)＝50−Ex）")
phi0, phi10 = F(50), F(10)
E = (phi0-phi10)/F(1,10)
ok += chk("E 首末全区间 (V/m)", float(E), 400.0)
ok += chk("φ(0.10) 线性式 (V)", float(phi0 - E*F(1,10)), 10.0)
e = F(16,10**20)
ok += chk("E_p＝(−e)·φ (J)", float(-e*10), -1.6e-18)

print("R4L-09（独立路线：ΔE_p＝q(φ_N−φ_M) 直算 → W＝−ΔE_p → E_kN＝E_kM−ΔE_p）")
q, phiM, phiN, EkM = F(-3,10**9), F(20), F(-10), F(24,10**8)
dEp = q*(phiN - phiM)
ok += chk("ΔE_p (J)", float(dEp), 9e-8)
W = -dEp
ok += chk("W＝−ΔE_p (J)", float(W), -9e-8)
ok += chk("U_MN＝φ_M−φ_N (V)", float(phiM - phiN), 30.0)
EkN = EkM + W
ok += chk("E_kN (J)", float(EkN), 1.5e-7)

print("=" * 60)
print(f"丙臂亲算抽验读数：{ok}/14 PASS")
assert ok == 14, "存在 FAIL"
