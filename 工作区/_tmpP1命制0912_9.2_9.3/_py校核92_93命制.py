# P1 白名单命制末批 9.2+9.3 三题 数值独立重算校核
# 授权：看板九十一（末批额度 3＝全简：9.2×1＋9.3×2）＋看板九十二单臂 interim（glm 执行）
# 口径：k＝9.0×10⁹ N·m²/C²

k = 9.0e9  # N·m²/C²

# ---------- 命制-P1-9.2-简-1：同号两球接触均分·放回原距 ----------
q1, q2 = 2.0e-8, 4.0e-8          # C
qm = (q1 + q2) / 2               # 接触后每球电荷量
assert abs(qm - 3.0e-8) < 1e-20, qm
F  = k * q1 * q2                 # 接触前 ∝，同除 r²
Fp = k * qm**2                   # 接触后
ratio = Fp / F                   # F'/F
assert abs(ratio - 9.0 / 8.0) < 1e-12, ratio
# 陷阱核
inv = F / Fp                     # A 项＝比值取反
assert abs(inv - 8.0 / 9.0) < 1e-12
trap_d = (qm / q1) ** 2          # D 项＝只与 q₁ 比、漏掉积 q₁q₂
assert abs(trap_d - 9.0 / 4.0) < 1e-12
total = q1 + q2                  # 总量不变（B 项迷思核）
assert abs(total - 6.0e-8) < 1e-20 and abs(qm**2 - 9.0e-16) < 1e-24
print("9.2-简-1: q均分=%.2e C, 积比 %.1f->%.1f, F'/F=%.4f (=9/8) ✓ [陷阱: 反比8/9=%.4f, (3/2)²=9/4=%.2f]"
      % (qm, q1*q2/1e-16, qm**2/1e-16, ratio, inv, trap_d))

# ---------- 命制-P1-9.3-简-1：点电荷场强直代＋方向 ----------
Q, r = 1.0e-8, 0.30              # C, m
E = k * Q / r**2
assert abs(E - 1.0e3) < 1e-6, E
trap_b = k * Q / r               # B 项＝漏掉 r 的平方
assert abs(trap_b - 3.0e2) < 1e-6
trap_d2 = k * Q / 0.10**2        # D 项数值来源＝r 误读为 0.10 m
assert abs(trap_d2 - 9.0e3) < 1e-6
print("9.3-简-1: E=%.4g N/C ✓ [陷阱: 漏平方=%.4g, r误读0.10m=%.4g]" % (E, trap_b, trap_d2))

# ---------- 命制-P1-9.3-简-2：定义式直算＋无关性辨析 ----------
q, Fq = 2.0e-8, 6.0e-4           # C, N
E2 = Fq / q
assert abs(E2 - 3.0e4) < 1e-6, E2
trap_c = q / Fq                  # C 项＝定义式倒置
assert abs(trap_c - 3.3333333333333335e-05) < 1e-19
# B 项核：改放 4.0×10⁻⁸ C 试探电荷，力加倍、场强不变
F2 = q * 2 * E2                  # 电荷量加倍 → 受力加倍
assert abs(F2 - 1.2e-3) < 1e-19
E_after = F2 / 4.0e-8
assert abs(E_after - 3.0e4) < 1e-6
print("9.3-简-2: E=%.4g N/C ✓ [倒置=%.4g; 改放4e-8: F'=1.2e-3 N, E 仍=%.4g N/C]" % (E2, trap_c, E_after))

print("ALL CHECKS PASSED (3 题/9 组断言)")
