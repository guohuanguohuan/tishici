# 盲解阶段独立复算（阶段一，台账/快照未开）：122修正 + 128~160
import sympy as sp

print("=== 122/126 修正（点到平面距离须减面上点） ===")
Bs = sp.Matrix([0,0,0]); As = sp.Matrix([2,0,0]); Cs = sp.Matrix([0,2,0]); Ss = sp.Matrix([0,0,2])
Ps = (As+Bs)/2; Qs = (Cs+Bs)/2; Os = sp.Matrix([1,1,1])
n = (Ss-Ps).cross(Qs-Ps); dd = (Os-Ps).dot(n)/n.norm()
print("n =", n.T, " d² =", sp.simplify(dd**2), " 截面面积 =", sp.simplify(sp.pi*(3-dd**2)),
      " 截面周长 =", sp.simplify(2*sp.pi*sp.sqrt(3-dd**2)))

print("=== 128/130 正四面体 与EF垂直的截面 面积最大 ===")
t, a = sp.symbols('t', real=True), sp.symbols('a', positive=True)
# 立方体嵌入：顶点 (w,w,w),(w,-w,-w),(-w,w,-w),(-w,-w,w), 棱 a=2√2 w
w = a/(2*sp.sqrt(2))
A = sp.Matrix([w,w,w]); B = sp.Matrix([w,-w,-w]); C = sp.Matrix([-w,w,-w]); D = sp.Matrix([-w,-w,w])
u = (w - t)/(2*w)   # 高度 t 处参数
P1 = A + u*(B-A); P2 = A + u*(C-A); P3 = D + u*(B-D); P4 = D + u*(C-D)
area = sp.simplify(sp.Rational(1,2)*(P2-P1).cross(P4-P1).norm())
print("截面面积(t) =", sp.factor(area), " t=0 →", sp.simplify(area.subs(t,0)),
      " a=4 →", sp.simplify(area.subs(t,0).subs(a,4)), " a=1 →", sp.simplify(area.subs(t,0).subs(a,1)))
# 数值核验是否为该平行四边形面积
num = sp.lambdify(t, area.subs(a,4), 'numpy')
print("a=4: area(0)=%.6f area(0.3)=%.6f area(0.6)=%.6f" % (num(0), num(0.3), num(0.6)))

print("=== 129 与四顶点等距的平面 截面面积和 (a=4) ===")
a4 = 4
sq = a4**2/4                    # 2-2 分型：中点正方形
tri = sp.sqrt(3)/4*(a4/2)**2    # 3-1 分型：相似比1/2
print("3个正方形 =", 3*sq, " 4个三角形 =", sp.simplify(4*tri), " 和 =", 3*sq + 4*tri)

print("=== 131 正方体2 截面五边形 ⟺ CM 范围 ===")
m = sp.symbols('m', positive=True)   # C 原点, CB=x, CD=y, CC1=z ; M=(m,0,0)
Am = sp.Matrix([2,2,0]); Mm = sp.Matrix([m,0,0]); Nm = sp.Matrix([0,0,sp.Rational(2,3)])
pl = Am.cross(Mm) + Mm.cross(Nm) + Nm.cross(Am)   # 法向（等价 (M-A)×(N-A)）
nn = (Mm-Am).cross(Nm-Am)
print("法向 =", nn.T)
# 与棱 D D1 (x=0,y=2) 的交点 z；与棱 A1D1 (y=2,z=2) 的交点 x
z_K = sp.solve(sp.Eq(nn.dot(sp.Matrix([0,2,sp.Symbol('zz')])-Am), 0), sp.Symbol('zz'))[0]
x_L = sp.solve(sp.Eq(nn.dot(sp.Matrix([sp.Symbol('xx'),2,2])-Am), 0), sp.Symbol('xx'))[0]
y_T = sp.solve(sp.Eq(nn.dot(sp.Matrix([0,sp.Symbol('yy'),2])-Am), 0), sp.Symbol('yy'))[0]
print("K(棱DD₁) z =", sp.simplify(z_K), "  L(棱A₁D₁) x =", sp.simplify(x_L), " T(棱C₁D₁) y =", sp.simplify(y_T))
print("K 在棱内(0≤z≤2) ⟺", sp.solve_univariate_inequality(sp.And(z_K>=0, z_K<=2), m, relational=False))
print("L 在棱内(0≤x≤2) ⟺", sp.solve_univariate_inequality(sp.And(x_L>=0, x_L<=2), m, relational=False))
print("候选值:", [(v, float(v) < 2/3) for v in (1, sp.Rational(1,2), sp.sqrt(2)/3, sp.Rational(3,4))])

print("=== 132/134 侧面展开 周长最小 ===")
print("132: PA=2, 总角3×40°=120° →", sp.simplify(sp.sqrt(4+4-2*4*sp.cos(sp.rad(120)))))
th = sp.acos(sp.Rational(7,8))
print("134: cosθ=7/8, PA=8 → 周长² =", sp.simplify(64+64-2*64*sp.cos(3*th)), " 周长 =", sp.sqrt(sp.simplify(128-128*sp.cos(3*th))))

print("=== 135 四棱锥 展开 AE+EF+BF ===")
Av = sp.Matrix([0,0,0]); Bv = sp.Matrix([2,0,0]); Cv = sp.Matrix([2,2,0]); Dv = sp.Matrix([0,2,0]); Pv = sp.Matrix([1,0,sp.sqrt(3)])
print("PA,PB,PC,PD =", [sp.simplify((Pv-X).norm()) for X in (Av,Bv,Cv,Dv)])
c1 = sp.cos(sp.angle_between(Av-Pv, Dv-Pv)); c2 = sp.cos(sp.angle_between(Dv-Pv, Cv-Pv)); c3 = sp.cos(sp.angle_between(Cv-Pv, Bv-Pv))
print("∠APD cos =", c1, " ∠DPC cos =", c2, " ∠CPB cos =", c3)
tot = sp.acos(c1)+sp.acos(c2)+sp.acos(c3)
d2 = sp.simplify(4+4-8*sp.cos(tot))
print("展开总角 =", sp.N(tot), " 距离² =", sp.nsimplify(d2), " 距离 =", sp.simplify(sp.sqrt(d2)), "=", sp.N(sp.sqrt(7)+1))

print("=== 136 圆锥侧面展开 SC=2 SA=6 最短2√13 ===")
al = sp.symbols('alpha', positive=True)
sol = sp.solve(sp.Eq(36+4-24*sp.cos(al), 52), al)
print("扇形角 α =", sol, " → r = 3α/π =", [sp.simplify(3*s/sp.pi) for s in sol])
rv = 2; print("r=2 → h =", sp.sqrt(36-4), " V =", sp.simplify(sp.Rational(1,3)*sp.pi*rv**2*sp.sqrt(32)))

print("=== 137 半周展开 AB=2 AD=1 最短√5 ===")
rr = sp.symbols('r', positive=True)
eq = sp.Eq(4+1-4*sp.cos(sp.pi*rr/2), 5)
print("解:", sp.solve(eq, rr))

print("=== 138 阳马 △PEF周长最小 → P-AEF外接球 ===")
tt = sp.symbols('t', real=True)
f = sp.sqrt(t**2+1) + sp.sqrt((1-t)**2+1)
ts = sp.solve(sp.diff(f, tt), tt)
print("t* =", ts, " 周长 =", sp.simplify(f.subs(tt, ts[0])) + sp.sqrt(3))
Ev = sp.Matrix([sp.Rational(1,2),0,0]); Fv = sp.Matrix([1,1,0]); Pv2 = sp.Matrix([0,0,1]); Av2 = sp.Matrix([0,0,0])
cx,cy,cz = sp.symbols('cx cy cz'); Om = sp.Matrix([cx,cy,cz])
so = sp.solve([sp.Eq((Om-Av2).dot(Om-Av2),(Om-Ev).dot(Om-Ev)),
               sp.Eq((Om-Av2).dot(Om-Av2),(Om-Fv).dot(Om-Fv)),
               sp.Eq((Om-Av2).dot(Om-Av2),(Om-Pv2).dot(Om-Pv2))],[cx,cy,cz],dict=True)[0]
Oc = sp.Matrix([so[cx],so[cy],so[cz]]); R2 = sp.simplify(Oc.dot(Oc))
print("球心 =", Oc.T, " R² =", R2, " 表面积 =", sp.simplify(4*sp.pi*R2))

print("=== 139 阿氏圆/球 + M-B₁CF体积最小 ===")
x,y,z = sp.symbols('x y z', real=True)
Pv3 = sp.Matrix([x,y,z]); Bv3 = sp.Matrix([6,0,0]); Ev3 = sp.Matrix([2,0,0])
circ = sp.expand((Pv3-Bv3).dot(Pv3-Bv3) - 3*(Pv3-Ev3).dot(Pv3-Ev3))
print("轨迹方程:", circ, "= 0 → 半径² = 12 →", sp.sqrt(12))
# 体积
B1 = sp.Matrix([6,0,3]); C3 = sp.Matrix([6,3,0]); F3 = sp.Matrix([3,3,3])
M0 = sp.Matrix([3,sp.Rational(3,2),0])   # M 球心
n = (C3-B1).cross(F3-B1)
area3 = sp.simplify(n.norm()/2)
dist_center = sp.simplify((M0-B1).dot(n)/n.norm())
print("S(△B₁CF) =", area3, " M₀到面距离 =", dist_center, " → min d =", sp.simplify(sp.Abs(dist_center)-sp.sqrt(3)))
Vmin = sp.simplify(sp.Rational(1,3)*area3*(sp.Abs(dist_center)-sp.sqrt(3)))
print("V_min =", Vmin)
# 直代校核：P=(2,2,2) → M=(4,2.5,1)
for Pp in [sp.Matrix([2,2,2]), sp.Matrix([sp.sqrt(12),0,0]), sp.Matrix([0,sp.sqrt(6),sp.sqrt(6)])]:
    M = (Pp + C3)/2
    V = sp.simplify(sp.Rational(1,6)*sp.Abs((B1-M).cross(C3-M).dot(F3-M)))
    print("  P =", Pp.T, "|P|²=", sp.simplify(Pp.dot(Pp)), " V =", V)
