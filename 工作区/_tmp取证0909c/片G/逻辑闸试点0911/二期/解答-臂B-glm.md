# 逻辑闸试点0911（二期）· 解答-臂B-glm

> 盲解声明：本次只读了 `工作区/_tmp取证0909c/片G/逻辑闸试点0911/二期/题目-盲解版.md`，未读该目录其他文件、未读 variantF/、靠齐样张/、素材普查/，未联网检索题源。

## 题1

- **最终答案**：B（若 a,b 为相反向量，则 a+b=0）
- **方法一句话**：逐项用向量定义排查——等长推不出共线（A 错）；相反向量按定义 b=−a 故 a+b=零向量（B 对）；零向量规范表述是"方向任意"而非"没有方向"（C 错）；单位向量方向可不同（D 错）。
- **把握度**：确定。唯一可议处是 C 的措辞：教材标准表述为"零向量的方向是任意的"，"没有方向"判错是常规口径；即便对 C 有歧义，B 按定义也必然正确，且单选不冲突。

## 题2

- **最终答案**：D（若 a∥b，则 |a|=|b| ——此项错误）
- **方法一句话**：逐项核对——A 是教材规定（零向量与任意向量平行，真）；模为零的向量只有零向量（B 真）；相等向量必有相等模（C 真）；平行只约束方向不约束模长，如 a 与 2a 平行但模不等（D 假）。
- **把握度**：确定。

## 题3

- **最终答案**：$\overrightarrow{A_{1}B}=\overrightarrow{b}-\overrightarrow{a}-\overrightarrow{c}$
- **方法一句话**：基底分解 $\overrightarrow{A_{1}B}=\overrightarrow{A_{1}A}+\overrightarrow{AB}=-\overrightarrow{c}+(\overrightarrow{CB}-\overrightarrow{CA})=\overrightarrow{b}-\overrightarrow{a}-\overrightarrow{c}$。
- **把握度**：确定。已用第二条路径互验：$\overrightarrow{A_{1}C_{1}}+\overrightarrow{C_{1}B}=\overrightarrow{AC}+(\overrightarrow{CB}-\overrightarrow{c})=(-\overrightarrow{a})+(\overrightarrow{b}-\overrightarrow{c})$，结果一致。

## 题4

- **最终答案**：$\overrightarrow{D_{1}B}=\overrightarrow{a}-\overrightarrow{b}-\overrightarrow{c}$
- **方法一句话**：$\overrightarrow{D_{1}B}=\overrightarrow{D_{1}D}+\overrightarrow{DB}=-\overrightarrow{c}+(\overrightarrow{AB}-\overrightarrow{AD})=\overrightarrow{a}-\overrightarrow{b}-\overrightarrow{c}$。
- **把握度**：确定。已用第二条路径互验：$\overrightarrow{D_{1}A_{1}}+\overrightarrow{A_{1}A}+\overrightarrow{AB}=(-\overrightarrow{b})+(-\overrightarrow{c})+\overrightarrow{a}$，结果一致。

## 题5

- **最终答案**：P，M，A，B 四点共面。理由：$\overrightarrow{MP}-\overrightarrow{MA}=3\overrightarrow{MA}-2\overrightarrow{MB}-\overrightarrow{MA}$，即 $\overrightarrow{AP}=2(\overrightarrow{MA}-\overrightarrow{MB})=2\overrightarrow{BA}$，故 $\overrightarrow{AP}\parallel\overrightarrow{BA}$，即 A、B、P 三点共线；A、B、P 在一条直线上，该直线与点 M 必共面，所以四点共面（实为更强的结论：P 在直线 AB 上）。
- **方法一句话**：将 $\overrightarrow{MP}=x\overrightarrow{MA}+y\overrightarrow{MB}$ 移项消去 M，判定 $\overrightarrow{AP}$ 与 $\overrightarrow{BA}$ 共线（系数 3+(−2)=1 的共面定理视角同向印证）。
- **把握度**：确定。共面性结论无歧义；无需 M 不在直线 AB 上的附加条件——直线加一点总共面。

## 题6

- **最终答案**：$\overrightarrow{BC_{1}}$ 与 $\overrightarrow{AC}$ 的夹角为 60°（$\dfrac{\pi}{3}$）。推理：设棱长为 a，以 A 为原点、$\overrightarrow{AB},\overrightarrow{AD},\overrightarrow{AA_{1}}$ 为 x,y,z 轴建系，则 $\overrightarrow{BC_{1}}=(0,a,a)$，$\overrightarrow{AC}=(a,a,0)$，$\cos\theta=\dfrac{0\cdot a+a\cdot a+a\cdot 0}{\sqrt{2}a\cdot\sqrt{2}a}=\dfrac12$，故 θ=60°。
- **方法一句话**：空间直角坐标系求数量积夹角（几何验算：$\overrightarrow{BC_{1}}=\overrightarrow{AD_{1}}$，而 △ACD₁ 三边均为 √2a 是等边三角形，∠D₁AC=60°，互证一致）。
- **把握度**：确定。两向量夹角按定义取 [0,π]，60° 无歧义。
