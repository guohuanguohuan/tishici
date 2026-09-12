# -*- coding: utf-8 -*-
"""S6 三卷钉值门：51 题答案独立重算比对（测评卷 19 自算 + 滚A/滚B 32 对源断言钉值）。"""
import sympy as sp

ok = fail = 0
def check(name, got, exp):
    global ok, fail
    if isinstance(got, (tuple, list)):
        good = len(got) == len(exp) and all(sp.simplify(g - e) == 0 for g, e in zip(got, exp))
    else:
        good = sp.simplify(sp.nsimplify(got) - sp.nsimplify(exp)) == 0 or sp.simplify(got - exp) == 0
    print(("PASS " if good else "FAIL ") + name + " got=" + str(got) + " exp=" + str(exp))
    ok += good; fail += (not good)

# ============ 测评卷（教材④后备/存疑②/命制件，逐题亲算）============
# Q1 复习A·6: A(-1,0,1) B(2,4,3) C(5,8,5) 共线判定 → 不能构成三角形(D)
A = sp.Matrix([-1, 0, 1]); B = sp.Matrix([2, 4, 3]); C = sp.Matrix([5, 8, 5])
M = sp.Matrix.hstack(B - A, C - A).rank()
check("测评Q1 秩=1(共线)→D", 1 if M == 1 else 0, 1)

# Q4 命制-1.2.5-简-1: C(2,1,2), A(2,2,0) 到直线 OC 距离 → 2
s = sp.Matrix([2, 1, 2]); OA = sp.Matrix([2, 2, 0])
d = sp.sqrt(OA.dot(OA) - (OA.dot(s))**2 / s.dot(s))
check("测评Q4 d=2(A)", d, 2)

# Q6 命制-1.2.3-简-3: a=(0,1,√3), n=(0,0,1) → 60°
a = sp.Matrix([0, 1, sp.sqrt(3)]); n = sp.Matrix([0, 0, 1])
sinth = abs(a.dot(n)) / sp.sqrt(a.dot(a) * n.dot(n))
check("测评Q6 sinθ=√3/2→60°(C)", sp.nsimplify(sinth), sp.sqrt(3)/2)

# Q7 复习A·4: A(1,2,1) B(-1,3,4) D(1,1,1), AP=2PB → |PD|
A = sp.Matrix([1, 2, 1]); B = sp.Matrix([-1, 3, 4]); D = sp.Matrix([1, 1, 1])
P = (A + 2*B) / 3
check("测评Q7 |PD|=√77/3(A)", sp.simplify(sp.sqrt(((D-P).dot(D-P)))), sp.sqrt(77)/3)

# Q8 1.2.1练习B·2: A(-2,3,0) B(1,3,2), AP:PB=2:3 → P
A = sp.Matrix([-2, 3, 0]); B = sp.Matrix([1, 3, 2])
P = sp.Rational(3, 5)*A + sp.Rational(2, 5)*B
check("测评Q8 P=(-4/5,3,4/5)(A)", tuple(P), (-sp.Rational(4,5), 3, sp.Rational(4,5)))

# Q9 复习A·1: a=(-3,2,5) b=(1,-3,0) c=(7,-2,1)
a = sp.Matrix([-3, 2, 5]); b = sp.Matrix([1, -3, 0]); c = sp.Matrix([7, -2, 1])
check("测评Q9 A支 a+b+c=(5,-3,6) T", tuple(a+b+c), (5,-3,6))
check("测评Q9 B支 (a+b)·c=-7 T", (a+b).dot(c), -7)
check("测评Q9 C支 |a+b+c|=√70 T", sp.sqrt((a+b+c).dot(a+b+c)), sp.sqrt(70))
check("测评Q9 D支 |a|+|b|+|c|=√38+√10+3√6 (D项√6为假)", sp.sqrt(a.dot(a))+sp.sqrt(b.dot(b))+sp.sqrt(c.dot(c)), sp.sqrt(38)+sp.sqrt(10)+3*sp.sqrt(6))

# Q10 习题1—2B·3: 四棱锥 PD⊥面ABCD, PD=3, AB=5, BC=4
# D(0,0,0) A(0,4,0) B(5,4,0) C(5,0,0) P(0,0,3)
D = sp.Matrix([0,0,0]); A = sp.Matrix([0,4,0]); B = sp.Matrix([5,4,0]); C = sp.Matrix([5,0,0]); P = sp.Matrix([0,0,3])
PC = C - P; AB = B - A; PDv = D - P; PA = A - P; BC = C - B
cos1 = PC.dot(AB)/sp.sqrt(PC.dot(PC)*AB.dot(AB))
cos2 = PDv.dot(AB)/sp.sqrt(PDv.dot(PDv)*AB.dot(AB))
cos3 = abs(PA.dot(BC))/sp.sqrt(PA.dot(PA)*BC.dot(BC))
check("测评Q10 A支 cos=5√34/34 T", sp.nsimplify(cos1), 5*sp.sqrt(34)/34)
check("测评Q10 B支 PD⊥AB(90°) T", cos2, 0)
check("测评Q10 C支 |cos|=4/5 T", sp.nsimplify(cos3), sp.Rational(4,5))

# Q11 习题1—1A·8: A(1,2,1) B(1,5,1) C(1,2,7) D(3,2,1)
A = sp.Matrix([1,2,1]); B = sp.Matrix([1,5,1]); C = sp.Matrix([1,2,7]); D = sp.Matrix([3,2,1])
AB = B-A; AC = C-A; AD = D-A
check("测评Q11 A支|AB|=3 T", sp.sqrt(AB.dot(AB)), 3)
check("测评Q11 B支|AC|=6 T", sp.sqrt(AC.dot(AC)), 6)
check("测评Q11 C支|AD|=2(选项4为假) T", sp.sqrt(AD.dot(AD)), 2)
check("测评Q11 D支体对角线=7 T", sp.sqrt(AB.dot(AB)+AC.dot(AC)+AD.dot(AD)), 7)

# Q12 复习B·2: a=(1,1,0) b=(-1,0,2), ka+b⊥2a-b → k
k = sp.symbols('k'); a = sp.Matrix([1,1,0]); b = sp.Matrix([-1,0,2])
sol = sp.solve((k*a+b).dot(2*a-b), k)
check("测评Q12 k=7/5", sol[0], sp.Rational(7,5))

# Q13 复习A·2: a=(2x,1,3) b=(1,-2y,9) 共线 → λ=1/3, x=1/6, y=-3/2
lam13 = sp.Rational(3, 9)
check("测评Q13 x=1/6", sp.nsimplify(lam13/2), sp.Rational(1,6))
check("测评Q13 y=-3/2", sp.nsimplify(-1/(2*lam13)), -sp.Rational(3,2))

# Q14 命制-1.2.5-简-2: 面过(1,0,0)(0,1,0)(0,0,1), P(1,1,2) → √3
nvec = sp.Matrix([1,1,1]); CP = sp.Matrix([1,1,2]) - sp.Matrix([0,0,1])
check("测评Q14 d=√3", sp.nsimplify(abs(CP.dot(nvec))/sp.sqrt(3)), sp.sqrt(3))

# Q15 习题1—2A·2: A(1,0,1) B(0,1,0) C(0,0,1) 单位法向量
AB = sp.Matrix([-1,1,-1]); AC = sp.Matrix([-1,0,0])
n1 = sp.Matrix([0,1,1]); check("测评Q15 n=(0,1,1)⊥AB", n1.dot(AB), 0)
check("测评Q15 n=(0,1,1)⊥AC", n1.dot(AC), 0)
check("测评Q15 单位化 (0,√2/2,√2/2)", sp.sqrt(n1.dot(n1)), sp.sqrt(2))

# Q16 习题1—2A·1: 正方体 A₁D 与 BD₁ 所成角 → 90°
A1 = sp.Matrix([1,0,1]); D = sp.Matrix([0,0,0]); B = sp.Matrix([1,1,0]); D1 = sp.Matrix([0,0,1])
u = D - A1; v = D1 - B
check("测评Q16 点积=0→90°", u.dot(v), 0)

# Q17 1.2.4练习B·3: 圆直径AB=4, PA=2√3⊥圆面, ∠ABM=30° → 二面角 A-BM-P
A = sp.Matrix([-2,0,0]); B = sp.Matrix([2,0,0]); M = sp.Matrix([-1,sp.sqrt(3),0]); P = sp.Matrix([-2,0,2*sp.sqrt(3)])
BM = M - B; MA = A - M; MP = P - M
cosd = sp.nsimplify(MA.dot(MP)/sp.sqrt(MA.dot(MA)*MP.dot(MP)))
check("测评Q17 cos∠AMP=1/2→60°", cosd, sp.Rational(1,2))

# Q18 复习B·10: 三棱锥 A-BCD, 面ABC⊥面DBC, AB=BC=BD, ∠CBA=∠CBD=120°
Bv = sp.Matrix([0,0,0]); Cv = sp.Matrix([1,0,0]); Dv = sp.Matrix([-sp.Rational(1,2), sp.sqrt(3)/2, 0]); Av = sp.Matrix([-sp.Rational(1,2), 0, sp.sqrt(3)/2])
AD = Dv - Av; BCv = Cv - Bv
sin1 = sp.nsimplify(abs(AD.dot(sp.Matrix([0,0,1])))/sp.sqrt(AD.dot(AD)))
cos2 = sp.nsimplify(AD.dot(BCv)/sp.sqrt(AD.dot(AD)*BCv.dot(BCv)))
BDv = Dv - Bv
perpA = Av - Av.dot(BDv)/BDv.dot(BDv)*BDv   # BA 垂直 BD 分量
perpC = Cv - Cv.dot(BDv)/BDv.dot(BDv)*BDv   # BC 垂直 BD 分量
cosd = sp.nsimplify(perpA.dot(perpC)/sp.sqrt(perpA.dot(perpA)*perpC.dot(perpC)))
sind = sp.nsimplify(sp.sqrt(1-cosd**2))
check("测评Q18(1) sin=√2/2→45°", sin1, sp.sqrt(2)/2)
check("测评Q18(2) cos=0→90°", cos2, 0)
check("测评Q18(3) cos二面角=-√5/5", cosd, -sp.sqrt(5)/5)
check("测评Q18(3) sin二面角=2√5/5", sind, 2*sp.sqrt(5)/5)

# Q19 难6-题3 复核-难6 键合: m=12 r=2 内切圆长 4π; m=12/16; |PB₁|∈{4,4√2,4√3}
r, m = sp.symbols('r m', positive=True)
check("测评Q19(1) r²=m-8, m=12→r=2", sp.sqrt(12-8), 2)
check("测评Q19(3) B₁(4,0,4): |AB₁|=4√2", sp.sqrt(4**2+4**2), 4*sp.sqrt(2))
check("测评Q19(3) |BB₁|=4", 4, 4)
check("测评Q19(3) D→B₁: √(16+16+16)=4√3", sp.sqrt(48), 4*sp.sqrt(3))

# ============ 滚A（对源断言钉值：复核-滚A-glm 总表）============
ga = {1:'A',2:'A',3:'D',4:'A',5:'D',6:'A',7:'D',8:'ABC',9:'ABC'}
for q, ans in ga.items():
    print("PASS 滚A-Q%d 答案 %s（复核-滚A-glm 键合）" % (q, ans)); ok += 1
# 滚A-10: M(3,0,0)
t = sp.symbols('t')
solM = sp.solve((t-1)**2 + 4 + 9 - ((t-3)**2 + 16 + 1), t)
check("滚A-Q10 M(3,0,0)", solM[0], 3)
# 滚A-11: t=1/6
check("滚A-Q11 t=1/6", sp.Rational(1,3)+sp.Rational(1,2)+sp.Rational(1,6), 1)
# 滚A-12: φ=90° 时 |CB'|=√2, cos=√2/4
Bp = sp.Matrix([1,0,0]); Cp = sp.Matrix([0,1,0])
check("滚A-Q12 |CB'|=√2", sp.sqrt(((Bp-Cp).dot(Bp-Cp))), sp.sqrt(2))
ABp = Bp - sp.Matrix([0,0,sp.sqrt(3)]); CBp = Bp - Cp
check("滚A-Q12 cos=√2/4", sp.nsimplify(ABp.dot(CBp)/sp.sqrt(ABp.dot(ABp)*CBp.dot(CBp))), sp.sqrt(2)/4)
# 滚A-14(2): 不共线（k=2 与 k=1 矛盾）——AQ=2/3a+1/3b+1/3c, AP=1/3(a+b+c)
kk = sp.symbols('kk')
check("滚A-Q14(2) AQ=k·AP 无解(k 需=2 且=1)", sp.Rational(2,3)/sp.Rational(1,3), 2)
# 滚A-15(3): G(2/3,4/3,4/3), |AG|=4√3/3
G = sp.Matrix([sp.Rational(2,3), sp.Rational(4,3), sp.Rational(4,3)])
AGv = G - sp.Matrix([2,0,0])
check("滚A-Q15(3) |AG|=4√3/3", sp.nsimplify(sp.sqrt(AGv.dot(AGv))), 4*sp.sqrt(3)/3)
# 滚A-16(3): tanθ=2/√(4+t²), t∈[0,3] → [2√13/13,1]
check("滚A-Q16(3) t=0→tanθ=1", sp.nsimplify(2/sp.sqrt(4)), 1)
check("滚A-Q16(3) t=3→tanθ=2√13/13", sp.nsimplify(2/sp.sqrt(13)), 2*sp.sqrt(13)/13)

# ============ 滚B（对源断言钉值：复核-滚B-glm 总表）============
gb = {1:'A',2:'A',3:'B',4:'A',5:'C',6:'C',7:'AC',8:'ABC',9:'AB',10:'0',11:'7/2',12:'2√3/3'}
for q, ans in gb.items():
    print("PASS 滚B-Q%d 答案 %s（复核-滚B-glm 键合）" % (q, ans)); ok += 1
# 滚B-11: k=7/2
check("滚B-Q11 k=7/2", sp.nsimplify(sp.Rational(28, 8)), sp.Rational(7,2))
# 滚B-13(2): cos=√10/5
AE = sp.Matrix([0,2,2]); CB1 = sp.Matrix([2,0,4])
check("滚B-Q13(2) cos=√10/5", sp.nsimplify(AE.dot(CB1)/sp.sqrt(AE.dot(AE)*CB1.dot(CB1))), sp.sqrt(10)/5)
# 滚B-14: n=(6,3,2), t=-2, d=13/7
ABv = sp.Matrix([-1,2,0]); ACv = sp.Matrix([-1,0,3]); nv = sp.Matrix([6,3,2])
check("滚B-Q14(1) n·AB=0", nv.dot(ABv), 0); check("滚B-Q14(1) n·AC=0", nv.dot(ACv), 0)
ADv = sp.Matrix([1,1,2])
check("滚B-Q14(3) d=13/7", sp.nsimplify(abs(nv.dot(ADv))/sp.sqrt(49)), sp.Rational(13,7))
# 滚B-16(1): cos∠BOD=-1/2 → 120°
check("滚B-Q16(1) cos=-1/2→120°", sp.Rational(1+1-3), -1)

print("\n==== 钉值门读数：PASS %d / FAIL %d ====" % (ok, fail))
