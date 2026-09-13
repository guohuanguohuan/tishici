# P2 批A 抽验6题盲解（sed 单行窗制精神：独立重算，不抄源详解链）
# 题样：01-G4(池简2/源Q3)、01-E1(池简4/源Q62)、02-G1(池简6/源Q10)、02-G3(池中6/源Q11)、
#       02-G5(池中8/源Q14)、02-E6(池中12/源Q69)——两节各3题，覆盖单选/多选/填空三形态。
import math

ok = []

# 01-G4 池简2(Q3)：E=W1/(q·L_ab)；W2=q·E·L_bc·cos60°
E = 1.6e-7 / (2e-8 * 0.05)
W2 = 2e-8 * E * 0.12 * math.cos(math.radians(60))
ok.append(("01-G4 Q3", E, 160.0, W2, 1.92e-7))

# 01-E1 池简4(Q62)：W_G+W_f+W_电=ΔEk；Δ机=W_f+W_电
W电 = 24 - 48 - (-16)
D机 = -16 + W电
ok.append(("01-E1 Q62", W电, -8.0, D机, -24.0))  # ⇒ C(电势能增8J)、D(机械能减24J)，AB错

# 02-G1 池简6(Q10)：U_AB=75>0⇒φA>φB；U_BC=-200⇒φB<φC；U_AC=-125⇒φA<φC
U_AB, U_BC = 75.0, -200.0
U_AC = U_AB + U_BC
rel = (U_AB > 0, U_BC < 0, U_AC < 0)  # φA>φB, φB<φC, φA<φC ⇒ φC>φA>φB
ok.append(("02-G1 Q10", U_AC, -125.0, rel, (True, True, True)))

# 02-G3 池中6(Q11)：φA=-W1/q1，φB=-W2/q2（无穷远为0）；W3=q3·U_AB
phiA = -(4e-8) / 1e-9
phiB = -(-6e-8) / (-2e-9)
Uab = phiA - phiB
W3 = (-3e-9) * Uab
ok.append(("02-G3 Q11", (phiA, phiB), (-40.0, -30.0), W3, 3e-8))

# 02-G5 池中8(Q14)：mg sin30°−kQq/(2L)²=m·g/3 ⇒ kQq/L²=2mg/3；a_B=(kQq/L²−mg sin30°)/m
kQq_L2 = None
# 由 A 点：mg/2 − kQq/(4L²) = mg/3 ⇒ kQq/(4L²) = mg/6
kQq_over_4L2 = (1/2 - 1/3)  # ×mg
kQq_over_L2 = 4 * kQq_over_4L2  # = 2mg/3
aB = (kQq_over_L2 - 1/2)  # ×g
# A→B 动能定理：mgL·sin30°+qU_AB=0 ⇒ U_BA=−U_AB=mgL·sin30°/q = mgL/(2q)
UBA_unit = math.sin(math.radians(30))  # ×mgL/q
ok.append(("02-G5 Q14", aB, 1/6, UBA_unit, 0.5))

# 02-E6 池中12(Q69)：x=20cm 斜率零 ⇒ kQ_M/(2r)²=kQ_N/r² ⇒ Q_M:Q_N=4:1（C 说 2:1 错）；x0 处斜率非零⇒E≠0（B 错）
ratio = (2 ** 2) / (1 ** 2)  # Q_M/Q_N = 4
judge = {"A": True, "B": False, "C": False, "D": True}  # A对B错C错D对 ⇒ 答案 AD
ok.append(("02-E6 Q69", ratio, 4.0, (judge["A"], judge["B"], judge["C"], judge["D"], "".join(k for k, v in judge.items() if v)), (True, False, False, True, "AD")))

print(f"{'题号':<12}{'实算':>28}{'应得':>28}{'判定'}")
for name, got, want, got2, want2 in ok:
    def close(a, b):
        if isinstance(a, tuple) and isinstance(b, tuple):
            return all(close(x, y) for x, y in zip(a, b)) and len(a) == len(b)
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return abs(a - b) < 1e-6
        return a == b
    g1, g2 = close(got, want), close(got2, want2)
    print(f"{name:<12}{str(got)+', '+str(got2):>34}{str(want)+', '+str(want2):>34}{'一致 ✓' if g1 and g2 else '✗ 存疑'}")
