import sympy as sp

x, y, m, k, p = sp.symbols('x y m k p', real=True)

print("=== t17-19 right-branch intersection check (x^2 - y^2/4 = 1, x>=1) ===")
e19 = sp.expand(4*x**2 - (m*(x+1))**2 - 4)
for mv in [0, sp.Rational(3,2), -sp.Rational(3,2), 2, -2, sp.Rational(5,2), sp.Rational(9,5)]:
    eq = e19.subs(m, mv)
    if sp.Poly(eq, x).degree() == 1:
        rts = sp.solve(eq, x)
    else:
        rts = [sp.nsimplify(r) for r in sp.solve(eq, x)]
    good = any(sp.re(r) >= 1 for r in rts if sp.im(r) == 0)
    print("  m=%-5s roots=%-40s |m|<2? %s -> 有公共点? %s" % (mv, [str(r) for r in rts],
                                                              bool(abs(mv) < 2), good))

print()
print("=== t17-21 (3章件12-#19) AB 中点为圆心、|AB|^2、m ===")
s = sp.symbols('s')
expr = sp.expand(2*(s-1)**2 - (s-2)**2 - 2)   # 2x^2 - y^2 = 2,  x = s-1, y = s-2 (k=1)
print("  u-equation:", expr, " roots:", sp.solve(expr, s))
r1, r2 = sp.solve(expr, s)
A = (r1-1, r1-2)
B = (r2-1, r2-2)
d2 = sp.simplify((A[0]-B[0])**2 + (A[1]-B[1])**2)
print("  A,B =", A, B, " |AB|^2 =", d2)
print("  m:", sp.solve(sp.Eq(20-4*sp.Symbol('M'), d2), sp.Symbol('M')))
print("  on curve check:", [sp.simplify(a[0]**2 - a[1]**2/2 - 1) for a in (A, B)])

print()
print("=== t17-02 real roots of k^4+k^2-2 ===")
print("  ", sp.factor(k**4+k**2-2), " k^2 =", sp.solve(sp.Eq(k**4+k**2-2, 0), k**2))

print()
print("=== t17-10 three lines through (0,p), p=2 ===")
X, Yy = sp.symbols('X Yy')
pv = 2
for desc, eqs in [("x=0", [sp.Eq(X, 0), sp.Eq(Yy**2, 2*pv*X)]),
                  ("y=p", [sp.Eq(Yy, pv), sp.Eq(Yy**2, 2*pv*X)]),
                  ("y=x/2+p", [sp.Eq(Yy, X/2+pv), sp.Eq(Yy**2, 2*pv*X)]),
                  ("y=x+p", [sp.Eq(Yy, X+pv), sp.Eq(Yy**2, 2*pv*X)]),
                  ("y=2x+p", [sp.Eq(Yy, 2*X+pv), sp.Eq(Yy**2, 2*pv*X)])]:
    sol = sp.solve(eqs, [X, Yy], dict=True)
    print("  %-10s -> %d 公共点 %s" % (desc, len(sol), sol))

print()
print("=== 17-16 (x^2=2py) 焦点弦 ratio, p=3 numeric ===")
pv = 3
Xv, Yv = sp.symbols('Xv Yv')
sol = sp.solve([sp.Eq(Yv, Xv/sp.sqrt(3)+pv/2), sp.Eq(Xv**2, 2*pv*Yv)], [Xv, Yv], dict=True)
for s_ in sol:
    xv, yv = sp.simplify(s_[Xv]), sp.simplify(s_[Yv])
    print("   pt x=%s y=%s |MF|=%s" % (xv, yv, sp.simplify(yv+pv/2)))
print("   ratio =", sp.simplify((sol[0][Yv]+pv/2)/(sol[1][Yv]+pv/2)), "or inverse",
      sp.simplify((sol[1][Yv]+pv/2)/(sol[0][Yv]+pv/2)))

print()
print("=== t17-16 two circles through A,B tangent to x=-1 (direct numeric) ===")
Xv, Yv = sp.symbols('Xv Yv')
pts = sp.solve([sp.Eq(Yv, Xv-1), sp.Eq(Yv**2, 4*Xv)], [Xv, Yv], dict=True)
A_ = (sp.simplify(pts[0][Xv]), sp.simplify(pts[0][Yv]))
B_ = (sp.simplify(pts[1][Xv]), sp.simplify(pts[1][Yv]))
print("  A,B =", A_, B_)
a, b, R = sp.symbols('a b R')
eqs = [sp.Eq((A_[0]-a)**2 + (A_[1]-b)**2, R**2),
       sp.Eq((B_[0]-a)**2 + (B_[1]-b)**2, R**2),
       sp.Eq(R, sp.Abs(a+1))]
sols = sp.solve([sp.Eq((A_[0]-a)**2 + (A_[1]-b)**2, (a+1)**2),
                 sp.Eq((B_[0]-a)**2 + (B_[1]-b)**2, (a+1)**2),
                 sp.Eq(b, -a+5)], [a, b], dict=True)
print("  centers:", [(sp.simplify(s[a]), sp.simplify(s[b])) for s in sols])
for s_ in sols:
    print("    center", sp.simplify(s_[a]), sp.simplify(s_[b]), "r=", sp.simplify(s_[a]+1),
          " check |CA|^2-r^2 =", sp.simplify((A_[0]-s_[a])**2 + (A_[1]-s_[b])**2 - (s_[a]+1)**2))
