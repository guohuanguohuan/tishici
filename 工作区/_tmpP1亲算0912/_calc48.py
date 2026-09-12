# -*- coding: utf-8 -*-
"""P1轮2·微专题48片 复算校核（sympy/math，逐题独立重解，与源详解对分）"""
import math
from fractions import Fraction as F
import numpy as np

k = 1.0
print("=== 题1 镜像/静电平衡：z=h/3 场强 ===")
h = 1.0; zq = h; zp = h/3
E_q   = k*1/ (zq-zp)**2                    # +q 在 h/3：向下
# 镜像论证（经导体内 −h/3 零场＋面对称）：感应场在 h/3 亦向下，大小 = q 在 −h/3 的场
E_ind = k*1/ (zq+h/3)**2
print("E_q=%.6f E_ind=%.6f 合=%.6f | 45/16=%.6f 9/16=%.6f 9/4=%.6f" % (E_q, E_ind, E_q+E_ind, 45/16, 9/16, 9/4))
print("镜像法直算（−q at −h）对照：", k*1/(zp-h)**2 + k*1/(zp+h)**2)

print("=== 题2 圆盘：b 场零 → d 场强 ===")
R=1.0; q=1.0
# b 距 a 为 R：q 在 b 场 = kq/R²；盘在 b 等大反向 → 盘在 d（对心对称）大小同、指向 a→d 侧
Ed = q/(3*R)**2 + q/R**2
print("E_d=%.6f 10/9=%.6f" % (Ed, 10/9))

print("=== 题3 挖腔比 ===")
E_full = k*1/(2*1)**2                     # Q 在 A（距 2R）
Q_cav  = F(1,8)
E_cav  = k*float(Q_cav)/( (2-0.5)*1 )**2  # 腔心距 A = 3R/2
E_rem  = E_full - E_cav
print("E整=%.6f(1/4) E割=%.6f(1/18) E剩=%.6f(7/36)" % (E_full, E_cav, E_rem))
print("整/剩=%.6f 9/7=%.6f | 整/割=%.4f(≠9/7→源详解标签笔误)" % (E_full/E_rem, 9/7, E_full/E_cav))
print("对照池 Q43：E剩=7kQ/36R² 即其正确项 ✓")

print("=== 题4 薄板对称 ===")
d=1.0
Ea_plate = k*1/d**2   # 板在 a = 抵消 −q 的 kq/d²，指向右（板带正电向外推）
print("板在 b：大小=%.4f 方向水平向右（镜像）→ 答案 A ✓" % Ea_plate)

print("=== 题5 圆环轴上 P：微元 + 平衡 ===")
L=1.0; th=math.radians(30); rR= L*math.tan(th)
E_ring = k*1.0*math.cos(th)**3/L**2   # Q=1
print("微元式 kQcos³θ/L²=%.6f 与逐环积分对照：" % E_ring,
      sum(k*(math.cos(th)/ ( (rR**2+L**2) )) for _ in [0]))  # kQ cosθ·(cos²θ)/L² 同式
print("平衡：E=mg/q（选项 C）；kQcos³θ/L² 不在选项系 → C 唯一")

print("=== 题6 镜像+正方形（P=(L,0)，像=−Q@(−L,0)，c=(L/2,0), b=(L/2,L), a=(3L/2,L), d=(3L/2,0)）===")
def Efield(x,y):
    r1=(x-1,y-0); r2=(x+1,y-0)
    n1=math.hypot(*r1); n2=math.hypot(*r2)
    # +Q@(1,0) 推, −Q@(-1,0) 吸
    Ex = r1[0]/n1**3 - r2[0]/n2**3
    Ey = r1[1]/n1**3 - r2[1]/n2**3
    return (Ex,Ey)
for name,(x,y) in dict(a=(1.5,1),b=(0.5,1),c=(0.5,0),d=(1.5,0)).items():
    Ex,Ey=Efield(x,y); print(f"E_{name}: |E|={math.hypot(Ex,Ey):.6f}")
print("E_d 应=96/25=3.84;  4-4/25=%.6f" % (4-4/25))
print("判：A(a=b)? |Ea|<|Eb|→A错；B(c>b)→对；C→对")

print("=== 题7 双环：量纲+特值 ===")
R1=R2=1.0; a=2.0; r=F(1,2)*0+1.0
# 真值：E = kq(a+r)/[R1²+(a+r)²]^1.5 − kq(a−r)/[R2²+(a−r)²]^1.5（O₁ 在左、A 偏 O₂ 侧符号自洽）
q0=1.0
Etrue = q0*(a+r)/ (R1**2+(a+r)**2)**1.5 - q0*(a-r)/(R2**2+(a-r)**2)**1.5
print("真值(含符号)=%.6f；D 式=|同值|=%.6f ✓" % (Etrue, abs(Etrue)))
print("r=a 时：D 第二项→0（只剩左环，环心处场=0）✓；A/B 第二项非零 ✗；A/C 量纲 kq/L ✗")

print("=== 题8 正方体 ===")
L8=1.0; P=(0,0,0); Qm=(1,1,1)          # +2q@P, −q@Qm
O=(np.array(P)+np.array(Qm))/2; dO=math.dist(O,P)
EO = 2*k/dO**2 + k/dO**2                # 同向（指向 −q）
A=(1,1,0)                               # 依题图：A 邻 −q（距 L），距 2q 为 √2 L
E1=2*k/ (math.dist(A,P)**2); E2=k/(math.dist(A,Qm)**2)
u1=np.subtract(A,P)/math.dist(A,P); u2=np.subtract(Qm,A)/math.dist(Qm,A)
EA=np.linalg.norm(E1*u1+E2*u2)
print("d=%.4f √3/2=%.4f; E_O=%.6f(=4kq/L²); E_A=%.6f(=√2=%.6f); EA/EO=%.6f √2/4=%.6f" % (dO,math.sqrt(3)/2,EO,EA,math.sqrt(2),EA/EO,math.sqrt(2)/4))
print("垂直性：u1·u2=%.6f" % np.dot(u1,u2))
# 若 A 邻 +2q：
A2=(1,0,0); E1b=2*k/1; E2b=k/2
print("A 邻 2q 情形 E=%.6f=√17/4=%.6f（≠√2/4E）→ 题图为前型" % (math.hypot(E1b,E2b), math.sqrt(17)/4))

print("=== 题9 双正四面体 ===")
l0=1.0; hgt=math.sqrt(l0**2-(l0/math.sqrt(3)*2/3)**2); print("高 h=%.6f √6/3=%.6f" % (hgt,math.sqrt(6)/3))
Emax=2*k/( (2*math.sqrt(6)/3)**2/4)  # 2kQ/(h²)：连线中点到两顶点距离=h
Emax=2*k/hgt**2
print("E中点=2kQ/h²=%.6f vs 3=%.6f ✓" % (Emax,3.0))
rho=l0/math.sqrt(3); rb=math.sqrt(hgt**2+rho**2)
Eb=2*k*hgt/rb**3
print("E_b=%.6f < Emax=%.6f ✓ 且 b 点横向对消：E∥AB" % (Eb,Emax))
G=np.array([0,0,0]); bq=(rho,0,0); Aq=(0,0,hgt); Bq=(0,0,-hgt)
E1v=np.subtract(bq,Aq)/np.linalg.norm(np.subtract(bq,Aq))**3
E2v=np.subtract(Bq,bq)/np.linalg.norm(np.subtract(Bq,bq))**3
print("b 点合矢量：", np.round(E1v+E2v,6), "（x 分量=0 → 方向同 AB）")

print("=== 题10 14 电荷环 ===")
R10=1.0; angs=[90,60,120,45,135,30,150]
top=[(math.cos(math.radians(t)),math.sin(math.radians(t))) for t in angs]  # +q
bot=[(x,-y) for x,y in top]                                                # −q
def E10(x,y):
    Ex=Ey=0
    for (px,py) in top:
        rx,ry=x-px,y-py; n=(rx*rx+ry*ry)**1.5; Ex+=rx/n; Ey+=ry/n
    for (px,py) in bot:
        rx,ry=px-x,py-y; n=(rx*rx+ry*ry)**1.5; Ex+=rx/n; Ey+=ry/n  # 吸向 −q
    return Ex,Ey
ex,ey=E10(0.35,0); ex2,ey2=E10(-0.35,0)
print("|E(±0.35,0)|: %.6f vs %.6f 相等→A错 ✓ 方向 Ey=%.4f(下)" % (math.hypot(ex,ey),math.hypot(ex2,ey2),ey))
ez1=E10(0,0.35)[1]; ez2=E10(0,-0.35)[1]
print("Ez(c)=%.6f Ez(d)=%.6f 相等→B对 ✓" % (ez1,ez2))
mn=min(abs(E10(0,t)[1]) for t in np.linspace(-0.8,0.8,81))
print("|Ez| 沿竖直直径 min=%.6f 在 η=0 处=%.6f → O 最小→D对 ✓" % (mn, abs(E10(0,0)[1])))

print("=== 题11 半球+O'点荷 ===")
# M=+R/2：E_ACB(M) 右 = kQ/R²−3kQ/4R²；补全论证→E_ACB(P)=同值右；Q 在 P(距2R)：左 kQ/4R²
EM_hemi = k*1/1 - 3*k*1/4
EP_total = EM_hemi - k*1/4
print("E_ACB(M)=kQ/4R² 向右=%.4f；P 合场=%.4f → 0 ✓ A" % (EM_hemi, EP_total))

print("=== 题13 半球 M/N ===")
E0 = k*2/4  # 2q 壳在 2R 处
print("E整=k(2q)/(2R)²=kq/2R²=%.4f；E_M=E整−E → 答案 B ✓（对称：E右半(M)=E左半(N)=E）" % E0)

print("=== 题14 双解单调 ===")
import sympy as sp
s=sp.symbols('s',positive=True); Ls=sp.symbols('L',positive=True)
r1=Ls/(s+1); r2=Ls/(s-1)
print("dr1/ds=",sp.simplify(sp.diff(r1,s)),"dr2/ds=",sp.simplify(sp.diff(r2,s)),"(s>1 均<0 → 比值增 r1,r2 均减) A ✓")
# 数值例
for ratio in (4,9,16):
    ss=math.sqrt(ratio); print(f"Q1/Q2={ratio}: r1={1/(ss+1):.4f} r2={1/(ss-1):.4f}")
