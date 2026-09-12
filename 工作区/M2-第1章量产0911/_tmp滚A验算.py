import sympy as sp
import itertools

R = sp.Rational
print("=== S1 正方体棱长1 顶点集 中与 AC 相等的向量个数 ===")
V = {}
for x, y, z in itertools.product([0, 1], repeat=3):
    V[(x, y, z)] = sp.Matrix([x, y, z])
names = {(0,0,0):'A',(1,0,0):'B',(1,1,0):'C',(0,1,0):'D',
         (0,0,1):'A1',(1,0,1):'B1',(1,1,1):'C1',(0,1,1):'D1'}
A=V[(0,0,0)]; C=V[(1,1,0)]
AC = C-A
eq=[]
for p,q in itertools.permutations(V.keys(),2):
    if (V[q]-V[p]).equals(AC) and not (p==A.is_):
        pass
for p,q in itertools.permutations(V.keys(),2):
    if (V[q]-V[p]).equals(AC) and (p,q)!=( (0,0,0),(1,1,0) ):
        eq.append((names[p],names[q]))
print("与AC相等的向量(除自身):",eq)
# 棱向量 AB 的相等向量个数
B=V[(1,0,0)]; AB=B-A
e2=[(names[p],names[q]) for p,q in itertools.permutations(V.keys(),2) if (V[q]-V[p]).equals(AB) and (p,q)!=((0,0,0),(1,0,0))]
print("与AB相等的顶点向量(除自身):",e2)

print("=== S2 与三坐标轴夹角 60,60,? ===")
c=sp.symbols('c',real=True)
sols=sp.solve(sp.Eq(R(1,4)+R(1,4)+c**2,1),c)
print("cos gamma =",sols,"-> gamma deg:",[sp.deg(sp.acos(s)) for s in sols])

print("=== S6 三垂四面体 |AB+AC+AD| ===")
u=sp.Matrix([2,0,0]);v=sp.Matrix([0,2,0]);w=sp.Matrix([0,0,2])
print((u+v+w).norm())

print("=== M1 a=(1,2,2) b=(2,-2,1) ===")
a=sp.Matrix([1,2,2]);b=sp.Matrix([2,-2,1])
print("a.b",a.dot(b),"|a|",a.norm(),"|b|",b.norm(),"(a+b).(a-b)",(a+b).dot(a-b))

print("=== F9 重心 lambda+mu ===")
BA=sp.Matrix(sp.symbols('b1 b2'));BC=sp.Matrix(sp.symbols('c1 c2'))
Be=sp.Symbol('B')
# 用坐标: B=(0,0), A=(4,1), C=(2,5)
Bp=sp.Matrix([0,0]);Ap=sp.Matrix([4,1]);Cp=sp.Matrix([2,5])
D=(Bp+Cp)/2
E=Ap+R(2,3)*(D-Ap)
BE=E-Bp
lam,mu=sp.symbols('lam mu')
sol=sp.solve(list(BE-(lam*(Ap-Bp)+mu*(Cp-Bp))),[lam,mu],dict=True)
print("B(0,0),A(4,1),C(2,5): E=",E.T,sol,"sum=",sp.nsimplify(sol[0][lam]+sol[0][mu]))
Bp2=sp.Matrix([1,-2]);Ap2=sp.Matrix([3,4]);Cp2=sp.Matrix([-1,3])
D2=(Bp2+Cp2)/2;E2=Ap2+R(2,3)*(D2-Ap2);BE2=E2-Bp2
sol2=sp.solve(list(BE2-(lam*(Ap2-Bp2)+mu*(Cp2-Bp2))),[lam,mu],dict=True)
print("second triangle:",sol2,"sum=",sp.nsimplify(sol2[0][lam]+sol2[0][mu]))

print("=== F10 长方体 AC1 ===")
print(sp.sqrt(16+9+24))

print("=== F11 ===")
# 单位向量 a,b |a-2b|=sqrt3 -> a.b=1/2 ; (2a+b).(a-3b)
ab=sp.symbols('ab')
val=sp.solve(sp.Eq(1+4-4*ab,3),ab)[0]
print("a.b =",val," (2a+b).(a-3b) =",sp.simplify(2-6*val+val-3))

print("=== F12 |a|=2 |b|=1 min of |a+t b| = sqrt3 ===")
th,t=sp.symbols('theta t',real=True)
f=t**2+2*t*(2*sp.cos(th))+4
mn=sp.simplify(sp.minimum(f,t))
print("min f =",mn)
sols=sp.solve(sp.Eq(mn,3),th)
print("theta solutions (rad):",sols,"deg:",[sp.deg(s) for s in sols])
for s in sols:
    t0=sp.solve(sp.diff(f,t).subs(th,s),t)
    print("  theta=",sp.deg(s),"t0=",t0,"min|a+tb|=",sp.sqrt(f.subs([(th,s),(t,t0[0])])).simplify())
# 另路：顶点公式 t0=-2cos, min^2=4-4cos^2
ct=sp.symbols('ct',real=True)
print("check 4-4ct^2=3 ->",sp.solve(sp.Eq(4-4*ct**2,3),ct))

print("=== T1 平面 AB=5 AC=8 A=60 ===")
AB=sp.Matrix([5,0]);ang=sp.pi/3
AC=sp.Matrix([8*sp.cos(ang),8*sp.sin(ang)])
BC=AC-AB
print("|BC|",sp.simplify(BC.norm()),"AB.BC",sp.simplify(AB.dot(BC)))
AM=(AB+AC)/2
print("AM.BC",sp.simplify(AM.dot(BC)))

print("=== T2 ===")
A=sp.Matrix([2,-1,3]);B=sp.Matrix([0,3,-1])
x=sp.symbols('x',real=True);P=sp.Matrix([x,0,0])
print("P:",sp.solve(sp.Eq((P-A).dot(P-A),(P-B).dot(P-B)),x))
y=sp.symbols('y',real=True);Q=sp.Matrix([0,y,0])
g=sp.expand((Q-A).dot(Q-B))
print("QA.QB =",g,"=",sp.complete_square(sp.symbols('y'),g) if False else sp.factor(g))
print("min:",sp.minimum(g,y),"at",sp.solve(sp.diff(g,y),y))

print("=== T3 空间四边形 ===")
a0=sp.Matrix([0,0,0]);bb=sp.Matrix(sp.symbols('b1:4'));cc=sp.Matrix(sp.symbols('c1:4'));dd=sp.Matrix(sp.symbols('d1:4'))
E=(a0+dd)/2; F=(bb+cc)/2
EF=F-E; ABv=bb-a0; DC=cc-dd
print("EF-1/2(AB+DC)=",sp.simplify((EF-(ABv+DC)/2)).T)
G=(a0+F)/2; H=(cc+E)/2
GH=H-G
print("GH in AB,AC,AD:",sp.simplify(GH).T)
# 共面性 E F G H
M=sp.Matrix([(G-E).T,(F-E).T,(H-E).T])
print("rank symbolic:",M.rank())
import random
random.seed(5)
for _ in range(5):
    P4=[sp.Matrix([random.randint(-7,7) for i in range(3)]) for _ in range(4)]
    AA,BB,CC,DD=P4
    Ee=(AA+DD)/2;Ff=(BB+CC)/2;Gg=(AA+Ff)/2;Hh=(CC+Ee)/2
    Mx=sp.Matrix([(Gg-Ee).T,(Ff-Ee).T,(Hh-Ee).T])
    print("  rank:",Mx.rank())

print("=== T4 四面体 重心 交点 ===")
lam,mu=sp.symbols('lam mu',real=True)
a,b,c,d=[sp.Matrix(sp.symbols(v+'1:4')) for v in 'abcd']  # position vectors from A? use A origin
# A origin: AB=b, AC=c, AD=d ; G1=(b+c+d)/3
G1=(b+c+c)*0  # placeholder
G1=(b+c+d)/3
AQ=lam*G1
G2=(c+d)/3   # centroid of ACD with A origin: (0+c+d)/3
Q2=(1-mu)*b+mu*G2
eqs=[sp.Eq(AQ[i],Q2[i]) for i in range(3)]
s=sp.solve(eqs,[lam,mu],dict=True)
print("lam,mu:",s)
print("AQ =",AQ.subs(s[0]).T, " -> 1/4(b+c+d)?", sp.simplify(AQ.subs(s[0])-(b+c+d)/4).T)
# G3 centroid of ABD
G3=(b+d)/3
CG=sp.Rational(1,4)*(b+c+d)-c
CG4=G3-c
print("CG = k*(C->G3)?", sp.simplify(CG-R(4,3)*CG4).T)
