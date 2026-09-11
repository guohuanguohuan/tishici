# 逻辑闸试点0911（二期）· 盲解答-臂A-qwen

## 题1〔选择〕

**最终答案：B**

- A 错：模相等只约束长度，方向可任意，既不一定同向也不一定反向（如平面内任意两个等长向量）。
- B 对：相反向量定义即 \(\overrightarrow{b}=-\overrightarrow{a}\)，故 \(\overrightarrow{a}+\overrightarrow{b}=\overrightarrow{0}\)。
- C 错：零向量并非"没有方向"，教材规定其方向是任意的（仍属"有方向"这一属性的退化情形，说"没有方向"表述错误）。
- D 错：单位向量只保证模都为 1，方向可不相同，故不一定相等。

**方法一句话**：逐项按向量相等、相反向量、零向量、单位向量的定义判真伪。

**把握度**：确定。

## 题2〔选择〕

**最终答案：D**

- A 对：教材规定零向量与任一向量平行（方向任意）。
- B 对：模为 0 的向量就是零向量，\(\overrightarrow{a}=\overrightarrow{0}\)。
- C 对：相等向量模必相等。
- D 错：平行（共线）只约束方向关系，不约束长度，如 \(\overrightarrow{a}\parallel\overrightarrow{b}\) 时 \(|\overrightarrow{a}|\) 可为 \(|\overrightarrow{b}|\) 的任意正倍。

**方法一句话**：逐项检验平行、模、相等三个概念的蕴含方向，找错误项。

**把握度**：确定。

## 题3〔填空〕

**最终答案：\(\overrightarrow{A_{1}B}=-\overrightarrow{a}+\overrightarrow{b}-\overrightarrow{c}\)（即 \(\overrightarrow{b}-\overrightarrow{a}-\overrightarrow{c}\)）**

演算：\(\overrightarrow{CA_1}=\overrightarrow{CA}+\overrightarrow{AA_1}=\overrightarrow{CA}+\overrightarrow{CC_1}=\overrightarrow{a}+\overrightarrow{c}\)；
\(\overrightarrow{A_1B}=\overrightarrow{CB}-\overrightarrow{CA_1}=\overrightarrow{b}-(\overrightarrow{a}+\overrightarrow{c})=\overrightarrow{b}-\overrightarrow{a}-\overrightarrow{c}\)。

**方法一句话**：以 \(C\) 为公共起点，用"终点位矢减起点位矢"（三角形法则）拆链。

**把握度**：确定。

## 题4〔填空〕

**最终答案：\(\overrightarrow{D_1B}=\overrightarrow{a}-\overrightarrow{b}-\overrightarrow{c}\)**

演算：以 \(A\) 为起点，\(\overrightarrow{AB}=\overrightarrow{a}\)；\(\overrightarrow{AD_1}=\overrightarrow{AD}+\overrightarrow{DD_1}=\overrightarrow{AD}+\overrightarrow{AA_1}=\overrightarrow{b}+\overrightarrow{c}\)；
\(\overrightarrow{D_1B}=\overrightarrow{AB}-\overrightarrow{AD_1}=\overrightarrow{a}-\overrightarrow{b}-\overrightarrow{c}\)。

**方法一句话**：平行六面体中棱向量平移相等（\(\overrightarrow{DD_1}=\overrightarrow{AA_1}\)），再用终点减起点。

**把握度**：确定。

## 题5〔解答·判断说理〕

**最终答案：\(P\)、\(M\)、\(A\)、\(B\) 四点共面。**

理由：由已知 \(\overrightarrow{MP}=3\overrightarrow{MA}-2\overrightarrow{MB}\)，\(\overrightarrow{MP}\) 可表示为 \(\overrightarrow{MA}\)、\(\overrightarrow{MB}\) 的线性组合，由共面向量定理，\(\overrightarrow{MP}\)、\(\overrightarrow{MA}\)、\(\overrightarrow{MB}\) 三个向量共面；又它们有公共起点 \(M\)，所以 \(P\)、\(M\)、\(A\)、\(B\) 四点共面（若 \(M,A,B\) 共线则四点甚至共线，更共面）。

可再深一层：系数和 \(3+(-2)=1\)，两边减去 \(\overrightarrow{MB}\) 得 \(\overrightarrow{MP}-\overrightarrow{MB}=3(\overrightarrow{MA}-\overrightarrow{MB})\)，即 \(\overrightarrow{BP}=3\overrightarrow{BA}\)，故 \(P\) 其实在直线 \(AB\) 上——共面结论更强地成立。

**方法一句话**：用"向量可线性表出⇒共面，且公共起点⇒四点共面"的判定定理（辅以系数和为 1 验证 \(P\in\) 直线 \(AB\)）。

**把握度**：确定（共面结论唯一；"P 在直线 AB 上"是额外强化，也已自算验证）。

## 题6〔解答〕

**最终答案：夹角为 \(60^\circ\)（即 \(\dfrac{\pi}{3}\)）。**

推理：连 \(AD_1\)。正方体中 \(\overrightarrow{BC_1}=\overrightarrow{AD_1}\)（侧面 \(BCC_1B_1\) 与 \(ADD_1A_1\) 中对应面对角线平行且同向），故 \(\langle\overrightarrow{BC_1},\overrightarrow{AC}\rangle=\langle\overrightarrow{AD_1},\overrightarrow{AC}\rangle=\angle D_1AC\)。设棱长为 1，则 \(AC\)、\(CD_1\)、\(D_1A\) 均为面的对角线，长都为 \(\sqrt{2}\)，\(\triangle ACD_1\) 为等边三角形，\(\angle D_1AC=60^\circ\)。坐标验证：\(A(0,0,0),B(1,0,0),C(1,1,0),C_1(1,1,1)\)，\(\overrightarrow{BC_1}=(0,1,1)\)，\(\overrightarrow{AC}=(1,1,0)\)，\(\cos\theta=\frac{1}{\sqrt{2}\cdot\sqrt{2}}=\frac12>0\)，\(\theta=60^\circ\)。

**方法一句话**：平移 \(\overrightarrow{BC_1}\) 到 \(\overrightarrow{AD_1}\) 构造等边三角形求夹角，并用坐标法独立复核。

**把握度**：确定。

---

自证盲性：本次我只读了 `工作区/_tmp取证0909c/片G/逻辑闸试点0911/二期/题目-盲解版.md` 这一个文件，未读任何其他文件、未联网。
