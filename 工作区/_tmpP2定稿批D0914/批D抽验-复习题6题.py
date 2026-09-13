# 批D抽验-复习题6题.py —— P2第10章 章末板块「复习题选编」定量6题独立复算
# 口径：教材章末9题无源答案，全量自算；本脚本对定量6题独立复算（先自算后对定稿＝盲解精神）。
# 题2/3/9 为定性说理题，不设脚本（说理链入定稿详解）。产出日 2026-09-14。
import math

out = []
def w(s):
    out.append(s)
    print(s)

# ---- 题1（教材A组1）：电子从 b(0V) 等势面移到 e(15V) 等势面 ----
e = 1.6e-19
W = -e * (0 - 15)
w(f"题1(A1) W_be = q(φ_b−φ_e) = (−e)(0−15V) = {W:.3e} J（=15eV，做正功）")

# ---- 题4（教材A组4）：U_AC=W/q；副证＝点电荷等距等势面电势差比较 ----
Uac = 1.92e-5 / 1.6e-6
w(f"题4(A4) U_AC = W/q = 1.92e−5/1.6e−6 = {Uac:.4f} V ⇒ φ_A = {Uac:.4f} V（取 φ_C=0）")
kQ, r = 1.0, (1.0, 2.0, 3.0)
Uab = kQ * (1/r[0] - 1/r[1]); Ubc = kQ * (1/r[1] - 1/r[2])
w(f"题4(A4) 副证（设 kQ=1，r=1/2/3 等距）: U_AB={Uab:.4f} > U_BC={Ubc:.4f} ⇒ {Uab > Ubc}")

# ---- 题5（教材A组5）：C=1.5×10⁻⁴μF，Q=6×10⁻⁸C，d=1mm ----
C, Q5, d5 = 1.5e-4 * 1e-6, 6e-8, 1e-3
U5 = Q5 / C; E5 = U5 / d5
w(f"题5(A5) C=1.5e−10 F ⇒ U=Q/C={U5:.1f} V；E=U/d={E5:.3e} V/m")

# ---- 题6（教材B组1）：等量异种（+Q 上、−Q 下，间距 2a）库仑直接求和 ----
a = 1.0
charges = ((+kQ, (0.0, a)), (-kQ, (0.0, -a)))
def field(p):
    x, y = p; Ex = Ey = 0.0
    for q0, (cx, cy) in charges:
        dx, dy = x - cx, y - cy; r2 = dx*dx + dy*dy; rr = math.sqrt(r2)
        Ex += q0 * dx / rr**3; Ey += q0 * dy / rr**3
    return Ex, Ey
def pot(p):
    x, y = p; s = 0.0
    for q0, (cx, cy) in charges:
        s += q0 / math.hypot(x - cx, y - cy)
    return s
w("题6(B1) 中垂线(x轴)电势 φ: " + ", ".join(f"x={x}:{pot((x,0)):.2e}" for x in (-3,-1,0,1,3)) + "（恒0⇒等势线✓）")
w("题6(B1) 中垂线|E|: " + ", ".join(f"x={x}:{math.hypot(*field((x,0))):.4f}" for x in (0,1,2,3)) + "（中点最大✓）")
w("题6(B1) 连线段(y轴向+Q)|E|: " + ", ".join(f"y={y}:{math.hypot(*field((0,y))):.4f}" for y in (0,0.5,0.9)) + "（向+Q渐增✓）")
w("题6(B1) 连线段φ: " + ", ".join(f"y={y}:{pot((0,y)):.4f}" for y in (0,0.5,0.9)) + "（向+Q升高✓）")

# ---- 题7（教材B组2）：v=√(2eUh/m) 数值与极限核 ----
m = 9.1e-31
v7 = math.sqrt(2 * e * 100.0 * 0.01 / m)
w(f"题7(B2) 数值例(U=100V,h=1cm): v={v7:.3e} m/s；符号式 v=√(2eUh/m)，h→0⇒v→0、U↑⇒v↑（极限自洽✓；题给 d 为背景量不入结果）")

# ---- 题8（教材B组3）：坐标法（A=(0,y0), B=(x0,y0), C=(x0,0)，按渲染图 AB:BC≈2:√3） ----
x0, y0 = 2.0, math.sqrt(3.0)
q8, Wab, Wbc = -6e-6, -2.4e-5, 1.2e-5
Uab8 = Wab / q8; Ubc8 = Wbc / q8
phiA = Uab8; phiC = -Ubc8   # φ_B=0
Ex = Uab8 / x0; Ey = -Ubc8 / y0
w(f"题8(B3) U_AB={Uab8:.4f} V，U_BC={Ubc8:.4f} V；φ_A={phiA:.4f} V，φ_C={phiC:.4f} V（φ_B=0）")
w(f"题8(B3) AB中点 φ_M=(φ_A+φ_B)/2={(phiA+0)/2:.4f} V ＝ φ_C ⇒ MC 为等势线 ✓")
w(f"题8(B3) E=({Ex:.4f},{Ey:.4f})（线性场梯度）；E·MC=(E)·(x0/2,−y0)={Ex*x0/2 + Ey*(-y0):.3e} ⇒ E⊥MC ✓；指向右（{Ex>0}）上（{Ey>0}）低电势侧 ✓")
w(f"题8(B3) E 与 AB(A→B)夹角 = {math.degrees(math.atan2(Ey, Ex)):.1f}°（按测距比例 AB:BC=2:√3；原图精确比例随图10-7自绘钉死，详解构造法不依赖该角）")

with open(r"C:/提示词/工作区/_tmpP2定稿批D0914/批D抽验-复习题6题-输出.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("SAVED")
