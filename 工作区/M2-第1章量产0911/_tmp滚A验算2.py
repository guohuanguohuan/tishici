# -*- coding: utf-8 -*-
# 滚动卷A 16题 独立验算脚本（sympy）
import sympy as sp
import random
from sympy import Matrix, Rational, sqrt, cos, sin, pi, simplify, solve, Symbol, Rational as Fr

ok = []
def chk(name, cond):
    ok.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name)

# ---------- 题1 充分不必要 ----------
# |a+b|=|a|+|b| 平方化简 -> a·b=|a||b| -> cosθ=1 -> 同向共线（充分）；反向共线为反例（不必要）
a = Matrix([1, 2, 3]); b = Matrix([2, 4, 6])          # 同向
brev = Matrix([-2, -4, -6])                            # 反向
lhs = (a + b).norm(); rhs = a.norm() + b.norm()
chk("1 同向=>等式成立", simplify(lhs - rhs) == 0)
lhs2 = (a + brev).norm(); rhs2 = a.norm() + brev.norm()
chk("1 反向=>等式不成立(不必要)", sp.simplify(lhs2 - rhs2) != 0)
# 一般 cosθ 推演
t = Symbol('t', real=True)
eq = sp.expand(1 + t**2 + 2*t) - sp.expand((1 + sp.Abs(t))**2)  # |a|=1, b=t*a 同/反向参数
chk("1 共线参数化：等式仅 t>=0", sp.simplify(eq.subs(t, 2)) == 0 and sp.simplify(eq.subs(t, -2)) != 0)

# ---------- 题2 合力 ----------
F1 = Matrix([3, 0]); F2 = Matrix([0, 4]); F = F1 + F2
chk("2 |F|=5", F.norm() == 5)
c2 = (F.dot(F1)) / (F.norm() * F1.norm())
chk("2 cos=3/5", c2 == Rational(3, 5))

# ---------- 题3 基底（以 a,b,c 为形式基，看 c 分量） ----------
# AB=a=(1,0,0) AC=b=(0,1,0) AD=c=(0,0,1)（抽象基下坐标即系数）
va, vb, vc = Matrix([1,0,0]), Matrix([0,1,0]), Matrix([0,0,1])
A_opt = (vc - va) + (-vc)          # BD + DA = -a         γ=0
B_opt = va - vb                    # AB - AC = a-b        γ=0
C_opt = (vb - va) + (vc - vb) + (-vc) + va   # BC+CD+DA+AB = 0
D_opt = (vb - va) + (vc - va)      # BC + BD = -2a+b+c
def can_basis(v): return v[2] != 0   # 与 a,b 成基底 <=> c 分量非0
chk("3 A不可(∥a)", not can_basis(A_opt) and A_opt == -va)
chk("3 B不可(共面)", not can_basis(B_opt))
chk("3 C不可(零向量)", C_opt == Matrix([0,0,0]))
chk("3 D可(含c分量2)", can_basis(D_opt) and D_opt == Matrix([-2,1,1]))

# ---------- 题4 三角形形状 ----------
A4 = Matrix([1,1,0]); B4 = Matrix([1,-1,0]); C4 = Matrix([0,0,sqrt(2)])
dAB = simplify((A4-B4).norm()**2); dAC = simplify((A4-C4).norm()**2); dBC = simplify((B4-C4).norm()**2)
chk("4 三边平方 4,4,4", dAB == 4 and dAC == 4 and dBC == 4)

# ---------- 题5 点位置 ----------
m = Symbol('m', real=True)
P = Matrix([m-1, m+2, 0])
chk("5 x轴可(m=-2)", P.subs(m,-2)[0] == -3 and P.subs(m,-2)[1] == 0)
chk("5 y轴可(m=1)", P.subs(m,1)[0] == 0 and P.subs(m,1)[1] == 3)
chk("5 xOy恒成立", P[2] == 0)
chk("5 原点不可", solve([m-1, m+2], m, dict=True) == [])

# ---------- 题6 中点链 ----------
def mid(X, Y): return (X + Y) / 2
for i in range(3):
    Ax, Bx, Cx, Dx = [Matrix([random.randint(-9,9) for _ in range(3)]) for _ in range(4)]
    E = mid(Ax, Cx); Fm = mid(Bx, Dx)
    EF = Fm - E
    chk(f"6 随机组{i+1} EF=1/2(AB+CD)", simplify(EF - ((Bx-Ax)+(Dx-Cx))/2)==Matrix([0,0,0]))
# 严格：EF=1/2(AB+DC)？
Ax = Matrix([0,0,0]); Bx = Matrix([1,2,3]); Cx = Matrix([-1,4,0]); Dx = Matrix([2,-1,5])
E = mid(Ax,Cx); Fm = mid(Bx,Dx); EF = Fm - E
chk("6 反例：EF≠1/2(AD+BC)", simplify(EF - ((Dx-Ax)+(Cx-Bx))/2) != 0)
chk("6 恒等：EF=1/2(AB+CD)", simplify(EF - ((Bx-Ax)+(Dx-Cx))/2) == Matrix([0,0,0]))
chk("6 四边和=0", simplify((Bx-Ax)+(Cx-Bx)+(Dx-Cx)+(Ax-Dx)) == Matrix([0,0,0]))

# ---------- 题7 类比 ----------
i_, j_, k_ = Matrix([1,0,0]), Matrix([0,1,0]), Matrix([0,0,1])
chk("7 D反例 i⊥k,k⊥j 但 i∦j", i_.dot(k_)==0 and k_.dot(j_)==0 and i_.cross(j_) != Matrix([0,0,0]))

# ---------- 题8 多选 ----------
A8 = Matrix([0,0,0]); B8 = Matrix([2,-2,1]); C8 = Matrix([1,2,2])
mm = Symbol('m8', real=True); D8 = Matrix([4,mm,5])
AB8 = B8-A8; AC8 = C8-A8; AD8 = D8-A8
chk("8 ①AB⊥AC", AB8.dot(AC8) == 0)
chk("8 ②模均3", AB8.norm()==3 and AC8.norm()==3)
x8, y8 = Symbol('x8'), Symbol('y8')
sol8 = solve([2*x8 + y8 - 4, x8 + 2*y8 - 5], [x8, y8], dict=True)[0]
mneed = simplify((-2*x8 + 2*y8 - mm).subs(sol8))
chk("8 ③m=2共面", sp.Eq(mneed, 2) is True or mneed.subs(mm,2)==0)
BC8 = C8 - B8; ADm2 = Matrix([4,2,5])
chk("8 ④m=2时AD∦BC", simplify(ADm2 - sp.Symbol('r')*BC8) != Matrix([0,0,0]) and (ADm2[0]*BC8[1] != ADm2[1]*BC8[0]))

# ---------- 题9 四心 ----------
PA_ = Matrix([2,1]); PB_ = Matrix([-1,3]); # 构造：取重心情形验证 A
Av = Matrix([0,0]); Bv = Matrix([6,0]); Cv = Matrix([1,5])
G9 = (Av+Bv+Cv)/3
chk("9 A 重心满足PA+PB+PC=0", simplify((Av-G9)+(Bv-G9)+(Cv-G9))==Matrix([0,0]))
# 垂心等价：对锐角三角形求垂心，验证数量积相等
def orthocenter(Ax_,Bx_,Cx_):
    # 解 (H-A)·(B-C)=0, (H-B)·(A-C)=0
    hx, hy = sp.symbols('hx hy'); H = Matrix([hx,hy])
    s = solve([(H-Ax_).dot(Bx_-Cx_), (H-Bx_).dot(Ax_-Cx_)], [hx,hy], dict=True)[0]
    return Matrix([s[hx], s[hy]])
A9=Matrix([0,0]); B9=Matrix([5,0]); C9v=Matrix([2,4])
H9 = orthocenter(A9,B9,C9v)
e1 = simplify((A9-H9).dot(B9-H9)); e2 = simplify((B9-H9).dot(C9v-H9)); e3 = simplify((C9v-H9).dot(A9-H9))
chk("9 B 垂心=>三数量积相等", e1==e2 and e2==e3)
# 外心
def circumcenter(Ax_,Bx_,Cx_):
    hx, hy = sp.symbols('hx hy'); H = Matrix([hx,hy])
    s = solve([(H-Ax_).dot(H-Ax_)-(H-Bx_).dot(H-Bx_), (H-Bx_).dot(H-Bx_)-(H-Cx_).dot(H-Cx_)],[hx,hy],dict=True)[0]
    return Matrix([s[hx],s[hy]])
O9 = circumcenter(A9,B9,C9v)
chk("9 C 外心等距", simplify((O9-A9).norm()-(O9-B9).norm())==0 and simplify((O9-B9).norm()-(O9-C9v).norm())==0)
# D：OP=1/3(OA+OB+OC) 是重心而非内心（直角3-4-5例，内心到原点距离≠重心）
A9b=Matrix([0,0]); B9b=Matrix([3,0]); C9b=Matrix([0,4])
Gd = (A9b+B9b+C9b)/3
inr = (B9b-C9b).norm()  # 3-4-5: r=1，内心(1,1)
chk("9 D 重心≠内心", Gd != Matrix([1,1]))

# ---------- 题10 ----------
x10 = sp.symbols('x10')
M10 = Matrix([x10,0,0]); A10=Matrix([1,2,3]); B10=Matrix([3,4,1])
s10 = solve((M10-A10).dot(M10-A10)-(M10-B10).dot(M10-B10), x10, dict=True)[0]
chk("10 x=3", s10[x10] == 3)
Mv = Matrix([3,0,0])
chk("10 距离平方均17", simplify((Mv-A10).dot(Mv-A10))==17 and simplify((Mv-B10).dot(Mv-B10))==17)

# ---------- 题11 ----------
t11 = sp.symbols('t11')
chk("11 t=1/6", solve(sp.Eq(Fr(1,3)+Fr(1,2)+t11, 1), t11)[0] == Fr(1,6))

# ---------- 题12 翻折 ----------
phi = sp.symbols('phi', positive=True)
D12 = Matrix([0,0,0]); C12 = Matrix([1,0,0]); A12 = Matrix([0,0,sqrt(3)])
Bp = Matrix([cos(phi), sin(phi), 0])   # DB'=1, ∠B'DC=phi
ABp = Bp - A12; DC = C12 - D12; DA = A12 - D12
chk("12 |AB'|=2 恒成立", simplify(ABp.norm()-2)==0)
chk("12 AD⊥DB' 恒成立", simplify((Bp-D12).dot(DA))==0)
chk("12 AB'·DC=cosφ", simplify(ABp.dot(DC)-cos(phi))==0)
chk("12 ⊥=>φ=90°(φ∈(0,π))", list(sp.solveset(sp.Eq(cos(phi),0), phi, sp.Interval.open(0, pi)))==[pi/2])
chk("12 平行不可能：AB'·DA=-3≠0=DC·DA", simplify(ABp.dot(DA))==-3 and simplify(DC.dot(DA))==0)
Bp90 = Bp.subs(phi, pi/2)
CBp = Bp90 - C12
chk("12 |CB'|=√2", simplify(CBp.norm()-sqrt(2))==0)
AB90 = Bp90 - A12
cosang = simplify(AB90.dot(CBp)/(AB90.norm()*CBp.norm()))
chk("12 cos<AB',CB'>=√2/4", cosang == sqrt(2)/4)
chk("12 |DB'|=|DC|=1", simplify(Bp.norm())==1 and simplify(C12.norm())==1)

# ---------- 题13 平行四边形恒等式 ----------
p, q, r = sp.symbols('p q r', real=True)
u = Matrix([p,q]); v = Matrix([r, sp.symbols('s', real=True)])
AC = u+v; BD = v-u
lhs13 = simplify(AC.dot(AC)+BD.dot(BD)); rhs13 = simplify(2*(u.dot(u)+v.dot(v)))
chk("13 |AC|²+|BD|²=2|u|²+2|v|²", lhs13==rhs13)

# ---------- 题14 ----------
A14=Matrix([0,0,0]); B14=Matrix([3,1,0]); C14=Matrix([-1,2,1]); D14=Matrix([2,-2,3])
a14=B14-A14; b14=C14-A14; c14=D14-A14
E14=(C14+D14)/2
P14 = B14 + Fr(2,3)*(E14-B14)   # BP=2PE
AP14 = P14-A14
chk("14 AP=(a+b+c)/3", simplify(AP14-(a14+b14+c14)/3)==Matrix([0,0,0]))
AQ14 = Fr(2,3)*a14+Fr(1,3)*b14+Fr(1,3)*c14
kk = sp.symbols('kk')
sol14 = solve(list(AQ14 - kk*AP14),[kk],dict=True)
chk("14 不共线(唯一分解矛盾)", sol14 == [])

# ---------- 题15 ----------
D15=Matrix([0,0,0]); A15=Matrix([2,0,0]); B15=Matrix([2,2,0]); C15=Matrix([0,2,0])
D1_=Matrix([0,0,2]); A1_=Matrix([2,0,2]); B1_=Matrix([2,2,2]); C1_=Matrix([0,2,2])
edges = [(A15,C15),(A15,B1_),(A15,D1_),(C15,B1_),(C15,D1_),(B1_,D1_)]
chk("15 六棱均2√2", all(simplify((X-Y).norm()-2*sqrt(2))==0 for X,Y in edges))
G15 = (C15+B1_+D1_)/3
chk("15 G=(2/3,4/3,4/3)", G15 == Matrix([Fr(2,3),Fr(4,3),Fr(4,3)]))
AG15 = G15-A15
chk("15 AG·CB1=0", simplify(AG15.dot(B1_-C15))==0)
chk("15 AG·CD1=0", simplify(AG15.dot(D1_-C15))==0)
chk("15 |AG|=4√3/3", simplify(AG15.norm()-4*sqrt(3)/3)==0)
chk("15 GC+GB1+GD1=0", simplify((C15-G15)+(B1_-G15)+(D1_-G15))==Matrix([0,0,0]))

# ---------- 题16 ----------
tt = sp.symbols('t', real=True)
B16=Matrix([0,0,0]); A16=Matrix([2,0,0]); C16=Matrix([0,2,0]); P16=Matrix([0,2,tt])
ABs=simplify((A16-B16).dot(A16-B16)); PBs=simplify((P16-B16).dot(P16-B16)); PAs=simplify((P16-A16).dot(P16-A16))
chk("16 (1) 4, 4+t², 8+t²", ABs==4 and PBs==4+tt**2 and PAs==8+tt**2)
BA16=A16-B16; BP16=P16-B16; AP16=P16-A16; AA16=B16-A16
chk("16 直角在B恒成立", simplify(BA16.dot(BP16))==0)
chk("16 直角在A不可能", simplify((B16-A16).dot(P16-A16))==4)
chk("16 直角在P不可能", simplify((A16-P16).dot(B16-P16))==4+tt**2)
chk("16 非退化：BA×BP≠0", simplify((BA16.cross(BP16)).norm())==simplify(2*sp.sqrt(4+tt**2)) and simplify(BA16.cross(BP16)) != Matrix([0,0,0]))
chk("16 等腰仅AB=PB=>t=0", solve(sp.Eq(ABs,PBs),tt)==[0] and solve(sp.Eq(ABs,PAs),tt)==[] and solve(sp.Eq(PBs,PAs),tt)==[])
PAv=A16-P16; PBv=B16-P16
tan_th = simplify(PAv.cross(PBv).norm()/(PAv.dot(PBv)))
chk("16 tanθ=2/√(4+t²)", simplify(tan_th-2/sqrt(4+tt**2))==0)
v0 = tan_th.subs(tt,0); v3 = sp.simplify(tan_th.subs(tt,3))
chk("16 端点 tan: 1 与 2√13/13", v0==1 and simplify(v3-2*sqrt(13)/13)==0)
dtt = sp.simplify(sp.diff(tan_th, tt))
chk("16 tanθ在[0,3]单调减", all(simplify(dtt.subs(tt,q0))<0 for q0 in [Fr(1,2),1,2]) and simplify(dtt + 2*tt/(tt**2+4)**sp.Rational(3,2))==0)
bad=[n for n,c in ok if not c]
print("\n==== 结果：", len(ok), "项检查，失败", len(bad), "====")
for n in bad: print("FAILED:", n)
