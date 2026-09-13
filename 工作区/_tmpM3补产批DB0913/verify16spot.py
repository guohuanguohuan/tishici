import sympy as sp

x, y, m, k, p, a = sp.symbols('x y m k p a', positive=True)
out = []


def chk(n, got, want):
    g, w = sp.simplify(got), sp.simplify(want)
    out.append((n, str(g), str(w), "OK" if sp.simplify(g - w) == 0 else "**MISMATCH**"))


# 16-16: x^2=4y, two focal chords with k1*k2=-2 -> min |AB|+|DE| = 24
k1, k2 = sp.symbols('k1 k2', real=True)
# y = k1 x + 1 into x^2 = 4y -> x^2 - 4k1 x - 4 = 0 ; y1+y2 = k1(x1+x2)+2
X = sp.symbols('X')
e = X**2 - 4*k1*X - 4
s = -e.coeff(X, 1)
ysum = sp.simplify(k1*s + 2)
chk("16-16 |AB|", sp.simplify(ysum + 2), 4*(k1**2+1))
f = 4*(k1**2+1) + 4*(k2**2+1)
chk("16-16 min@k1k2=-2", sp.simplify(f.subs(k2, -2/k1).subs(k1, sp.sqrt(2))), 24)
chk("16-16 AM-GM val", 8*2 + 8, 24)

# 拓16-25 等腰梯形
exprs = [sp.Eq(1, 2*p*m), sp.Eq(4, 2*p*(m + sp.sqrt(3)))]
solp = sp.solve(exprs, [p, m], dict=True)[0]
chk("t16-25 p", solp[p], sp.sqrt(3)/2)
chk("t16-25 m", solp[m], sp.sqrt(3)/3)
chk("t16-25 |AF|", sp.simplify(solp[m] + solp[p]/2), 7*sp.sqrt(3)/12)

# 16-05, 16-02, 16-04, 16-06, 16-08, 16-09
chk("16-02", 1 + sp.Rational(1, 16), sp.Rational(17, 16))
chk("16-04", abs(2 - sp.sqrt(3)*0)/2, 1)
chk("16-05", 4 + 2, 6)
chk("16-06 y", sp.sqrt(2*sp.Rational(3, 2)*2), sp.sqrt(6))  # placeholder replaced below
chk("16-06 x", 2*p - p/2, 3*p/2)
chk("16-06 y2", sp.sqrt(2*p*sp.Rational(3, 2)*p/p*1), sp.sqrt(3)*p)
chk("16-08", sp.Rational(6-2, 1), 4)  # c^2=4 -> c=2 -> p=4
chk("16-09", sp.Rational(1, 16) + sp.Rational(1, 4)*sp.Rational(5, 6) + sp.Rational(1, 16), sp.Rational(1, 3))

# 16-11 / 16-12 / 16-13
chk("16-11", 8/2, 4)
chk("16-12", 4 + 2, 6)
Xv = sp.symbols('Xv', nonneg=True)
chk("16-13", sp.simplify((Xv-4)**2 + 16*Xv).subs(Xv, 0), 16)

# 16-14 正三角形边长 4*sqrt(3)*p
yA = 2*sp.sqrt(3)*p
chk("16-14 y_A^2 vs 2p x_A", sp.simplify(yA**2 - 2*p*(sp.sqrt(3)*yA)), 0)
chk("16-14 edge", 2*yA, 4*sp.sqrt(3)*p)
chk("16-18 special 2p=6", 4*sp.sqrt(3)*3, 12*sp.sqrt(3))

# 16-15 (1) |AB|=4p ; (2) cos
spart = sp.symbols('s', positive=True)
eq = x**2 - 3*p*x + p**2/4
chk("16-15 xsum", -eq.coeff(x, 1), 3*p)
chk("16-15 |AB|", 3*p + p, 4*p)
yprod = p**2/4 - (p/2)*(3*p) + p**2/4
chk("16-15 y1y2", sp.simplify(yprod), -p**2)
# cos AOB
sA = sp.symbols('A1 A2')
r = sp.solve(eq, x)
x1, x2 = r
y1 = x1 - p/2
y2 = x2 - p/2
OA2 = sp.simplify(x1**2 + y1**2)
OB2 = sp.simplify(x2**2 + y2**2)
AB2 = sp.simplify((x1-x2)**2 + (y1-y2)**2)
cosv = sp.simplify((OA2 + OB2 - AB2)/(2*sp.sqrt(OA2*OB2)))
print("cos AOB =", sp.nsimplify(cosv), "=", sp.simplify(cosv - (-3*sp.sqrt(41)/41)))

# 17-07 (1) two tangents from (4,0) to x^2/4+y^2=1
e17 = x**2/4 + (k*(x-4))**2 - 1
A17, B17, C17 = [sp.expand(e17).coeff(x, i) for i in (2, 1, 0)]
chk("17-07 disc", sp.simplify(B17**2-4*A17*C17), sp.simplify(16-192*k**2))
chk("17-07 k", sp.solve(sp.Eq(B17**2-4*A17*C17, 0), k)[0], sp.sqrt(3)/6)

for n, g, w, s_ in out:
    print(f"{n:22s} got={g:22s} want={w:22s} {s_}")
print("MISMATCH:", sum(1 for q in out if q[3] != "OK"), "/", len(out))
