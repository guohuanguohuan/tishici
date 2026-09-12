# 盲解阶段独立复算（阶段一，台账/快照未开）：111~127
import sympy as sp

print("=== 111 正四面体 PQmax=R+r=(√6/3)a=4√6/3 ===")
a = sp.symbols('a', positive=True)
R = a*sp.sqrt(6)/4; r = a*sp.sqrt(6)/12
print("R+r =", sp.simplify(R+r), " a =", sp.solve(sp.Eq(R+r, 4*sp.sqrt(6)/3), a))

print("=== 112 点P到直线AB距离 ===")
A = sp.Matrix([3,3,3]); B = sp.Matrix([0,6,0]); P = sp.Matrix([0,0,6])
v = B - A; w = P - B
print(sp.simplify(w.cross(v).norm()/v.norm()))

print("=== 113 正八面体棱2 内切球直径MN, P表面动点 PM·PN ===")
s = sp.sqrt(2)   # 顶点(±s,0,0)…使棱长=2
f0 = sp.Matrix([s,0,0]); f1 = sp.Matrix([0,s,0]); f2 = sp.Matrix([0,0,s])
n = (f1-f0).cross(f2-f0)
d_face = sp.simplify(abs(f0.dot(n))/n.norm())
print("棱长复核 =", sp.simplify((f0-f1).norm()), " 面心距r =", d_face, " 顶点距 =", s)
print("r² =", sp.simplify(d_face**2), " → PM·PN 范围 [0, %s]" % sp.simplify(s**2 - d_face**2))

print("=== 114 正方体12 → 正四面体棱长上限 ===")
print("a_max = 6·4/√6 =", sp.simplify(24/sp.sqrt(6)), " = 4√6?", sp.simplify(24/sp.sqrt(6)-4*sp.sqrt(6)))

print("=== 115/117 正四面体棱6 内切球 → 正方体棱/外接球面积 ===")
r_in = sp.simplify(6*sp.sqrt(6)/12)
s115 = sp.simplify(r_in*2/sp.sqrt(3))
print("内切球半径 =", r_in, " 正方体棱 =", s115, " 117 外接球表面积 =", sp.simplify(4*sp.pi*(s115*sp.sqrt(3)/2)**2))

print("=== 118 圆锥内切球r=1, 体积最小 → V锥:V球 ===")
h = sp.symbols('h', positive=True)
Rexpr = sp.sqrt(h/(h-2))
Vc = sp.Rational(1,3)*sp.pi*Rexpr**2*h
print("临界 h =", sp.solve(sp.diff(Vc/sp.pi, h), h))
hv = 4; Rv = sp.sqrt(hv/(hv-2))
print("h=4: R =", sp.simplify(Rv), " r复核 =", sp.simplify(Rv*hv/(Rv+sp.sqrt(Rv**2+hv**2))),
      " V锥 =", sp.simplify(Vc.subs(h,hv)), " 比 =", sp.simplify(Vc.subs(h,hv)/(sp.Rational(4,3)*sp.pi)))

print("=== 119 圆锥底4 高8√2 内切球; 球内接正三棱柱侧面积最大 → 体积 ===")
Rb, Hh = 4, 8*sp.sqrt(2)
ll = sp.sqrt(Rb**2 + Hh**2); rs = sp.simplify(Rb*Hh/(Rb+ll))
print("母线 =", ll, " 内切球半径 =", rs)
rho, t, lam = sp.symbols('rho t lam', positive=True)
Lg = 6*sp.sqrt(3)*rho*t - lam*(rho**2 + t**2 - rs**2)
sols = sp.solve([sp.diff(Lg,rho), sp.diff(Lg,t), rho**2+t**2-rs**2], [rho,t,lam], dict=True)
for so in sols:
    rr = sp.simplify(so[rho]); tt = sp.simplify(so[t]); edge = sp.simplify(rr*sp.sqrt(3))
    print("rho =", rr, " t(半高) =", tt, " 底边 =", edge, " 侧面积 =", sp.simplify(6*sp.sqrt(3)*rr*tt),
          " 体积 =", sp.simplify(sp.sqrt(3)/4*edge**2*2*tt))

print("=== 120 圆锥内切球2 表面积最小 → 外接球表面积 ===")
R2 = sp.sqrt(4*h/(h-4))
Sf = sp.simplify(sp.pi*R2**2*h/2)     # S=πR(R+l)=πR·(Rh/2)
print("S(h) =", Sf, " 临界:", sp.solve(sp.diff(Sf/sp.pi, h), h))
hv = 8; Rv = sp.sqrt(4*hv/(hv-4)); lv = sp.sqrt(Rv**2+hv**2)
print("h=8: R =", sp.simplify(Rv), " l =", sp.simplify(lv), " r复核 =", sp.simplify(Rv*hv/(Rv+lv)))
rho_c = sp.simplify((Rv**2+hv**2)/(2*hv))
print("外接球半径 =", rho_c, " 表面积 =", sp.simplify(4*sp.pi*rho_c**2))

print("=== 121 正方体2 BDE⊥A₁BD → 面A₁BD截四面体ABCE外接球 ===")
e = sp.symbols('e', positive=True)
Av = sp.Matrix([0,0,0]); Bv = sp.Matrix([2,0,0]); Dv = sp.Matrix([0,2,0]); A1 = sp.Matrix([0,0,2])
Ev = sp.Matrix([2,2,e])
sol = sp.solve(sp.Eq((Dv-Bv).cross(A1-Bv).dot((Dv-Bv).cross(Ev-Bv)), 0), e)
print("e =", sol)
ev = sol[0]; Ev = sp.Matrix([2,2,ev]); Cv = sp.Matrix([2,2,0])
cx,cy,cz = sp.symbols('cx cy cz'); Om = sp.Matrix([cx,cy,cz])
so = sp.solve([sp.Eq((Om-Av).dot(Om-Av),(Om-Bv).dot(Om-Bv)),
               sp.Eq((Om-Av).dot(Om-Av),(Om-Cv).dot(Om-Cv)),
               sp.Eq((Om-Av).dot(Om-Av),(Om-Ev).dot(Om-Ev))],[cx,cy,cz],dict=True)[0]
Oc = sp.Matrix([so[cx],so[cy],so[cz]]); R2s = sp.simplify(Oc.dot(Oc))
d = sp.simplify(Oc.dot(sp.Matrix([1,1,1]))-2)/sp.sqrt(3)
print("球心 =", Oc.T, " R² =", R2s, " d² =", sp.simplify(d**2), " 截面面积 =", sp.simplify(sp.pi*(R2s-d**2)))

print("=== 122/126 SB⊥面ABC, AB⊥BC, SB=AB=BC=2 ===")
Bs = sp.Matrix([0,0,0]); As = sp.Matrix([2,0,0]); Cs = sp.Matrix([0,2,0]); Ss = sp.Matrix([0,0,2])
Ps = (As+Bs)/2; Qs = (Cs+Bs)/2; Os = sp.Matrix([1,1,1])
n = (Ss-Ps).cross(Qs-Ps); dd = sp.simplify(Os.dot(n)/n.norm())
print("n =", n.T, " d² =", sp.simplify(dd**2), " 截面面积 =", sp.simplify(sp.pi*(3-dd**2)),
      " 截面周长 =", sp.simplify(2*sp.pi*sp.sqrt(3-dd**2)), " 球体积 =", sp.simplify(sp.Rational(4,3)*sp.pi*sp.sqrt(3)**3))

print("=== 123/124 过G截面范围 ===")
for (sa, ab) in [(2,2), (sp.sqrt(2),sp.sqrt(2))]:
    Aq = sp.Matrix([0,0,0]); Bq = sp.Matrix([ab,0,0]); Cq = sp.Matrix([ab,ab,0])
    Oq = sp.Matrix([ab/2, ab/2, sa/2]); R2q = sp.simplify(Oq.dot(Oq)); G = (Aq+Bq+Cq)/3
    OG2 = sp.simplify((Oq-G).dot(Oq-G))
    print("SA=%s: R²=%s OG²=%s → [%s, %s]" % (sa, R2q, OG2, sp.simplify(sp.pi*(R2q-OG2)), sp.simplify(sp.pi*R2q)))

print("=== 125 过C,D,E截面 ===")
Cp = sp.Matrix([0,0,0]); Ap = sp.Matrix([2,0,0]); Bp = sp.Matrix([0,2,0]); Pp = sp.Matrix([2,0,2])
Dp = (Ap+Pp)/2; Ep = (Ap+Bp)/2
cx,cy,cz = sp.symbols('cx cy cz'); Om = sp.Matrix([cx,cy,cz])
so = sp.solve([sp.Eq((Om-Ap).dot(Om-Ap),(Om-Cp).dot(Om-Cp)),
               sp.Eq((Om-Bp).dot(Om-Bp),(Om-Cp).dot(Om-Cp)),
               sp.Eq((Om-Pp).dot(Om-Pp),(Om-Cp).dot(Om-Cp))],[cx,cy,cz],dict=True)[0]
Oc = sp.Matrix([so[cx],so[cy],so[cz]]); R2m = sp.simplify(Oc.dot(Oc))
nn = (Dp-Cp).cross(Ep-Cp); dm = sp.simplify(Oc.dot(nn)/nn.norm())
print("球心 =", Oc.T, " R² =", R2m, " d² =", sp.simplify(dm**2), " 截面面积 =", sp.simplify(sp.pi*(R2m-dm**2)))

print("=== 127 球表100π OP=√10 弦AB=4√5 ===")
Rp = 5; Pv2 = sp.Matrix([0,0,sp.sqrt(10)]); Hv2 = sp.Matrix([sp.sqrt(10)/2,0,5/sp.sqrt(10)])
print("d(球心,AB) =", sp.simplify(sp.sqrt(Rp**2-(2*sp.sqrt(5))**2)))
print("|H| =", sp.simplify(Hv2.norm()), " OH·HP =", sp.simplify(Hv2.dot(Pv2-Hv2)))
u = (Pv2-Hv2)/sp.sqrt(5)
Aa = Hv2 + 2*sp.sqrt(5)*u; Bb = Hv2 - 2*sp.sqrt(5)*u
r1 = sp.sqrt(sp.simplify(Aa[0]**2+Aa[1]**2)); r2v = sp.sqrt(sp.simplify(Bb[0]**2+Bb[1]**2))
hh = sp.simplify(abs(sp.re(Aa[2]-Bb[2])))
print("A =", sp.simplify(Aa.T), " r1 =", sp.simplify(r1), " B =", sp.simplify(Bb.T), " r2 =", sp.simplify(r2v), " h =", hh)
print("圆台体积 =", sp.simplify(sp.pi/3*hh*(r1**2+r1*r2v+r2v**2)))
print("AB复核 =", sp.simplify((Aa-Bb).norm()))
