from sympy import *
import json

out={}
# ---------- 拓-069 ----------
# 原梯形 BC=CD=2, AB=4, O=AB中点 => OA=OD=2, OA 垂直 OD ; OBCD 正方形边2
O=Matrix([0,0,0]); B=Matrix([2,0,0]); C=Matrix([2,2,0]); D=Matrix([0,2,0])
t=symbols('t',real=True)
A=Matrix([2*cos(t),0,2*sin(t)])      # 折叠圆轨迹 (OA=2, OA 垂直 OD)
sol=solve(Eq((A-C).dot(A-C),12),t)   # AC^2=(2sqrt3)^2=12
print("069 AC=2sqrt3 -> cos t in",sol)
Af=Matrix([0,0,2])
M=(Af+D)/2; N=(Af+B)/2
n1=Af.cross(M).cross(Af.cross(N)) if False else (M.cross(N))
print("069 OM,ON:",M.T,N.T,"n=",n1.T,"cos with z:",Abs(n1[2])/n1.norm())
print("069 AC.OM:",((C-Af).dot(M)).simplify())

# ---------- 拓-073 ----------
h,t2=symbols('h t2',positive=True)
Bs=Matrix([1,0,0]); Cs=Matrix([-1,0,0]); Ds=Matrix([0,sqrt(3),0]); As=Matrix([0,0,h])
E=As+t2*(Cs-As)                       # t2=AE/AC
BD=Ds-Bs; BE=E-Bs
n=BD.cross(BE)
cosd=simplify(Abs(n[2])/n.norm())     # 与底面(z=0)夹角余弦(二面角 E-BD-C)
print("073 cos dihedral:",cosd)
print("073 t=1/3 ->",simplify(cosd.subs(t2,Rational(1,3))))
print("073 h solve from ①②:",solve(Eq(cosd.subs(t2,Rational(1,3)),Rational(1,2)),h))
print("073 ③ -> h=3 ; then ②③ solve t:",solve(Eq(cosd.subs(h,3),Rational(1,2)),t2))

# ---------- 拓-076 ----------
a,c=symbols('a c',real=True)
A6=Matrix([0,0,0]); C6=Matrix([2,0,0]); B6=Matrix([1,sqrt(3),0])
A1=Matrix([a,0,c]); C1=C6+A1
E6=(A1+C1)/2; F6=(B6+C6)/2; G6=C6+(A1)/3
EG=G6-E6; EA=A6-E6; EF=F6-E6
u=EG/EG.norm()
vA=(EA-(EA.dot(u))*u); vF=(EF-(EF.dot(u))*u)
cos6=simplify(vA.dot(vF)/(vA.norm()*vF.norm()))
print("076 cos(a,c)=",cos6)
for (av,cv) in [(1,sqrt(3)),(-1,sqrt(3))]:
    print("   a=%s c=sqrt3 ->"%(av), nsimplify(simplify(cos6.subs({a:av,c:cv}))), float(cos6.subs({a:av,c:cv})))
print("076 ③ solve a:",solve(Eq(( (a+4)/(2*sqrt(5+2*a)) )**2, Rational(3,4)),a))

# ---------- 拓-062 ----------
H=symbols('H',positive=True)
A2=Matrix([0,0,0]);B2=Matrix([2,0,0]);D2=Matrix([0,2,0]);P2=Matrix([1,0,H])
AB=Matrix([1,0,0]); PD=D2-P2
c2=simplify(PD.dot(AB)/PD.norm())
nA=Matrix([0,1,0]); nB=Matrix([0,2*H,4])
c3=simplify(nA.dot(nB)/(nA.norm()*nB.norm()))
print("062 cos(PD,AB)=",c2," cos(planes)=",c3)
for hv in [sqrt(3),2,1]:
    print("   H=",hv," ->(2)",nsimplify(c2.subs(H,hv)),"(3)cos",nsimplify(c3.subs(H,hv)))

# ---------- 拓-059 ----------
s=symbols('s',positive=True)
B5=Matrix([0,0,0]);A5=Matrix([2,0,0]);C5=Matrix([0,2,0]);A15=Matrix([2,0,2]);C15=Matrix([0,2,2]);D15=Matrix([0,0,2])
for name,Dp in [("CC1中点",Matrix([0,2,1])),("A1C1中点",Matrix([1,1,2])),("A1C中点",Matrix([1,1,1])),("AC1中点",Matrix([1,1,1]))]:
    BD=Dp-B5; BA=A5-B5; BC=C5-B5
    vA_=BA-BA.dot(BD)/BD.dot(BD)*BD; vC_=BC-BC.dot(BD)/BD.dot(BD)*BD
    cv=simplify(vA_.dot(vC_)/(vA_.norm()*vC_.norm()))
    print("059 D=%s cos="%name,cv,"sin=",simplify(sqrt(1-cv**2)))
