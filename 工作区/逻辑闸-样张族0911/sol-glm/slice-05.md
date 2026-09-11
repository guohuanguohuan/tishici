# sol-glm｜slice-05 盲解（glm 臂·零上下文）

- 解题日期：2026-09-11
- 输入：仅读 `工作区/逻辑闸-样张族0911/slices/slice-05.md`（题面片，去答案版）
- 判据：《内容质量闸》卷三全量档——判断√/×＋一句理由；填空给值；选择逐选项判定后给字母；计算/解答完整求解＋二法互验或代验
- 实解题数：16（练-课 10 ＋ 测 6）；练-课-7~9、13~14、16 及测评卷未排题位在源中无题面，不在本片题号内

## 一、练习线·课时训练（第1课时 空间向量的概念及线性运算）

### 练-课-1（单选）
- 答案：C
- 解法要点：设夹角 θ，\(\vec a·\vec b=|\vec a||\vec b|\cosθ\)；因 \(|\vec a|,|\vec b|>0\)，故 \(\vec a·\vec b=0\iff\cosθ=0\iff θ=90°\iff\vec a⊥\vec b\)，互为充要。
- 逐选项判定：A ✗（"不必要"错：垂直必得点积为零，必要性成立）；B ✗（"不充分"错：点积为零必垂直，充分性成立）；C ✓（两向均成立）；D ✗。
- 验证方式与结论：二法——按定义正、逆两个方向各自独立推导，均成立，结论 C。

### 练-课-2（填空）
- 答案：\(\overrightarrow{D_1B}=\vec a-\vec b-\vec c\)
- 解法要点：\(\overrightarrow{D_1B}=\overrightarrow{D_1A_1}+\overrightarrow{A_1A}+\overrightarrow{AB}=-\vec b-\vec c+\vec a\)。
- 验证方式与结论：二法——顶点坐标法：以 A 为基点，B=A+\vec a、D₁=A+\vec b+\vec c，则 \(\overrightarrow{D_1B}=\vec a-(\vec b+\vec c)\)，与拆路一一致。

### 练-课-3（填空）
- 答案：\(x=1\)，\(y=\dfrac12\)
- 解法要点：\(\overrightarrow{A_1C_1}=\overrightarrow{A_1B_1}+\overrightarrow{B_1C_1}=\vec a+\vec b\)；\(\overrightarrow{AE}=\overrightarrow{AA_1}+\overrightarrow{A_1E}=\vec c+\dfrac12(\vec a+\vec b)=1·\overrightarrow{AA_1}+\dfrac12(\overrightarrow{AB}+\overrightarrow{AD})\)。
- 验证方式与结论：代验——代回 \(x=1,\ y=\frac12\)：\(\vec c+\frac12(\vec a+\vec b)=\overrightarrow{AA_1}+\overrightarrow{A_1E}=\overrightarrow{AE}\) ✓。

### 练-课-4（填空）
- 答案：\(-11\)
- 解法要点：原式 \(=\vec a^{\,2}+\vec a·\vec b-2\vec b^{\,2}=4+2×3×\cos60°-2×9=4+3-18=-11\)。
- 验证方式与结论：代验——取 \(\vec a=(2,0,0)\)，\(\vec b=(\frac32,\frac{3\sqrt3}2,0)\)：\(\vec a+2\vec b=(5,3\sqrt3,0)\)，\(\vec a-\vec b=(\frac12,-\frac{3\sqrt3}2,0)\)，点积 \(=\frac52-\frac{27}2=-11\) ✓。

### 练-课-5（填空）
- 答案：\(\dfrac{\sqrt{10}}5\)
- 解法要点：记 \(\overrightarrow{AB}=\vec a,\overrightarrow{AD}=\vec b,\overrightarrow{AA_1}=\vec c\)（两两垂直，|a|=|b|=2、|c|=1）；\(\overrightarrow{AB_1}=\vec a+\vec c\)，\(\overrightarrow{AC}=\vec a+\vec b\)；点积 \(=\vec a^{\,2}=4\)；\(|\overrightarrow{AB_1}|=\sqrt5\)，\(|\overrightarrow{AC}|=2\sqrt2\)；\(\cos\langle\overrightarrow{AB_1},\overrightarrow{AC}\rangle=\dfrac4{\sqrt5·2\sqrt2}=\dfrac{\sqrt{10}}5\)。
- 验证方式与结论：代验——坐标 \(A(0,0,0),B(2,0,0),C(2,2,0),B_1(2,0,1)\)：\(\overrightarrow{AB_1}·\overrightarrow{AC}=4\)，模同上，\(\cos=\dfrac4{\sqrt{40}}=\dfrac{\sqrt{10}}5\) ✓。

### 练-课-6（填空）
- 答案：\(\overrightarrow{A_1B}=\vec b-\vec a-\vec c\)
- 解法要点：\(\overrightarrow{A_1B}=\overrightarrow{A_1A}+\overrightarrow{AB}=-\vec c+(\vec b-\vec a)=\vec b-\vec a-\vec c\)。
- 验证方式与结论：二法——另一拆路 \(\overrightarrow{A_1B}=\overrightarrow{A_1C_1}+\overrightarrow{C_1B}=-\vec a+(\vec b-\vec c)\)，两路一致。

### 练-课-10（解答，13分）
- 答案：P、M、A、B 四点共面。
- 求解：\(\overrightarrow{MP}=3\overrightarrow{MA}-2\overrightarrow{MB}\)，即 \(\overrightarrow{MP}\) 可由 \(\overrightarrow{MA}\)、\(\overrightarrow{MB}\) 线性表示，由共面向量定理，\(\overrightarrow{MP}\) 与 \(\overrightarrow{MA}\)、\(\overrightarrow{MB}\) 共面，故 P 落在 M、A、B 所确定的平面内；若 M、A、B 共线，则四点同在过该直线的任一平面内，亦共面。综上，四点共面。
- 验证方式与结论：二法——特例坐标：M(0,0,0)、A(1,0,0)、B(0,1,0)，则 \(\overrightarrow{MP}=(3,-2,0)\)，P=(3,−2,0) 与 M、A、B 同在平面 z=0 内 ✓，共面成立。

### 练-课-11（填空）
- 答案：\(1\)
- 解法要点：两正方形公共边 EF 为棱；正方形中 \(\overrightarrow{FB}\parallel\overrightarrow{EA}\)、\(\overrightarrow{FD}\parallel\overrightarrow{EC}\)，且 EA⊥EF、EC⊥EF，故平面角 \(\angle AEC=60°\)，从而 \(\cos\angle BFD=\cos\langle\overrightarrow{FB},\overrightarrow{FD}\rangle=\frac12\)；\(|\overrightarrow{FB}|=|\overrightarrow{FD}|=1\)，在三角形 BFD 中 \(BD^2=BF^2+FD^2-2·BF·FD·\cos\angle BFD=1+1-1=1\)。
- 验证方式与结论：二法——坐标法：E(0,0,0)、F(1,0,0)、B(1,0,1)、D(1,\frac{\sqrt3}2,\frac12)，\(\overrightarrow{BD}=(0,\frac{\sqrt3}2,-\frac12)\)，模 \(=\sqrt{\frac34+\frac14}=1\) ✓。

### 练-课-12（多选）
- 答案：AD
- 逐选项判定：
  - A ✓：\(\vec a^{\,2}=\vec a·\vec a=|\vec a|^2\)（数量积定义）。
  - B ✗：向量运算无除法，\(\dfrac{\vec b}{\vec a}\) 无定义，等式无意义。
  - C ✗：左 \(=|\vec a|^2|\vec b|^2\cos^2θ\)，右 \(=|\vec a|^2|\vec b|^2\)，仅当 a∥b 时成立；反例：a⊥b 且均为单位向量时左 0 右 1。
  - D ✓：\((\vec a-\vec b)^2=\vec a^{\,2}-2\vec a·\vec b+\vec b^{\,2}\)（展开＋交换律）。
- 验证方式与结论：二法——A、D 按定义展开证明，B、C 举反例，判定成立。

### 练-课-15（填空）
- 答案：\(\dfrac{\sqrt7}2\)
- 解法要点：\(AC=\sqrt{1+3}=2\)。B 到 AC 垂足 M：\(BM=\frac{AB·BC}{AC}=\frac{\sqrt3}2\)，\(AM=\frac{AB^2}{AC}=\frac12\)；D 到 AC 垂足 N：\(DN=\frac{AD·CD}{AC}=\frac{\sqrt3}2\)，\(CN=\frac{CD^2}{AC}=\frac12\)，故 \(MN=1\)。折后 \(\overrightarrow{BD}=\overrightarrow{BM}+\overrightarrow{MN}+\overrightarrow{ND}\)，其中 \(\overrightarrow{BM}⊥\overrightarrow{MN}\)、\(\overrightarrow{ND}⊥\overrightarrow{MN}\)，\(\langle\overrightarrow{MB},\overrightarrow{ND}\rangle=60°\Rightarrow\langle\overrightarrow{BM},\overrightarrow{ND}\rangle=120°\)：\(BD^2=\frac34+1+\frac34+2·\frac34·(-\frac12)=\frac74\)，即 \(BD=\frac{\sqrt7}2\)。
- 验证方式与结论：二法——坐标法：A(0,0,0)、C(2,0,0)、M(\frac12,0,0)、B(\frac12,\frac{\sqrt3}2,0)、N(\frac32,0,0)、D(\frac32,\frac{\sqrt3}4,\frac34)（\(\overrightarrow{ND}\) 方向 \((0,\frac12,\frac{\sqrt3}2)\) 与 \((0,1,0)\) 成 60°、长 \(\frac{\sqrt3}2\)）：\(\overrightarrow{BD}=(1,-\frac{\sqrt3}4,\frac34)\)，模² \(=1+\frac3{16}+\frac9{16}=\frac74\) ✓。

## 二、测评卷·单元素养测评卷（一）

### 测-1（选择）
- 答案：B
- 逐选项判定：
  - A ✗：模相等只保证长度相同，方向可成任意角（反例：两等长向量夹 60°），推不出 \(\vec a=\pm\vec b\)。
  - B ✓：相反向量即 \(\vec a=-\vec b\)，由定义 \(\vec a+\vec b=\vec 0\)。
  - C ✗：教材规定零向量方向是任意的，"没有方向"与规定不符。
  - D ✗：单位向量仅要求模为 1，方向可不同（反例：x 轴与 y 轴正向单位向量）。
- 验证方式与结论：逐选项判定＋反例——B 按定义直接成立，A、C、D 反例排除，结论 B。

### 测-2（选择）
- 答案：D
- 逐选项判定：
  - A ✓（说法正确）：规定零向量与任意向量平行。
  - B ✓：\(|\vec a|=0\) 即模为零，必为零向量。
  - C ✓：相等向量必等长。
  - D ✗（说法错误，为所求）：平行只约束方向；反例 \(\vec a=(1,0,0)\)、\(\vec b=(2,0,0)\)，平行但模不等。
- 验证方式与结论：逐选项判定＋反例——D 举反例证伪，A、B、C 按定义逐一确认正确，结论 D。

### 测-3（选择）
- 答案：B（\(k=2\)）
- 解法要点：\(\vec e_1,\vec e_2\) 不共线可作基；\(\vec a\parallel\vec b\Rightarrow\vec b=\lambda\vec a\Rightarrow 4=2\lambda,\ k=\lambda\Rightarrow\lambda=2,\ k=2\)。
- 逐选项判定：A（\(\frac12\)）✗；B（2）✓；C（\(-\frac12\)）✗；D（3）✗。
- 验证方式与结论：代验——k=2 时 \(\vec b=4\vec e_1+2\vec e_2=2\vec a\)，确与 \(\vec a\) 平行 ✓，结论 B。

### 测-4（多选，6分）
- 答案：AD
- 逐选项判定：与练-课-12 同题——A ✓（\(\vec a^{\,2}=|\vec a|^2\) 定义）；B ✗（向量除法无定义）；C ✗（仅 a∥b 时成立，反例 a⊥b 单位向量：左 0 右 1）；D ✓（展开成立）。
- 验证方式与结论：二法——定义展开证明 A、D，反例证伪 B、C，结论 AD。

### 测-5（填空，5分）
- 答案：\(3\)
- 解法要点：\(\vec a·\vec b=|\vec a||\vec b|\cos60°=2×3×\frac12=3\)。
- 验证方式与结论：代验——\(\vec a=(2,0,0)\)、\(\vec b=(\frac32,\frac{3\sqrt3}2,0)\)，点积 \(=2×\frac32=3\) ✓。

### 测-6（解答，13分）
- 答案：\(|\vec a+\vec b|=\sqrt{13}\)
- 求解：\(\vec a·\vec b=4×3×\cos120°=-6\)；\(|\vec a+\vec b|^2=\vec a^{\,2}+2\vec a·\vec b+\vec b^{\,2}=16+2×(-6)+9=13\)，故 \(|\vec a+\vec b|=\sqrt{13}\)。
- 验证方式与结论：代验——\(\vec a=(4,0,0)\)、\(\vec b=(-\frac32,\frac{3\sqrt3}2,0)\)，\(\vec a+\vec b=(\frac52,\frac{3\sqrt3}2,0)\)，模² \(=\frac{25}4+\frac{27}4=13\) ✓，\(|\vec a+\vec b|=\sqrt{13}\)。

---

- 盲性自证：仅读切片文件，未触任何答案键。
