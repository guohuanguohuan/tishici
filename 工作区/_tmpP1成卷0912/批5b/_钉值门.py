# 批5b 钉值门：拓展册抽验（48 讲 3 题）＋测评卷抽验（Q28／47题1／冲4），sympy 实算
from sympy import *

k, q, Q, h, R, L, l0, g, m, E, d = symbols('k q Q h R L l_0 g m E d', positive=True)
print("=== A 拓展册·拓36（48 讲题1·无穷大导体平面感应，答案 B）===")
# 镜像法精确核：感应电荷面 ≡ 像电荷 -q 位于 z=-h；求 z=+h/3 处合场强
z0 = h/3
E_q   = k*q/(h - z0)**2                 # 源电荷 q 在 z=h，场点 z=h/3 → 方向 -z（向下）
E_ind = k*q/(z0 + h)**2                 # 像电荷 -q 在 z=-h → 场点在其上方，方向 -z（向下）
Etot  = simplify(E_q + E_ind)
print(" q 单独贡献        E_q  =", E_q,   "=", nsimplify(E_q/(k*q/h**2)), "*kq/h^2")
print(" 感应（像电荷）贡献 E_ind=", E_ind, "=", nsimplify(E_ind/(k*q/h**2)), "*kq/h^2")
print(" 合场强            E    =", Etot, "；源件答案 B = 45kq/16h^2 →",
      "一致" if simplify(Etot - Rational(45,16)*k*q/h**2)==0 else "不一致")
# 源件「远端忽略」近似链复算（E1=E2=9kq/16h^2；E3=9kq/4h^2）
E1 = k*q/(Rational(4,3)*h)**2; E3 = k*q/(Rational(2,3)*h)**2
print(" 源链：E1 =", E1, " E3 =", E3, " E1+E3 =", simplify(E1+E3), "→ 与镜像法同值 =",
      simplify(E1+E3-Etot)==0)

print("\n=== B 拓展册·拓34（48 讲题9·双正四面体，◐删原B→印面 B＝原C）===")
hm = sqrt(l0**2 - (Rational(2,3)*sqrt(3)/2*l0)**2)          # 正四面体的高
print(" 高 h =", simplify(hm), "（源件 √6/3·l0 →", simplify(hm - sqrt(6)/3*l0)==0, "）")
Emax = 2*k*Q/hm**2                                          # 中点两侧荷场同向叠加
print(" Emax = 2kQ/h^2 =", simplify(Emax), "；源件选项 C = 3kQ/l0^2 →",
      "一致" if simplify(Emax - 3*k*Q/l0**2)==0 else "不一致")
print(" 选项 D = 3kQ/(2l0^2) → 排除：", simplify(Emax - Rational(3,2)*k*Q/l0**2)!=0)
# 中垂面上 b 点（离轴 r）场强随 r 单调减 → 中点最大（数值抽样）
r = symbols('r', positive=True)
Eb = 2*k*Q*(hm**2/(hm**2+r**2))**Rational(3,2)
print(" 中垂面上距心 r 处 E(r) =", simplify(Eb), "；dE/dr 在 r>0 为负 →",
      bool(diff(Eb, r).subs({r: L}).is_negative if L.is_positive else False))

print("\n=== C 拓展册·拓32（48 讲题11·半球壳＋轴上点荷，答案 A＝0）===")
# O 为原点；P=-R/2，M=+R/2，O'=+3R/2；Q 在 O'
EQ_at_M   = k*Q/R**2                       # Q 在 M（左方 R）产生的场，方向 -x（向左）
E_tot_M   = Rational(3,4)*k*Q/R**2         # 题给 M 合场强，向左
E_hemi_M  = simplify(EQ_at_M - E_tot_M)    # 半球壳在 M 的场＝向右
print(" 半球壳在 M 的场 =", E_hemi_M, "（向右）")
E_hemi_P  = E_hemi_M                       # 补全球壳内部合场为零 ⇒ 半球壳在 P 与在 M 等值同向（向右）
EQ_at_P   = k*Q/(2*R)**2                   # Q 在 P（左方 2R）产生的场，方向 -x（向左）
E_tot_P   = simplify(E_hemi_P - EQ_at_P)
print(" P 点合场强 =", E_tot_P, "→ 源件答案 A（0）", "一致" if E_tot_P==0 else "不一致")

print("\n=== D 测评卷·题10（讲和练 Q28，答案 CD）===")
Lp = symbols("L'", positive=True); AO = symbols('AO', positive=True)
# 相似三角形：mg/AO = F/AB ⇒ F = mg·AB/AO；F = k·QA·QB/AB^2 ⇒ AB^3 = k·QA·QB·AO/mg
AB1 = solve(Eq(m*g/AO, k*2*q*4*q/L**3 - 0), L)              # 占位不用
f = lambda QA, QB: (QA*QB)**Rational(1,3)
print(" 接触前 QA*QB =", 2*4, "q^2；接触后各 3q →", 3*3, "q^2")
print(" L'/L =", simplify(f(3,3)/f(2,4)), "=", N(f(3,3)/f(2,4), 6), "→ 距离增大（D 正确）")
print(" F'/F =", simplify((f(3,3)**-2*9)/(f(2,4)**-2*8)), "→ 库仑力增大（C 正确）")
print(" T = mg·OB/AO（与电荷量无关）→ 拉力大小不变；源件以「方向改变」判 B 错误（口径照源）")

print("\n=== E 测评卷·题13（47 讲题1 双空，答案 < ；kg·m^3·s^-4·A^-2）===")
x, Rr, Qr, qr = symbols('x R_r Q_r q_r', positive=True)
Eax = simplify(k*Qr*x/(x**2 + Rr**2)**Rational(3,2))        # 均匀带电圆环轴线场强
print(" 环轴线场强 E =", Eax)
print(" E < kQ/x^2 ? →", simplify(k*Qr/x**2 - Eax) > 0, "（差值 =", factor(simplify(k*Qr/x**2 - Eax)), "）")
kg_, m_, s_, A_ = symbols('kg m s A', positive=True)
kunit = simplify((kg_*m_*s_**-2) * m_**2 / (A_*s_)**2)      # N·m^2/C^2 → 基本单位
print(" k 单位＝N·m^2/C^2 →", kunit, "＝kg·m^3·s^-4·A^-2 →",
      kunit == kg_*m_**3*s_**-4*A_**-2)

print("\n=== F 测评卷·题19（冲刺卷 冲4·球壳双层割补，答案 |3kq/8R^2 - 2E|）===")
Qfull = q + q/2                                             # 补全后完整球壳总电荷
E_full = simplify(k*Qfull/(2*R)**2)                         # 球外 2R 处等效点荷
print(" 完整球壳总电荷 =", Qfull, "；在 M/N（距心 2R）处场强 =", E_full, "＝3kq/8R^2 →",
      simplify(E_full - Rational(3,8)*k*q/R**2)==0)
# 补片记账：AB 面实际 -q/2，补成 +q/2 ⇒ 修正片 -q（＝1/3 面 +q/2 的两倍且异号）
print(" 修正片电荷 = -q/2 - (+q/2) =", simplify(-q/2 - q/2), "＝ 1/3 面 A1B1(+q/2) 的 -2 倍")
print(" ⇒ 修正片在 N 的场强大小 = 2E（对称位），方向与 3kq/8R^2 相反")
EN = Abs(Rational(3,8)*k*q/R**2 - 2*E)
print(" N 点合场强 =", EN, "→ 与选项 C 同式 =", str(EN)==str(Abs(Rational(3,8)*k*q/R**2-2*E)))
