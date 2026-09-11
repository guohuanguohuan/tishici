# slice-02 盲解卷（glm 臂）

- 题源片：`slices/slice-02.md`（导学件·课中探究，探究点一～九，共 18 题）
- 盲解纪律：仅读切片文件，未触任何答案键；以下全部为本臂独立盲解，不迁就任何答案键形式。
- 约定说明：探究点八、九题面附图不在片内，按四边形顶点顺序约定作图——四边形 \(ABFE\)、\(CDEF\) 顶点按字母序相邻（\(A\) 邻 \(E\)、\(B\) 邻 \(F\)；\(D\) 邻 \(E\)、\(C\) 邻 \(F\)），两正方形以 \(EF\) 为公共棱；矩形 \(ABCD\) 顶点按字母序，\(B\)、\(D\) 位于对角线 \(AC\) 两侧。

## 导-T1-例1
- 题号：导-T1-例1｜答案：B
- 解法要点（逐选项判定）：
  - A 错：模相等仅长度相同，方向可任意，未必 \(\overrightarrow{a}=\pm\overrightarrow{b}\)；
  - B 对：相反向量即等长反向，其和为 \(\overrightarrow{0}\)，此为定义直接推论；
  - C 错：教材规定零向量的方向是任意的，"没有方向"说法不成立；
  - D 错：单位向量仅模为 1，方向可不同，未必相等。
- 验证方式与结论：逐选项概念判定（概念题），正确项为 B。

## 导-T1-变1
- 题号：导-T1-变1｜答案：D
- 解法要点（逐选项判定，找错误项）：
  - A 正确：规定零向量与任意向量平行（共线）；
  - B 正确：模为 0 当且仅当是零向量；
  - C 正确：相等向量必等模；
  - D 错误：平行向量仅要求方向相同或相反，模可不等，反例 \(\overrightarrow{b}=2\overrightarrow{a}\)。
- 验证方式与结论：逐选项判定，错误项为 D。

## 导-T2-例1
- 题号：导-T2-例1｜答案：\(\overrightarrow{A_{1}B}=-\overrightarrow{a}+\overrightarrow{b}-\overrightarrow{c}\)
- 解法要点：\(\overrightarrow{A_{1}B}=\overrightarrow{CB}-\overrightarrow{CA_{1}}\)，而 \(\overrightarrow{CA_{1}}=\overrightarrow{CC_{1}}+\overrightarrow{C_{1}A_{1}}=\overrightarrow{c}+\overrightarrow{a}\)（棱柱中 \(\overrightarrow{C_{1}A_{1}}=\overrightarrow{CA}=\overrightarrow{a}\)），故 \(\overrightarrow{A_{1}B}=\overrightarrow{b}-(\overrightarrow{a}+\overrightarrow{c})=-\overrightarrow{a}+\overrightarrow{b}-\overrightarrow{c}\)。
- 验证方式与结论：二法。换路径 \(\overrightarrow{A_{1}B}=\overrightarrow{A_{1}A}+\overrightarrow{AB}=(-\overrightarrow{c})+(\overrightarrow{b}-\overrightarrow{a})=-\overrightarrow{a}+\overrightarrow{b}-\overrightarrow{c}\)，两法一致。

## 导-T2-变1
- 题号：导-T2-变1｜答案：\(\overrightarrow{D_{1}B}=\overrightarrow{a}-\overrightarrow{b}-\overrightarrow{c}\)
- 解法要点：\(\overrightarrow{D_{1}B}=\overrightarrow{DB}-\overrightarrow{DD_{1}}=(\overrightarrow{AB}-\overrightarrow{AD})-\overrightarrow{AA_{1}}=\overrightarrow{a}-\overrightarrow{b}-\overrightarrow{c}\)。
- 验证方式与结论：二法。换路径 \(\overrightarrow{D_{1}B}=\overrightarrow{D_{1}A_{1}}+\overrightarrow{A_{1}A}+\overrightarrow{AB}=(-\overrightarrow{b})+(-\overrightarrow{c})+\overrightarrow{a}\)，一致。

## 导-T3-例1
- 题号：导-T3-例1｜答案：\(x=1\)，\(y=\dfrac{1}{4}\)
- 解法要点：\(\overrightarrow{AE}=\overrightarrow{AA_{1}}+\overrightarrow{A_{1}E}=\overrightarrow{AA_{1}}+\frac{1}{4}\overrightarrow{A_{1}C_{1}}\)；正方体中 \(\overrightarrow{A_{1}C_{1}}=\overrightarrow{AC}=\overrightarrow{AB}+\overrightarrow{AD}\)，故 \(\overrightarrow{AE}=1\cdot\overrightarrow{AA_{1}}+\frac14(\overrightarrow{AB}+\overrightarrow{AD})\)，得 \(x=1,\ y=\frac14\)。
- 验证方式与结论：代验。设棱长 1 建系 \(A(0,0,0),B(1,0,0),D(0,1,0),A_{1}(0,0,1)\)，则 \(E=A_{1}+\frac14(1,1,0)=(\frac14,\frac14,1)\)，与 \(\overrightarrow{AA_{1}}+\frac14(\overrightarrow{AB}+\overrightarrow{AD})=(\frac14,\frac14,1)\) 相符。

## 导-T3-变1
- 题号：导-T3-变1｜答案：\(x=1\)，\(y=\dfrac{1}{2}\)
- 解法要点：同上，\(E\) 为 \(A_{1}C_{1}\) 中点，\(\overrightarrow{AE}=\overrightarrow{AA_{1}}+\frac12\overrightarrow{A_{1}C_{1}}=\overrightarrow{AA_{1}}+\frac12(\overrightarrow{AB}+\overrightarrow{AD})\)，得 \(x=1,\ y=\frac12\)。
- 验证方式与结论：代验。坐标核对：\(E=(\frac12,\frac12,1)\)，而 \(\overrightarrow{AA_{1}}+\frac12(\overrightarrow{AB}+\overrightarrow{AD})=(\frac12,\frac12,1)\)，成立。

## 导-T4-例1
- 题号：导-T4-例1｜答案：C（①③）
- 解法要点（逐项判定）：
  - ① 对：\(\overrightarrow{p}=x\overrightarrow{a}+y\overrightarrow{b}\) 时 \(\overrightarrow{p}\) 落在由 \(\overrightarrow{a},\overrightarrow{b}\) 张成的平面方向内（若 \(\overrightarrow{a}\parallel\overrightarrow{b}\)，则三者共线向更共面），故共面；
  - ② 错：缺少"\(\overrightarrow{a},\overrightarrow{b}\) 不共线"条件。反例：取 \(\overrightarrow{b}=2\overrightarrow{a}\)、\(\overrightarrow{p}\) 与 \(\overrightarrow{a}\) 不平行，则三者平行于同一平面（共面），但 \(x\overrightarrow{a}+y\overrightarrow{b}=(x+2y)\overrightarrow{a}\) 恒平行于 \(\overrightarrow{a}\)，表不出 \(\overrightarrow{p}\)；
  - ③ 对：\(\overrightarrow{MP}=x\overrightarrow{MA}+y\overrightarrow{MB}\) 时三向量共面且共起点 \(M\)，故 \(P\) 落在过 \(M\) 由 \(\overrightarrow{MA},\overrightarrow{MB}\) 确定的平面内，四点共面；
  - ④ 错：缺少"\(\overrightarrow{MA},\overrightarrow{MB}\) 不共线"。反例：\(M,A,B\) 为直线上三点而 \(P\) 在直线外，四点共面，但 \(\overrightarrow{MA},\overrightarrow{MB}\) 共线，其线性组合只能平行于该直线，给不出 \(\overrightarrow{MP}\)。
- 验证方式与结论：二法（正面论证＋反例排除），正确组为 ①③，选 C。

## 导-T4-变1
- 题号：导-T4-变1｜答案：共面
- 解法要点：\(\overrightarrow{MP}=3\overrightarrow{MA}-2\overrightarrow{MB}\) 是 \(\overrightarrow{MA},\overrightarrow{MB}\) 的线性组合，由共面向量定理，\(\overrightarrow{MP},\overrightarrow{MA},\overrightarrow{MB}\) 共面；三向量又有公共起点 \(M\)，故 \(P,M,A,B\) 四点共面。
- 验证方式与结论：代验。\(\overrightarrow{AP}=\overrightarrow{MP}-\overrightarrow{MA}=2(\overrightarrow{MA}-\overrightarrow{MB})=2\overrightarrow{BA}\)，即 \(P\) 在直线 \(AB\) 上（\(B\) 恰为 \(AP\) 中点），当然与 \(M,A,B\) 共面，结论甚至更强，代验成立。

## 导-T5-例1
- 题号：导-T5-例1｜答案：AD
- 解法要点（逐选项判定，多选）：
  - A 对：\(\overrightarrow{a}^{2}=\overrightarrow{a}\cdot\overrightarrow{a}=|\overrightarrow{a}|^{2}\)，此为数量积定义；
  - B 错：向量无除法运算，"\(\frac{\overrightarrow{b}}{\overrightarrow{a}}\)"无意义（左边 \(\frac{\overrightarrow{a}\cdot\overrightarrow{b}}{\overrightarrow{a}\cdot\overrightarrow{a}}\) 是数量）；
  - C 错：\((\overrightarrow{a}\cdot\overrightarrow{b})^{2}=|\overrightarrow{a}|^{2}|\overrightarrow{b}|^{2}\cos^{2}\theta\le\overrightarrow{a}^{2}\,\overrightarrow{b}^{2}\)，仅当 \(\overrightarrow{a},\overrightarrow{b}\) 共线时取等，一般不成立；
  - D 对：数量积满足分配律，完全平方展开 \((\overrightarrow{a}-\overrightarrow{b})^{2}=\overrightarrow{a}^{2}-2\overrightarrow{a}\cdot\overrightarrow{b}+\overrightarrow{b}^{2}\) 成立。
- 验证方式与结论：逐选项判定，正确的为 AD。

## 导-T5-变1
- 题号：导-T5-变1｜答案：\(-11\)
- 解法要点：\(\overrightarrow{a}\cdot\overrightarrow{b}=2\times3\times\cos60^\circ=3\)，\(\overrightarrow{a}^{2}=4\)，\(\overrightarrow{b}^{2}=9\)。\((\overrightarrow{a}+2\overrightarrow{b})\cdot(\overrightarrow{a}-\overrightarrow{b})=\overrightarrow{a}^{2}-\overrightarrow{a}\cdot\overrightarrow{b}+2\overrightarrow{a}\cdot\overrightarrow{b}-2\overrightarrow{b}^{2}=4+3-18=-11\)。
- 验证方式与结论：代验。取 \(\overrightarrow{a}=(2,0,0)\)，\(\overrightarrow{b}=(\frac32,\frac{3\sqrt3}{2},0)\)（模 3、夹角 \(60^\circ\)），则 \(\overrightarrow{a}+2\overrightarrow{b}=(5,3\sqrt3,0)\)，\(\overrightarrow{a}-\overrightarrow{b}=(\frac12,-\frac{3\sqrt3}{2},0)\)，数量积 \(=\frac52-\frac{27}{2}=-11\)，一致。

## 导-T6-例1
- 题号：导-T6-例1｜答案：\(60^\circ\)
- 解法要点：设棱长 1，建系 \(A(0,0,0),B(1,0,0),C(1,1,0),C_{1}(1,1,1)\)。则 \(\overrightarrow{BC_{1}}=(0,1,1)\)，\(\overrightarrow{AC}=(1,1,0)\)，\(\cos\langle\overrightarrow{BC_{1}},\overrightarrow{AC}\rangle=\frac{0+1+0}{\sqrt2\cdot\sqrt2}=\frac12\)，故夹角为 \(60^\circ\)。
- 验证方式与结论：二法（几何平移法）。平移 \(\overrightarrow{BC_{1}}=\overrightarrow{AD_{1}}\)，夹角即 \(\angle D_{1}AC\)；\(\triangle ACD_{1}\) 三边 \(AC,AD_{1},CD_{1}\) 均为面对角线 \(\sqrt2\)，等边三角形，故 \(\angle D_{1}AC=60^\circ\)，两法一致。

## 导-T6-变1
- 题号：导-T6-变1｜答案：\(\dfrac{\sqrt{10}}{5}\)
- 解法要点：建系 \(A(0,0,0),B(2,0,0),C(2,2,0),B_{1}(2,0,1)\)。\(\overrightarrow{AB_{1}}=(2,0,1)\)，\(|\overrightarrow{AB_{1}}|=\sqrt5\)；\(\overrightarrow{AC}=(2,2,0)\)，\(|\overrightarrow{AC}|=2\sqrt2\)；数量积 \(=4+0+0=4\)。\(\cos\theta=\frac{4}{\sqrt5\cdot2\sqrt2}=\frac{4}{2\sqrt{10}}=\frac{\sqrt{10}}{5}\)。
- 验证方式与结论：二法（基底法）。\(\overrightarrow{AB_{1}}\cdot\overrightarrow{AC}=(\overrightarrow{AB}+\overrightarrow{AA_{1}})\cdot(\overrightarrow{AB}+\overrightarrow{AD})=|\overrightarrow{AB}|^{2}+0+0+0=4\)，\(\cos\theta=\frac{4}{\sqrt{40}}=\frac{\sqrt{10}}{5}\)，一致。

## 导-T7-例1
- 题号：导-T7-例1｜答案：\(\lambda\in\left(-1-\sqrt{3},\,-1+\sqrt{3}\right)\)
- 解法要点：\(\overrightarrow{a}\cdot\overrightarrow{b}=2\times1\times\cos60^\circ=1\)，\(\overrightarrow{a}^{2}=4\)，\(\overrightarrow{b}^{2}=1\)。夹角为钝角 \(\iff\) 数量积 \(<0\) 且两向量不反向共线：
  \((\overrightarrow{a}+\lambda\overrightarrow{b})\cdot(\lambda\overrightarrow{a}-2\overrightarrow{b})=4\lambda-2+\lambda^{2}-2\lambda=\lambda^{2}+2\lambda-2<0\iff -1-\sqrt3<\lambda<-1+\sqrt3\)。
  共线剔除检验：若 \(\overrightarrow{a}+\lambda\overrightarrow{b}=t(\lambda\overrightarrow{a}-2\overrightarrow{b})\)（\(t<0\)），比较 \(\overrightarrow{a},\overrightarrow{b}\) 系数得 \(1=t\lambda\)，\(\lambda=-2t\)，消去得 \(\lambda^{2}=-2\)，无实解，故不存在反向共线情形，区间内无需剔除任何值。
- 验证方式与结论：代验。区间内取 \(\lambda=0\)：\(\overrightarrow{a}\) 与 \(-2\overrightarrow{b}\) 的夹角为 \(180^\circ-60^\circ=120^\circ\)，确为钝角；区间外取 \(\lambda=2\)：数量积 \(=4+4-2=6>0\)，夹角非钝角。代验通过。

## 导-T7-变1
- 题号：导-T7-变1｜答案：\(\lambda=-\dfrac{3}{2}\)
- 解法要点：\(\overrightarrow{m}\perp\overrightarrow{n}\iff\overrightarrow{m}\cdot\overrightarrow{n}=0\)。其中 \(|\overrightarrow{a}|^{2}=18\)，\(\overrightarrow{a}\cdot\overrightarrow{b}=3\sqrt2\times4\times\cos135^\circ=12\sqrt2\times\left(-\frac{\sqrt2}{2}\right)=-12\)，\(|\overrightarrow{b}|^{2}=16\)。
  \(\overrightarrow{m}\cdot\overrightarrow{n}=(\overrightarrow{a}+\overrightarrow{b})\cdot(\overrightarrow{a}+\lambda\overrightarrow{b})=18+(\lambda+1)(-12)+16\lambda=6+4\lambda=0\iff\lambda=-\frac32\)。
- 验证方式与结论：代验。回代 \(\overrightarrow{m}\cdot\overrightarrow{n}=18+\left(-\frac12\right)\times(-12)+\left(-\frac32\right)\times16=18+6-24=0\)，成立。（一元一次方程求解，无实质第二解法，登记：仅代验。）

## 导-T8-例1
- 题号：导-T8-例1｜答案：D（\(\sqrt{3-\sqrt{2}}\)）
- 解法要点（数量积展开法）：以 \(E\) 为参考点。正方形 \(ABFE\) 中 \(\overrightarrow{EB}=\overrightarrow{EF}+\overrightarrow{FB}\)；正方形 \(CDEF\) 中 \(D\) 过 \(E\) 且 \(ED\perp EF\)。
  \(\overrightarrow{BD}=\overrightarrow{BE}+\overrightarrow{ED}=-\overrightarrow{EF}-\overrightarrow{FB}+\overrightarrow{ED}\)。
  交叉项：\(\overrightarrow{EF}\perp\overrightarrow{FB}\)（正方形），\(\overrightarrow{EF}\perp\overrightarrow{ED}\)；\(\overrightarrow{FB}\) 与 \(\overrightarrow{ED}\) 分别位于二面角两个半平面内且均垂直于棱 \(EF\)，其夹角即二面角 \(45^\circ\)。
  \(|\overrightarrow{BD}|^{2}=1^{2}+1^{2}+1^{2}-2|\overrightarrow{FB}||\overrightarrow{ED}|\cos45^\circ=3-2\times\frac{\sqrt2}{2}=3-\sqrt2\)，故 \(BD=\sqrt{3-\sqrt2}\)。
- 验证方式与结论：二法（坐标法）。取 \(E(0,0,0),F(1,0,0)\)，半平面 \([EF,A]\) 内 \(A(0,1,0),B(1,1,0)\)，半平面 \([EF,D]\) 与其成 \(45^\circ\)：\(D=E+(0,\cos45^\circ,\sin45^\circ)=(0,\frac{\sqrt2}{2},\frac{\sqrt2}{2})\)。\(\overrightarrow{BD}=(-1,\frac{\sqrt2}{2}-1,\frac{\sqrt2}{2})\)，\(|\overrightarrow{BD}|^{2}=1+\left(\frac32-\sqrt2\right)+\frac12=3-\sqrt2\)，一致，选 D。

## 导-T8-变1
- 题号：导-T8-变1｜答案：\(\sqrt{2}\)
- 解法要点：同例1展开法，\(\overrightarrow{FB}\) 与 \(\overrightarrow{ED}\) 夹角为 \(60^\circ\)：
  \(|\overrightarrow{BD}|^{2}=3-2\cos60^\circ=3-1=2\)，故 \(BD=\sqrt2\)。
- 验证方式与结论：二法（坐标法）。\(B(1,1,0)\)，\(D=E+(0,\cos60^\circ,\sin60^\circ)=(0,\frac12,\frac{\sqrt3}{2})\)，\(\overrightarrow{BD}=(-1,-\frac12,\frac{\sqrt3}{2})\)，\(|\overrightarrow{BD}|^{2}=1+\frac14+\frac34=2\)，一致。

## 导-T9-例1
- 题号：导-T9-例1｜答案：A（\(\dfrac{\sqrt{10}}{2}\)）
- 解法要点（垂足拆分＋数量积法）：折叠不变量：\(AC=\sqrt{1+3}=2\)；\(\triangle ABC\) 中 \(\angle ABC=90^\circ\)。设 \(BE\perp AC\) 于 \(E\)，\(DF\perp AC\) 于 \(F\)，由射影定理：
  \(BE=\frac{AB\cdot BC}{AC}=\frac{\sqrt3}{2}\)，\(AE=\frac{AB^{2}}{AC}=\frac12\)；\(DF=\frac{\sqrt3}{2}\)，\(AF=\frac{AD^{2}}{AC}=\frac32\)；故 \(EF=AF-AE=1\)。
  折后平面 \(ABC\perp\) 平面 \(ACD\)，又 \(BE\perp AC\)，故 \(BE\perp\) 平面 \(ACD\)，从而 \(BE\perp EF\)、\(BE\perp FD\)，且 \(FD\perp EF\)。分解 \(\overrightarrow{BD}=\overrightarrow{BE}+\overrightarrow{EF}+\overrightarrow{FD}\)（各段两两垂直）：
  \(|\overrightarrow{BD}|^{2}=BE^{2}+EF^{2}+FD^{2}=\frac34+1+\frac34=\frac52\)，故 \(BD=\frac{\sqrt{10}}{2}\)。
- 验证方式与结论：二法（坐标法）。取 \(AC\) 为 \(x\) 轴：\(A(0,0,0),C(2,0,0)\)，平面 \(ACD\) 为 \(xy\) 面，\(D=(\frac32,\frac{\sqrt3}{2},0)\)；\(B\) 在过 \(E(\frac12,0,0)\) 垂直于 \(xy\) 面的直线上，\(BE=\frac{\sqrt3}{2}\)，取 \(B=(\frac12,0,\frac{\sqrt3}{2})\)。则 \(\overrightarrow{BD}=(1,-\frac{\sqrt3}{2},\frac{\sqrt3}{2})\)，\(|\overrightarrow{BD}|^{2}=1+\frac34+\frac34=\frac52\)，一致，选 A。

## 导-T9-变1
- 题号：导-T9-变1｜答案：\(\dfrac{\sqrt{7}}{2}\)
- 解法要点（数量积法）：沿用例1的垂足 \(E,F\)：\(BE=DF=\frac{\sqrt3}{2}\)，\(EF=1\)。分解 \(\overrightarrow{BD}=\overrightarrow{BE}+\overrightarrow{EF}+\overrightarrow{FD}\)，其中 \(\overrightarrow{BE}\perp\overrightarrow{EF}\)，\(\overrightarrow{FD}\perp\overrightarrow{EF}\)；二面角 \(B\text{-}AC\text{-}D=60^\circ\) 即从棱出发指向 \(B\)、\(D\) 的两条垂线（\(\overrightarrow{EB}\) 与 \(\overrightarrow{FD}\)）夹角为 \(60^\circ\)，故 \(\overrightarrow{BE}\)（指向棱）与 \(\overrightarrow{FD}\)（背离棱）的夹角为 \(120^\circ\)：
  \(|\overrightarrow{BD}|^{2}=\frac34+1+\frac34+2\times\frac{\sqrt3}{2}\times\frac{\sqrt3}{2}\times\cos120^\circ=\frac52-\frac34=\frac74\)，故 \(BD=\frac{\sqrt7}{2}\)。
- 验证方式与结论：二法（坐标法）。\(A(0,0,0),C(2,0,0)\)，平面 \(ACD\) 为 \(xy\) 面，\(D=(\frac32,\frac{\sqrt3}{2},0)\)；半平面 \([AC,B]\) 与半平面 \([AC,D]\)（方向 \((0,1,0)\)）成 \(60^\circ\)：\(\overrightarrow{EB}\) 方向 \((0,\cos60^\circ,\sin60^\circ)\)，即 \(B=E+\frac{\sqrt3}{2}(0,\frac12,\frac{\sqrt3}{2})=(\frac12,\frac{\sqrt3}{4},\frac34)\)。则 \(\overrightarrow{BD}=(1,\frac{\sqrt3}{4},-\frac34)\)，\(|\overrightarrow{BD}|^{2}=1+\frac{3}{16}+\frac{9}{16}=\frac74\)，一致。

---

## 答案速览

| 题号 | 答案 | 验证方式 |
| --- | --- | --- |
| 导-T1-例1 | B | 逐选项判定 |
| 导-T1-变1 | D | 逐选项判定 |
| 导-T2-例1 | \(-\overrightarrow{a}+\overrightarrow{b}-\overrightarrow{c}\) | 二法 |
| 导-T2-变1 | \(\overrightarrow{a}-\overrightarrow{b}-\overrightarrow{c}\) | 二法 |
| 导-T3-例1 | \(x=1,\ y=\frac14\) | 代验 |
| 导-T3-变1 | \(x=1,\ y=\frac12\) | 代验 |
| 导-T4-例1 | C（①③） | 正面论证＋反例排除 |
| 导-T4-变1 | 共面（且 \(P\) 在直线 \(AB\) 上，\(B\) 为 \(AP\) 中点） | 代验 |
| 导-T5-例1 | AD | 逐选项判定 |
| 导-T5-变1 | \(-11\) | 代验 |
| 导-T6-例1 | \(60^\circ\) | 二法 |
| 导-T6-变1 | \(\frac{\sqrt{10}}{5}\) | 二法 |
| 导-T7-例1 | \(\left(-1-\sqrt3,\,-1+\sqrt3\right)\) | 代验（含共线剔除检验） |
| 导-T7-变1 | \(-\frac32\) | 仅代验 |
| 导-T8-例1 | D（\(\sqrt{3-\sqrt2}\)） | 二法 |
| 导-T8-变1 | \(\sqrt2\) | 二法 |
| 导-T9-例1 | A（\(\frac{\sqrt{10}}{2}\)） | 二法 |
| 导-T9-变1 | \(\frac{\sqrt7}{2}\) | 二法 |

## 盲性自证
仅读切片文件，未触任何答案键。
