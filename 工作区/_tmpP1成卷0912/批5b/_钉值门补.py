from sympy import *
k, Q, l0, r, Rr, x, Qr = symbols('k Q l_0 r R_r x Q_r', positive=True)
print("=== 补1：48 讲题9 中垂面场强单调性（正解式）===")
h = sqrt(6)/3*l0                                   # 正四面体的高＝半间距
Eb = 2*k*Q*h/(h**2 + r**2)**Rational(3,2)          # 中垂面上距心 r 处（两荷场沿轴分量叠加）
print(" E(r) =", simplify(Eb))
print(" E(0) =", simplify(Eb.subs(r,0)), "＝3kQ/l0^2 →", simplify(Eb.subs(r,0)-3*k*Q/l0**2)==0)
rb = l0/sqrt(3)                                    # b、c、d 到面心距离＝等边三角形外接圆半径
print(" E(b) =", simplify(Eb.subs(r,rb)), "≈", N(simplify(Eb.subs(r,rb))/(k*Q/l0**2),5), "·kQ/l0^2 < E(0)=3 ✓")
dd = diff(Eb, r)
print(" dE/dr =", factor(dd), " 在 r>0 恒负 →", bool(dd.subs(r, l0).is_negative))
print("\n=== 补2：47 讲题1 第一空 F < kQq/d^2 的符号证 ===")
E_ring = k*Qr*x/(x**2 + Rr**2)**Rational(3,2)      # 环轴线场强（x＝轴距）
diff_  = simplify(k*Qr/x**2 - E_ring)
print(" kQ/x^2 - E_环 =", together(diff_))
num = numer(together(diff_)); den = denom(together(diff_))
print(" 分子 =", expand(num), " ；分子正？",
      [bool((num.subs({x:v, Rr:w, Qr:1, k:1}) > 0)) for v, w in ((1,1),(2,0.5),(0.3,3))],
      "（等价于 x^3 < (x^2+R^2)^{3/2}）")
print(" 环半径→0 极限（退化点荷）:", limit(E_ring, Rr, 0), "＝kQ/x^2 → 第一空取「<」成立")
