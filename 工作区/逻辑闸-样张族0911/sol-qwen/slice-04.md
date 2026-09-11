# sol-qwen｜slice-04 盲解答卷

- 解题对象：`slices/slice-04.md`（17 题＝增量 7＋滚动 10；滚动卷第 8、12–14 题位源中「略」无题面，不作答）
- 解题模式：盲解（qwen 臂）。全程仅读题面片，未接触任何键面/答案（见文末盲性自证）。
- 答案速览：增-探-例1＝B｜增-探-变1＝共面（且 P、A、B 共线）｜增-评1＝B｜增-评2＝C｜增-评3＝D｜增-评4＝3｜增-评5＝√13｜练-滚-1＝B｜练-滚-2＝D｜练-滚-3＝C｜练-滚-4＝D｜练-滚-5＝B｜练-滚-6＝A｜练-滚-7＝AD｜练-滚-9＝3｜练-滚-10＝√13｜练-滚-11＝\((-1-\sqrt3,\,-1+\sqrt3)\)

## 一、导学增量·课中探究

### 增-探-例1｜答案：B

- **解法要点（逐选项）**：
  - A 错：模相等只约束长度，不约束方向。反例：\(\vec a=(1,0),\ \vec b=(0,1)\)，\(|\vec a|=|\vec b|=1\)，但 \(\vec a\neq\vec b\) 且 \(\vec a\neq-\vec b\)。
  - B 对：相反向量的定义即"模相等、方向相反"，故 \(\vec a+\vec b=\vec 0\)（结果为**零向量**，写法带向量号，正确）。
  - C 错：教材规定零向量**方向任意**，而非"没有方向"。
  - D 错：单位向量只规定模为 1，方向任取。反例：\(\vec a=(1,0),\ \vec b=(0,1)\) 均为单位向量但不相等。
- **验证方式与结论**：第二法＝坐标特例复核——取 \(\vec a=(1,0),\vec b=(0,1)\) 同时否证 A、D；取 \(\vec b=-\vec a\) 代入 B 得 \(\vec 0\) 成立；C 与教材"方向任意"的规定直接矛盾。两法一致，判定 **B**。

### 增-探-变1｜答案：P、M、A、B 四点共面（更强结论：P、A、B 三点共线）

- **解法要点**：\(\overrightarrow{MP}=3\overrightarrow{MA}-2\overrightarrow{MB}\)。法一（共面向量定理）：\(\overrightarrow{MP}\) 可表为 \(\overrightarrow{MA},\overrightarrow{MB}\) 的线性组合，故 \(\overrightarrow{MP},\overrightarrow{MA},\overrightarrow{MB}\) 共面；三有向线段共起点 \(M\)，于是 \(P,A,B\) 都落在 \(M\) 与这些向量张成的平面内（若 \(\overrightarrow{MA},\overrightarrow{MB}\) 共线，则 \(M,A,B\) 共线，直线与点 \(P\)（其 \(\overrightarrow{MP}\) 亦沿该方向）仍共面），故四点共面。
- **验证方式与结论**：第二法（系数和＋坐标）。①系数和 \(3+(-2)=1\)：\(\overrightarrow{AP}=\overrightarrow{MP}-\overrightarrow{MA}=2\overrightarrow{MA}-2\overrightarrow{MB}=2\overrightarrow{BA}\)，得 \(P,A,B\) **共线**，与任意点 \(M\) 必共面（过直线 \(AB\) 与点 \(M\) 的平面即所求）。②坐标实例：取 \(M=(0,0,0),A=(1,0,0),B=(0,1,0)\)，则 \(P=3A-2B=(3,-2,0)\)，第三坐标为 0，与 \(M,A,B\) 同在 \(z=0\) 面；且 \(3+(-2)=1\) 满足直线 \(AB\) 方程 \(x+y=1\)，印证共线。两法一致：**共面成立**。

## 二、导学增量·课堂评价

### 增-评1｜答案：B（\(k=2\)）

- **解法要点（逐选项）**：\(\vec a\parallel\vec b\iff\exists\lambda,\ \vec b=\lambda\vec a\)（\(\vec a=2\vec{e_1}+\vec{e_2}\neq\vec 0\)，因 \(\vec{e_1},\vec{e_2}\) 不共线）。由 \(4\vec{e_1}+k\vec{e_2}=2\lambda\vec{e_1}+\lambda\vec{e_2}\)，不共线基底系数唯一：\(2\lambda=4,\ k=\lambda\)，得 \(k=2\)。A \(\frac12\)、C \(-\frac12\)、D \(3\) 均不满足方程组，逐否。
- **验证方式与结论**：第二法＝代回：\(k=2\) 时 \(\vec b=4\vec{e_1}+2\vec{e_2}=2\vec a\)，确平行。两法一致，**B**。

### 增-评2｜答案：C（充要条件）

- **解法要点（逐选项）**：题设 \(\vec a,\vec b\) 均**非零**。充分性：\(\vec a\cdot\vec b=|\vec a||\vec b|\cos\langle\vec a,\vec b\rangle=0\)，且非零故 \(|\vec a||\vec b|\neq0\)，得 \(\cos\langle\vec a,\vec b\rangle=0\)，即夹角 \(90^\circ\)，即 \(\vec a\perp\vec b\)。必要性：\(\vec a\perp\vec b\Rightarrow\langle\vec a,\vec b\rangle=90^\circ\Rightarrow\vec a\cdot\vec b=0\)。双向皆真，故充要。A（仅充分）、B（仅必要）、D（皆非）逐否。
- **验证方式与结论**：第二法＝坐标例示双向：\(\vec a=(1,0,0),\vec b=(0,2,3)\)，点乘为 0 且夹角直角，两向互推一致。注意"非零"前提正是排除零向量歧义的关卡，题面已给。两法一致，**C**。

### 增-评3｜答案：D（\(\overrightarrow{EF}\)）

- **解法要点**：两条路径拆 \(\overrightarrow{EF}\)：\(\overrightarrow{EF}=\overrightarrow{EA}+\overrightarrow{AD}+\overrightarrow{DF}\)；\(\overrightarrow{EF}=\overrightarrow{EB}+\overrightarrow{BC}+\overrightarrow{CF}\)。两式相加：\(2\overrightarrow{EF}=(\overrightarrow{EA}+\overrightarrow{EB})+(\overrightarrow{AD}+\overrightarrow{BC})+(\overrightarrow{DF}+\overrightarrow{CF})\)。\(E,F\) 为中点 \(\Rightarrow\overrightarrow{EA}+\overrightarrow{EB}=\vec 0,\ \overrightarrow{DF}+\overrightarrow{CF}=\tfrac12\overrightarrow{DC}+\tfrac12\overrightarrow{CD}=\vec 0\)。故 \(\overrightarrow{EF}=\frac12(\overrightarrow{AD}+\overrightarrow{BC})\)。A（差系数 2）、B（\(-\overrightarrow{EF}\)，方向反）、C（\(\overrightarrow{FE}=-\overrightarrow{EF}\)，同 B）逐否。
- **验证方式与结论**：第二法＝坐标实例：\(A(0,0,0),B(2,0,0),C(1,2,0),D(0,0,2)\)（不共面），算得 \(E(1,0,0),F(\tfrac12,1,1)\)，\(\frac12(\overrightarrow{AD}+\overrightarrow{BC})=(-\tfrac12,1,1)=\overrightarrow{EF}\)，≠\(\overrightarrow{FE}\)。两法一致，**D**。

### 增-评4｜答案：\(3\)

- **解法要点**：\(\vec a\cdot\vec b=|\vec a||\vec b|\cos\langle\vec a,\vec b\rangle=2\times3\times\cos60^\circ=6\times\frac12=3\)。
- **验证方式与结论**：第二法＝坐标实现：取 \(\vec a=(2,0),\ \vec b=(3\cos60^\circ,3\sin60^\circ)=(1.5,\tfrac{3\sqrt3}{2})\)，\(\vec a\cdot\vec b=2\times1.5=3\)；代验：\(|\vec a+\vec b|^2=4+9+2\times3=19\in[1,25]=(|\vec a|-|\vec b|)^2\text{..}(|\vec a|+|\vec b|)^2\)，范围合理。两法一致，**3**。

### 增-评5｜答案：\(\sqrt{13}\)

- **解法要点**：先 \(\vec a\cdot\vec b=4\times3\times\cos120^\circ=-6\)；再展开 \(|\vec a+\vec b|^2=|\vec a|^2+2\vec a\cdot\vec b+|\vec b|^2=16-12+9=13\)，取正根 \(|\vec a+\vec b|=\sqrt{13}\)。
- **验证方式与结论**：第二法＝三角形法则＋余弦定理：首尾相接时 \(\vec a+\vec b\) 对应三角形的第三边，其夹角内角为 \(180^\circ-120^\circ=60^\circ\)，\(d^2=16+9-2\cdot4\cdot3\cos60^\circ=13\)。代验范围：\(1=|4-3|<\sqrt{13}\approx3.61<7\)。两法一致，**\(\sqrt{13}\)**。

## 三、练习线·滚动习题（一）〔范围1.1〕

### 练-滚-1（单项选择）｜答案：B

- **解法要点（逐选项）**：与增-探-例1题面完全相同，判定同上——A 错（模等不定方向，反例 \(\vec a=(1,0),\vec b=(0,1)\)）；B 对（相反向量定义即 \(\vec a+\vec b=\vec 0\)）；C 错（零向量方向**任意**而非没有方向）；D 错（单位向量方向任取，未必相等）。
- **验证方式与结论**：坐标特例复核同增-探-例1（同题同法两道各自独立判一遍，结果一致）。**B**。

### 练-滚-2（单项选择）｜答案：D（选出"错误"的一项）

- **解法要点（逐选项）**：
  - A 对：教材规定零向量与任意向量平行（方向任意），不选。
  - B 对：模为 0 的向量唯有零向量，\(|\vec a|=0\Rightarrow\vec a=\vec 0\)，不选。
  - C 对：相等向量模必相等，不选。
  - D 错：平行（共线）只约束方向，不约束长度。反例：\(\vec a=2\vec b\)（\(\vec b\neq\vec 0\)）平行但 \(|\vec a|=2|\vec b|\neq|\vec b|\)。应选。
- **验证方式与结论**：第二法＝数轴共线实现：\(\vec a,\vec b\) 同向取长度 1 和 3，验证 D 断言崩溃，而 A、B、C 在同模型下均真。两法一致，**D**。

### 练-滚-3（单项选择）｜答案：C（①③）

- **解法要点（逐命题）**：
  - ① 对：\(\vec p=x\vec a+y\vec b\) 表明 \(\vec p,\vec a,\vec b\) 共面（共面向量定理的正向，无须 \(\vec a,\vec b\) 不共线：若二者共线，\(\vec p\) 亦沿同方向，三向量仍共面）。
  - ② 错：逆命题需 \(\vec a,\vec b\) **不共线**才成立，题面未给。反例：\(\vec a=\vec b=(1,0,0),\ \vec p=(0,1,0)\)，三向量同在 \(xy\) 面（共面），但 \(x\vec a+y\vec b=(x+y,0,0)\neq\vec p\)。
  - ③ 对：由①，\(\overrightarrow{MP},\overrightarrow{MA},\overrightarrow{MB}\) 共面，三有向线段共起点 \(M\)，故 \(P,M,A,B\) 四点共面。
  - ④ 错：同②，缺"不共线"关卡。反例：\(M(0,0,0),A(1,0,0),B(2,0,0),P(0,1,0)\) 同在 \(xy\) 面，但 \(\overrightarrow{MP}=(0,1,0)\neq(x+2y,0,0)=x\overrightarrow{MA}+y\overrightarrow{MB}\)。
  - 选项核对：A（①②）含②否；B（①③④）含④否；D（②④）两错全取否；C（①③）恰为真命题集。
- **验证方式与结论**：第二法＝把①③的正向推理各代入随机坐标验证（如 \(\vec a=(1,2,0),\vec b=(0,1,1),x=y=1\Rightarrow\vec p=(1,3,1)\) 与 \(\vec a,\vec b\) 同过原点，混合积 \((\vec a\times\vec b)\cdot\vec p=0\) 验共面），正向恒真、逆向两处反例均具体成立。两法一致，**C**。

### 练-滚-4（单项选择）｜答案：D

- **解法要点**：与增-评3题面完全相同：双路径相加 \(2\overrightarrow{EF}=(\overrightarrow{EA}+\overrightarrow{EB})+(\overrightarrow{AD}+\overrightarrow{BC})+(\overrightarrow{DF}+\overrightarrow{CF})=\overrightarrow{AD}+\overrightarrow{BC}\)（中点使两组向量和为 \(\vec 0\)），故 \(\frac12(\overrightarrow{AD}+\overrightarrow{BC})=\overrightarrow{EF}\)。A（\(2\overrightarrow{EF}\)）、B（\(-\overrightarrow{EF}\)）、C（\(\overrightarrow{FE}=-\overrightarrow{EF}\)）逐否。
- **验证方式与结论**：第二法＝换一组坐标独立复算：\(A(1,2,3),B(3,0,1),C(0,4,2),D(2,1,5)\)，\(E(2,1,2),F(1,2.5,3.5)\)；\(\overrightarrow{AD}=(1,-1,2),\overrightarrow{BC}=(-3,4,1)\)，和之半 \=(-1,1.5,1.5)=\overrightarrow{EF}=F-E\) ✓。两法一致，**D**。

### 练-滚-5（单项选择）｜答案：B

- **解法要点**：与增-评1题面完全相同：\(\vec b=\lambda\vec a\) 按不共线基底比较系数，\(4=2\lambda,\ k=\lambda\Rightarrow k=2\)；A、C、D 值代入均使方程组无解。
- **验证方式与结论**：代回 \(k=2\)：\(\vec b=2\vec a\) ✓ 平行。两法一致，**B**。

### 练-滚-6（单项选择）｜答案：A（\(|\overrightarrow{BD}|=\frac{\sqrt{10}}{2}\)）

- **解法要点**：矩形中 \(AB=1,BC=\sqrt3\Rightarrow AC=\sqrt{1+3}=2\)。折痕 \(AC\) 两侧三角形形状不变：\(B\) 到 \(AC\) 的垂足 \(P\) 满足 \(AP=\frac{AB^2}{AC}=\frac12\)、\(BP=\frac{AB\cdot BC}{AC}=\frac{\sqrt3}{2}\)；\(D\) 到 \(AC\) 的垂足 \(Q\) 满足 \(AQ=\frac{AD^2}{AC}=\frac{3}{2}\)（\(AD=\sqrt3,DC=1\)）、\(DQ=\frac{\sqrt3}{2}\)，\(PQ=1\)。建系：\(AC\) 为 \(x\) 轴，面 \(ACD\) 为 \(xy\) 面、面 \(ABC\) 为 \(xz\) 面（两面垂直）：\(B=(\frac12,0,\frac{\sqrt3}{2}),\ D=(\frac32,\frac{\sqrt3}{2},0)\)。\(\overrightarrow{BD}=(1,\frac{\sqrt3}{2},-\frac{\sqrt3}{2})\)，\(|\overrightarrow{BD}|^2=1+\frac34+\frac34=\frac52\Rightarrow |\overrightarrow{BD}|=\frac{\sqrt{10}}{2}\)。选项核对：B \(\frac{\sqrt6}{2}\)、C \(\frac{\sqrt5}{2}\)、D \(2\) 与 \(\sqrt{2.5}\approx1.581\) 不符。
- **验证方式与结论**：第二法＝垂线分解公式 \(BD^2=PQ^2+BP^2+DQ^2+2\,BP\cdot DQ\cos\langle BP\text{向},DQ\text{向}\rangle\)，二阶垂直于同一直线 \(AC\) 且两面成 \(90^\circ\) 二面角，故两垂向正交、交叉项为 0：\(BD^2=1+\frac34+\frac34=\frac52\) ✓；并用作废基准自检：若未折（二面角摊平，两垂向反向），公式给 \(BD^2=1+(\frac{\sqrt3}{2}+\frac{\sqrt3}{2})^2=4\Rightarrow BD=2\)，恰等于原矩形对角线长，公式外推正确。两法一致，**A**。

### 练-滚-7（多项选择）｜答案：AD

- **解法要点（逐选项）**：
  - A 对：\(\vec a^2=\vec a\cdot\vec a=|\vec a|^2\cos0^\circ=|\vec a|^2\)，数量积运算律。
  - B 错：\(\frac{\vec b}{\vec a}\) 无意义——向量之间没有除法运算，等式右端根本不是向量表达式；且左端是数、右端名义是向量，类型不通。
  - C 错：\((\vec a\cdot\vec b)^2=|\vec a|^2|\vec b|^2\cos^2\theta\)，仅当 \(\cos^2\theta=1\)（共线）时等于 \(\vec a^2\vec b^2\)。反例：\(\vec a\perp\vec b\) 时左端 \(=0\)、右端 \(=|\vec a|^2|\vec b|^2>0\)。
  - D 对：点乘满足交换律与分配律，\((\vec a-\vec b)^2=\vec a^2-2\vec a\cdot\vec b+\vec b^2\) 展开合法。
- **验证方式与结论**：第二法＝坐标数值化：\(\vec a=(1,0,0),\vec b=(0,1,1)\)：A：\(|\vec a|^2=1\) ✓；B 无定义 ✗；C：左 \((\vec a\cdot\vec b)^2=0\)，右 \(1\times2=2\) ✗；D：\((\vec a-\vec b)^2=|(1,-1,-1)|^2=3\)，\(\vec a^2-2\vec a\cdot\vec b+\vec b^2=1-0+2=3\) ✓。两法一致，**AD**。

### 练-滚-9（填空）｜答案：\(3\)

- **解法要点**：与增-评4题面相同：\(\vec a\cdot\vec b=|\vec a||\vec b|\cos60^\circ=2\times3\times\frac12=3\)。
- **验证方式与结论**：第二法＝坐标实现（\(\vec a=(2,0),\vec b=(1.5,\tfrac{3\sqrt3}{2})\) 点乘得 3）与代验 \(|\vec a+\vec b|^2=19\) 落在 \([1,25]\) 合理区间。两法一致，**3**。

### 练-滚-10（填空）｜答案：\(\sqrt{13}\)

- **解法要点**：与增-评5题面相同：\(\vec a\cdot\vec b=12\cos120^\circ=-6\)，\(|\vec a+\vec b|^2=16+9-12=13\)，\(|\vec a+\vec b|=\sqrt{13}\)。
- **验证方式与结论**：第二法＝余弦定理路线（第三边对角 \(60^\circ\)：\(16+9-24\cos60^\circ=13\)）。两法一致，**\(\sqrt{13}\)**。

### 练-滚-11（填空）｜答案：\(\lambda\in(-1-\sqrt3,\,-1+\sqrt3)\)

- **解法要点**：先备料 \(\vec a\cdot\vec b=2\times1\times\cos60^\circ=1\)。设 \(\vec u=\vec a+\lambda\vec b,\ \vec v=\lambda\vec a-2\vec b\)。
  - 夹角为钝角 \(\iff\begin{cases}\vec u\cdot\vec v<0\\ \vec u,\vec v\neq\vec 0\\ \vec u,\vec v\text{不同向反向（夹角}\neq180^\circ\text{）}\end{cases}\)
  - 主不等式：\(\vec u\cdot\vec v=\lambda|\vec a|^2-2\vec a\cdot\vec b+\lambda^2\vec a\cdot\vec b-2\lambda|\vec b|^2=4\lambda-2+\lambda^2-2\lambda=\lambda^2+2\lambda-2<0\)，解得 \(-1-\sqrt3<\lambda<-1+\sqrt3\)。
  - 排除零向量：\(\vec u=\vec 0\Rightarrow\vec a=-\lambda\vec b\parallel\vec b\)、\(\vec v=\vec 0\Rightarrow\lambda\vec a=2\vec b\parallel\vec b\)，均与夹角 \(60^\circ\)（不共线）矛盾，故任意 \(\lambda\) 下 \(\vec u,\vec v\) 恒非零（\(\lambda=0\) 时 \(\vec v=-2\vec b\neq\vec 0\) 亦核）。
  - 排除反向共线：设 \(\vec v=t\vec u\)，按不共线的 \(\vec a,\vec b\) 比较系数：\(\lambda=t\) 且 \(-2=t\lambda\)，得 \(\lambda^2=-2\) 无实解——\(\vec u,\vec v\) 对任何 \(\lambda\) 都不共线，\(180^\circ\) 情形自动排除，无需挖点。
  - 综上：\(\lambda\in(-1-\sqrt3,-1+\sqrt3)\)。
- **验证方式与结论**：第二法＝坐标硬算：取 \(\vec b=(1,0),\ \vec a=(2\cos60^\circ,2\sin60^\circ)=(1,\sqrt3)\)（模 \(2,1\)、夹角 \(60^\circ\) 全部达标），\(\vec u=(1+\lambda,\sqrt3),\ \vec v=(\lambda-2,\sqrt3\lambda)\)，\(\vec u\cdot\vec v=(1+\lambda)(\lambda-2)+3\lambda=\lambda^2+2\lambda-2\) 与法一逐字吻合。三点抽检：\(\lambda=0\)（区间内）：\(\vec u=\vec a,\vec v=-2\vec b\)，夹角 \(120^\circ\) 钝角 ✓；\(\lambda=1\)（区间外）：\(\vec u\cdot\vec v=1>0\) 非钝 ✓；\(\lambda=-1+\sqrt3\)（端点）：\(\vec u\cdot\vec v=0\) 直角，开区间正确剔除 ✓。两法一致，**\((-1-\sqrt3,-1+\sqrt3)\)**。

---

## 附：重复题说明

本片中 5 对题为源上重复（增-探-例1≡练-滚-1、增-评1≡练-滚-5、增-评3≡练-滚-4、增-评4≡练-滚-9、增-评5≡练-滚-10），两处各自独立盲判，答案一致（B/B、D/D、B/B、3/3、√13/√13），未互相抄录。

## 附：盲性自证

1. **读过内容的文件仅 2 类**：①题面片 `工作区/逻辑闸-样张族0911/slices/slice-04.md`（唯一题面来源，完整 120 行）；②我自己新建的答案卷 `sol-qwen/slice-04.md`（回读以修一处数学式排版笔误）。
2. **未读**：`keys/`、`sol-glm/`、`_源快照/`、`自检/`、`manifest.md`、其余 slice-01/02/03/05 题面与任何答案册/答案键文件——一律未打开。曾对样张族根目录与 `slices/`、`sol-qwen/` 执行过 `ls`（仅列文件名，用于确认 slice-04 完整性与输出目录，无内容泄露）。
3. **一次 Python 取证**仅打印我自己输出文件中 `slice-04.md` 内部字符串（排查 Edit 匹配失败），未触碰他档。
4. **未联网**：全程未调用 WebSearch/FetchURL，未搜题解。
5. 所有解答均由本臂独立推导，忠实自答，未迁就任何键面。
