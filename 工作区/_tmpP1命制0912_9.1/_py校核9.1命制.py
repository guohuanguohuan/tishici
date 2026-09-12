from fractions import Fraction as F
ok=[]
def chk(name, got, want):
    ok.append((name, str(got), str(want), got==want))

# 简-2 比荷
ratio = F("1.60")*F(10)**-19 / (F("9.11")*F(10)**-31)
print("比荷 =", float(ratio), "C/kg  -> 1.76e11?", abs(float(ratio)-1.76e11)/1.76e11 < 0.005)
print("倒数(质量/电荷量) =", 1/float(ratio), "kg/C -> 5.69e-12?", abs(1/float(ratio)-5.69e-12)/5.69e-12<0.01)
# 数量级错项 1.76e-11 显然不等
chk("简-2 数量级", round(float(ratio)/1e11,2), 1.76)

# 简-3 两球异号接触均分
a,b = F(3),F(-5)
chk("简-3 均分", (a+b)/2, F(-1))
chk("简-3 绝对值平均(误项B)", (abs(a)+abs(b))/2, F(4))

# 中-1 反求: A与D接触后 D=+2.5 -> A原=+5.0, B=-5.0
d = F("2.5")
chk("中-1 A初值", d*2, F(5))

# 难-1: 甲=-q 乙=+q 丙=0 ; 乙-丙 -> 各 q/2 ; 甲-丙 -> 各 (-q+q/2)/2 = -q/4
q = F(4)
甲,乙,丙 = -q, q, F(0)
乙,丙 = (乙+丙)/2,(乙+丙)/2
甲,丙 = (甲+丙)/2,(甲+丙)/2
print("难-1 q=4 时 甲,乙,丙 =",甲,乙,丙)
chk("难-1 丙末 = -q/4", 丙, -q/4)
chk("难-1 总和守恒", 甲+乙+丙, F(0))
chk("难-1 由丙末=-1.0反求q", -4*F(-1), F(4))
chk("难-1 若误取丙末=+1.0 得 q", -4*F(1), F(-4))

# 难-2 六序枚举 q=8
from itertools import permutations
def run(seq, q=F(8)):
    st={'A':q,'B':-q,'C':F(0)}
    for x,y in seq:
        v=(st[x]+st[y])/2
        st[x]=v; st[y]=v
    return st
pairs=[('A','C'),('A','B'),('B','C')]
allres=[]
for first in pairs:
    for second in pairs:
        if second==first: continue
        st=run([first,second])
        allres.append((first,second,st))
        assert st['A']+st['B']+st['C']==0, "守恒破"
for f,s,st in allres:
    print("难-2", f, s, "->", "A=%s B=%s C=%s"%(st['A'],st['B'],st['C']))
print("C 可能值集合:", sorted({st['C'] for _,_,st in allres}, key=lambda v:str(v)), "序数=",len(allres))
print("不同末态数:", len({tuple(sorted((st['A'],st['B'],st['C']))) for _,_,st in allres}))
