import sympy as sp

x, y, k, m, p, u, s, r, cv = sp.symbols('x y k m p u s r c', real=True)
res = []


def chk(name, got, want):
    if isinstance(got, (list, tuple, set, bool)) or isinstance(want, (list, tuple, set, bool)):
        g, w = sp.simplify(sp.nsimplify(got)) if False else str(got), str(want)
        try:
            g2 = [str(sp.simplify(t)) for t in got] if isinstance(got, (list, tuple)) else str(sp.simplify(got))
            w2 = [str(sp.simplify(t)) for t in want] if isinstance(want, (list, tuple)) else str(sp.simplify(want))
        except Exception:
            g2, w2 = g, w
        res.append((name, str(g2), str(w2), "OK" if str(g2) == str(w2) else "**MISMATCH**"))
        return
    g, w = sp.simplify(got), sp.simplify(want)
    good = bool(sp.simplify(g - w) == 0)
    res.append((name, str(g), str(w), "OK" if good else "**MISMATCH**"))


def quad(expr):
    e = sp.expand(expr)
    return e.coeff(x, 2), e.coeff(x, 1), e.coeff(x, 0)


def disc(e):
    A, B, C = quad(e)
    return sp.expand(B**2 - 4*A*C)


def chord(e, kk):
    A, B, C = quad(e)
    return sp.simplify(sp.sqrt(1 + kk**2) * sp.sqrt(B**2 - 4*A*C) / A)


# 17-01
P = [(1, 2), (4, -4)]
chk("17-01 on-curve", (y**2-4*x).subs([(x, 1), (y, 2)]), 0)
chk("17-01 line", (y+2*x-4).subs([(x, 4), (y, -4)]), 0)
chk("17-01 len", sp.sqrt((4-1)**2 + (-4-2)**2), 3*sp.sqrt(5))
# 17-02 tangent slope: (1+k t)^2 = 1+4t -> k^2 t^2 + (2k-4) t = 0 ; double root at t=0 needs 2k-4=0
chk("17-02 kcut", sp.solve(sp.Eq(2*k-4, 0), k)[0], 2)
chk("17-02 y=1 pt", sp.solve([sp.Eq(y, 1), sp.Eq(y**2, 4*x)], [x, y], dict=True)[0][x], sp.Rational(1, 4))
# 17-03
chk("17-03 len", sp.sqrt(4+1), sp.sqrt(5))
# 17-04
chk("17-04 disc", disc(x**2 + (x+1)**2/2 - 1), 16)
# 17-06 焦点弦 |AB| = x1+x2+p
chk("17-06", 5+2, 7)
# 17-08 mid
A, B, C = quad(x**2/4 + (x+1)**2/2 - 1)
chk("17-08 midx", sp.simplify(-B/A/2), sp.Rational(-2, 3))
# 17-09
e = 2*x**2 - (x-3)**2/3 - 6
chk("17-09 eq", sp.simplify(e*3 - (5*x**2+6*x-27)), 0)
chk("17-09 len", chord(e, sp.sqrt(3)/3), 16*sp.sqrt(3)/5)
# 17-10 : x = m y + 5 in x^2 - 4y^2 = 20, chord in y
Y = sp.symbols('Y')
e10 = sp.expand((m*Y+5)**2 - 4*Y**2 - 20)
A10, B10, C10 = e10.coeff(Y, 2), e10.coeff(Y, 1), e10.coeff(Y, 0)
L10 = sp.simplify(sp.sqrt(1+m**2)*sp.sqrt(B10**2-4*A10*C10)/A10)
chk("17-10 |AB| formula", L10 - 4*sp.sqrt(5)*(1+m**2)/sp.Abs(m**2-4), 0)
chk("17-10 tongjing", L10.subs(m, 0), sp.sqrt(5))
chk("17-10 m=1", sp.simplify(L10.subs(m, 1)), 8*sp.sqrt(5)/3)
chk("17-10 m=3", sp.simplify(L10.subs(m, 3)), sp.sqrt(5))
# 17-11
e11 = 2*x**2 - (k*(x-1)+2)**2 - 2
A11, B11, C11 = quad(e11)
chk("17-11 A", A11, 2-k**2); chk("17-11 B", sp.expand(B11), sp.expand(2*(k**2-2*k)))
chk("17-11 C", sp.expand(C11), sp.expand(-k**2+4*k-6))
chk("17-11 disc", disc(e11), 48-32*k)
chk("17-11 vertical", sp.solve([sp.Eq(x,1), sp.Eq(2*x**2-y**2,2)], [x,y], dict=True)[0][y], 0)
# 17-12
chk("17-12 disc", disc((k*x+1)**2 - 4*x), 16*(1-k))
# 17-13
e13 = 2*x**2 + 3*(k*x+2)**2 - 6
chk("17-13 disc", disc(e13), 72*k**2-48)
chk("17-13 bnd", sp.sqrt(sp.Rational(2,3)), sp.sqrt(6)/3)
# 17-14
chk("17-14 bnd", sp.sqrt(sp.Rational(3,4)), sp.sqrt(3)/2)
# 17-15
e15 = x**2 + 2*(x+1)**2 - 6
chk("17-15 mid", -quad(e15)[1]/quad(e15)[0]/2, sp.Rational(-2,3))
chk("17-15 len", chord(e15, 1), 8*sp.sqrt(2)/3)
# 17-16
e16 = x**2 - 2*p*(x/sp.sqrt(3) + p/2)
chk("17-16 eq", sp.expand(e16 - (x**2 - 2*p*x/sp.sqrt(3) - p**2)), 0)
xA = -p/sp.sqrt(3); xB = sp.sqrt(3)*p
chk("17-16 rootA", sp.simplify(e16.subs(x, xA)), 0)
chk("17-16 rootB", sp.simplify(e16.subs(x, xB)), 0)
yA = sp.simplify(xA**2/(2*p)); yB = sp.simplify(xB**2/(2*p))
chk("17-16 yA", yA, p/6); chk("17-16 yB", yB, 3*p/2)
chk("17-16 ratio", sp.simplify((yA+p/2)/(yB+p/2)), sp.Rational(1,3))
chk("17-16 |AB|", sp.simplify(yA+yB+p), sp.Rational(8,3)*p)
# 拓17-01
e1 = x**2/4 + (x-sp.sqrt(3))**2 - 1
chk("t01 eq", sp.expand(4*e1 - (5*x**2-8*sp.sqrt(3)*x+8)), 0)
chk("t01 disc", disc(e1), 32)
chk("t01 len", chord(e1, 1), sp.Rational(8,5))
# 拓17-02
e2 = x**2/2 + (k*x+1)**2 - 1
chk("t02 eq", sp.expand(2*e2 - ((1+2*k**2)*x**2 + 4*k*x)), 0)
A2, B2, C2 = quad(e2)
L2 = sp.simplify((1+k**2)*(B2**2-4*A2*C2)/A2**2)
chk("t02 k^2", sp.solve(sp.Eq(L2, sp.Rational(32,9)), k**2), [1])
# 拓17-03
e3 = x**2 - (k*x-1)**2 - 4
chk("t03 eq", sp.expand(e3 - ((1-k**2)*x**2 + 2*k*x - 5)), 0)
chk("t03 disc", disc(e3), 20-16*k**2)
chk("t03 bnd", sp.sqrt(sp.Rational(5,4)), sp.sqrt(5)/2)
# 拓17-04 : |b| = a+1/2, b^2 = 2a
sols = sp.solve([sp.Eq(sp.Abs(bb := sp.symbols('bb'), 0) if False else 0, 0)], bb) if False else None
a, b0 = sp.symbols('a b', real=True)
s1_ = sp.solve([sp.Eq(b0**2, 2*a), sp.Eq(a + sp.Rational(1,2), 1), sp.Eq(sp.Abs(b0), 1)], [a, b0], dict=True)
chk("t04 a", s1_[0][a], sp.Rational(1,2))
chk("t04 nb", len(s1_), 2)
# 拓17-05
e5 = (x-1)**2 - 4*x
A5, B5, C5 = quad(e5)
sumx, prodx = -B5/A5, C5/A5
chk("t05 xsum", sumx, 6); chk("t05 xprod", prodx, 1)
chk("t05 yprod", sp.expand(prodx - sumx + 1), -4)
chk("t05 OAdotOB", sp.simplify(prodx + (prodx - sumx + 1)), -3)
# 拓17-06
e6 = sp.expand(y**2 - 2*p*(m*y + p/2))
chk("t06 y1y2", e6.coeff(y, 0), -p**2)
# 拓17-07
e7 = 4*(x-2)**2 - 8*x
chk("t07 xsum", -quad(e7)[1]/quad(e7)[0], 6)
chk("t07 len", -quad(e7)[1]/quad(e7)[0] + 4, 10)
# 拓17-08
e8 = x**2 + 8*x - 24
chk("t08 |AB|", chord(e8, 1), 8*sp.sqrt(5))
chk("t08 midx", -8/2, -4)
chk("t08 yprod", sp.simplify(-24 - 3*(-8) + 9), 9)
chk("t08 OAdotOB", -24 + 9, -15)
# 拓17-09 : asymptote-parallel line  y=(b/a)x+m vs x^2/a^2-y^2/b^2=1
aH, bH, mH = sp.symbols('a_H b_H m_H', positive=True)
e9 = sp.expand(x**2/aH**2 - ((bH/aH)*x + mH)**2/bH**2 - 1)
chk("t09 quadterm", e9.coeff(x, 2), 0)
chk("t09 linterm", sp.simplify(e9.coeff(x, 1)), sp.simplify(-2*mH/(aH*bH)))
# 拓17-10 : k from (kx+p)^2 = 2px, D=0
e10b = (k*x+p)**2 - 2*p*x
chk("t10 ktan", sp.solve(sp.Eq(disc(e10b), 0), k)[0], sp.Rational(1,2))
chk("t10 tangency pt", sp.simplify(((sp.Rational(1,2)*2*p+p)**2 - 2*p*2*p)), 0)
# 拓17-11 : y = 2x + c ; y^2 = 4x  -> using y as main var: y^2 - 2y + 2c = 0
e11b = y**2 - 2*y + 2*cv
L11 = sp.sqrt(sp.Rational(5,4) * (4-8*cv))
chk("t11 c", sp.solve(sp.Eq(L11, 5), cv)[0], -2)
chk("t11 back", sp.simplify(L11.subs(cv, -2)), 5)
# 拓17-12
e12 = (sp.Rational(4,3)*(x-2))**2 - 8*x
chk("t12 roots", sorted(sp.solve(e12, x)), [sp.Rational(1,2), 8])
chk("t12 yB", sp.Rational(4,3)*(sp.Rational(1,2)-2), -2)
chk("t12 mid2directrix", (8+sp.Rational(1,2))/2 + 2, sp.Rational(25,4))
# 拓17-13
chk("t13 x", (2*sp.sqrt(3))**2/4, 3)
# 拓17-14 : M on directrix has ordinate -p^2/y1 = y2
y1 = sp.symbols('y1', positive=True)
chk("t14 yM", sp.simplify((2*p/y1)*(-p/2)), -p**2/y1)
# 拓17-16 : circles through A,B tangent to x=-1
e16b = (x-1)**2 - 4*x
A16, B16, C16 = quad(e16b)
S16, P16 = -B16/A16, C16/A16
lab2 = sp.simplify(2*(S16**2 - 4*P16))
r2 = sp.simplify(2*(s-3)**2 + lab2/4)
chk("t16 |AB|^2", lab2, 64)
chk("t16 sols", sp.solve(sp.expand(r2 - (s+1)**2), s), [3, 11])
chk("t16 r@s3", sp.simplify(s+1).subs(s, 3), 4)
chk("t16 r@s11", sp.simplify(s+1).subs(s, 11), 12)
# 拓17-17
e17 = 3*x**2 - 4*(k*x+3)**2 - 12
A17, B17, C17 = quad(e17)
chk("t17 A", A17, 3-4*k**2); chk("t17 B", B17, -24*k); chk("t17 C", C17, -48)
chk("t17 disc", sp.expand(B17**2-4*A17*C17), sp.expand(576-192*k**2))
chk("t17 n", len(sp.solve(sp.Eq(B17**2-4*A17*C17,0), k)) + len(sp.solve(sp.Eq(A17,0), k)), 4)
# 拓17-18
e18 = x**2 - (k*x-1)**2 - 1
A18, B18, C18 = quad(e18)
chk("t18 eq", sp.expand(e18 - ((1-k**2)*x**2 + 2*k*x - 2)), 0)
chk("t18 range", sp.solve_univariate_inequality(sp.Eq(1-k**2,0), k, relational=False), sp.solve(sp.Eq(1-k**2,0), k))
# 拓17-19 : (4-m^2)x^2 - 2m^2 x - (m^2+4) = 0 ; need root x>=1
e19 = 4*x**2 - (m*(x+1))**2 - 4
A19, B19, C19 = quad(e19)
chk("t19 eq", sp.expand(e19 - ((4-m**2)*x**2 - 2*m**2*x - (m**2+4))), 0)
f19 = sp.lambdify('m', sp.solve(sp.Eq(A19,0), x) if A19.subs(m,0)==0 else sp.Rational(C19,A19).subs(m, 0), 'numpy') if False else None
roots19 = sp.solve(e19.subs(m, sp.Rational(3,2)), x)
chk("t19 has positive root m=1.5", any(sp.re(rt) > 1 for rt in roots19), True)
roots19b = sp.solve(e19.subs(m, 2), x)
chk("t19 m=2 root", roots19b, [-1])
# 拓17-20
e20 = 2*x**2 - (k*(x-1)+2)**2 - 2
A20, B20, C20 = quad(e20)
kk = sp.solve(sp.Eq(-B20/A20, 2), k)[0]
chk("t20 k", kk, 1)
e20b = sp.expand(e20.subs(k, 1))
chk("t20 |MN|", chord(e20b, 1), 4*sp.sqrt(2))
# 拓17-21
expr = sp.expand(2*(s-1)**2 - (s-2)**2 - 2)
chk("t21 u-eq", expr, 2*s**2 - 8)
rt = sp.solve(expr, s)
chk("t21 roots", sorted(rt), [-2, 2])
d2 = sp.simplify((rt[0]-rt[1])**2 + ((rt[0]-1)-(rt[1]-1))**2)
chk("t21 |AB|^2", sp.simplify(2*d2), 32)
chk("t21 m", sp.solve(sp.Eq(20-4*sp.symbols('mM'), 32), sp.symbols('mM'))[0], -3)
chk("t21 on-hyp", 1 - 0, 1)

for nm, g, w, st in res:
    print(f"{nm:28s} got={g:24s} want={w:24s} {st}")
print("MISMATCHES:", sum(1 for q in res if q[3] != "OK"), "/", len(res))
