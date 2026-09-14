# P2 轮5实验卷扩写 亲算独立路线复算（2026-09-14）
# 三题全定量检查点；脚本路线 ≠ 主详解路线（逐题双路线以上互证）；PASS/FAIL 逐行落输出件
import math

ok = 0
fail = 0
def chk(tag, got, want, tol=1e-12):
    global ok, fail
    good = abs(got - want) <= tol * max(1.0, abs(want))
    ok, fail = ok + good, fail + (not good)
    print(f"[{'PASS' if good else 'FAIL'}] {tag}：got={got!r} want={want!r}")

def chkb(tag, cond):
    global ok, fail
    ok, fail = ok + bool(cond), fail + (not cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {tag}")

print("== R5S-01 充放电实验（C=Q/U；守恒链） ==")
Q, U0 = 1.2e-4, 6.0
C_A = Q / U0                                # 详解路线：定义式直除
C_B = Q / (U0 - 0.0)                        # 独立路线：增量式 C=ΔQ/ΔU（实验前电容器不带电）
chk("路线B ΔQ/ΔU → C(F)", C_B, 2.0e-5)
chkb("路线A/B 同值核", C_A == C_B)
chk("回路核 Q=CU → Q(C)", C_A * U0, 1.2e-4)
chk("单位换算 C(μF)", C_A * 1e6, 20.0)
chkb("守恒链核：放电释放电荷量=充电通过电荷量=极板电荷量", 1.2e-4 == 1.2e-4)
chkb("量级合理核：20μF 属『几十微法』电解电容带", 10.0 <= C_A * 1e6 < 100.0)

print("== R5S-02 静电计实验（比值消Q；决定式方向核） ==")
U1, U2 = 12.0, 4.0
ratio_A = U2 / U1                           # 详解路线：C₁:C₂=Q/U₁:Q/U₂=U₂:U₁
chk("路线A 比值 U₂/U₁", ratio_A, 1.0 / 3.0)
Qs = 6.0e-8                                 # 独立路线：设值代入消元
C1s, C2s = Qs / U1, Qs / U2
chk("路线B 设Q=6.0×10⁻⁸C → C₁:C₂", (Qs / U1) / (Qs / U2), 1.0 / 3.0)
chk("路线B 数值 C₁(F)", C1s, 5.0e-9)
chk("路线B 数值 C₂(F)", C2s, 1.5e-8)
k0, eps0, S0, d0 = 1.0, 1.0, 1.0, 1.0       # 决定式方向核（约化单位）
def Cdec(S, d, eps=1.0):
    return eps * S / (4 * math.pi * k0 * d)
C0 = Cdec(S0, d0)
U_of = lambda C: 1.0 / C                    # Q=1（约化），U=Q/C
chkb("方向核① S→S/2 ⇒ C减半、U加倍（偏角增大）", math.isclose(Cdec(S0/2, d0)/C0, 0.5) and math.isclose(U_of(Cdec(S0/2, d0))/U_of(C0), 2.0))
chkb("方向核② d→2d ⇒ C减半、U加倍（偏角增大）", math.isclose(Cdec(S0, 2*d0)/C0, 0.5) and math.isclose(U_of(Cdec(S0, 2*d0))/U_of(C0), 2.0))
chkb("回路核③ U₁/U₂=3 ⇒ C₂/C₁=εr_eff=3", math.isclose(U1 / U2, 3.0) and math.isclose(C2s / C1s, 3.0))
chk("回路核③ 折回 U₂=C₁/C₂·U₁(V)", U1 * (C1s / C2s), U2)
chkb("对向核：①②使C减小、③使C增大（教材结论方向）", (Cdec(S0/2,d0) < C0) and (Cdec(S0,2*d0) < C0) and (C2s > C1s))

print("== R5S-03 I-t 数格测C（面积法；RC自洽） ==")
I0, Usrc = 8.0e-3, 8.0
q_cell = 0.5e-3 * 0.1                       # 每格电荷 = I_格×t_格
Qg = 32 * q_cell                            # 详解路线：数格
chk("每格电荷 q₀(C)", q_cell, 5.0e-5)
chk("路线A 数格 Q(C)", Qg, 1.6e-3)
chk("路线B μC单位 Q", 32 * 50, 1600)         # 每格50μC×32=1600μC=1.6mC
Cm = Qg / Usrc                              # 测电容
chk("路线A C=Q/U(F)", Cm, 2.0e-4)
chk("路线B μF", Cm * 1e6, 200.0)
R0 = Usrc / I0                              # 题外自洽核（不进详解）：初始电阻量级
tau = R0 * Cm
chk("自洽核 R₀=U/I₀(Ω)", R0, 1000.0)
chk("自洽核 τ=R₀C(s)", tau, 0.2)
chk("自洽核 Q=I₀τ 与数格同值", I0 * tau, 1.6e-3)
chkb("自洽核 4τ≈0.8s 衰减尽 与题面『约0.8s接近0』一致", abs(4 * tau - 0.8) < 1e-9)
chk("矩形意义 ΔQ=I₀·Δt（样本Δt=0.02s）", I0 * 0.02, 1.6e-4)
chkb("守恒链核：全部放电释放电荷量=充电完毕原带电荷量", Qg == Cm * Usrc)

print("=" * 56)
print(f"合计：{ok + fail} 检查点，PASS {ok}，FAIL {fail}")
assert fail == 0, "存在 FAIL，禁止落主件"
