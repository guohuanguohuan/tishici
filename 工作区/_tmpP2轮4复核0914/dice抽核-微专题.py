# 乙臂防撞抽核：对 5 对 top 值独立复算 4-gram Dice（指纹串取自防撞扫.py 存档口径）
def ng(s, n=4):
    s = "".join(ch for ch in s if not ch.isspace())
    return set(s[i:i+n] for i in range(len(s)-n+1))
def dice(a, b):
    A, B = ng(a), ng(b)
    return 2*len(A & B)/(len(A)+len(B))
pairs = [
 ("R4M-01×中14(库max)", "等边三角形三顶点各+Q题给φ=kQ/r，中心O合场为零、MN中点K场强8kQ/a²陷阱真值4kQ/3a²、φ_O=3√3kQ/a、电子自K释放向P——多选ACD",
                       "题给φ=kQ/r，半圆环电势叠加求解", 0.13),
 ("R4M-10×批B-02", "φ-x曲线峰x₁=4V谷x₃=−2V，质子自峰静止释放最大动能e(4−(−2))=6eV=9.6×10⁻¹⁹J——单选A",
                   "1eV＝1.6×10⁻¹⁹J 单位换算＋电子经100V加速动能增100eV＝1.6×10⁻¹⁷J——填空", 0.12),
 ("R4M-07×简10", "一条电场线a、b、c，φ_a=6V、φ_c=−4V：直线≠匀强、φ_b∈(−4,6)可取2V、匀强特例φ_b=1V、电子a→c做功−10eV——多选BC",
                 "电场线a、b、c且ab=bc，定性比较E、φ、做功", 0.11),
 ("批内 R4M-08×R4M-09", "理想二极管+恒压6V电容器上板上移d倍增至2d₀：放电被阻Q不变、U增至12V、E=U/d不变微粒仍静止、反接则E减半微粒向下——单选B",
                        "可变电容器动片旋出正对面积减半保持6V相连：C减半、Q减半、E=U/d不变、P点电势不变——单选A", 0.108),
 ("批内 R4M-04×R4M-06", "匀强场任意四边形ABCD对角线中点M、N，W_AB=1.6×10⁻⁵J、W_DC=6×10⁻⁶J推U_AB=8V、U_DC=3V，推论①得U_MN=2.5V、W(M→N)=5×10⁻⁶J——多选AC",
                        "正四面体A-BCD棱长3m，A固定+Q匀强场平行底面，W_BC=6×10⁻⁶J、W_BD=3×10⁻⁶J点电荷等距零功分离，E₀=2V/m沿BC、U_CD=−3V——多选AB", 0.106),
]
print("对 ｜ 本臂复算Dice ｜ 命制件申报读数 ｜ 偏差")
for name, a, b, claimed in pairs:
    d = dice(a, b)
    ok = "✓" if abs(d-claimed) <= 0.005+0.004 else "✗"
    print(f"{name}  | {d:.3f} | {claimed} | {abs(d-claimed):.3f} {ok}")
