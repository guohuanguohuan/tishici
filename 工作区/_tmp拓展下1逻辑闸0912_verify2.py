from sympy import *
x,y,z=symbols('x y z',real=True); O=Matrix([x,y,z])
def circ(pts):
    p0=pts[0]
    eqs=[expand((O-p).dot(O-p)-(O-p0).dot(O-p0)) for p in pts[1:]]
    sol=solve(eqs,[x,y,z],dict=True)[0]
    Oc=Matrix([simplify(sol[v]) for v in (x,y,z)])
    return simplify((Oc-p0).dot(Oc-p0)), Oc
M=Matrix; S=Rational
p=[M(v) for v in [(0,0,0),(2,0,0),(0,2,0),(2,2,0),(0,0,2)]]
R2,c=circ(p); r=symbols('r',positive=True); rv=solve(Eq(2-2*r,r*sqrt(2)),r)[0]
print("093 R2",R2,"S外",expand(4*pi*R2),"r_in",rv,"S总",expand(4*pi*R2+4*pi*rv**2))
for nm,pts in [("097",[(sqrt(3),0,0),(-sqrt(3),0,0),(0,1,0),(0,S(1,2),sqrt(3)/2)]),
              ("098",[(0,0,0),(6,0,0),(0,8,0),(2,2,2)]),
              ("086",[(2/sqrt(3),0,0),(-1/sqrt(3),1,0),(-1/sqrt(3),-1,0),(0,0,sqrt(S(2,3)))]),
              ("090",[(0,0,0),(4,0,0),(2,2,0),(1,0,sqrt(3))]),
              ("095",[(1,0,0),(-1,0,0),(0,sqrt(3),0),(0,-sqrt(3)/2,S(3,2))]),
              ("096",[(1,0,0),(-1,0,0),(0,3*sqrt(3),0),(0,-3*sqrt(3)/2,S(9,2))]),
              ("094",[(1,0,0),(-1,0,0),(0,sqrt(3),0),(0,0,sqrt(3))])]:
    R2,cc=circ([M(v) for v in pts]); print(nm,"R2=",R2,"S=",expand(4*pi*R2))
a=symbols('a',positive=True); print("091 a=",solve(Rational(4,3)*pi*(Rational(9,16)*a**2)**Rational(3,2)-36*pi,a))
s=3; R2,O9=circ([M([0,0,0]),M([s,0,0]),M([0,s,0]),M([0,0,s])]); r9=simplify(s/(3+sqrt(3))); O1=M([r9]*3); d=simplify((O9-O1).norm())
print("109 R2",R2,"r_in",r9,"|O1O2|",d,"minEF",simplify(sqrt(R2)-d-r9),"resid",simplify(sqrt(R2)-d-r9-(2*sqrt(3)-3)),"V外",simplify(Rational(4,3)*pi*R2**Rational(3,2)),"S内",expand(4*pi*r9**2))
print("110 max",simplify(Rational(6,4)-Rational(6,36)))
t=symbols('t',real=True); f=(2-t)**2/(2*((2-t)**2+4*t**2))
print("068b cos@0",simplify(sqrt(f.subs(t,0))),"@1",simplify(sqrt(f.subs(t,1))),"df",factor(diff(f,t)))
u=M([-S(1,2),sqrt(3)/2,0]); BC=M([1,0,0]); BA=M([-S(1,2),0,sqrt(3)/2]); vC=BC-BC.dot(u)*u; vA=BA-BA.dot(u)*u
print("067 cos=",simplify(vA.dot(vC)/(vA.norm()*vC.norm())))
A=M([-4,0,0]);D=M([0,3*sqrt(3),0]);E=M([-8,3*sqrt(3),0]);C=M([0,-2*sqrt(3),6])
CE=E-C; DC=C-D; DF=-D
print("070(2) tan=",simplify(sqrt(CE[1]**2+CE[2]**2)/Abs(CE[0])),"070(3) cos=",simplify(DC.dot(DF)/(DC.norm()*DF.norm())))
def dih(P1,L,P2):
    dd=L/L.norm(); v1=P1-P1.dot(dd)*dd; v2=P2-P2.dot(dd)*dd; return simplify(v1.dot(v2)/(v1.norm()*v2.norm()))
D7=M([0,0,0]);A7=M([2,0,0]);C7=M([0,2,0]);B7=M([2,1,0]);P7=M([0,-1,sqrt(3)]); n7=(A7-P7).cross(B7-P7)
print("074①",simplify(abs(n7[2])/n7.norm()),"②",dih(P7-D7,B7-D7,C7-D7),"③",dih(P7-B7,C7-B7,D7-B7))
H=sqrt(2);E75=M([1,1,H/2]);A1=M([1,0,H]);C1=M([0,1,H]);D75=M([0,0,0])
n1=(A1-E75).cross(C1-E75); n2=A1.cross(C1); print("075(3)",simplify(abs(n1.dot(n2))/(n1.norm()*n2.norm())))
Ad=M([1,0,0]);Cd=M([0,1,0]);Md=M([0,S(1,2),1]);s2=symbols('s'); nd=(Ad-Cd).cross(Ad-Md)
print("077(1)",simplify(abs(nd[2])/nd.norm()),"(2) s=",solve(nd.dot(M([-1,0,s2])),s2))
print("071",simplify(M([-1,1,1]).dot(M([0,1,1]))/(sqrt(3)*sqrt(2))))
t78=symbols('t78',positive=True); Mz=M([-t78,0,sqrt(3)*(1-t78)]);Bz=M([-1,1,0]); nz=Mz.cross(Bz)
print("078 sol",solve(Eq(nz[1]**2/nz.dot(nz),S(3,10)),t78))
print("103",simplify(4*pi*(2*sqrt(6)/12)**2),"107",simplify(Rational(4,3)*pi*(sqrt(3)/2)**3),"108",simplify((2*sqrt(6)/12)/2))
aa=symbols('aa',positive=True); print("105 resid",simplify(2*aa/(2+sqrt(2))-aa*(2-sqrt(2))),"104",solve(Eq(sqrt(symbols('h')**2+9),3*symbols('h')-3),symbols('h')))
print("087 S=",4*pi*Rational(5,16),"083 R=",simplify(sqrt(Rational(9,2))),"084",simplify(Rational(3,2)+sqrt(6)/6),"085",simplify(sqrt(3)+sqrt(3)/3),"088",simplify(sqrt(8)))
print("099",simplify(Rational(4,3)*pi*(2*sqrt(3))**3),"100",expand(4*pi*((sqrt(2)-1)/2)**2),"106",simplify(Rational(1,2)*sqrt(3)*(2*sqrt(3))**2*2/2))
print("098 r_in",simplify(Rational(3,2)/(24+24*sqrt(2))*3*8/8*8),simplify(48/(24+24*sqrt(2))))
print("081",4*pi*9,"082",simplify(4*(sqrt(3)/2)/sqrt(6)),"080",simplify(sqrt(6)/4))
