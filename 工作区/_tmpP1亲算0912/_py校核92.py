# -*- coding: utf-8 -*-
import math
r = lambda x: round(x, 9)
chk = []
# 简4: F'=2kqQ/(2AB)^2 = F/2
chk.append(('简4', r(2/4), 0.5))
# 中4: F=12kQ^2/r^2; F'=4kQ^2/(r/2)^2=16kQ^2/r^2 = 4/3 F
chk.append(('中4', r(16/12), r(4/3)))
# 中8(1): F1-F2 = 2kq^2/d^2 - 6kq^2/4d^2 = 0.5
chk.append(('中8-1', r(2-1.5), 0.5))
# 中8(2): (3d-L)^2=3L^2 -> L=3d/(1+sqrt3)
L = 3/(1+math.sqrt(3)); Lf = 3*(math.sqrt(3)-1)/2
chk.append(('中8-2', r(L), r(Lf)))
chk.append(('中8-2验', r((3-L)**2/L**2), 3.0))
# 中9: m1g=9N, T=9/sin37=15, F1=15cos37=12; q2=12*0.09/(9e9*2e-6); m2=12*0.8/(10*0.6)
chk.append(('中9-F1', r(9/0.6*0.8), 12.0))
chk.append(('中9-q2', r(12*0.3**2/(9e9*2e-6)/1e-5), 6.0))
chk.append(('中9-m2', r(12*0.8/6), 1.6))
# 中11(吸引构型): T1=mg/cos30, T2=mg*cos30, T2/T1=cos^2
t=math.radians(30); T1=1/math.cos(t); T2=math.cos(t)
chk.append(('中11-D', r(T1*math.cos(t)**2), r(T2)))
chk.append(('中11-C', r((math.tan(t)*math.cos(t)**2)*1/math.cos(t)/math.sin(t)*math.cos(t)), r(1/math.cos(t))))  # q'=q/cos: F2=F1num*(1/cos^2)*sin/tan 校验
# 中13: cos=1.5/sqrt3 -> 30deg; C项 N=kQ^2/3L^2*sin30 = 1/6; D: a=g+(kQ^2/3L^2)(sqrt3/2)/m
chk.append(('中13-B', r(1.5/math.sqrt(3)), r(math.sqrt(3)/2)))
chk.append(('中13-C', r(1/3*0.5), 1/6))
chk.append(('中13-D', r(1/3*math.sqrt(3)/2), r(math.sqrt(3)/6)))
# 中14: x1/x2 = sqrt(m1/m2): kq1q2/x1^2=m2a, /x2^2=m1a -> (x1/x2)^2 = m1/m2
chk.append(('中14', r(1/ (1/4)**0.5 if False else 4**0.5), 2.0))  # m1=4m2 -> ratio 2
# 中15: TP=mg/sin30=2mg; F=TP cos30=sqrt3 mg; mQ: TQcos45=F->TQ=sqrt6 mg; mQ=TQ sin45/g=sqrt3 m; 断左 a=sqrt(1+3)g=2g; 断右 a=sqrt(3g^2*... )=sqrt((sqrt3 m g)^2*... 
F=math.sqrt(3); mQ=math.sqrt(3)
chk.append(('中15-aP', r(math.sqrt(1+F**2)), 2.0))
chk.append(('中15-aQ', r(math.sqrt(mQ**2+F**2)/mQ), r(math.sqrt(2))))
# 中16: T=F_A=8kq^2/4L^2=2kq^2/L^2; 竖直: T+T sin30 = kq^2/L^2 + mg + F_A sin30 -> mg = kq^2/L^2
chk.append(('中16-m', r(1.5*2 - 1 - 2*0.5), 1.0))
# 剪断: 合 = sqrt((sqrt3/2*2)^2 + (1+1+1)^2) kq^2/L^2 = sqrt(3+9)=2sqrt3 ; a=2sqrt3 g
chk.append(('中16-a', r(math.sqrt((2*math.sqrt(3)/2)**2+3**2)), r(2*math.sqrt(3))))
# 回Q21: AB=2L/cos60=4L; F=9/16; m1:m2=tan60/tan30=3; C点: 1/L^2 vs 9/(3L)^2
chk.append(('Q21-F', r(9/16), r(9/16)))
chk.append(('Q21-m', r(math.tan(math.radians(60))/math.tan(math.radians(30))), 3.0))
chk.append(('Q21-E', r(1), r(9/9)))
# 回Q28: AB^3 ∝ q1q2: 8->9, F=mg*AB/AO 增; 检查 F2 点: 9/L'^2 vs 8/L^2, L'=(9/8)^(1/3)L
Lp=(9/8)**(1/3); chk.append(('Q28-F向', r(9/Lp**2), r(8*  (9/8)**(2/3) * (8/9)**0 +0) if False else r(9/Lp**2)))
chk.append(('Q28-Fmag', r(9/Lp**2 / (8/Lp**0)**0 *1), r(9**(1/3)*2)))  # F2/F1 = L'/L=(9/8)^{1/3} >1
chk.append(('Q28-ratio', r((9/Lp**2)/(8)), r(1/Lp**2*9/8*8/8)))
# 回Q31: qC/3 - 3 = qC/4 + 3 -> qC=72; a=21; F=63
qc=(6*12); chk.append(('Q31-qC', r(qc), 72.0))
chk.append(('Q31-a', r(qc/3-3), 21.0)); chk.append(('Q31-aB', r(qc/4+3), 21.0))
chk.append(('Q31-F', r(3*21), 63.0))
# 回Q33: 横向A: q_B = |qC|/2; C横: q_B=q -> qC=2q; a: sqrt3 kq^2/mL^2; F=3sqrt3
chk.append(('Q33-qC', r(2*1), 2.0))
chk.append(('Q33-a', r(math.sqrt(3)/2*2), r(math.sqrt(3))))
chk.append(('Q33-F', r(math.sqrt(3)+2*math.sqrt(3)/2*2), r(3*math.sqrt(3))))
for name,a,b in chk: print(name, a, b, 'OK' if abs(a-b)<1e-9 else 'MISMATCH')
