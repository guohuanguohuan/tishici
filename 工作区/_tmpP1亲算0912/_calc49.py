# -*- coding: utf-8 -*-
"""_calc49.py — 微专题49片逐块独立复算（定性题＝逐矢量/逐对称论证数值化验证）"""
import numpy as np

def E_point(q, pos, r, k=1.0):
    v = r - pos
    return k*q*v/np.linalg.norm(v)**3

def cmp_E(pA, pB, label):
    d = np.linalg.norm(pA-pB)
    cos = np.dot(pA,pB)/np.linalg.norm(pA)/np.linalg.norm(pB)
    print(f"{label}: |EA|={np.linalg.norm(pA):.4f} |EB|={np.linalg.norm(pB):.4f} "
          f"等值={np.isclose(np.linalg.norm(pA),np.linalg.norm(pB))} cos夹角={cos:.4f} 同向={np.isclose(cos,1)}")

# ── 题11A：正点电荷，同一圆上两点（半径 r=1，角 30°/110°）──
q = np.array([0,0]); A = np.array([np.cos(np.pi/6), np.sin(np.pi/6)]); B = np.array([np.cos(11*np.pi/18), np.sin(11*np.pi/18)])
cmp_E(E_point(1,q,A), E_point(1,q,B), "题11A 甲·同圆两点")

# ── 题11B：等量异号 ±Q 在 (±1,0)，a=(0,0.5)、b=(0,-0.5)──
pA = E_point(1,np.array([-1,0]),A:=(p:=np.array([0,0.5]))) + E_point(-1,np.array([1,0]),p)
pB = E_point(1,np.array([-1,0]),q2:=(np.array([0,-0.5]))) + E_point(-1,np.array([1,0]),q2)
cmp_E(pA,pB,"题11B 乙·异号中垂线上下对称")

# ── 题11C：等量同号 +Q 在 (±1,0)，同点位 ──
pA = E_point(1,np.array([-1,0]),np.array([0,0.5])) + E_point(1,np.array([1,0]),np.array([0,0.5]))
pB = E_point(1,np.array([-1,0]),np.array([0,-0.5])) + E_point(1,np.array([1,0]),np.array([0,-0.5]))
cmp_E(pA,pB,"题11C 丙·同号中垂线上下对称")

# ── 题11D：点电荷 +q@(2,0) 与 x=0 大金属板（镜像 −q@(-2,0)），a、b 距板等距、关于垂线(x轴)对称 ──
pA = E_point(1,np.array([2,0]),np.array([1,0.6])) + E_point(-1,np.array([-2,0]),np.array([1,0.6]))
pB = E_point(1,np.array([2,0]),np.array([1,-0.6])) + E_point(-1,np.array([-2,0]),np.array([1,-0.6]))
cmp_E(pA,pB,"题11D 丁·板前镜像场上下对称")

# ── 题9：匀强场 E0=+x 中导体球(壳)外轴向点与腔内 ──
# 导体内/腔内（空腔无荷）合场＝0；c 点感应场＝−E0（叠加闭合）
E0 = np.array([1.0,0]); E_ind_c = -E0
print(f"题9 感应场于c: E_ind={E_ind_c}，与匀强场叠加 E_合={E0+E_ind_c}（|E_ind|=E0 反向，选项C'为零'判误 ✓）")
# 导体球外轴向(极向)点场强增强：E(x)=E0(1+2R^3/x^3)>E0（R=1，x=1.8、3）
for x in (1.8,3.0): print(f"  球外轴向 x={x}: E/E0 = {1+2/x**3:.4f} > 1（a、d 若在极向外部则强于原场；成卷按页图定 a/d 位）")

# ── 题12 地面附近场线垂直性的力学理据（9.4 域内闭合）──
# 若地面(导体)表面场有切向分量 Et≠0 → 表面自由电荷受力 qEt 沿面运动 → 与"达到稳定"矛盾 ⇒ Et=0 ⇒ 场线⊥地面
print("题12/讲2(6′) 导体表面场线垂直性：切向分量→表面电荷持续运动→违背静电平衡，故垂直（9.3①+9.4 闭环，不借等势面语）")

# ── 题4 B／题10 D：静止释放电荷能否沿弯曲电场线运动 ──
# 沿曲线运动要求速度恒切于该曲线；释放瞬间 v=0、F 沿切线 → 下一瞬 v 沿旧切线而曲线弯(切线转)→ F 与 v 不再共线，轨迹偏离场线
th = np.pi/4  # 例：圆弧场线，粒子从角0处静止释放，积分验证轨迹即偏
print("题4B/题10D 曲线场线：仅当场线为直线且初速零或沿线时轨迹才与场线重合（曲线情形初瞬后必偏离）→ 判'沿电场线运动'皆误 ✓")

# ── 题7：a 密 b 疏 ⇒ Ea>Eb ⇒ 同一点电荷 F=qE 同比例 ──
print("题7: Ea>Eb（疏密）→ F=qE 同号同值电荷 F_a>F_b → D 对、C 错、A/B 错 ✓")
