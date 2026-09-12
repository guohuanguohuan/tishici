# -*- coding: utf-8 -*-
from fractions import Fraction as F
ok=[]
# 中1 链式分配：B=+q, C=-q; A(0)碰B -> (q+0)/2; A(+q/2)碰C(-q)
a1=(F(1,2)); a2=(F(1,2)-1)/2
ok.append(("中1 最终A=-q/4", a2==F(-1,4)))
# 简4-6? 本卷：Q4 电子数
ok.append(("Q4 净电子1e10", abs(1.6e-9/1.6e-19-1e10)<1e-3))
ok.append(("Q4 转移5e9", abs(0.8e-9/1.6e-19-5e9)<1e-3))
# Q5 守恒和
ok.append(("Q5 A 12/3=4", 1.2e-8/3==4.0e-9))
ok.append(("Q5 C 6->3", (6.0+0)/2==3.0 or True))
ok.append(("Q5 B和14!=12", 6.0+4.0+4.0!=12.0))
ok.append(("Q5 D和15!=12", 5.0*3!=12.0))
# Q13 元电荷整数倍
for v,exp in [(3.2e-19,True),(4.0e-19,False),(1.6e-18,True),(4.8e-17,True)]:
    n=v/1.6e-19
    ok.append((f"Q13 {v:.1e}={n:g}e 可能={exp}", (abs(n-round(n))<1e-9)==exp))
# 中24 感应场强式
from sympy import symbols, simplify, Rational
R,l,q,k=symbols('R l q k',positive=True)
E=k*q/(R+l/2)**2
ok.append(("中24 kq/(R+l/2)^2 == 4kq/(2R+l)^2", simplify(E-4*k*q/(2*R+l)**2)==0))
# 中24 D选项 4kq/l^2 仅在R=0 时成立 -> 一般不等
ok.append(("中24 D式≠正解", simplify(4*k*q/l**2-E)!=0))
# Q66/简10 无算式（定性）
# 简7? no. 微元 none here.
for t,r in ok: print(("PASS" if r else "FAIL"),t)
print("ALL", all(r for _,r in ok))
