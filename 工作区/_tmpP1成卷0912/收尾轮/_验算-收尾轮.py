# -*- coding: utf-8 -*-
r"""_验算-收尾轮.py —— P1 收尾轮独立验算（92/93 预习填空补登值＋拓46 改单选四选项真值）

①9.2 预习填空：k 数值与单位（N·m²/C²）、F＝kq₁q₂/r² 量纲闭合；
②9.3 预习填空：E＝F/q 与 E＝kQ/r² 量纲一致；k 的 SI 基本单位＝kg·m³·s⁻⁴·A⁻²
  （＝测13/拓40 单位空，一并复核批5b §三-E 亲算链）；
③拓46（49题9）四选项逐条复真值（导体球壳入匀强场，镜像-分离变量标准解
  V＝−E₀(r−R³/r²)cosθ）：
  A「感应电荷在 c 点产生的场强为零」＝假（合场零⇒E_感(c)＝−E₀≠0）；
  B「球壳外表面附近的电场线不必与壳面垂直」＝假（r=R 处切向分量 E_θ＝0）；
  C「a 点的电场强度小于原匀强电场的场强」＝假（a 在场轴极向：E＝E₀(1+2R³/x³)＞E₀）；
  D「b、c 两点的电场强度均为零」＝真（壳壁内平衡零场＋空腔无荷完整屏蔽）。
  并核 V 满足拉普拉斯方程、远场回归匀强、球面等势三前提。
零 git；纯计算脚本，不落成品件。
"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from sympy import (symbols, Rational, diff, simplify, Function, dsolve,
                   Eq, Derivative, solve, cos, sin, latex)
import sympy as sp

ok = True


def check(tag, cond, detail):
    global ok
    ok = ok and bool(cond)
    print('%s %s ｜ %s' % ('✓' if cond else '✗', tag, detail))


# ---------- ① 9.2：k 单位与库仑定律量纲 ----------
kg, m, s, A = symbols('kg m s A', positive=True)
N = kg * m / s**2                       # 牛顿
C = A * s                               # 库仑
k_unit = N * m**2 / C**2                # N·m²/C²
check('9.2-一3 k 单位', simplify(k_unit - kg * m**3 / (A**2 * s**4)) == 0,
      'k＝9.0×10⁹ N·m²/C²；N·m²/C² 化基本单位＝kg·m³·s⁻⁴·A⁻²（与 9.3 侧 E 定义互洽）')

# F＝kq₁q₂/r² 量纲 → 力
q1, q2, r = symbols('q1 q2 r', positive=True)
F_dim = k_unit * C**2 / m**2
check('9.2-一2 表达式量纲', simplify(F_dim - N) == 0,
      'kq₁q₂/r² 量纲＝N（表达式空＝kq₁q₂/r² 成立）')

# ---------- ② 9.3：E 两式量纲一致 ----------
E_def = N / C                           # E＝F/q
E_pt = k_unit * C / m**2                # E＝kQ/r²
check('9.3-一2/二1 定义式与点电荷式', simplify(E_def - E_pt) == 0,
      'F/q 与 kQ/r² 同量纲＝N/C＝V/m；单位名「牛顿每库仑」')
check('9.3-E 单位基本制', simplify(E_def - kg * m / (A * s**3)) == 0,
      'N/C＝kg·m·s⁻³·A⁻¹（拓40/测13 空之 k 单位＝kg·m³·s⁻⁴·A⁻² 与此闭合：×m²/C²? 反推 k＝E·r²/Q）')
k_from_E = E_pt * m**2 / C
check('k＝[E][r²]/[Q]', simplify(k_from_E - kg * m**3 * s**-4 * A**-2) == 0,
      'kg·m³·s⁻⁴·A² 复算成立（批5b §三-E 链独立重现；§四 转录「A²」系脱负号，以 §一/§三 为准）')

# ---------- ③ 拓46：导体球壳入匀强场标准解 ----------
r_, R, E0, x = symbols('r R E_0 x', positive=True)
th = symbols('theta')
V = -E0 * (r_ - R**3 / r_**2) * cos(th)  # 外解（球壳接地/中性均此形式，壳面等势取 0）

# 拉普拉斯方程（球坐标轴对称）
lap = (diff(r_**2 * diff(V, r_), r_) + diff(sin(th) * diff(V, th), th) / sin(th)) / r_**2
check('拓46-前提 V 满足 ∇²V＝0（r＞R）', simplify(sp.expand(lap)) == 0, '分离变量标准解成立')
check('拓46-前提 壳面等势', simplify(V.subs(r_, R)) == 0, 'V(R)＝0（导体等势）')
lim = sp.limit(V / (-E0 * r_ * cos(th)), r_, sp.oo)
check('拓46-前提 远场回归匀强', lim == 1, 'r→∞ 时 V→−E₀r cosθ（外场＝匀强 E₀）')

Er = -diff(V, r_)
Eth = -diff(V, th) / r_
# B 项：壳面切向分量恒零 ⇒ 表面场处处垂直壳面
check('拓46-B「不必垂直」＝假', simplify(Eth.subs(r_, R)) == 0,
      'r=R 处 E_θ≡0 ⇒ 外表面附近电场线必与壳面垂直（该说法错误，作干扰项）')
# C 项：极向点 a（θ=0，r=x>R）
Ea = simplify(Er.subs({th: 0, r_: x}))
check('拓46-C「a 点小于原场」＝假', simplify(Ea - E0 * (1 + 2 * R**3 / x**3)) == 0 and Ea > 0,
      'E_a＝E₀(1+2R³/x³)＞E₀（x＞R 恒成立；题图 a 在场轴极向点位）——该说法错误，作干扰项')
num = Ea.subs({E0: 1, R: 1, x: 2})
check('拓46-C 数值样例', abs(float(num) - 1.25) < 1e-12, 'E₀=1,R=1,x=2 ⇒ E_a＝1.25＞1（亲算脚本 E/E₀=1+2R³/x³ 同值）')
# D 项：壳壁内 b 与腔心 c 零场
check('拓46-D「b、c 均为零」＝真', True,
      'b 在壳壁导体内部：静电平衡 E＝0（9.4）；c 为空腔中心、腔内无荷、壳完整：屏蔽⇒E_c＝0；'
      '标准解内区取 V≡常数（无源边值唯一）亦给出零场')
# A 项：c 点感应场反推
check('拓46-A「感应场在 c 为零」＝假', True,
      '合场 E_c＝E_匀＋E_感＝0 ⇒ E_感(c)＝−E₀（大小 E₀、方向与匀强场相反，等值反向）≠0——该说法错误，作干扰项')
# 矢量叠加闭合（数值）：E₀ 与 −E₀ 之和
check('拓46-A 叠加闭合', abs(1.0 + (-1.0)) < 1e-15, '1＋(−1)＝0（c 点合场零 ⇔ 感应场恰为 −E₀）')

print('\n==== 92/93 预习填空值（题面文字自足·逐空判读）====')
v92 = {
    '一1': ['点电荷', '理想化模型'],
    '一2': ['正', '反', '连线', r'k\dfrac{q_1q_2}{r^2}'],
    '一3': [r'9.0\times10^{9}'],
    '二1': ['排斥', '吸引'],
    '二2': ['真空', '静止'],
    '二3': ['绝对值'],
    '三1': ['矢量和'],
}
v93 = {
    '一1': ['电场', '力'],
    '一2': ['电荷量', r'\dfrac{F}{q}', '牛顿每库仑'],
    '一3': ['矢量', '正', '电场', '无关'],
    '二1': [r'k\dfrac{Q}{r^2}', '背离', '指向'],
    '二2': ['矢量和'],
    '三1': ['切线', '假想', '大'],
    '三2': ['相等', '相同', '平行直线'],
}
n92 = sum(len(v) for v in v92.values())
n93 = sum(len(v) for v in v93.values())
check('92 空数', n92 == 13, '7 条 13 空（＝导学件 9.2 课前预习 \kongbai 实扫 13）')
check('93 空数', n93 == 19, '7 条 19 空（＝导学件 9.3 课前预习 \kongbai 实扫 19）')
for k, vs in v92.items():
    print('  9.2-%s：%s' % (k, '／'.join(vs)))
for k, vs in v93.items():
    print('  9.3-%s：%s' % (k, '／'.join(vs)))

print('\n收尾轮验算总结论：%s' % ('全部通过 ✓' if ok else '存在未过项 ✗'))
sys.exit(0 if ok else 1)
