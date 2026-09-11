# slice-05 盲解作答（qwen 臂）

- 题源：`工作区/逻辑闸-样张族0911/slices/slice-05.md`（去答案题面片，唯一读取文件）
- 纪律：未读 `keys/`、任何答案册/答案键、`sol-glm/`、`sol-qwen/`（除本次产出文件本身），未联网搜题解
- 题数：16（练-课 10 ＋ 测 6）
- 约定：`⟨a,b⟩` 表示向量夹角；所有坐标法均在「长方体/平行六面体按互相垂直的棱建系」或「以题给基底为坐标」下完成

---

## 一、练习线·课时训练（第1课时 空间向量的概念及线性运算）

### 练-课-1（基础巩固·单选）
**答案：C（充要条件）**

**逐选项判定**
- 题设：a、b 均为非零空间向量。
- 充分性：a·b = |a||b|cos⟨a,b⟩ = 0，因 |a|≠0 且 |b|≠0，故 cos⟨a,b⟩ = 0，⟨a,b⟩ = 90°（夹角范围 [0°,180°]），即 a⊥b。充分性成立。
- 必要性：a⊥b ⇒ ⟨a,b⟩ = 90° ⇒ a·b = |a||b|cos90° = 0。必要性成立。
- A（仅充分）错、B（仅必要）错、D（都不）错，C 对。

**验证方式与结论**：反向排除非零前提的作用——若允许零向量，则「a⊥b」在教材中只对非零向量定义夹角，题目已明确「非零」，故双向皆通。两向互验（定义展开 ⇄ 夹角反解）一致。结论：C。

### 练-课-2（基础巩固·填空）
**答案：\(\overrightarrow{D_1B}=\overrightarrow{a}-\overrightarrow{b}-\overrightarrow{c}\)**

**解法要点**（法一·向量链）
\(\overrightarrow{D_1B}=\overrightarrow{D_1D}+\overrightarrow{DA}+\overrightarrow{AB}=(-\overrightarrow{c})+(-\overrightarrow{b})+\overrightarrow{a}=\overrightarrow{a}-\overrightarrow{b}-\overrightarrow{c}\)。

**验证**（法二·基底坐标）
以 A 为原点、\((\overrightarrow{AB},\overrightarrow{AD},\overrightarrow{AA_1})\) 为基底写坐标：A=(0,0,0)、B=(1,0,0)、D=(0,1,0)、A₁=(0,0,1)，则 D₁=D+AA₁=(0,1,1)。\(\overrightarrow{D_1B}=B-D_1=(1,-1,-1)\)，即 \(1\cdot a+(-1)\cdot b+(-1)\cdot c\)，与法一相同。结论一致。

### 练-课-3（基础巩固·填空）
**答案：\(x=1\)，\(y=\dfrac{1}{2}\)**

**解法要点**（法一）
平行六面体中 \(\overrightarrow{A_1C_1}=\overrightarrow{AC}=\overrightarrow{AB}+\overrightarrow{AD}\)（侧棱平移保持向量不变）。E 为 \(A_1C_1\) 中点（因 \(\overrightarrow{A_1E}=\tfrac12\overrightarrow{A_1C_1}\)），
\(\overrightarrow{AE}=\overrightarrow{AA_1}+\overrightarrow{A_1E}=\overrightarrow{AA_1}+\tfrac12(\overrightarrow{AB}+\overrightarrow{AD})\)。
对照 \(\overrightarrow{AE}=x\overrightarrow{AA_1}+y(\overrightarrow{AB}+\overrightarrow{AD})\)：因 \(\overrightarrow{AA_1},\overrightarrow{AB},\overrightarrow{AD}\) 不共面，表示唯一，得 x=1，y=1/2。

**验证**（法二·坐标）
以 A 为原点，\(\overrightarrow{AB}=(1,0,0),\overrightarrow{AD}=(0,1,0),\overrightarrow{AA_1}=(0,0,1)\)。则 A₁=(0,0,1)，C₁=(1,1,1)，E=中点=\((\tfrac12,\tfrac12,1)\)，\(\overrightarrow{AE}=(\tfrac12,\tfrac12,1)\)。右边 \(x\overrightarrow{AA_1}+y(\overrightarrow{AB}+\overrightarrow{AD})=(y,y,x)\)，令相等：y=1/2、x=1。两法一致。

### 练-课-4（基础巩固·填空）
**答案：\(-11\)**

**解法要点**（法一·数量积展开）
\(\overrightarrow{a}\cdot\overrightarrow{b}=2\times3\times\cos60^\circ=3\)。
\((\overrightarrow{a}+2\overrightarrow{b})\cdot(\overrightarrow{a}-\overrightarrow{b})=|\overrightarrow{a}|^2-\overrightarrow{a}\cdot\overrightarrow{b}+2\overrightarrow{b}\cdot\overrightarrow{a}-2|\overrightarrow{b}|^2=|\overrightarrow{a}|^2+\overrightarrow{a}\cdot\overrightarrow{b}-2|\overrightarrow{b}|^2=4+3-18=-11\)。

**验证**（法二·坐标直算）
取 \(\overrightarrow{a}=(2,0)\)，\(\overrightarrow{b}=(3\cos60^\circ,3\sin60^\circ)=(\tfrac32,\tfrac{3\sqrt3}{2})\)。
\(\overrightarrow{a}+2\overrightarrow{b}=(5,\,3\sqrt3)\)，\(\overrightarrow{a}-\overrightarrow{b}=(\tfrac12,\,-\tfrac{3\sqrt3}{2})\)。
点乘 \(=5\cdot\tfrac12+3\sqrt3\cdot(-\tfrac{3\sqrt3}{2})=\tfrac52-\tfrac{27}{2}=-\tfrac{22}{2}=-11\)。两法一致。

### 练-课-5（基础巩固·填空）
**答案：\(\dfrac{\sqrt{10}}{5}\)（即 \(\dfrac{2}{\sqrt{10}}\)）**

**解法要点**（法一·坐标＋数量积）
长方体中以 A 为原点，AB、AD、AA₁ 为 x、y、z 轴：
A(0,0,0)、B(2,0,0)、C(2,2,0)、B₁(2,0,1)。
\(\overrightarrow{AB_1}=(2,0,1)\)，\(\overrightarrow{AC}=(2,2,0)\)。
\(\cos\theta=\dfrac{\overrightarrow{AB_1}\cdot\overrightarrow{AC}}{|\overrightarrow{AB_1}||\overrightarrow{AC}|}=\dfrac{4+0+0}{\sqrt5\cdot\sqrt8}=\dfrac{4}{2\sqrt{10}}=\dfrac{2}{\sqrt{10}}=\dfrac{\sqrt{10}}{5}\approx0.632\)。

**验证**（法二·余弦定理，不用坐标点乘）
三边长：\(|AB_1|=\sqrt{AB^2+BB_1^2}=\sqrt{4+1}=\sqrt5\)；\(|AC|=\sqrt{4+4}=2\sqrt2\)；
\(B_1C\): \(B_1=(2,0,1)\to C=(2,2,0)\)，长 \(\sqrt{0+4+1}=\sqrt5\)（即面对角线 \(CB_1\)，两直角边 2 与 1）。
\(\cos\angle B_1AC=\dfrac{5+8-5}{2\cdot\sqrt5\cdot2\sqrt2}=\dfrac{8}{4\sqrt{10}}=\dfrac{\sqrt{10}}{5}\)。两法一致，且 0<θ<90° 与图形相符。

### 练-课-6（基础巩固·填空）
**答案：\(\overrightarrow{A_1B}=\overrightarrow{b}-\overrightarrow{a}-\overrightarrow{c}\)**

**解法要点**（法一·向量链）
\(\overrightarrow{A_1B}=\overrightarrow{A_1A}+\overrightarrow{AB}=-\overrightarrow{CC_1}+(\overrightarrow{CB}-\overrightarrow{CA})=-\overrightarrow{c}+\overrightarrow{b}-\overrightarrow{a}=\overrightarrow{b}-\overrightarrow{a}-\overrightarrow{c}\)。

**验证**（法二·以 C 为原点的基分量）
以 C 为原点、基 \((\overrightarrow{a},\overrightarrow{b},\overrightarrow{c})\)：A=(1,0,0)、B=(0,1,0)、A₁=A+c=(1,0,1)。
\(\overrightarrow{A_1B}=B-A_1=(-1,\,1,\,-1)=-\overrightarrow{a}+\overrightarrow{b}-\overrightarrow{c}\)。两法一致。

### 练-课-10（基础巩固·解答，13分）
**答案：\(P,M,A,B\) 四点共面（事实上 P 在直线 AB 上）**

**解法要点**（法一·以 M 为起点的线性表示）
由 \(\overrightarrow{MP}=3\overrightarrow{MA}-2\overrightarrow{MB}\)，\(\overrightarrow{MP}\) 可表示为 \(\overrightarrow{MA},\overrightarrow{MB}\) 的线性组合，故 \(\overrightarrow{MP},\overrightarrow{MA},\overrightarrow{MB}\) 三向量共面（共面向量定理的推广：能被两向量线性表出者与之共面）。
三向量同起点 M，所以终点 P、A、B 与 M 共面。
（若 M、A、B 不共线，则 M 与直线 AB 确定的平面即含 P；若 M、A、B 共线，则四点更共面，结论不变。）

**法二·任意原点 O 化简（更强化）**
\(\overrightarrow{OP}-\overrightarrow{OM}=3(\overrightarrow{OA}-\overrightarrow{OM})-2(\overrightarrow{OB}-\overrightarrow{OM})=3\overrightarrow{OA}-2\overrightarrow{OB}-\overrightarrow{OM}\)，
两边消去 \(-\overrightarrow{OM}\) 得 \(\overrightarrow{OP}=3\overrightarrow{OA}-2\overrightarrow{OB}\)。
系数和 \(3+(-2)=1\) ⇒ P 在直线 AB 上。具体地 \(\overrightarrow{AP}=\overrightarrow{OP}-\overrightarrow{OA}=2\overrightarrow{OA}-2\overrightarrow{OB}=-2\overrightarrow{AB}\)，即 \(\overrightarrow{AP}=2\overrightarrow{BA}\)，P 在 AB 的延长线（A 的外侧）上。
直线 AB 与点 M 必共面，故 \(P,M,A,B\) 共面。

**验证方式与结论**：反向代回检验——以 M 为参考点，记 \(\overrightarrow{MA}=\overrightarrow{u}\)、\(\overrightarrow{MB}=\overrightarrow{v}\)，由法二得 P 满足 \(\overrightarrow{MP}=3\overrightarrow{u}-2\overrightarrow{v}\)；此时 \(\overrightarrow{AP}=\overrightarrow{MP}-\overrightarrow{MA}=2\overrightarrow{u}-2\overrightarrow{v}=-2\overrightarrow{AB}\)，即 \(\overrightarrow{AP}\parallel\overrightarrow{AB}\) 且有公共点 A，故 P∈直线 AB；再回代 \(3\overrightarrow{MA}-2\overrightarrow{MB}=3\overrightarrow{u}-2\overrightarrow{v}=\overrightarrow{MP}\) 恒等成立 ✓。两法互验一致，且法二给出「P∈直线 AB」这一比共面更强的结论。结论：\(P,M,A,B\) 四点共面。

### 练-课-11（综合提升·填空）
**答案：\(\sqrt{2}\)**

**解法要点**（法一·坐标）
二面角 A-EF-D 的棱为 EF；正方形 ABFE 中 EA⊥EF，正方形 CDEF 中 ED⊥EF，故平面角 \(\angle AED=60^\circ\)。
设 E 为原点，EF 为 z 轴，EA 在 x 轴上：E(0,0,0)、F(0,0,1)、A(1,0,0)、D(\(\cos60^\circ,\sin60^\circ,0)=(\tfrac12,\tfrac{\sqrt3}{2},0)\)。
正方形 ABFE 中 \(\overrightarrow{AB}=\overrightarrow{EF}=(0,0,1)\) ⇒ B(1,0,1)。
\(\overrightarrow{BD}=D-B=(-\tfrac12,\tfrac{\sqrt3}{2},-1)\)，\(|BD|^2=\tfrac14+\tfrac34+1=2\) ⇒ \(|BD|=\sqrt2\)。

**验证**（法二·向量模长公式）
\(\overrightarrow{BD}=\overrightarrow{ED}-\overrightarrow{EB}=\overrightarrow{ED}-\overrightarrow{EA}-\overrightarrow{EF}\)。
\(|\overrightarrow{BD}|^2=|\overrightarrow{ED}|^2+|\overrightarrow{EA}|^2+|\overrightarrow{EF}|^2-2\overrightarrow{ED}\cdot\overrightarrow{EA}-2\overrightarrow{ED}\cdot\overrightarrow{EF}+2\overrightarrow{EA}\cdot\overrightarrow{EF}\)
\(=1+1+1-2(1\cdot1\cdot\cos60^\circ)-0+0=3-1=2\) ⇒ \(|BD|=\sqrt2\)。

**验证**（法三·纯几何）
AB∥EF，而 EF⊥平面 AED（EA、ED 皆垂直于 EF），故 AB⊥平面 AED，从而 AB⊥AD，\(BD^2=AB^2+AD^2\)。
在 △AED 中 \(AD^2=AE^2+ED^2-2\cdot AE\cdot ED\cos60^\circ=1+1-1=1\)，故 \(BD=\sqrt{1+1}=\sqrt2\)。三法一致。

### 练-课-12（综合提升·多选）
**答案：AD**

**逐选项判定**（a、b 为空间任意两个非零向量）
- A．\(\overrightarrow{a}^2=|\overrightarrow{a}|^2\)：\(\overrightarrow{a}^2=\overrightarrow{a}\cdot\overrightarrow{a}=|\overrightarrow{a}||\overrightarrow{a}|\cos0^\circ=|\overrightarrow{a}|^2\)。**正确**。
- B．\(\dfrac{\overrightarrow{a}\cdot\overrightarrow{b}}{\overrightarrow{a}\cdot\overrightarrow{a}}=\dfrac{\overrightarrow{b}}{\overrightarrow{a}}\)：左边是实数（数量积之比），右边「向量除以向量」在向量运算中没有定义，等式两边类型不同、无意义。**错误**。
- C．\((\overrightarrow{a}\cdot\overrightarrow{b})^2=\overrightarrow{a}^2\cdot\overrightarrow{b}^2\)：左边 \(=|\overrightarrow{a}|^2|\overrightarrow{b}|^2\cos^2\langle a,b\rangle\)，右边 \(=|\overrightarrow{a}|^2|\overrightarrow{b}|^2\)，仅当 \(\cos^2=1\)（a∥b）时相等，一般不成立。**错误**。反例：a⊥b 且非零时左边 = 0、右边 > 0。
- D．\((\overrightarrow{a}-\overrightarrow{b})^2=\overrightarrow{a}^2-2\overrightarrow{a}\cdot\overrightarrow{b}+\overrightarrow{b}^2\)：数量积满足交换律与分配律，展开成立。**正确**。

**验证方式与结论**：C 用垂直反例否证（取 \(\overrightarrow{a}=(1,0,0),\overrightarrow{b}=(0,1,0)\)：左 = 0，右 = 1）；D 用坐标正验（\(\overrightarrow{a}=(1,2,3),\overrightarrow{b}=(4,0,1)\)：\(\overrightarrow{a}-\overrightarrow{b}=(-3,2,2)\)，平方和 = 9+4+4 = 17；\(|a|^2-2a\cdot b+|b|^2=14-2\times7+17=17\) ✓）。故选 AD。

### 练-课-15（思维探索·填空）
**答案：\(\dfrac{\sqrt{7}}{2}\)**

**解法要点**（法一·向量折线分解）
矩形 ABCD 中 AB=1、BC=√3，则 AC=2（∠ABC=90°）。作 BE⊥AC 于 E、DF⊥AC 于 F（折叠中 △ABC、△ACD 自身是刚性的，BE、DF 长度与垂足位置不变）。
- \(BE=\dfrac{AB\cdot BC}{AC}=\dfrac{\sqrt3}{2}\)，\(AE=\dfrac{AB^2}{AC}=\dfrac12\)；
- \(DF=\dfrac{AD\cdot DC}{AC}=\dfrac{\sqrt3\cdot1}{2}=\dfrac{\sqrt3}{2}\)，\(CF=\dfrac{DC^2}{AC}=\dfrac{1}{2}\Rightarrow AF=2-\dfrac12=\dfrac32\)；故 \(EF=AF-AE=1\)。
二面角 B-AC-D 的平面角即 \(\langle\overrightarrow{EB},\overrightarrow{FD}\rangle=60^\circ\)，所以 \(\overrightarrow{BE}\cdot\overrightarrow{FD}=-|BE||DF|\cos60^\circ=-\dfrac{\sqrt3}{2}\cdot\dfrac{\sqrt3}{2}\cdot\dfrac12=-\dfrac38\)。
\(\overrightarrow{BD}=\overrightarrow{BE}+\overrightarrow{EF}+\overrightarrow{FD}\)，且 BE、FD 均⊥AC、EF∥AC ⇒ 交叉项 BE·EF = EF·FD = 0。
\(|\overrightarrow{BD}|^2=\dfrac34+1+\dfrac34+2\left(-\dfrac38\right)=\dfrac52-\dfrac34=\dfrac74\Rightarrow |\overrightarrow{BD}|=\dfrac{\sqrt7}{2}\)。

**验证**（法二·坐标）
把 AC 放在 x 轴：A(0,0,0)、C(2,0,0)，E(1/2,0,0)、F(3/2,0,0)。半平面方向取垂直于 x 轴的 yOz 方向：
B = E + (√3/2)(0,1,0) = (1/2, √3/2, 0)；D = F + (√3/2)(0, cos60°, sin60°) = (3/2, √3/4, 3/4)。
核对四边长：|AB|=√(1/4+3/4)=1 ✓；|BC|=√(9/4+3/4)=√3 ✓；|AD|=√(9/4+3/16+9/16)=√3 ✓；|CD|=√(1/4+3/16+9/16)=1 ✓（折叠后长度守恒）。
\(\overrightarrow{BD}=(1,-\tfrac{\sqrt3}{4},\tfrac34)\)，\(|BD|^2=1+\tfrac{3}{16}+\tfrac{9}{16}=1+\tfrac34=\tfrac74\) ⇒ \(|BD|=\tfrac{\sqrt7}{2}\)。两法一致。

**验证**（法三·极限位情检验）
公式 \(|BD|^2=\tfrac52-\tfrac32\cos\theta\)（θ 为二面角）：θ=180°（未折叠的平面矩形）给 \(|BD|^2=4\)，即对角线 BD=2，与矩形两对角线相等 ✓；θ=0°（两三角形叠合）给 \(|BD|^2=1\)，与坐标同侧计算一致。θ=60° 给 \(2.5-0.75=1.75=\tfrac74\) ✓。三种检验一致。

---

## 二、测评卷·单元素养测评卷（一）

### 测-1（选择题）
**答案：B**

**逐选项判定**
- A．若 \(|\overrightarrow{a}|=|\overrightarrow{b}|\)，则 \(\overrightarrow{a}=\overrightarrow{b}\) 或 \(\overrightarrow{a}=-\overrightarrow{b}\)：错。模相等只约束长度，方向任意。反例：平面内夹角 60° 的两个单位向量，模相等但既不相等也不相反。
- B．若 \(\overrightarrow{a},\overrightarrow{b}\) 为相反向量，则 \(\overrightarrow{a}+\overrightarrow{b}=\overrightarrow{0}\)：对。相反向量定义为大小相等、方向相反（\(\overrightarrow{b}=-\overrightarrow{a}\)），故和为零向量。
- C．零向量是没有方向的向量：错。教材规定零向量的方向是**任意的**，不是「没有方向」。
- D．若 \(\overrightarrow{a},\overrightarrow{b}\) 是两个单位向量，则 \(\overrightarrow{a}=\overrightarrow{b}\)：错。单位向量只保证模为 1，方向可不同。

**验证方式与结论**：B 用定义正向推（\(\overrightarrow{a}+\overrightarrow{b}=\overrightarrow{a}+(-\overrightarrow{a})=\overrightarrow{0}\)）；A、D 用同模不同向反例否证（\((1,0,0)\) 与 \((0,1,0)\) 均为单位向量但不相等）；C 属概念性规定，与「零向量方向任意、与任一向量平行」一致。故选 B。

### 测-2（选择题）
**答案：D**（题目要求选「错误」的说法）

**逐选项判定**
- A．零向量与任意向量都平行：正确（教材规定 \(\overrightarrow{0}\) 方向任意，与任一向量平行）。
- B．若 \(|\overrightarrow{a}|=0\)，则 \(\overrightarrow{a}=\overrightarrow{0}\)：正确（模为 0 的向量即零向量，且唯一）。
- C．若 \(\overrightarrow{a}=\overrightarrow{b}\)，则 \(|\overrightarrow{a}|=|\overrightarrow{b}|\)：正确（相等向量模等且向同）。
- D．若 \(\overrightarrow{a}\parallel\overrightarrow{b}\)，则 \(|\overrightarrow{a}|=|\overrightarrow{b}|\)：错误。平行（共线）只约束方向，不约束长度。反例：\(\overrightarrow{a}=(1,0,0)\)，\(\overrightarrow{b}=(3,0,0)\)，平行但模 1≠3。

**验证方式与结论**：A、B、C 逐条由定义/规定成立；D 反例否证，且其逆否「模相等未必平行」同样说明两者互不蕴含。故错误说法为 D。

### 测-3（选择题）
**答案：B（\(k=2\)）**

**解法要点**（法一·共线向量定理）
\(\overrightarrow{a}\parallel\overrightarrow{b}\) 且 \(\overrightarrow{a}\ne\overrightarrow{0}\)，故存在实数 λ 使 \(\overrightarrow{b}=\lambda\overrightarrow{a}\)：
\(4\overrightarrow{e_1}+k\overrightarrow{e_2}=\lambda(2\overrightarrow{e_1}+\overrightarrow{e_2})=2\lambda\overrightarrow{e_1}+\lambda\overrightarrow{e_2}\)。
因 \(\overrightarrow{e_1},\overrightarrow{e_2}\) 不共线，平面向量基本定理保证表示唯一：\(2\lambda=4\Rightarrow\lambda=2\)，\(k=\lambda=2\)。

**验证**（法二·系数交叉相乘）
\(\overrightarrow{a}=x_1\overrightarrow{e_1}+y_1\overrightarrow{e_2}\)、\(\overrightarrow{b}=x_2\overrightarrow{e_1}+y_2\overrightarrow{e_2}\) 共线 ⇔ \(x_1y_2-x_2y_1=0\)：\(2k-4\times1=0\Rightarrow k=2\)。
回代：\(\overrightarrow{b}=4\overrightarrow{e_1}+2\overrightarrow{e_2}=2(2\overrightarrow{e_1}+\overrightarrow{e_2})=2\overrightarrow{a}\) ✓ 确为平行。
另检：A 项 \(k=\tfrac12\) 使 \(2\cdot\tfrac12-4=-3\ne0\)；C 项 \(-\tfrac12\)、D 项 3 亦不满足，均排除。两法一致，选 B。

### 测-4（多项选择，6分）
**答案：AD**

**逐选项判定**（与练-课-12 同题，独立重做）
- A．\(\overrightarrow{a}^2=|\overrightarrow{a}|^2\)：由 \(\overrightarrow{a}\cdot\overrightarrow{a}=|\overrightarrow{a}|^2\cos0^\circ=|\overrightarrow{a}|^2\)，**正确**。
- B．\(\dfrac{\overrightarrow{a}\cdot\overrightarrow{b}}{\overrightarrow{a}\cdot\overrightarrow{a}}=\dfrac{\overrightarrow{b}}{\overrightarrow{a}}\)：向量之间没有除法运算，\(\overrightarrow{b}/\overrightarrow{a}\) 无意义；左边是数量。**错误**。
- C．\((\overrightarrow{a}\cdot\overrightarrow{b})^2=\overrightarrow{a}^2\cdot\overrightarrow{b}^2\)：左 \(=|\overrightarrow{a}|^2|\overrightarrow{b}|^2\cos^2\theta\)，右 \(=|\overrightarrow{a}|^2|\overrightarrow{b}|^2\)，一般不等（仅共线时等）。**错误**。
- D．\((\overrightarrow{a}-\overrightarrow{b})^2=\overrightarrow{a}^2-2\overrightarrow{a}\cdot\overrightarrow{b}+\overrightarrow{b}^2\)：数量积可交换、可分配，完全平方公式对向量成立。**正确**。

**验证方式与结论**：取 \(\overrightarrow{a}=(1,0,0),\overrightarrow{b}=(0,2,0)\) 作统一反例/正验：A：\(|a|^2=1\)，\(\overrightarrow{a}^2=1\) ✓；C：左 = 0，右 = 1×4 = 4 ✗；D：\((a-b)^2=(-1,-2,0)\) 模方 = 5，右 = 1 − 0 + 4 = 5 ✓；B：式子无定义 ✗。故 AD。

### 测-5（填空，5分）
**答案：\(3\)**

**解法要点**
\(\overrightarrow{a}\cdot\overrightarrow{b}=|\overrightarrow{a}||\overrightarrow{b}|\cos\langle\overrightarrow{a},\overrightarrow{b}\rangle=2\times3\times\cos60^\circ=6\times\dfrac12=3\)。

**验证**（法二·坐标直算）
取 \(\overrightarrow{a}=(2,0,0)\)、\(\overrightarrow{b}=(3\cos60^\circ,3\sin60^\circ,0)=(\tfrac32,\tfrac{3\sqrt3}{2},0)\)，则 \(\overrightarrow{a}\cdot\overrightarrow{b}=2\times\tfrac32+0+0=3\) ✓。
（法三·极化恒等式互验）\(\overrightarrow{a}\cdot\overrightarrow{b}=\dfrac{|\overrightarrow{a}+\overrightarrow{b}|^2-|\overrightarrow{a}|^2-|\overrightarrow{b}|^2}{2}\)。由坐标 \(|a+b|^2=(\tfrac72)^2+(\tfrac{3\sqrt3}{2})^2=\tfrac{49}{4}+\tfrac{27}{4}=19\)，得 \((19-4-9)/2=3\) ✓。三法一致。

### 测-6（解答，13分）
**答案：\(|\overrightarrow{a}+\overrightarrow{b}|=\sqrt{13}\)**

**解法要点**（法一·先平方再开方）
\(\overrightarrow{a}\cdot\overrightarrow{b}=4\times3\times\cos120^\circ=12\times(-\tfrac12)=-6\)。
\(|\overrightarrow{a}+\overrightarrow{b}|^2=|\overrightarrow{a}|^2+2\overrightarrow{a}\cdot\overrightarrow{b}+|\overrightarrow{b}|^2=16-12+9=13\)。
模非负，故 \(|\overrightarrow{a}+\overrightarrow{b}|=\sqrt{13}\approx3.606\)。

**验证**（法二·坐标／平行四边形法则）
取 \(\overrightarrow{a}=(4,0,0)\)，\(\overrightarrow{b}=(3\cos120^\circ,3\sin120^\circ,0)=(-\tfrac32,\tfrac{3\sqrt3}{2},0)\)。
\(\overrightarrow{a}+\overrightarrow{b}=(\tfrac52,\tfrac{3\sqrt3}{2},0)\)，\(|\overrightarrow{a}+\overrightarrow{b}|^2=\tfrac{25}{4}+\tfrac{27}{4}=\tfrac{52}{4}=13\) ⇒ 同为 \(\sqrt{13}\) ✓。

**验证**（法三·余弦定理几何解释）
以 a、b 为邻边作平行四边形，\(|\overrightarrow{a}+\overrightarrow{b}|\) 是对应夹角 120° 的对角线：
\(d^2=4^2+3^2-2\cdot4\cdot3\cdot\cos(180^\circ-120^\circ)=16+9-24\cos60^\circ=25-12=13\) ⇒ \(d=\sqrt{13}\) ✓（三角形中 a 与 b 首尾相接所成内角为 180°−120°=60°，所对边即 \(|\overrightarrow{a}+\overrightarrow{b}|\)）。
**合理性检验**：\(|\,|a|-|b|\,|=1\le\sqrt{13}\approx3.606\le 7=|a|+|b|\)，符合三角不等式。三法一致。

---

## 三、答案速览（16 题）

| 题号 | 题型 | 答案 |
|---|---|---|
| 练-课-1 | 单选 | C |
| 练-课-2 | 填空 | \(\overrightarrow{a}-\overrightarrow{b}-\overrightarrow{c}\) |
| 练-课-3 | 填空 | \(x=1\)，\(y=\dfrac12\) |
| 练-课-4 | 填空 | \(-11\) |
| 练-课-5 | 填空 | \(\dfrac{\sqrt{10}}{5}\) |
| 练-课-6 | 填空 | \(\overrightarrow{b}-\overrightarrow{a}-\overrightarrow{c}\) |
| 练-课-10 | 解答13分 | \(P,M,A,B\) 四点共面（\(\overrightarrow{OP}=3\overrightarrow{OA}-2\overrightarrow{OB}\)，P 在直线 AB 上） |
| 练-课-11 | 填空 | \(\sqrt2\) |
| 练-课-12 | 多选 | AD |
| 练-课-15 | 填空 | \(\dfrac{\sqrt7}{2}\) |
| 测-1 | 单选 | B |
| 测-2 | 单选（选错误） | D |
| 测-3 | 单选 | B（k=2） |
| 测-4 | 多选6分 | AD |
| 测-5 | 填空5分 | 3 |
| 测-6 | 解答13分 | \(\sqrt{13}\) |

**方法覆盖登记**：16 题全部完成二法（及以上）互验或代验——
- 双/三法互验：练-课-2、3、4、5、6、10、11、15；测-3、4、5、6；
- 单选/多选按「定义正证 ＋ 反例否证 ＋ 坐标代验」三重判定：练-课-1、12；测-1、2。
- 无「仅单法」题项。
- **数值自校**：另用本地算术（Python，输入为本臂自设坐标，不含任何题解来源）复核课-4=−11、课-5=\(\sqrt{10}/5=0.6324555\)、课-11=\(\sqrt2=1.4142136\)、课-15=\(\sqrt7/2=1.3228757\)、测-5=3、测-6=\(\sqrt{13}=3.6055513\)，六项与解析结果逐位吻合。

**易错点自注（自查时特别核对过的三处）**
1. 练-课-15 中 \(\overrightarrow{BE}\cdot\overrightarrow{FD}\) 的**符号**：二面角 60° 是 \(\langle\overrightarrow{EB},\overrightarrow{FD}\rangle\)，折线链里出现的是 \(\overrightarrow{BE}\) 与 \(\overrightarrow{FD}\)，故为 \(-\tfrac38\)（首算 \(\tfrac{13}{4}\) 即此项符号失误，已由坐标法纠正为 \(\tfrac74\)）。
2. 练-课-11 平面角取自公共点 E 处两条垂直棱的边（EA、ED），不是 BF、CF（虽同为 60°，但混用端点易致向量链错误）。
3. 测-2 题干问「错误的是」，若按「正确的是」读将误选 A/B/C。

---

## 四、盲性自证

- **本次运行工具调用类型清单**（含对自有产出的校对；因自我校对本身会再产生调用，故按类型而非逐次计数，并注明主要次数）：
  1. `Read`：外部文本仅 `工作区/逻辑闸-样张族0911/slices/slice-05.md` ×1（91 行全量，唯一题面来源）；其余 `Read` 均落在本臂**自写产出** `sol-qwen/slice-05.md` 上用于校对（另有 2 次同类调用因参数校验失败，未产生任何读取）；
  2. `Grep`：仅在本臂自写产出 `sol-qwen/slice-05.md` 内查排版笔误与清单编号（×2 及以上），从未指向 `keys/`、答案册、`sol-glm/` 等目录；
  3. `Write` ×4：其中 3 次写入产出文件（首段 overwrite ＋ 两次 append），1 次误建一次性空占位文件 `sol-qwen/sol-qwen-tmp-seg3.md`（本臂自创，随即删除）；
  4. `Bash` ×5 及以上：①`wc -c`/`ls -la` 查产出字节数与目录文件名；②`cat >>` 追加自写产出第二段（＋末尾 `wc -c`）；③`rm -f` 删除上述自创占位文件并 `ls` 确认目录仅剩 slice-01…05；④`python -c` 用本臂自设坐标做算术复核（见「数值自校」）；⑤末次 `wc -c`/`ls` 确认成稿字节与目录清洁；全程未访问网络、未读取任何题库或答案文件内容；
  5. `Edit`（6 次及以上，最后一次即本条）：只改自写产出的排版笔误、表述清晰度与自证段事实，未改动任何题号的答案数值。
- **禁读项确认**：未打开 `keys/` 下任何文件；未打开任何答案册/答案键/`manifest`；未打开 `sol-glm/` 任何文件；`sol-qwen/` 目录内他臂产物（slice-01…04）仅由 `ls` 列出**文件名**，未读取其内容，亦未据此调整本题答案。
- **禁联网确认**：全程未调用 `WebSearch`/`FetchURL`，无任何题解检索；所有推导自含于本臂上下文。
- **独立性确认**：16 题解答与全部数值均在本次运行内独立推导；互验由本臂用**不同路径**（坐标 ⇄ 基底向量链 ⇄ 余弦定理/纯几何/极化恒等式）完成，忠实记录本臂结果，未向任何键面靠拢或调整。
- **过程留痕（不隐瞒）**：练-课-15 首次向量链计算因 \(\overrightarrow{BE}\cdot\overrightarrow{FD}\) 符号误取得 \(\tfrac{13}{4}\)，被坐标法（法二）否证后改为 \(\tfrac74\)，即最终答案 \(\dfrac{\sqrt7}{2}\)；该自纠过程已记入上节「易错点自注」第 1 条。
- 源片中题位标「略」及卷面未排题位（练-课 7～9、13～14、16 与测评卷未排题号）无题面，本臂未作答、未编造题面，按 manifest 处理。
