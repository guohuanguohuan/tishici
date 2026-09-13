import numpy as np
print("=== 48题12 修正重验 ===")
N = 4_000_000
SPAN = 2*np.pi/3                       # 120°弧
dth = SPAN/N
th = (np.arange(N)+0.5)*dth - np.pi/3  # 对称 [-60°,+60°]
# 半弧AO: θ∈[-60°,0]
Nh = N//2
thh = (np.arange(Nh)+0.5)*dth - np.pi/3
E_half = -np.sum(np.cos(thh))*dth
E_full = -np.sum(np.cos(th))*dth
print(f"半弧60°场强 |E|/（kλ/R）= {abs(E_half):.6f}  闭式2sin30°=1.000000")
print(f"整弧120°场强 |E|/（kλ/R）= {abs(E_full):.6f}  闭式√3={np.sqrt(3):.6f}")
print(f"E0=双弧=2|E_full|={2*abs(E_full):.6f}  4E·cos30°={4*abs(E_half)*np.cos(np.pi/6):.6f}  相等?{abs(2*abs(E_full)-4*abs(E_half)*np.cos(np.pi/6))<1e-4}")
print(f"E/E0 = 1/(2√3) = {1/(2*np.sqrt(3)):.6f} = √3/6 = {np.sqrt(3)/6:.6f}")
print(f"φ比: 半弧φ/φ0 = (π/3)/(4·π/3) = 1/4 -> φ=φ0/4 ✓")
# D: x轴上取点，+弧(xy面)与−弧(xz面) 合成
def arc_field(s, plane, sign, lam=1.0, R=1.0):
    M = 200000
    dt = SPAN/M
    t = (np.arange(M)+0.5)*dt - np.pi/3
    if plane == 'xy': rp = np.stack([R*np.cos(t), R*np.sin(t), 0*t], 1)
    else:             rp = np.stack([R*np.cos(t), 0*t, R*np.sin(t)], 1)
    d = np.array([s,0.0,0.0]) - rp
    l = np.linalg.norm(d, axis=1)
    return sign*lam*R*dt*np.sum(d/l[:,None]**3, axis=0)
for s in (-2.0, -0.5, 0.5, 1.5, 4.0):
    Et = arc_field(s,'xy',+1) + arc_field(s,'xz',-1)
    print(f"  D验 x={s:+.1f}: 合场 = {np.round(Et,12)}  (应全零)")
