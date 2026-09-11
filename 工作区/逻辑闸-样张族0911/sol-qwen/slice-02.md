# slice-02 解答报告（qwen 臂·盲解）

- 题面来源：`工作区/逻辑闸-样张族0911/slices/slice-02.md`（导学件·课中探究，探究点一～九，18 题）
- 判据：《内容质量闸》卷三全量档（选择→逐选项判定后给字母；计算/解答→完整求解＋二法互验或代验；填空→值）
- 作答日期：2026-09-11

## 答案速览

| 题号 | 答案 |
|---|---|
| 导-T1-例1 | B |
| 导-T1-变1 | D |
| 导-T2-例1 | \(-\vec a+\vec b-\vec c\) |
| 导-T2-变1 | \(\vec a-\vec b-\vec c\) |
| 导-T3-例1 | \(x=1,\ y=\tfrac14\) |
| 导-T3-变1 | \(x=1,\ y=\tfrac12\) |
| 导-T4-例1 | C（①③） |
| 导-T4-变1 | 共面 |
| 导-T5-例1 | ABD |
| 导-T5-变1 | \(-11\) |
| 导-T6-例1 | \(60^\circ\) |
| 导-T6-变1 | \(\tfrac{\sqrt{10}}{5}\) |
| 导-T7-例1 | \((-1-\sqrt3,\ -1+\sqrt3)\) |
| 导-T7-变1 | \(\lambda=-\tfrac32\) |
| 导-T8-例1 | D（\(\sqrt{3-\sqrt2}\)） |
| 导-T8-变1 | \(\sqrt2\) |
| 导-T9-例1 | A（\(\tfrac{\sqrt{10}}2\)） |
| 导-T9-变1 | \(\tfrac{\sqrt7}2\) |

---

## 探究点一　空间向量的概念辨析

### 导-T1-例1
**答案：B**

解法要点（逐选项）：
- A 错。模相等只约束长度，不约束方向：\(\vec a=(1,0,0),\ \vec b=(0,1,0)\) 满足 \(|\vec a|=|\vec b|\)，但 \(\vec a\ne\vec b\) 且 \(\vec a\ne-\vec b\)。
- B 对。相反向量定义即大小相等、方向相反的向量，二者相加恰为零向量 \(\vec a+\vec b=\vec 0\)。
- C 错。零向量并非"没有方向"，教材规定其方向是任意的。
- D 错。单位向量只要求模为 1，方向任意：\((1,0,0)\) 与 \((0,0,1)\) 都是单位向量但不相等。

验证方式与结论：正确项 B 由定义直接成立；错误项 A、D 各给出反例，C 与教材"零向量方向任意"的约定矛盾。四项判定无遗漏，锁定 B。

### 导-T1-变1
**答案：D**

解法要点（逐选项，选"错误"项）：
- A 对。规定：零向量与任意向量平行（共线）。
- B 对。模为 0 的向量就是零向量。
- C 对。相等向量必同模。
- D 错。平行只约束方向关系不约束长度：\(\vec a=(1,0,0),\ \vec b=(2,0,0)\) 平行但模不等。

验证方式与结论：A、B、C 均为教材规定或定义级真命题；D 给出反例证伪。故错误说法选 D。

## 探究点二　空间向量的线性运算

### 导-T2-例1
**答案：\(\overrightarrow{A_1B}=-\vec a+\vec b-\vec c\)（即 \(\vec b-\vec a-\vec c\)）**

解法要点（路径法）：\(\overrightarrow{A_1B}=\overrightarrow{A_1A}+\overrightarrow{AB}=-\overrightarrow{CC_1}+(\overrightarrow{CB}-\overrightarrow{CA})=-\vec c+(\vec b-\vec a)=-\vec a+\vec b-\vec c\)。

验证方式与结论（坐标法互验）：取 \(C=(0,0,0),\ A=(1,0,0),\ B=(0,1,0),\ C_1=(0,0,1)\)（直三棱柱按正交基建模不失一般性，因结论只依赖仿射关系），则 \(A_1=(1,0,1)\)，\(\overrightarrow{A_1B}=(0,1,0)-(1,0,1)=(-1,1,-1)=-\vec a+\vec b-\vec c\)。两法一致。

### 导-T2-变1
**答案：\(\overrightarrow{D_1B}=\vec a-\vec b-\vec c\)**

解法要点（路径法）：\(\overrightarrow{D_1B}=\overrightarrow{D_1D}+\overrightarrow{DB}=-\vec c+(\overrightarrow{AB}-\overrightarrow{AD})=\vec a-\vec b-\vec c\)。

验证方式与结论（坐标法互验）：取 \(A=(0,0,0),\ B=(1,0,0),\ D=(0,1,0),\ A_1=(0,0,1)\)，则 \(D_1=(0,1,1)\)，\(\overrightarrow{D_1B}=(1,0,0)-(0,1,1)=(1,-1,-1)=\vec a-\vec b-\vec c\)。两法一致。

## 探究点三　用基底表示向量

### 导-T3-例1
**答案：\(x=1,\quad y=\dfrac14\)**

解法要点：上底面中 \(\overrightarrow{A_1C_1}=\overrightarrow{A_1B_1}+\overrightarrow{A_1D_1}=\overrightarrow{AB}+\overrightarrow{AD}\)，故
\(\overrightarrow{AE}=\overrightarrow{AA_1}+\overrightarrow{A_1E}=\overrightarrow{AA_1}+\tfrac14\overrightarrow{A_1C_1}=\overrightarrow{AA_1}+\tfrac14(\overrightarrow{AB}+\overrightarrow{AD})\)。与题设形式对照得 \(x=1,\ y=\tfrac14\)。

验证方式与结论（坐标法互验）：设 \(A=(0,0,0),\ B=(1,0,0),\ D=(0,1,0),\ A_1=(0,0,1),\ C_1=(1,1,1)\)。则 \(E=A_1+\tfrac14(1,1,0)=(\tfrac14,\tfrac14,1)\)，\(\overrightarrow{AE}=(\tfrac14,\tfrac14,1)=1\cdot\overrightarrow{AA_1}+\tfrac14(\overrightarrow{AB}+\overrightarrow{AD})\)，分解系数唯一（两向量组不共线），一致。

### 导-T3-变1
**答案：\(x=1,\quad y=\dfrac12\)**

解法要点：平行六面体中同样 \(\overrightarrow{A_1C_1}=\overrightarrow{AB}+\overrightarrow{AD}\)，故 \(\overrightarrow{AE}=\overrightarrow{AA_1}+\tfrac12(\overrightarrow{AB}+\overrightarrow{AD})\)，得 \(x=1,\ y=\tfrac12\)（E 为上底面对角线中点）。

验证方式与结论（坐标法互验）：取 \(A=(0,0,0),\ B=(1,0,0),\ D=(0,1,0),\ A_1=(0,0,1),\ C_1=(1,1,1)\)，\(E=(\tfrac12,\tfrac12,1)\)，\(\overrightarrow{AE}=(\tfrac12,\tfrac12,1)=\overrightarrow{AA_1}+\tfrac12(\overrightarrow{AB}+\overrightarrow{AD})\)。一致。

## 探究点四　共面向量的判定

### 导-T4-例1
**答案：C（①③）**

解法要点（逐命题）：
- ① 对。\(\vec p=x\vec a+y\vec b\) 说明 \(\vec p\) 可由 \(\vec a,\vec b\) 线性表示，三个向量平行于同一平面（\(\vec a\parallel\vec b\) 时退化为全共线，仍共面），这是共面定理的充分方向，不需 \(\vec a,\vec b\) 不共线的前提。
- ② 错。反向需要 \(\vec a,\vec b\) 不共线这一前提。反例：\(\vec a=\vec b=\vec 0\)，任意非零 \(\vec p\) 与它们"共面"（规定零向量与任何向量共面），但 \(\vec p\ne x\vec 0+y\vec 0\)。
- ③ 对。由 ①，\(\overrightarrow{MP},\overrightarrow{MA},\overrightarrow{MB}\) 共面向量；三向量又共起点 \(M\)，故终点 \(P,A,B\) 与 \(M\) 四点共面。
- ④ 错。同样缺"不共线"前提。反例：\(M,A,B\) 共线而 \(P\) 在该线外——四点仍共面（一线加一点确定平面），但任何 \(x\overrightarrow{MA}+y\overrightarrow{MB}\) 都沿该直线，表不出 \(\overrightarrow{MP}\)。

验证方式与结论：正向 ①③ 依共面定理及其推论成立；逆向 ②④ 各构造反例证伪。正确为 ①③，选项含 ①③ 而不含 ②④ 的只有 C。

### 导-T4-变1
**答案：\(P,M,A,B\) 四点共面。**

解法要点：已知 \(\overrightarrow{MP}=3\overrightarrow{MA}-2\overrightarrow{MB}\)，即 \(\overrightarrow{MP}\) 是 \(\overrightarrow{MA},\overrightarrow{MB}\) 的线性组合。分两种情形：
1. 若 \(\overrightarrow{MA},\overrightarrow{MB}\) 不共线，二者确定过 \(M\) 的平面 \(\alpha\)，则 \(\overrightarrow{MP}\parallel\alpha\) 且起点 \(M\in\alpha\)，故 \(P\in\alpha\)，四点共面；
2. 若 \(\overrightarrow{MA},\overrightarrow{MB}\) 共线，则 \(M,A,B\) 共线，且 \(\overrightarrow{MP}=3\overrightarrow{MA}-2\overrightarrow{MB}\) 与该直线共线，\(P\) 也在直线上，四点共线，当然共面。
综上四点必共面。

验证方式与结论（坐标实例）：取 \(M=(0,0,0),A=(1,0,0),B=(0,1,0)\)，则 \(\overrightarrow{MP}=3(1,0,0)-2(0,1,0)=(3,-2,0)\)，\(P=(3,-2,0)\) 落在 \(z=0\) 平面内，与 \(M,A,B\) 共面，与结论一致。

## 探究点五　数量积的概念与运算律（多选题）

### 导-T5-例1（多选）
**答案：ABD**

解法要点（逐项）：
- A 对。\(\vec a^{\,2}=\vec a\cdot\vec a=|\vec a||\vec a|\cos 0^\circ=|\vec a|^2\)，数量积自身的定义式。
- B 错。向量之间没有除法，\(\dfrac{\vec b}{\vec a}\) 无意义；且左边是数、右边若强行解释也不是数，等式两端类型不符。
- C 错。\((\vec a\cdot\vec b)^2=|\vec a|^2|\vec b|^2\cos^2\theta\)，而 \(\vec a^{\,2}\vec b^{\,2}=|\vec a|^2|\vec b|^2\)，仅当 \(\cos^2\theta=1\)（共线）时相等。反例：\(\vec a\perp\vec b\) 非零时左边 \(=0\)、右边 \(>0\)。
- D 对。数量积满足分配律，\((\vec a-\vec b)^2=(\vec a-\vec b)\cdot(\vec a-\vec b)=\vec a^{\,2}-2\vec a\cdot\vec b+\vec b^{\,2}\)，与多项式展开同构。

验证方式与结论：A、D 由定义与运算律推出；B 属类型错误；C 用垂直反例证伪（取 \(\vec a=(1,0,0),\vec b=(0,1,0)\)：左 \(=0\)，右 \(=1\)）。故选 ABD。

### 导-T5-变1
**答案：\(-11\)**

解法要点：\(\vec a\cdot\vec b=2\times3\times\cos 60^\circ=3\)。
\((\vec a+2\vec b)\cdot(\vec a-\vec b)=|\vec a|^2-\vec a\cdot\vec b+2\vec b\cdot\vec a-2|\vec b|^2=|\vec a|^2+\vec a\cdot\vec b-2|\vec b|^2=4+3-18=-11\)。

验证方式与结论（坐标法互验）：取 \(\vec a=(2,0,0),\ \vec b=(3\cos60^\circ,3\sin60^\circ,0)=(1.5,\tfrac{3\sqrt3}2,0)\)。则 \(\vec a+2\vec b=(5,3\sqrt3,0)\)，\(\vec a-\vec b=(0.5,-\tfrac{3\sqrt3}2,0)\)，点积 \(=5(0.5)+3\sqrt3\cdot(-\tfrac{3\sqrt3}2)=2.5-13.5=-11\)。两法一致。

## 探究点六　数量积求夹角与投影

### 导-T6-例1
**答案：夹角为 \(60^\circ\)**

解法要点（坐标法）：设棱长为 1，\(A=(0,0,0),B=(1,0,0),C=(1,1,0),C_1=(1,1,1)\)。
\(\overrightarrow{BC_1}=(0,1,1),\ \overrightarrow{AC}=(1,1,0)\)，
\(\cos\theta=\dfrac{0+1+0}{\sqrt2\cdot\sqrt2}=\dfrac12\)，\(\theta=60^\circ\)。

验证方式与结论（几何法互验）：正方体中 \(\overrightarrow{BC_1}=\overrightarrow{AD_1}\)，故所求角即 \(\angle D_1AC\)（或其补角判定）；连 \(CD_1\)，\(\triangle AD_1C\) 三边均为面对角线，是等边三角形，\(\angle D_1AC=60^\circ\)。两法一致，夹角 \(60^\circ\)。

### 导-T6-变1
**答案：\(\dfrac{\sqrt{10}}{5}\)（即 \(\dfrac{2}{\sqrt{10}}\)）**

解法要点（坐标法）：\(A=(0,0,0),\ B=(2,0,0),\ D=(0,2,0),\ A_1=(0,0,1)\)，则 \(B_1=(2,0,1),\ C=(2,2,0)\)。
\(\overrightarrow{AB_1}=(2,0,1),\ \overrightarrow{AC}=(2,2,0)\)，
\(\cos\theta=\dfrac{4+0+0}{\sqrt5\cdot2\sqrt2}=\dfrac{4}{2\sqrt{10}}=\dfrac{2}{\sqrt{10}}=\dfrac{\sqrt{10}}5\approx0.632\)。

验证方式与结论（余弦定理互验）：三角形 \(AB_1C\) 中 \(AB_1=\sqrt{4+1}=\sqrt5,\ AC=\sqrt{4+4}=2\sqrt2,\ B_1C=\sqrt{0+4+1}=\sqrt5\)。
\(\cos\angle B_1AC=\dfrac{AB_1^2+AC^2-B_1C^2}{2\cdot AB_1\cdot AC}=\dfrac{5+8-5}{2\cdot\sqrt5\cdot2\sqrt2}=\dfrac{8}{4\sqrt{10}}=\dfrac{\sqrt{10}}5\)。两法一致。

## 探究点七　数量积条件求参

### 导-T7-例1
**答案：\(\lambda\in(-1-\sqrt3,\ -1+\sqrt3)\)**

解法要点：\(\vec a\cdot\vec b=2\times1\times\cos60^\circ=1,\ |\vec a|^2=4,\ |\vec b|^2=1\)。
设 \(\vec u=\vec a+\lambda\vec b,\ \vec v=\lambda\vec a-2\vec b\)，
\(\vec u\cdot\vec v=\lambda|\vec a|^2+(\lambda^2-2)\vec a\cdot\vec b-2\lambda|\vec b|^2=4\lambda+\lambda^2-2-2\lambda=\lambda^2+2\lambda-2\)。
夹角为钝角需 \(\vec u\cdot\vec v<0\)：\(\lambda^2+2\lambda-2<0\ \Rightarrow\ -1-\sqrt3<\lambda<-1+\sqrt3\)。
再排除共线（反向即 \(180^\circ\) 不属于钝角）情形：设 \(\vec a+\lambda\vec b=t(\lambda\vec a-2\vec b)\)，因 \(\vec a,\vec b\) 夹角 \(60^\circ\) 不共线，比较系数得 \(1=t\lambda,\ \lambda=-2t\)，消元得 \(\lambda^2=-2\)，无实数解——两向量恒不共线，无须从区间中挖点。（\(\vec u,\vec v\) 也恒非零：\(\vec a+\lambda\vec b=\vec 0\) 将迫使 \(\vec a\parallel\vec b\)，矛盾。）

验证方式与结论（坐标法互验）：取 \(\vec a=(2,0,0),\ \vec b=(\tfrac12,\tfrac{\sqrt3}2,0)\)。
\(\vec u\cdot\vec v=(2+\tfrac\lambda2)(2\lambda-1)+\tfrac{\sqrt3\lambda}2(-\sqrt3)=\lambda^2+2\lambda-2\)，与展开法一致；共线条件 \(u_xv_y-u_yv_x=-\sqrt3(\lambda^2+2)\ne0\) 恒成立，佐证"恒不共线"。区间内取 \(\lambda=0\)：\(\cos=\frac{-2}{2\cdot2}=-\tfrac12\)，夹角 \(120^\circ\) 为钝角 ✓；区间外取 \(\lambda=1\)：点积 \(=1>0\)，非钝角 ✓。答案 \((-1-\sqrt3,\,-1+\sqrt3)\)。

### 导-T7-变1
**答案：\(\lambda=-\dfrac32\)**

解法要点：\(\vec a\cdot\vec b=3\sqrt2\times4\times\cos135^\circ=12\sqrt2\times(-\tfrac{\sqrt2}2)=-12\)；\(|\vec a|^2=18,\ |\vec b|^2=16\)。
\(\vec m\cdot\vec n=(\vec a+\vec b)\cdot(\vec a+\lambda\vec b)=|\vec a|^2+(\lambda+1)\vec a\cdot\vec b+\lambda|\vec b|^2=18-12(\lambda+1)+16\lambda=6+4\lambda\)。
\(\vec m\perp\vec n\iff 6+4\lambda=0\iff \lambda=-\tfrac32\)。

验证方式与结论（坐标法互验）：取 \(\vec b=(4,0,0)\)，\(\vec a=3\sqrt2(\cos135^\circ,\sin135^\circ,0)=(-3,3,0)\)。则 \(\vec m=(1,3,0)\)，\(\vec n=(-3+4\lambda,\,3,\,0)\)，\(\vec m\cdot\vec n=(-3+4\lambda)+9=6+4\lambda=0\Rightarrow\lambda=-1.5\)。两法一致；代回 \(\vec n=(-9,3,0)\)，与 \(\vec m=(1,3,0)\) 点积 \(-9+9=0\) ✓。

## 探究点八　数量积求距离（展开法）

### 导-T8-例1
**答案：D（\(\sqrt{3-\sqrt2}\)）**

解法要点（向量展开法）：两正方形共用棱 \(EF\)，\(AE\perp EF,\ DE\perp EF\)，故二面角 \(A\text{-}EF\text{-}D\) 的平面角 \(\angle AED=45^\circ\)，且 \(BF\parallel AE\)。
\(\overrightarrow{BD}=\overrightarrow{BF}+\overrightarrow{FE}+\overrightarrow{ED}\)，其中 \(\overrightarrow{BF}\perp\overrightarrow{FE}\)、\(\overrightarrow{FE}\perp\overrightarrow{ED}\)，\(\langle\overrightarrow{BF},\overrightarrow{ED}\rangle=180^\circ-45^\circ=135^\circ\)（\(\overrightarrow{BF}=-\overrightarrow{EA}\) 方向反向）。
\(|\overrightarrow{BD}|^2=1+1+1+2\cos135^\circ=3-\sqrt2\)。
逐项判定：A \(\sqrt3\) 对应直二面角（\(90^\circ\)）情形，错；B \(\sqrt2\) 对应 \(60^\circ\)（即变1之值），错；C \(1\) 明显偏小，错；D 与展开结果一致，对。

验证方式与结论（坐标法互验）：取 \(E=(0,0,0),\ F=(1,0,0),\ A=(0,1,0),\ D=(0,\tfrac{\sqrt2}2,\tfrac{\sqrt2}2)\)（保证 \(AE\perp EF,\ DE\perp EF\) 且平面角 \(\angle AED=45^\circ\)），\(B=A+\overrightarrow{EF}=(1,1,0)\)。
\(\overrightarrow{BD}=(-1,\tfrac{\sqrt2}2-1,\tfrac{\sqrt2}2)\)，\(|\overrightarrow{BD}|^2=1+(\tfrac32-\sqrt2)+\tfrac12=3-\sqrt2\approx1.586\)，\(|BD|\approx1.259\)。两法一致，选 D。

### 导-T8-变1
**答案：\(\sqrt2\)**

解法要点：与例1同构，二面角平面角改为 \(60^\circ\)，\(\langle\overrightarrow{BF},\overrightarrow{ED}\rangle=120^\circ\)。
\(|\overrightarrow{BD}|^2=|\overrightarrow{BF}|^2+|\overrightarrow{FE}|^2+|\overrightarrow{ED}|^2+2|\overrightarrow{BF}||\overrightarrow{ED}|\cos120^\circ=3-1=2\)，\(BD=\sqrt2\)。

验证方式与结论（坐标法互验）：\(E=(0,0,0),F=(1,0,0),B=(1,1,0),D=(0,\cos60^\circ,\sin60^\circ)=(0,\tfrac12,\tfrac{\sqrt3}2)\)。
\(\overrightarrow{BD}=(-1,-\tfrac12,\tfrac{\sqrt3}2)\)，\(|\overrightarrow{BD}|^2=1+(-\tfrac12)^2+(\tfrac{\sqrt3}2)^2=1+0.25+0.75=2\)，\(BD=\sqrt2\)。两法一致。

## 探究点九　数量积求距离（折叠矩形）

### 导-T9-例1
**答案：A（\(\dfrac{\sqrt{10}}{2}\)）**

解法要点：矩形中 \(AC=\sqrt{1+3}=2\)。设 \(B,D\) 在 \(AC\) 上的垂足分别为 \(B',D'\)。
Rt△ABC（直角在 B）：\(BB'=\dfrac{AB\cdot BC}{AC}=\dfrac{\sqrt3}2,\ AB'=\dfrac{AB^2}{AC}=\dfrac12\)；
Rt△ACD（直角在 D）：\(DD'=\dfrac{\sqrt3}2,\ AD'=\dfrac{AD^2}{AC}=\dfrac32\)。故 \(B'D'=\dfrac32-\dfrac12=1\)。
折叠不改变各面内的长度与垂直关系，所以仍有 \(BB'\perp AC,\ DD'\perp AC\)，于是射线 \(\overrightarrow{B'B}\) 与 \(\overrightarrow{D'D}\) 的夹角即二面角 \(B\text{-}AC\text{-}D\) 的平面角 \(90^\circ\)，故 \(\overrightarrow{B'B}\perp\overrightarrow{D'D}\)。
\(\overrightarrow{BD}=\overrightarrow{BB'}+\overrightarrow{B'D'}+\overrightarrow{D'D}\)，三段两两垂直（\(\overrightarrow{BB'}\perp\overrightarrow{B'D'}\)、\(\overrightarrow{B'D'}\perp\overrightarrow{D'D}\)、\(\overrightarrow{BB'}\perp\overrightarrow{D'D}\) 由直二面角），
\(|\overrightarrow{BD}|^2=\tfrac34+1+\tfrac34=\tfrac52\)，\(|\overrightarrow{BD}|=\sqrt{\tfrac52}=\tfrac{\sqrt{10}}2\)。
逐项判定：B、C 的平方分别为 \(\tfrac32,\tfrac54\)，均不等于 \(\tfrac52\)，错；D \(2\) 是未折叠（平展 \(180^\circ\)）情形的距离，错；A 对。

验证方式与结论（空间坐标互验）：沿 \(AC\) 建系：\(B'=(\tfrac12,0,0),\ D'=(\tfrac32,0,0),\ B=(\tfrac12,\tfrac{\sqrt3}2,0),\ D=(\tfrac32,0,\tfrac{\sqrt3}2)\)（两面垂直故 \(D\) 偏离方向取 \(z\) 轴）。
\(\overrightarrow{BD}=(1,-\tfrac{\sqrt3}2,\tfrac{\sqrt3}2)\)，\(|\overrightarrow{BD}|^2=1+\tfrac34+\tfrac34=\tfrac52\)，\(|\overrightarrow{BD}|=\tfrac{\sqrt{10}}2\approx1.581\)。另以通用式 \(|BD|^2=\tfrac52-\tfrac32\cos\theta\)（\(\theta\) 为二面角）自检：\(\theta=180^\circ\) 时 \(|BD|=2\) 恰为原矩形对角线距（原矩形中 \(B=(1,0),D=(0,\sqrt3)\)，距离 2）✓。多法一致，选 A。

### 导-T9-变1
**答案：\(\dfrac{\sqrt7}{2}\)**

解法要点：例1 的框架不变，仅二面角平面角由 \(90^\circ\) 改为 \(60^\circ\)，即 \(\langle\overrightarrow{B'B},\overrightarrow{D'D}\rangle=60^\circ\)，\(\langle\overrightarrow{BB'},\overrightarrow{D'D}\rangle=120^\circ\)。
\(|\overrightarrow{BD}|^2=\tfrac34+1+\tfrac34+2\cdot\tfrac{\sqrt3}2\cdot\tfrac{\sqrt3}2\cos120^\circ=\tfrac52-\tfrac34=\tfrac74\)，\(|\overrightarrow{BD}|=\dfrac{\sqrt7}2\)。

验证方式与结论（坐标法＋通式互验）：\(B=(\tfrac12,\tfrac{\sqrt3}2,0)\)，\(D=(\tfrac32,\ \tfrac{\sqrt3}2\cos60^\circ,\ \tfrac{\sqrt3}2\sin60^\circ)=(\tfrac32,\tfrac{\sqrt3}4,\tfrac34)\)。
\(\overrightarrow{BD}=(1,\tfrac{\sqrt3}4-\tfrac{\sqrt3}2,\tfrac34)=(1,-\tfrac{\sqrt3}4,\tfrac34)\)，
\(|\overrightarrow{BD}|^2=1+\tfrac{3}{16}+\tfrac{9}{16}=1+\tfrac{12}{16}=\tfrac74\) ✓；亦合通用式 \(\tfrac52-\tfrac32\cos60^\circ=\tfrac52-\tfrac34=\tfrac74\)。两法一致，\(|\overrightarrow{BD}|=\tfrac{\sqrt7}2\approx1.323\)。

---

## 附注

- 18 题全部完成二法互验或代验（选择题为逐选项判定＋反例/坐标双重确认），无"仅单法"登记项。
- 两处图形题（导-T3-例1、导-T6-例1、导-T8-例1 附图）仅按题面文字与标准命名约定（正方体/长方体顶点上下对应、正方形顶点顺序即周界顺序）建模，坐标验证均自洽。

## 盲性自证

仅读切片文件 `工作区/逻辑闸-样张族0911/slices/slice-02.md`，未触任何答案键与他人解答：全程未读取 `keys/` 目录、未读取任何答案册/答案键文件、未进入 `sol-glm/` 目录、未联网搜题解、未使用 git。所有答案均为本臂独立盲算所得。
