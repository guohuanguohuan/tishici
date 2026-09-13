# 债清18块 亲算验算行（47块6模型 / 48题12 / 49块6分布结论）
import numpy as np

print("=== 47块6 三电荷平衡模型 ===")
q1, q3, L = 1.0, 4.0, 3.0
r1, r3 = np.sqrt(q1), np.sqrt(q3)
a = L*r1/(r1+r3); b = L*r3/(r1+r3); q2 = q1*q3/(r1+r3)**2
k = 1.0
F1 = k*q1*q2/a**2 - k*q1*q3/L**2          # 电荷1：q2吸引(+) − q3排斥(−)
F2 = -k*q1*q2/a**2 + k*q2*q3/b**2         # 电荷2：向q1(−) + 向q3(+)
F3 = k*q1*q3/L**2 - k*q2*q3/b**2          # 电荷3：q1排斥(+) − q2吸引(−)
print(f"a={a} b={b} q2={q2:.6f}  F1={F1:.2e} F2={F2:.2e} F3={F3:.2e}  (应全零)")
print(f"两大夹小: q2={q2:.4f} < min(q1,q3)={min(q1,q3)} -> {q2<min(q1,q3)}")
print(f"近小远大: b/a={b/a:.4f} = sqrt(q3/q1)={np.sqrt(q3/q1):.4f} -> 中近小电荷q1={b<a}")
# 与47题4公式互验: sqrt(q1*q2)+sqrt(q2*q3) == sqrt(q1*q3)
print(f"互验 sqrt(q1q2)+sqrt(q2q3)={np.sqrt(q1*q2)+np.sqrt(q2*q3):.6f} vs sqrt(q1q3)={np.sqrt(q1*q3):.6f}")

print("=== 48题12 双弧正交 ===")
N = 4_000_000
dth = (np.pi/3)/N
def arc_field(s, plane, sign, lam=1.0, R=1.0):
    # 弧心P为原点，弧平分线沿+x(O在+x)。plane='xy'竖直弧/'xz'水平弧；s为轴上观察点
    th = (np.arange(N)+0.5)*dth - np.pi/3          # 120°弧
    if plane == 'xy': rp = np.stack([R*np.cos(th), R*np.sin(th), 0*th], 1)
    else:             rp = np.stack([R*np.cos(th), 0*th, R*np.sin(th)], 1)
    X = np.array([s, 0.0, 0.0])
    d = X - rp; l = np.linalg.norm(d, axis=1)
    E = sign*lam*R*dth*np.sum(d/l[:,None]**3, axis=0)
    return E
# 半弧AO场强（θ∈[-60°,0]）
Nh = N//2
thh = (np.arange(Nh)+0.5)*(dth) - np.pi/3
Eh = -np.sum(np.cos(thh))*(np.pi/3)/Nh
print(f"半弧60°在心场强 kλ/R×{Eh:.6f} (闭式2sin30°=1.000000)")
th120 = (np.arange(N)+0.5)*dth - np.pi/3
E120 = -np.sum(np.cos(th120))*dth
print(f"整弧120°在心场强 kλ/R×{E120:.6f} (闭式√3={np.sqrt(3):.6f})")
print(f"E0(双弧)=2×{E120:.4f}={2*E120:.4f}; 4Ecos30°={4*1.0*np.cos(np.pi/6):.4f} 相等?{abs(2*E120-4*np.cos(np.pi/6))<1e-3}")
print(f"E=√3E0/6? E/E0={1.0/(2*np.sqrt(3)):.6f} vs √3/6={np.sqrt(3)/6:.6f}")
print(f"φ: 整弧φ=kλ(2π/3)/R, 半弧φ=kλ(π/3)/R, φ_P=4φ->φ=φ0/4 = {1/4}")
for s in (-2.0, -0.5, 0.5, 1.5):
    E1 = arc_field(s, 'xy', +1); E2 = arc_field(s, 'xz', -1)
    Et = E1+E2
    print(f"  D验 x={s}: E(+弧)={np.round(E1,4)} E(−弧)={np.round(E2,4)} 合={np.round(Et,10)}")
print("C验: eφ0=½mv² => v=√(2eφ0/m); 选项√(eφ0/2m)差√4倍 -> C错")

print("=== 49块6 两电荷分布结论 ===")
L = 2.0; q = 1.0; k = 1.0; h0 = L/2
xs = np.linspace(-h0*0.99, h0*0.99, 200001)
E_line_pm = k*q/(xs+h0)**2 + k*q/(h0-xs)**2          # 等量异种连线上（同向相加）
i = np.argmin(E_line_pm)
print(f"异种连线: E(0)={k*q/h0**2*k*2:.4f}=8kq/L²={8*k*q/L**2:.4f}; 最小点x={xs[i]:.4f}≈0")
hs = np.linspace(0, 3, 200001)
E_mid_pm = 2*k*q*h0/(h0**2+hs**2)**1.5               # 异种中垂线
print(f"异种中垂线: 最大在h={hs[np.argmax(E_mid_pm)]:.4f}≈0(=O点), 单调减? {np.all(np.diff(E_mid_pm)<=1e-12)}")
E_line_pp = k*q/(xs+h0)**2 - k*q/(h0-xs)**2          # 等量同种连线上
i0 = np.argmin(np.abs(E_line_pp))
print(f"同种连线: E(0)=0? E({xs[i0]:.4f})={E_line_pp[i0]:.2e}")
E_mid_pp = 2*k*q*hs/(h0**2+hs**2)**1.5               # 同种中垂线
im = np.argmax(E_mid_pp)
print(f"同种中垂线: E(0)=0, 峰h={hs[im]:.6f} vs √2L/4={np.sqrt(2)*L/4:.6f}, 峰后单调减? {np.all(np.diff(E_mid_pp[im:])<=1e-12)}")
print("=== 验算完 ===")
