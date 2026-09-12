# 盲解阶段独立复算（阶段一）：128~150 修订版
import sympy as sp

def cosang(u_, v_):
    return sp.simplify(u_.dot(v_)/(u_.norm()*v_.norm()))

print("=== 128/130 截面面积（平行四边形 |u×v|） ===")
a, t = sp.symbols('a t', positive=True)
w = a/(2*sp.sqrt(2))
A = sp.Matrix([w,w,w]); B = sp.Matrix([w,-w,-w]); C = sp.Matrix([-w,w,-w]); D = sp.Matrix([-w,-w,w])
u = (w-t)/(2*w)
P1 = A+u*(B-A); P2 = A+u*(C-A); P4 = D+u*(C-D)
ar = sp.simplify((P2-P1).cross(P4-P1).norm())
print("area(t) =", sp.factor(ar), " max(t=0) =", sp.simplify(ar.subs(t,0)),
      " a=4 →", sp.simplify(ar.subs([(t,0),(a,4)])), " a=1 →", sp.simplify(ar.subs([(t,0),(a,1)])))

print("=== 134 余弦三倍角 ===")
print("cosθ=7/8 → cos3θ =", sp.simplify(4*sp.Rational(7,8)**3 - 3*sp.Rational(7,8)),
      " 周长² = 128(1−cos3θ) =", sp.simplify(128*(1-sp.Rational(7,128))), " 周长 =", 11)

print("=== 135 四棱锥侧面展开 ===")
Av = sp.Matrix([0,0,0]); Bv = sp.Matrix([2,0,0]); Cv = sp.Matrix([2,2,0]); Dv = sp.Matrix([0,2,0]); Pv = sp.Matrix([1,0,sp.sqrt(3)])
c1 = cosang(Av-Pv, Dv-Pv); c2 = cosang(Dv-Pv, Cv-Pv); c3 = cosang(Cv-Pv, Bv-Pv)
print("cos∠APD, ∠DPC, ∠CPB =", c1, c2, c3)
tot = sp.acos(c1)+sp.acos(c2)+sp.acos(c3)
d2 = sp.simplify(8-8*sp.cos(tot))
print("距离² =", sp.nsimplify(d2), " 距离 =", sp.simplify(sp.sqrt(sp.nsimplify(d2))), " √7+1 =", sp.N(sp.sqrt(7)+1), " 数值 =", sp.N(sp.sqrt(d2)))

print("=== 136 ===")
al = sp.symbols('alpha', positive=True)
print("α =", sp.solve(sp.Eq(40-24*sp.cos(al), 52), al), "→ r = 3α/π =", sp.simplify(3*(2*sp.pi/3)/sp.pi),
      " V =", sp.simplify(sp.Rational(1,3)*sp.pi*4*sp.sqrt(32)))

print("=== 137 ===")
rr = sp.symbols('r', positive=True)
print("半周读法:", sp.solve(sp.Eq(5-4*sp.cos(sp.pi*rr/2), 5), rr), " 全周读法:", sp.solve(sp.Eq(5-4*sp.cos(sp.pi*rr), 5), rr))

print("=== 138 ===")
tt = sp.symbols('t', real=True)
f = sp.sqrt(t**2+1) + sp.sqrt((1-t)**2+1)
tsol = sp.solve(sp.diff(f, tt), tt)
print("t* =", tsol, " minPE+EF =", sp.simplify(f.subs(tt, tsol[0])), " 周长 =", sp.simplify(f.subs(tt, tsol[0])+sp.sqrt(3)))
Ev = sp.Matrix([sp.Rational(1,2),0,0]); Fv = sp.Matrix([1,1,0]); Pz = sp.Matrix([0,0,1]); Az = sp.Matrix([0,0,0])
cx,cy,cz = sp.symbols('cx cy cz'); Om = sp.Matrix([cx,cy,cz])
so = sp.solve([sp.Eq((Om-Az).dot(Om-Az),(Om-Ev).dot(Om-Ev)),
               sp.Eq((Om-Az).dot(Om-Az),(Om-Fv).dot(Om-Fv)),
               sp.Eq((Om-Az).dot(Om-Az),(Om-Pz).dot(Om-Pz))],[cx,cy,cz],dict=True)[0]
Oc = sp.Matrix([so[cx],so[cy],so[cz]]); R2 = sp.simplify(Oc.dot(Oc))
print("球心 =", Oc.T, " R² =", R2, " 表面积 =", sp.simplify(4*sp.pi*R2))

print("=== 139 ===")
x,y,z = sp.symbols('x y z', real=True)
Pv3 = sp.Matrix([x,y,z]); Bv3 = sp.Matrix([6,0,0]); Ev3 = sp.Matrix([2,0,0])
print("轨迹:", sp.expand((Pv3-Bv3).dot(Pv3-Bv3) - 3*(Pv3-Ev3).dot(Pv3-Ev3)), "= 0")
B1 = sp.Matrix([6,0,3]); C3 = sp.Matrix([6,3,0]); F3 = sp.Matrix([3,3,3]); M0 = sp.Matrix([3,sp.Rational(3,2),0])
n = (C3-B1).cross(F3-B1); area3 = sp.simplify(n.norm()/2)
dc = sp.simplify((M0-B1).dot(n)/n.norm())
print("S(△B₁CF) =", area3, " 带符号心距 =", dc, " min d =", sp.simplify(abs(dc)-sp.sqrt(3)),
      " V_min =", sp.simplify(sp.Rational(1,3)*area3*(abs(dc)-sp.sqrt(3))))
for Pp in [sp.Matrix([2,2,2]), sp.Matrix([sp.sqrt(12),0,0]), sp.Matrix([0,0,sp.sqrt(12)])]:
    M = (Pp+C3)/2
    print("  P =", Pp.T, "|P|²=", sp.simplify(Pp.dot(Pp)), " V =", sp.simplify(sp.Rational(1,6)*sp.Abs((B1-M).cross(C3-M).dot(F3-M))))

print("=== 140 ===")
Pv4 = sp.Matrix([x,y,z]); A4 = sp.Matrix([0,0,0]); B14 = sp.Matrix([1,0,1]); A14 = sp.Matrix([0,0,1])
zsub = sp.solve(sp.Eq((Pv4-A14).dot(B14-A4), 0), z)[0]
Pv4b = sp.Matrix([x,y,zsub]); PA = A4-Pv4b; PB = B14-Pv4b
print("约束面:", zsub, " |PA|²−|PB|² =", sp.simplify(PA.dot(PA)-PB.dot(PB)), " cos∠APB₁ =", sp.simplify(PA.dot(PB)/PA.dot(PA)))
# cos∠ADB₁
D4 = sp.Matrix([0,1,0]); print("cos∠ADB₁ =", cosang(A4-D4, B14-D4))
g = sp.simplify(sp.expand((PA.dot(PB))**2*3 - PA.dot(PA)*PB.dot(PB)))
print("轨迹方程(×3):", sp.factor(g))

print("=== 141 圆柱∩垂面=圆（数值核验） ===")
q = sp.symbols('q', real=True)
B141 = sp.Matrix([1,1,0]); Ad = sp.Matrix([-1,1,0]); Dd = sp.Matrix([-1,-1,0]); ad = Dd-Ad
Pp1 = B141 + sp.Matrix([sp.cos(q)*sp.sqrt(2)/2*0, 0, 0])
# 直接构造：AD 方向 ŷ；平面 ⊥AD 即 y=const；圆柱 x²+z²=R²
print("平面 y=y₀ 与圆柱 x²+z²=ρ² 之交线：圆，半径 ρ（数值由面积定值给出）")

print("=== 143 ===")
Ax = sp.Matrix([-sp.sqrt(3),0,0]); Cx = sp.Matrix([sp.sqrt(3),0,0]); Bx = sp.Matrix([0,-1,0]); Dx = sp.Matrix([0,1,0])
Px = sp.Matrix([-sp.sqrt(3)/2, sp.Rational(1,2), 1])
print("PA =", sp.simplify((Px-Ax).norm()), " PD =", sp.simplify((Px-Dx).norm()), " AD =", sp.simplify((Dx-Ax).norm()),
      " PA·PD =", sp.simplify((Ax-Px).dot(Dx-Px)), " 面PAD⊥底? 法向 y分量:", sp.simplify(((Dx-Ax).cross(Px-Ax))[2]))
T = Px + sp.Rational(1,3)*(Cx-Px)
print("T =", sp.simplify(T.T), " |BT| =", sp.simplify((T-Bx).norm()), " T在PC上:", sp.simplify((T-Px).cross(Cx-Px).norm()))

print("=== 144 ===")
h = sp.symbols('h', positive=True); mm = sp.symbols('m', positive=True)
Pv5 = sp.Matrix([x,y,0]); A5 = sp.Matrix([0,0,0]); B5 = sp.Matrix([h,0,h])
expr = sp.expand(Pv5.dot(Pv5) - mm**2*(Pv5-B5).dot(Pv5-B5))
print("方程:", expr)
print("m=1 →", sp.simplify(expr.subs(mm,1)), " → x =", sp.solve(sp.Eq(expr.subs(mm,1),0), x))
cf = expr.coeff(x**2); R2e = sp.simplify((expr.coeff(x)**2 + expr.coeff(y)**2)/(4*cf) - expr.subs([(x,0),(y,0)])/cf)
print("半径² =", sp.factor(R2e), " >0 的 m 范围(h=1):", sp.solve_univariate_inequality(R2e.subs(h,1) > 0, mm, relational=False))

print("=== 145 ===")
av = sp.sqrt(sp.Rational(1,2))
A6 = sp.Matrix([av,0,0]); B6 = sp.Matrix([0,av,0]); M6 = (A6+B6)/2
abd = (B6-A6); abd = abd/abd.norm(); me = M6/M6.norm(); perp = abd.cross(me)
Cv6 = M6 + me*sp.sqrt(2)/2 + perp/2; Dv6 = M6 - me*sp.sqrt(2)/2 - perp/2; E6 = (Cv6+Dv6)/2
print("棱长核验 AB,CD,AC,AD,BC,BD =", [sp.simplify(q) for q in [(B6-A6).norm(),(Dv6-Cv6).norm(),(Cv6-A6).norm(),(Dv6-A6).norm(),(Cv6-B6).norm(),(Dv6-B6).norm()]])
print("|OM| =", sp.simplify(M6.norm()), " |ME| =", sp.simplify((E6-M6).norm()), " |OE| =", sp.simplify(E6.norm()), " 上界(1+√2)/2 =", sp.N((1+sp.sqrt(2))/2))

print("=== 146 ===")
tv, uv = sp.symbols('t v', real=True)
f = (tv-2)**2 + (tv-uv)**2 + tv**2
so2 = sp.solve([sp.diff(f,tv), sp.diff(f,uv)], [tv,uv], dict=True)[0]
print("t,v =", so2, " d =", sp.simplify(sp.sqrt(f.subs(so2))))

print("=== 147 ===")
p = sp.symbols('p', real=True)
A1_ = sp.Matrix([0,0,3]); C_ = sp.Matrix([1,2,0]); P_ = sp.Matrix([0,2,p])
cr = (P_-A1_).cross(C_-A1_); ar2 = sp.expand(cr.dot(cr))
print("4·面积² =", ar2, " p* =", sp.solve(sp.diff(ar2,p), p), " DP/PD₁ =", sp.simplify(sp.Rational(3,5)/(3-sp.Rational(3,5))),
      " min面积 =", sp.simplify(sp.sqrt(ar2.subs(p,sp.Rational(3,5)))/2))

print("=== 148 ===")
xx = sp.symbols('x', real=True)
D148 = sp.Matrix([xx,0,2]); F148 = sp.Matrix([0,2,1]); E148 = sp.Matrix([1,1,0]); Bf = sp.Matrix([0,0,0])
print("(1) BF·DE =", sp.simplify((F148-Bf).dot(E148-D148)))
n1 = (E148-F148).cross(D148-F148); n2 = sp.Matrix([1,0,0])
sin2 = sp.simplify(1 - sp.expand(n1.dot(n2))**2/sp.expand((n1.dot(n1))*(n2.dot(n2))))
print("sin² =", sin2, " 临界:", sp.solve(sp.diff(sin2,xx),xx), " x=1/2 → sin =", sp.simplify(sp.sqrt(sin2.subs(xx,sp.Rational(1,2)))))

print("=== 149 ===")
A149 = sp.Matrix([0,0,0]); B149 = sp.Matrix([2,0,0]); C149 = sp.Matrix([0,2,0]); A1149 = sp.Matrix([1,1,sp.sqrt(6)])
print("A₁A,A₁B,A₁C =", [sp.simplify(q) for q in [(A1149-A149).norm(),(A1149-B149).norm(),(A1149-C149).norm()]])
E149 = (B149+C149)/2; C1149 = C149+(A1149-A149); F149 = A1149 + sp.symbols('s')*(C1149-A1149)
print("AB·EF =", sp.simplify((B149-A149).dot(F149-E149)))
rr = sp.symbols('r', real=True); P149 = A149 + rr*(A1149-A149)
PE2 = sp.expand((P149-E149).dot(P149-E149))
rsol = sp.solve(sp.diff(PE2,rr),rr)[0]
print("r* =", rsol, " 高 =", sp.simplify(P149[2].subs(rr,rsol)), " V(P-ABC) =", sp.simplify(sp.Rational(1,3)*2*P149[2].subs(rr,rsol)),
      " min PE =", sp.simplify(sp.sqrt(PE2.subs(rr,rsol))))

print("=== 150 ===")
u2 = sp.symbols('u', real=True)
A150 = sp.Matrix([0,0,0]); B150 = sp.Matrix([2,0,0]); C150 = sp.Matrix([1,sp.sqrt(3),0]); D150 = sp.Matrix([1,sp.sqrt(3)/3,2*sp.sqrt(6)/3])
E150 = (A150+B150)/2; F150 = A150 + sp.Rational(1,3)*(D150-A150); P150 = C150 + u2*(D150-C150)
EF = F150-E150; BP = P150-B150
c2s = sp.simplify(sp.expand(EF.dot(BP))**2/sp.expand(EF.dot(EF)*BP.dot(BP)))
print("cos²(u) =", c2s, " 临界:", sp.solve(sp.diff(c2s,u2),u2), " 值:", sp.N(c2s.subs(u2,0)), sp.N(c2s.subs(u2,sp.Rational(7,8))), sp.N(c2s.subs(u2,1)))
print("sin² =", sp.simplify(1-c2s.subs(u2,sp.Rational(7,8))), " → sin =", sp.simplify(sp.sqrt(1-c2s.subs(u2,sp.Rational(7,8)))))
