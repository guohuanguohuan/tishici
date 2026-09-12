# -*- coding: utf-8 -*-
# 滚B16题 独立验算脚本（sympy），仅作私下核对旁证，不入成品解法。
import sympy as sp

ok = []
bad = []
def chk(name, got, want):
    if isinstance(got, (bool, sp.logic.boolalg.Boolean)) or isinstance(want, (bool, sp.logic.boolalg.Boolean)):
        same = bool(got) == bool(want)
        (ok if same else bad).append((name, got, want)); return
    g = sp.simplify(sp.nsimplify(got)); w = sp.simplify(sp.nsimplify(want))
    (ok if g == w else bad).append((name, g, w))

# ---- 题1: a.b=|a||b|cos120, a.(a+2b)
chk('1', 4 + 2*(2*1*sp.Rational(-1,2)), 2)

# ---- 题2: BC.AB = (AC-AB).AB, AB=2, AC=1, AB 与 AC 垂直
AB = sp.Matrix([2,0,0]); AC = sp.Matrix([0,1,0])
chk('2', (AC-AB).dot(AB), -4)

# ---- 题3: {a,b} 张成的平面包含性判断（选项是否成基底）
a = sp.Matrix([1,1,0]); b = sp.Matrix([0,1,1])   # 在 e1,e2,e3 系数空间
def in_span(v):
    t = sp.symbols('t0 t1')
    sol = sp.solve(list(a*t[0] + b*t[1] - sp.Matrix(v)), list(t), dict=True)
    return len(sol) > 0
chk('3-A(e1-e3 dependent)', in_span([1,0,-1]), True)
chk('3-C(a+2b dependent)', in_span([1,3,2]), True)
chk('3-D(a+b dependent)', in_span([1,2,1]), True)
chk('3-B(e1+e2+e3 independent)', in_span([1,1,1]), False)
# 行列式法复核 B：
chk('3-B det', sp.Matrix([list(a.T), list(b.T), [1,1,1]]).det(), 1)

# ---- 题4: 球心 S(1,2,-1) r=3
S = sp.Matrix([1,2,-1])
for nm, P in [('A',[1,2,2]),('B',[0,0,0]),('C',[1,2,-2]),('D',[2,1,1])]:
    d2 = sp.simplify((sp.Matrix(P)-S).dot(sp.Matrix(P)-S))
    chk('4-'+nm+(' on sphere' if nm=='A' else ' off sphere'), d2 == 9, nm=='A')
chk('4-A on sphere', (sp.Matrix([1,2,2])-S).norm(), 3)
chk('4-B off', (sp.Matrix([0,0,0])-S).norm(), sp.sqrt(6))
chk('4-C off', (sp.Matrix([1,2,-2])-S).norm(), 1)
chk('4-D off', (sp.Matrix([2,1,1])-S).norm(), sp.sqrt(6))

# ---- 题5: 垂线AA'=2sqrt3 射影A'B=2 -> tan=sqrt3 -> 60°；斜线=4
chk('5-tan', sp.simplify(2*sp.sqrt(3)/2), sp.sqrt(3))
chk('5-hyp', sp.sqrt(12+4), 4)
chk('5-sin', sp.simplify(2*sp.sqrt(3)/4), sp.sqrt(3)/2)

# ---- 题10: a=(1,2,2) b=(1,-2,2): (a+b).(a-b)
aa = sp.Matrix([1,2,2]); bb = sp.Matrix([1,-2,2])
chk('10', (aa+bb).dot(aa-bb), 0)
chk('10-|a|=|b|', sp.simplify(aa.norm()-bb.norm()), 0)

# ---- 题11: 平面 A(1,2) B(5,10) C(3,2k-1) 共线
k = sp.symbols('k')
ABv = sp.Matrix([4,8]); ACv = sp.Matrix([2, 2*k-3])
sol = sp.solve(ABv[0]*ACv[1]-ABv[1]*ACv[0], k)
chk('11', sol[0], sp.Rational(7,2))

# ---- 题12: 正方体棱2 D原点, E(0,0,s), 面A1BD n1=(1,-1,-1)过D, 面AB1D1 n2=(1,-1,1) 过A(2,0,0)
s = sp.symbols('s', nonnegative=True)
E = sp.Matrix([0,0,s]); D = sp.Matrix([0,0,0]); A = sp.Matrix([2,0,0]); B = sp.Matrix([2,2,0]); A1 = sp.Matrix([2,0,2]); B1 = sp.Matrix([2,2,2]); D1 = sp.Matrix([0,0,2])
n1 = sp.Matrix([1,-1,-1]); n2 = sp.Matrix([1,-1,1])
chk('12-n1⊥DA1', n1.dot(A1-D), 0); chk('12-n1⊥DB', n1.dot(B-D), 0)
chk('12-n2⊥AB1', n2.dot(B1-A), 0); chk('12-n2⊥AD1', n2.dot(D1-A), 0)
d1 = sp.simplify((E-D).dot(n1).abs() if hasattr((E-D).dot(n1),'abs') else sp.Abs((E-D).dot(n1))/sp.sqrt(3))
d2 = sp.Abs((E-D1).dot(n2))/sp.sqrt(3)
d1 = sp.Abs((E-D).dot(n1))/sp.sqrt(3)
for sv in [0, sp.Rational(1,2), 1, sp.Rational(3,2), 2]:
    chk('12-sum@s=%s' % sv, sp.simplify((d1+d2).subs(s,sv)), 2*sp.sqrt(3)/3)
chk('12-d1>=0', sp.simplify(d1.subs(s,1)) >= 0, True)
chk('12-d2>=0', sp.simplify(d2.subs(s,1)) >= 0, True)
# 关键点复核
chk('12-s=0', sp.simplify(d1+d2).subs(s,0), 2*sp.sqrt(3)/3)
chk('12-s=2', sp.simplify(d1+d2).subs(s,2), 2*sp.sqrt(3)/3)

# ---- 题13: 长方体 AB=AD=2 AA1=4, D原点, E=BB1中点
Aa=sp.Matrix([2,0,0]); Bb=sp.Matrix([2,2,0]); Cc=sp.Matrix([0,2,0]); B1b=sp.Matrix([2,2,4]); Ee=sp.Matrix([2,2,2])
AE = Ee-Aa; CB = B1b-Cc
chk('13-dot', AE.dot(CB), 8)
chk('13-|AE|', AE.norm(), 2*sp.sqrt(2))
chk('13-|CB1|', CB.norm(), 2*sp.sqrt(5))
chk('13-cos', sp.simplify(AE.dot(CB)/(AE.norm()*CB.norm())), sp.sqrt(10)/5)

# ---- 题14: 面 ABC A(1,0,0) B(0,2,0) C(0,0,3)
Ax=sp.Matrix([1,0,0]); Bx=sp.Matrix([0,2,0]); Cx=sp.Matrix([0,0,3])
n = sp.symbols('x y z')
eqs = [n[0]*(Bx-Ax)[0]+n[1]*(Bx-Ax)[1]+n[2]*(Bx-Ax)[2],
       n[0]*(Cx-Ax)[0]+n[1]*(Cx-Ax)[1]+n[2]*(Cx-Ax)[2]]
soln = sp.solve(eqs, [n[0], n[1]], dict=True)[0]
# 取 x=6: y=3 z=2
nv = sp.Matrix([6,3,2])
chk('14-n.AB', nv.dot(Bx-Ax), 0); chk('14-n.AC', nv.dot(Cx-Ax), 0)
t = sp.symbols('t')
Q = sp.Matrix([1,t,3])
chk('14-t', sp.solve(nv.dot(Q-Ax), t)[0], -2)
Dd = sp.Matrix([2,1,2])
chk('14-d', sp.simplify(sp.Abs(nv.dot(Dd-Ax))/nv.norm()), sp.Rational(13,7))

# ---- 题15: PA⊥底面矩形? 不：三棱锥 PA⊥面ABC AB⊥BC PA=2 BC=2 d(A,PBC)=√3 求AB
x = sp.symbols('x', positive=True)  # AB
# AE⊥面PBC（BC⊥面PAB），AE = PA*AB/PB = 2x/sqrt(x^2+4)
eq = sp.Eq(2*x/sp.sqrt(x**2+4), sp.sqrt(3))
sols = sp.solve(eq, x)
chk('15-AB', sols[0], 2*sp.sqrt(3))
# (3) sin: P=(2√3,0,2) C=(0,2,0) plane PAB = y=0
P = sp.Matrix([2*sp.sqrt(3),0,2]); C = sp.Matrix([0,2,0])
PC = C-P
chk('15-|PC|', PC.norm(), 2*sp.sqrt(5))
chk('15-sin', sp.simplify(abs(PC[1])/PC.norm()), sp.sqrt(5)/5)

# ---- 题16: 四面体 AB=BC=AD=DC=2, AC=2√3, BD=√3
# O 为 AC 中点, BO⊥AC DO⊥AC, BO=DO=1
chk('16-BO', sp.sqrt(4-3), 1)
# (1) cos∠BOD=(1+1-3)/2
chk('16-cos', sp.Rational(2-3,2), sp.Rational(-1,2))
# 建系验证：O原点, AC沿x, 底面ACD在xy: D=(cos? ∠BOD=120: 取 OD 沿 (1,0,0)... 设平面ACD=z0
import math
OD = sp.Matrix([1,0,0])
OB = sp.Matrix([sp.cos(sp.rad(120)), sp.sin(sp.rad(120)), 0*1])
OB = sp.Matrix([sp.Rational(-1,2), sp.sqrt(3)/2, 0])
A = sp.Matrix([0,-sp.sqrt(3),0]); Cc2 = sp.Matrix([0,sp.sqrt(3),0])  # AC 沿 y ⊥ xOz? 需 AC⊥OB且⊥OD: AC 沿 z? 重设：
# 令 AC 沿 z 轴: A=(0,0,-√3), C=(0,0,√3); OD 沿 x: D=(1,0,0); OB 在 xOy 平面与 OD 成120°:
Aa2 = sp.Matrix([0,0,-sp.sqrt(3)]); Cc3 = sp.Matrix([0,0,sp.sqrt(3)]); Dd2 = sp.Matrix([1,0,0])
Bb2 = sp.Matrix([sp.cos(sp.rad(120)), sp.sin(sp.rad(120)), 0])
chk('16-AB', sp.simplify((Bb2-Aa2).norm()), 2)
chk('16-BC', sp.simplify((Bb2-Cc3).norm()), 2)
chk('16-AD', sp.simplify((Dd2-Aa2).norm()), 2)
chk('16-CD', sp.simplify((Dd2-Cc3).norm()), 2)
chk('16-BD', sp.simplify((Bb2-Dd2).norm()), sp.sqrt(3))
chk('16-AC', (Cc3-Aa2).norm(), 2*sp.sqrt(3))
# (2) d(B, 面ACD): 面ACD 法向 = y 轴 (A,C沿z, D沿x): n=(0,1,0)
chk('16-d', sp.simplify(abs(Bb2[1])), sp.sqrt(3)/2)
# (3) sin<AB与面ACD>: dist/|AB|
chk('16-sin', sp.simplify((sp.sqrt(3)/2)/2), sp.sqrt(3)/4)

# ---- 题8/9 数值复核（正方体棱1）
Ax1=sp.Matrix([1,0,0]); Bx1=sp.Matrix([1,1,0]); Cx1=sp.Matrix([0,1,0]); Dx1=sp.Matrix([0,0,0])
A1x=sp.Matrix([1,0,1]); B1x=sp.Matrix([1,1,1]); C1x=sp.Matrix([0,1,1]); D1x=sp.Matrix([0,0,1])
def ang(u,v): return sp.simplify(abs(u.dot(v))/(u.norm()*v.norm()))
chk('8-①A1B^B1C', ang(Bx1-A1x, Cx1-B1x), sp.Rational(1,2))
chk('8-②AC1⊥BD', (Cx1-Ax1).dot(Dx1-Bx1), 0)
chk('8-③AA1^BC1', ang(A1x-Ax1, C1x-Bx1), sp.sqrt(2)/2)
chk('8-④|AB1|', (B1x-Ax1).norm(), sp.sqrt(2))
# 题9 二面角
O = (Bx1+Dx1)/2
OC = Cx1-O; OC1 = C1x-O
chk('9-②C1-BD-C cos', sp.simplify(OC.dot(OC1)/(OC.norm()*OC1.norm())), sp.sqrt(3)/3)
Oa = (Ax1+Cx1)/2
OB1 = B1x-Oa; OD1 = D1x-Oa
chk('9-③B1-AC-D1 cos', sp.simplify(OB1.dot(OD1)/(OB1.norm()*OD1.norm())), sp.Rational(1,3))
# ④ A1-CD-B：棱CD(D-C 沿 x? C=(0,1,0),D=(0,0,0): 方向(0,1,0))
# 半平面1 A1侧: 从D: DA1=(1,0,1) ⊥ (0,1,0)✓; 半平面2 B侧: 从D 底面⊥棱 toward B: (1,0,0)
chk('9-④A1-CD-B cos', sp.simplify((A1x-Dx1).dot(sp.Matrix([1,0,0]))/((A1x-Dx1).norm()*1)), sp.sqrt(2)/2)
# ① D-AB-A1: 棱AB 沿 y: DA=(-1,0,0)? 从A: AD=(-1,0,0)⊥AB✓, AA1=(0,0,1)⊥AB✓ cos=0
chk('9-①', (Dx1-Ax1).dot(A1x-Ax1), 0)

# ---- 题7 概念判断的坐标旁证（正方体棱1，D 原点）
dAB = sp.Matrix([0,1,0]); dCC1 = sp.Matrix([0,0,1])          # AB 与 CC1 方向向量
chk('7-② not parallel', sp.Matrix([list(dAB.T), list(dCC1.T)]).rank(), 2)
lam, mu = sp.symbols('lam mu')
inter = sp.solve(list((Ax1 + lam*dAB) - (Cx1 + mu*dCC1)), [lam, mu], dict=True)   # 有无公共点
chk('7-② no intersection', len(inter), 0)
u7 = sp.Matrix([1,0,0]); v7 = sp.Matrix([-1,1,0])            # 方向向量夹角为钝角的异面直线
chk('7-③ |cos| route', sp.simplify(abs(u7.dot(v7))/(u7.norm()*v7.norm())), sp.sqrt(2)/2)
chk('7-③ raw cos', sp.simplify(u7.dot(v7)/(u7.norm()*v7.norm())), -sp.sqrt(2)/2)

# ---- 题8 A项：A1B 与 B1C 确为异面（方向不共线且无公共点）
dA1B = Bx1-A1x; dB1C = Cx1-B1x
chk('8-A not parallel (rank 2)', sp.Matrix([list(dA1B.T), list(dB1C.T)]).rank(), 2)
a8, b8 = sp.symbols('a8 b8')
sol8 = sp.solve(list((A1x + a8*dA1B) - (B1x + b8*dB1C)), [a8, b8], dict=True)
chk('8-A no intersection', len(sol8), 0)
chk('8-A A1B // D1C', sp.simplify((Cx1-D1x).cross(dA1B).norm()), 0)

print('PASS %d' % len(ok))
for b in bad:
    print('FAIL', b)
if not bad:
    print('ALL CHECKS PASSED')
