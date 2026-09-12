# -*- coding: utf-8 -*-
import math
from fractions import Fraction as F
r3=math.sqrt(3)
print("== 题1: F=kQq/d^2*cos^3θ < kQq/d^2  (cosθ<1 for R>0) OK; k units: kg*m^3*s^-4*A^-2: N*m^2/C^2=(kg*m/s^2)*m^2/(A*s)^2 ✓")
# == 题2 (2021海南): Q on smooth N: F along PQ (⊥M); N-M angle between = 60°; angle F vs slope N=30°
# Q: F cos30 = mg sin60 = mg cos30 -> F=mg; P: f = mg sin60; N2 = mg cos60 + F; mu = f/N2
mu=(r3/2)/(0.5+1.0); print("== 题2: mu_min =",mu,"= √3/3?",r3/3)
# == 题3 (2020浙江): order down-slope A,B,C; solve q_C, r^2, F on A
import sympy as sp
q0,k,M,g_,a_,r,qC=sp.symbols('q0 k M g alpha r q_C',positive=True)
# C (bottom): k q0 qC/r^2 = M g sinα + k q0 qC/(2r)^2
eqC=sp.Eq(k*q0*qC/r**2, M*g_*sp.sin(a_)+k*q0*qC/(2*r)**2)
# B (middle): k q0^2/r^2 = M g sinα + k q0 qC/r^2
eqB=sp.Eq(k*q0**2/r**2, M*g_*sp.sin(a_)+k*q0*qC/r**2)
sols=sp.solve([eqC,eqB],[qC,r**2],dict=True)
for s in sols: print("== 题3: qC=",sp.simplify(s[qC]),"; r^2=",sp.simplify(s[r**2]))
# F on A: k q0^2/r^2 (pull to B, down) - k q0 qC/(4r^2)(push up)... net Coulomb down = ?
FA=k*q0**2/r**2 - k*q0*(4*q0/7)/(4*r**2)
FAsub=FA.subs(r**2, sp.solve([eqC,eqB],[qC,r**2],dict=True)[0][r**2])
print("== 题3: |F_Coul on A| =", sp.simplify(FAsub), "(expect 2Mg sinα); spring x=3Mg sinα/k0")
# == 题5: unique sign combo P(-)Q(+) — logical, check: P left: E ext right; need F_C on P right → attract → Q+ ; on Q: attract left vs qE: need Q+ → right ✓
# == 题6: a = √3 kq²/ml²; F=3ma; qC=-2q
kq=1.0; m=1.0; l=1.0
FBA=kq/l**2; FCA=FBA/sp.Rational(1,2)  # FCA sin30=FBA -> FCA=2
qC_=2; aC=math.sqrt(3)/1*math.sqrt(1)**-0; a_=FCA*math.cos(math.pi/6)/1
print("== 题6: FCA/FBA=",float(FCA/FBA),"(=2 → qC=−2q); a=",a_,"=√3?",math.sqrt(3),"; F_total=",3*a_,"= 3√3?",3*math.sqrt(3),"; optD 2√3?",2*math.sqrt(3))
# == 题8: A above O, B horiz-through-O below rod line → repulsion: F cos30 = mg sin30 → F=mg/√3; N = mg cos30 − F sin30 = ?
Fv=1/r3; Nv=r3/2-Fv/2; print("== 题8: F=",Fv,"N=",Nv,"equal?",abs(Fv-Nv)<1e-12,"(=√3/3 mg)")
# == 题9: tan²α=3→α=60°; F=mg tan60=√3mg; NA=mg/cos60=2mg; NB=3mg/cos30=3.464
Fk=r3; print("== 题9: F=√3mg=",Fk," NA=",1/0.5," NB=",3/(r3/2),"=2√3?",2*r3)
# == 题10: OC = l/sqrt(1+F²/(m1m2g²)) — F↑→OC↓; AC/BC = m2/m1 const ✓
# == 题11:
kk=9e9; QM=1e-6; QN=r3/2*1e-6; d=0.03
Ff=kk*QM*QN/d**2; print("== 题11: F=",Ff,"=5√3?",5*r3)
m_g=Ff/math.tan(math.radians(60)); T=m_g/math.cos(math.radians(60))
print("   mg=",m_g,"(→m=0.5kg g=10)  T=",T,"(10N)  f_ground=T·cos30=",T*math.cos(math.radians(30)),"(5√3=8.66)  与Tsin60等值✓")
muD=(2*10*0.5-5)/(2*10*r3/2); print("   μ=(mb g sinθ − mg)/(mb g cosθ)=",muD,"=√3/6?",r3/6,"optD √3/3?",r3/3)
# == 题13: B: F=√3mg, N_B=mg inward; A: N_A=2.5mg, f=√3/2 mg, μmin=√3/5
mu13=(r3/2)/2.5; print("== 题13: μmin=",mu13,"=√3/5?",r3/5,"=√3/4?",r3/4,"; N_A=mg+√3mg·cos30=",1+math.sqrt(3)*math.sqrt(3)/2)
# == 题14: E_M/E_N = tan60/tan30; r ratio
print("== 题14: E_M/E_N=",r3/(1/r3),"→ 3:1; r_M:r_N=1:√3 ✓, optB √3:1 误")
# == 题15: expansion F=kQq*2lh/(h²−l²/4)² ≈ 2kQql/h³ — wait: (r₊²−r₋²)=2hl... F=kQq[(h+l/2)^-2-(h-l/2)^-2]... ≈ kQq·2l/h³ ✓
h=10.0;l=0.1;Q=1;q=1;K=1
Fexact=K*Q*q*(1/(h-l)**2-1/(h)**2*0)  # use ±l/2 separation:
Fex=K*Q*q*(1/(h-l/2)**2-1/(h+l/2)**2); print("== 题15: exact=",Fex,"2kQql/h³=",2*K*Q*q*l/h**3,"≈match")
# == 题16:
g=10; s53=0.8; c53=0.6
QA=7.5; AB=4.5
kQqm=(8-6.4)*QA**2/c53*c53  # mgsin53 − (kQq/AQ²)cos53 = ma → kQq/m = (8−6.4)·56.25/0.6
kQqm=(8-6.4)*56.25/0.6; print("== 题16: kQq/m=",kQqm)
aA=g*s53-kQqm*(4.5/7.5**3); aC=g*s53+kQqm*(4.5/7.5**3)
print("   a_A rod-comp check:",aA,"(6.4)  a_C=",aC,"(9.6)")
aD=g+kQqm/10**2; print("   at D: F=kQq/100 →",kQqm/100,"m/s²; a_D=",aD,"(11.5) ✓")
# v_C (deleted option B) cross-check: mg·AC·sin53 = ½v² → v=sqrt(2*8*9)? AC=9m: v=sqrt(2*10*9*0.8)=12 ✓ (B claimed 10, itself wrong)
print("   v_C=",math.sqrt(2*10*9*0.8),"(12; opt B 10 wrong)")
# == 题17: v1²=2gd sinθ; v2=v1/2; v3²=v²+v2²
import sympy as sp
gdv=sp.symbols('g d theta',positive=True)
v1sq=2*sp.symbols('g')*sp.symbols('d')*sp.sin(sp.symbols('θ'))
print("== 题17: v2²=v1²/4=gd sinθ/2 → v3=√(v²+½gd sinθ) ✓ D; opt C 无½ 误; qB=mgl²sinθ/kQ ✓")
# == 题18: trivial F=mgtanα; E=F/q; Q=Fr²/kq ✓
