# 盲解阶段独立复算（阶段一）：151~160
import sympy as sp

print("=== 151 正四面体+正八面体 拼接体积 ===")
a = sp.symbols('a', positive=True)
vt = sp.sqrt(2)/12*a**3; vo = sp.sqrt(2)/3*a**3
print("V_tet =", vt, " V_oct =", vo, " 和 =", sp.simplify(vt+vo), " 5√2/12 =", sp.simplify(vt+vo) == 5*sp.sqrt(2)/12*a**3)

print("=== 152 截角四面体 ===")
u = sp.symbols('u', positive=True)
S = 4*sp.sqrt(3)/4*u**2 + 4*6*sp.sqrt(3)/4*u**2
us = sp.solve(sp.Eq(sp.expand(S), 28*sp.sqrt(3)), u)
print("表面积式 =", sp.expand(S), " → u =", us)
uv = 2
V = sp.sqrt(2)/12*(3*uv)**3 - 4*sp.sqrt(2)/12*uv**3
print("体积 =", sp.simplify(V), " （原棱 6，截去 4×棱2）")
s2 = 3/uv*sp.sqrt(2)   # 立方体嵌入：棱=2√2 s =6 → s=6/(2√2)
sv = 6/(2*sp.sqrt(2)); p = sp.Matrix([sv, sv/3, sv/3])
print("外接：截点 =", p.T, " |p|² =", sp.simplify(p.dot(p)), " 表面积 =", sp.simplify(4*sp.pi*p.dot(p)))
q2 = sp.Matrix([sv, sv, sv/3]); print("另一型截点 |q|² =", sp.simplify(q2.dot(q2)), " 顶点距 =", sp.simplify(sp.Matrix([sv,sv,sv]).norm()))

print("=== 153 离散曲率 ===")
vals = {"正四面体 a": 1 - (3*sp.pi/3)/(2*sp.pi), "正八面体 b": 1 - (4*sp.pi/3)/(2*sp.pi),
        "正十二面体 c": 1 - (3*(3*sp.pi/5))/(2*sp.pi), "正二十面体 d": 1 - (5*sp.pi/3)/(2*sp.pi)}
for k, v in vals.items(): print(" ", k, "=", sp.nsimplify(v), "=", sp.N(v))

print("=== 154 二十四等边体（立方八面体） ===")
vs = [(1,1,0),(1,-1,0),(-1,1,0),(-1,-1,0),(1,0,1),(1,0,-1),(-1,0,1),(-1,0,-1),(0,1,1),(0,1,-1),(0,-1,1),(0,-1,-1)]
V0 = [sp.Matrix(v) for v in vs]
ed = sorted(set(sp.simplify((V0[i]-V0[j]).norm()) for i in range(12) for j in range(i+1,12)))
print("顶点间距离谱 =", ed, " 棱长√2 → 外接球 R² = 2 → 表面积 =", 8*sp.pi)
print("体积：正方体2 减 8 角锥 =", sp.simplify(8 - 8*sp.Rational(1,6)), " （=20/3）")
print("边数核验：棱 =", sp.simplify(sum(1 for i in range(12) for j in range(i+1,12) if (V0[i]-V0[j]).norm()==sp.sqrt(2))), " 面 8三角+6正方 = 14")
# ②③真；①④依图标号。举一例标号下④的可能：
print(" 例：若 PN 为过中心的对面顶点连线之……（无图不可判）")

print("=== 155 ===")
aa,bb,cc,dd = sp.symbols('a1 b1 c1 d1', real=True)
B155 = sp.Matrix([0,0,0]); C155 = sp.Matrix([2*sp.sqrt(3),0,0])
A155 = sp.Matrix([0,aa,bb]); D155 = sp.Matrix([2*sp.sqrt(3),cc,dd])
Vv = sp.simplify(sp.Rational(1,6)*sp.Abs((A155-B155).cross(C155-B155).dot(D155-B155)))
print("|AB|=|BC|=|CD|核验:", sp.simplify((A155-B155).norm()), sp.simplify((C155-B155).norm()), sp.simplify((D155-C155).norm()))
print("V =", Vv)
sol = sp.solve([sp.Eq(aa**2+bb**2,12), sp.Eq(cc**2+dd**2,12), sp.Eq(Vv,6)], [dd, cc, aa], dict=True)
print("一组解:", sol[:2])
ad_ = D155 - A155
for sgn in [1,-1]:
    # 取 (a1,b1)=(0,2√3); (c1,d1)=(±√3·... ) 使 ad−bc=±6√3
    A1 = sp.Matrix([0,0,2*sp.sqrt(3)]); C2 = sp.Matrix([2*sp.sqrt(3),0,0]); B2 = sp.Matrix([0,0,0])
    D1 = sp.Matrix([2*sp.sqrt(3), sgn*3*sp.sqrt(3)/1*0 + 6*sp.sqrt(3)/(2*sp.sqrt(3)), 0])
    D1 = sp.Matrix([2*sp.sqrt(3), 3, 0])   # c=3,d=0 → |CD|=3? 需=2√3 → 换
    # 参数化：(a1,b1)=2√3(cosθ,sinθ), (c1,d1)=2√3(cosφ,sinφ), |ad−bc|=12|sin(φ−θ)|=6√3 → sin=√3/2
    for phi in [sp.pi/3, 2*sp.pi/3]:
        Av = sp.Matrix([0, 2*sp.sqrt(3)*sp.cos(0), 2*sp.sqrt(3)*sp.sin(0)])
        Dv = sp.Matrix([2*sp.sqrt(3), 2*sp.sqrt(3)*sp.cos(phi), 2*sp.sqrt(3)*sp.sin(phi)])
        ad3 = Dv - Av; bc3 = sp.Matrix([2*sp.sqrt(3),0,0])
        cosang = sp.simplify(sp.Abs(ad3.dot(bc3))/(ad3.norm()*bc3.norm()))
        Vc = sp.simplify(sp.Rational(1,6)*sp.Abs(Av.cross(bc3).dot(Dv)))
        print("  φ=%s: V=%s |AD|=%s cos(AD,BC)=%s 角=%s" % (phi, Vc, sp.simplify(ad3.norm()), cosang, sp.deg(sp.acos(cosang))))

print("=== 156 ===")
Aq = sp.Matrix([0,0,0]); Bu = sp.Matrix([sp.sqrt(3),0,-1]); Cu = sp.Matrix([0,2*sp.sqrt(3),-2]); uq = sp.Matrix([0,0,4])
A1q = uq; B1q = Bu+uq; C1q = Cu+uq; Pq = uq/2
print("AA₁=%s AB=%s AC=%s ∠B₁A₁A cos=%s ∠C₁A₁A cos=%s 面垂直?(n1·n2)=%s" % (
 sp.simplify((A1q-Aq).norm()), sp.simplify((Bu-Aq).norm()), sp.simplify((Cu-Aq).norm()),
 sp.simplify((Bu-Aq).dot(-uq)/(2*4)), sp.simplify((Cu-Aq).dot(-uq)/(4*4)),
 sp.simplify((uq.cross(Cu)).dot(uq.cross(Bu)))))
lam = sp.symbols('lam', positive=True); Qq = lam*Cu
n1 = (Qq-Pq).cross(B1q-Pq); n2 = (Qq-Pq).cross(C1q-Pq)
cs = sp.simplify(sp.Abs(n1.dot(n2))/(n1.norm()*n2.norm()))
print("|cos二面角| =", sp.simplify(sp.together(cs)))
sl = sp.solve(sp.Eq(cs, sp.sqrt(13)/13), lam); print("λ =", sl)
lamv = sp.Rational(1,2); Qm = lamv*Cu
Hm = (Bu+Qm)/2; Dm = Bu + sp.Rational(1,3)*(Cu-Bu)
print("(1) D =", sp.simplify(Dm.T), " H·2 =", sp.simplify((2*Hm).T), " 共线:", sp.simplify(Dm - sp.Rational(4,3)*Hm).T)
nn = (Qm-Pq).cross(B1q-Pq); print("   AD·n =", sp.simplify(Dm.dot(nn)), " A在面上?", sp.simplify((Aq-Pq).dot(nn)))
nbb = (B1q-Bu).cross(Qm-Bu); print("(2) 平面BQB₁法向 =", sp.simplify(nbb.T), " P到面距离 =", sp.simplify((Pq-Bu).dot(nbb)/nbb.norm()))

print("=== 157 ===")
Be = sp.Matrix([0,0,0]); Ae = sp.Matrix([6,0,0]); Ce = sp.Matrix([0,6,0]); De = sp.Matrix([0,3,0]); Ee = sp.Matrix([0,0,6])
print("BE⊥底:", sp.simplify(Ee.dot(sp.Matrix([1,0,0]))), sp.simplify(Ee.dot(sp.Matrix([0,1,0]))),
      " AB=%s BC=%s AD=%s ∠ABC=%s ∠BAD=%s" % (sp.simplify((Ae-Be).norm()), sp.simplify((Ce-Be).norm()), sp.simplify((De-Ae).norm()),
      sp.deg(sp.acos(sp.simplify((Be-Ae).dot(Ce-Ae)/((Be-Ae).norm()*(Ce-Ae).norm())))),
      sp.deg(sp.acos(sp.simplify((Be-Ae).dot(De-Ae)/((Be-Ae).norm()*(De-Ae).norm()))))))
n = (Ce-De).cross(Ee-De); d157 = sp.simplify((Be-De).dot(n)/n.norm())
print("(1) d(B,CDE) =", sp.simplify(abs(d157)))
m1 = sp.Matrix([0,0,1]); 
cosn = sp.simplify(n.dot(m1)/(n.norm()*m1.norm())); print("(2) 两面法向cos =", cosn, " → tan =", sp.simplify(sp.sqrt(1-cosn**2)/abs(cosn)))
# 直接二面角 A-CD-E
CD = D - Ce if False else (De-Ce); uA = Ae - Ce; uE = Ee - Ce
v1 = sp.simplify(uA - uA.dot(CD)/CD.dot(CD)*CD); v2 = sp.simplify(uE - uE.dot(CD)/CD.dot(CD)*CD)
cc2 = sp.simplify(v1.dot(v2)/(v1.norm()*v2.norm()))
print("   二面角 cos =", cc2, " tan =", sp.simplify(sp.sqrt(1-cc2**2)/cc2))

print("=== 158/159/160 ===")
print("158 对棱中点距 =", sp.simplify(sp.sqrt(2)/2))
Ax = sp.Matrix([2,2,0]); Bx = sp.Matrix([1,4,2]); Cx = sp.Matrix([0,0,5]); Ox = sp.Matrix([0,0,0])
nx = (Bx-Ax).cross(Cx-Ax); print("159 法向 =", nx.T, " |n| =", sp.simplify(nx.norm()), " d =", sp.simplify(sp.Abs((Ox-Ax).dot(nx)/nx.norm())),
      " = ", sp.nsimplify(sp.Rational(30,1)/sp.sqrt(233)), " 有理式:", sp.simplify(30*sp.sqrt(233)/233))
Oa = sp.Matrix([0,0,0]); Ba = sp.Matrix([3,0,0]); Aa = sp.Matrix([3,0,3*sp.sqrt(3)]); Cdir = sp.Matrix([sp.cos(sp.rad(30)), sp.sin(sp.rad(30)), 0])
print("160 OB =", sp.simplify((Ba-Oa).norm()), " AB =", sp.simplify((Aa-Ba).norm()),
      " ∠AOB =", sp.deg(sp.acos(sp.simplify((Oa-Aa).dot(Ba-Aa)/((Oa-Aa).norm()*(Ba-Aa).norm())))),
      " d(A,OC) =", sp.simplify(sp.sqrt((sp.Rational(3,2))**2 + 27)), "= 3√13/2?", sp.simplify(sp.sqrt(117)/2 - 3*sp.sqrt(13)/2))
# 直算
P0 = Aa - (Aa.dot(Cdir)/Cdir.dot(Cdir))*Cdir
print("     垂足距 =", sp.simplify(P0.norm()), " 复核OA=6:", sp.simplify((Aa-Oa).norm()))
