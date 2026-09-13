import sympy as sp

x, y, k, m, p = sp.symbols('x y k m p', real=True)
print("=== 17-04 (multiply eq by 2) ===")
e = sp.expand(2*(x**2 + (x+1)**2/2 - 1))
A, B, C = e.coeff(x, 2), e.coeff(x, 1), e.coeff(x, 0)
print(" eq:", A, "x^2 +", B, "x +", C, " Δ =", sp.simplify(B**2-4*A*C))

print("=== 17-10 |AB| = 4*sqrt(5)(1+m^2)/|m^2-4|, min over m^2<4 ===")
Y = sp.symbols('Y')
q = sp.expand((m*Y+5)**2 - 4*Y**2 - 20)
a, b, c = q.coeff(Y, 2), q.coeff(Y, 1), q.coeff(Y, 0)
L = sp.simplify(sp.sqrt(1+m**2)*sp.sqrt(sp.simplify(b**2-4*a*c))/sp.Abs(a))
print(" L(m) simplified:", sp.simplify(L))
for val in [0, sp.Rational(1,2), 1, sp.Rational(3,2)]:
    print("   m=%s -> |AB| = %s" % (val, sp.simplify(L.subs(m, val))))
uu = sp.symbols('u', positive=True)
f = 4*sp.sqrt(5)*(1+uu)/(4-uu)
print(" f(u) on [0,4): f(0)=", sp.simplify(f.subs(uu,0)), " f(1)=", sp.simplify(f.subs(uu,1)),
      " f(3.9)=", sp.simplify(f.subs(uu, sp.Rational(39,10))))
g = 4*sp.sqrt(5)*(1+uu)/(uu-4)
print(" cross-branch g(u) for u>4: g(5)=", sp.simplify(g.subs(uu,5)), " g(9)=", sp.simplify(g.subs(uu,9)),
      " g(100)=", sp.simplify(g.subs(uu,100)))
print(" numeric min of f over grid:", min([float(f.subs(uu, i/100)) for i in range(0, 400)]))
print(" numeric min of g over grid:", min([float(g.subs(uu, 4.001 + i/10)) for i in range(0, 2000)]))

print("=== 拓17-18: right branch two distinct points ===")
e18 = sp.expand(x**2 - (k*x-1)**2 - 1)
A18, B18, C18 = e18.coeff(x, 2), e18.coeff(x, 1), e18.coeff(x, 0)
rts = sp.solve(e18, x)
for kv in [sp.Rational(9,10), 1, sp.Rational(11,10), sp.sqrt(2)-sp.Rational(1,100), sp.sqrt(2), sp.sqrt(2)+sp.Rational(1,10), 2]:
    sub = {k: kv}
    ev = [sp.N(r.subs(sub)) for r in rts]
    dd = sp.N((B18**2-4*A18*C18).subs(sub))
    print("   k=%.4f  Δ=%.4f  roots=%s" % (float(kv), dd, ev))

print("=== 拓17-19: 2x=sqrt(4+y^2) vs y=m(x+1) ===")
e19 = sp.expand(4*x**2 - (m*(x+1))**2 - 4)
r19 = sp.solve(e19, x)
for mv in [0, sp.Rational(3,2), 2, sp.Rational(5,2), -sp.Rational(3,2), 3]:
    roots = [sp.N(r.subs(m, mv)) for r in r19]
    pos = [r for r in roots if r > 1]
    print("   m=%s roots=%s -> right-branch pt? %s" % (mv, roots, bool(pos)))

print("=== 拓17-10: three lines through (0,p) ===")
pv = 2  # concrete p
X, Yy = sp.symbols('X Yy')
for desc, eqs in [("x=0", [sp.Eq(X, 0), sp.Eq(Yy**2, 2*pv*X)]),
                  ("y=p", [sp.Eq(Yy, pv), sp.Eq(Yy**2, 2*pv*X)]),
                  ("y=x/2+p", [sp.Eq(Yy, X/2+pv), sp.Eq(Yy**2, 2*pv*X)]),
                  ("y=x+p (other slope)", [sp.Eq(Yy, X+pv), sp.Eq(Yy**2, 2*pv*X)])]:
    print("  ", desc, sp.solve(eqs, [X, Yy], dict=True))

print("=== 17-02 tangent y=2x+1/2 double-root check ===")
print("  ", sp.solve([sp.Eq(y, 2*x+sp.Rational(1,2)), sp.Eq(y**2, 4*x)], [x, y], dict=True))
print("   line y=1 ->", sp.solve([sp.Eq(y, 1), sp.Eq(y**2, 4*x)], [x, y], dict=True))

print("=== t21 |AB|^2 ===")
r = sp.solve(sp.expand(2*(s := sp.Symbol('s'))**2 - 8), s)
d2 = sp.simplify((r[0]-r[1])**2 + ((r[0]-1)-(r[1]-1))**2)
print("   roots", r, " |AB|^2 =", d2, " m:", sp.solve(sp.Eq(20-4*sp.Symbol('mM'), d2), sp.Symbol('mM')))

print("=== t02 real k ===")
print("   ", sp.solve(sp.Eq(sp.Symbol('K2')**2+sp.Symbol('K2')-2, 0), sp.Symbol('K2')))

print("=== t01 unscaled eq disc ===")
e1 = sp.expand(5*x**2 - 8*sp.sqrt(3)*x + 8)
print("   Δ=", sp.simplify(e1.coeff(x,1)**2-4*e1.coeff(x,2)*e1.coeff(x,0)),
      " |AB|=", sp.simplify(sp.sqrt(2)*sp.sqrt(e1.coeff(x,1)**2-4*e1.coeff(x,2)*e1.coeff(x,0))/5))
