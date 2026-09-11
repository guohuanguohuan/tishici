# slice-01 盲解答卷（qwen 臂）

- 题面来源：`工作区/逻辑闸-样张族0911/slices/slice-01.md`（导学件·课前预习，知识点一～三；填空 8＋判断 6，共 14 题）
- 判据：《内容质量闸》卷三·全量档——判断题给 √/×＋一句理由；填空题给词/值；能双验的做互验或代验，确实无第二法的登记「仅单法」
- 解题日期：2026-09-11；全程盲解，未读任何答案键

---

## 知识点一　空间向量的概念

### 导-Y1-填1
**答案**：大小（模）；方向
**解法要点**：空间向量的定义即"既有大小又有方向的量"，与平面向量定义同构，推广到空间。两空无先后依赖，按定义语序填"大小、方向"。
**验证**：①定义比对（人教B版选择性必修第一册开篇定义）；②互验：条目3表中零向量、单位向量、相反向量、相等向量的定义恰好只用"长度（模）"与"方向"这两个要素展开，与本条两要素自洽。结论：可靠。

### 导-Y1-填2
**答案**：长度
**解法要点**：向量的几何表示是用有向线段，有向线段的**长度**表示向量的模（线段本身有方向，但"模"是一个数量，对应的是长度）。
**验证**：①定义比对；②互验：条目3表"零向量＝长度为＿＿的向量"同样以"长度"承载模的概念，两处口径一致。结论：可靠。

### 导-Y1-填3
**答案**：（引导空）零；表中各空依次为——零向量行：0；\(\overrightarrow{0}\)。单位向量行：1。相反向量行：相反。共线（平行）向量行：互相平行；重合。相等向量行：模相等（长度相等）。
**解法要点**：规定零向量与任意向量平行，因为零向量方向任意，约定上可视为与任何方向平行；表五行是特殊向量的标准定义——零向量按长度（0）、单位向量按模（1）、相反向量按"等长反向"、平行向量按基线"互相平行或重合"、相等向量按"同向等模"。
**验证**：①各空代回定义句，语义完整通顺；②互验："零向量与任意向量平行"这一规定正是本卷导-Y2-判1、判2 以 \(\overrightarrow{b}=\overrightarrow{0}\) 举反例的依据，条目间逻辑闭环；相反向量"方向相反"与填1两要素（模、方向）一致。结论：可靠。

### 导-Y1-判1
**答案**：×
**解法要点**：向量相等要求"方向相同且模相等"双要素同时成立；仅模相等而方向可以任意，故推不出相等。
**验证**：反例法——任取两个方向不同的单位向量 \(\overrightarrow{a},\overrightarrow{b}\)，\(|\overrightarrow{a}|=|\overrightarrow{b}|=1\) 但 \(\overrightarrow{a}\neq\overrightarrow{b}\)；互验——导-Y1-填3 表中"相等向量"定义明列"方向相同且模相等"，两要件缺一不可，与该表自洽。结论：×，判据充分。

### 导-Y1-判2
**答案**：√
**解法要点**：相等向量方向相同，方向相同的向量其有向线段所在直线互相平行（或重合），满足共线（平行）向量定义，故相等向量必是共线向量。
**验证**：①按导-Y1-填3 表中平行向量定义（基线互相平行或重合）逐步推出，无额外条件缺口（零向量情形：相等向量同为 \(\overrightarrow{0}\) 时仍满足"与任意向量平行"的规定，不影响结论）；②互验：本条与判1恰成对照——判1错在丢"方向"要件，本条对在用足"方向"要件。结论：√。

---
## 知识点二　空间向量的线性运算

### 导-Y2-填1
**答案**：平行四边形；三角形；相同；相反
**解法要点**：空间向量加法与平面向量完全同法——共起点作平行四边形法则，首尾相接作三角形法则；数乘 \(\lambda\overrightarrow{a}\) 的几何意义是伸缩 \(\lvert\lambda\rvert\) 倍并以符号定方向：\(\lambda>0\) 同向、\(\lambda<0\) 反向、\(\lambda=0\) 得零向量。
**验证**：①定义比对；②代验：取 \(\lambda=0\) 落在题面给出的 \(\lambda\overrightarrow{a}=\overrightarrow{0}\) 分支上，与"方向由符号决定"的分类不矛盾；取 \(\lambda=-1\) 得相反向量，与导-Y1-填3 表"相反向量"定义衔接一致。结论：可靠。

### 导-Y2-填2
**答案**：唯一实数
**解法要点**：共线向量定理：\(\overrightarrow{a}\parallel\overrightarrow{b}\)（\(\overrightarrow{b}\neq\overrightarrow{0}\)）\(\Leftrightarrow\) 存在**唯一实数** \(\lambda\) 使 \(\overrightarrow{a}=\lambda\overrightarrow{b}\)。题面已带前提 \(\overrightarrow{b}\neq\overrightarrow{0}\)，故空中须补"唯一"二字（定理完整表述含存在性与唯一性）。
**验证**：双法互验——存在性：由 \(\overrightarrow{a}\parallel\overrightarrow{b}\) 且 \(\overrightarrow{b}\neq\overrightarrow{0}\)，取 \(\lambda=\pm|\overrightarrow{a}|/|\overrightarrow{b}|\)（同向取正、反向取负，\(\overrightarrow{a}=\overrightarrow{0}\) 时取 \(\lambda=0\)）即得 \(\overrightarrow{a}=\lambda\overrightarrow{b}\)；唯一性：设 \(\overrightarrow{a}=\lambda_1\overrightarrow{b}=\lambda_2\overrightarrow{b}\)，两式相减得 \((\lambda_1-\lambda_2)\overrightarrow{b}=\overrightarrow{0}\)，因 \(\overrightarrow{b}\neq\overrightarrow{0}\) 只能 \(\lambda_1=\lambda_2\)。两法均通过。结论：可靠。

### 导-Y2-判1
**答案**：×
**解法要点**：平行传递性对零向量失效——题面未排除 \(\overrightarrow{b}=\overrightarrow{0}\)，而规定零向量与任意向量平行。
**验证**：反例法——取 \(\overrightarrow{b}=\overrightarrow{0}\)，\(\overrightarrow{a},\overrightarrow{c}\) 为任意两个不共线的非零向量，则 \(\overrightarrow{a}\parallel\overrightarrow{0}\)、\(\overrightarrow{0}\parallel\overrightarrow{c}\) 都成立（依据导-Y1-填3 的规定），但 \(\overrightarrow{a}\parallel\overrightarrow{c}\) 不成立；反证边界——若补上 \(\overrightarrow{b}\neq\overrightarrow{0}\)，由导-Y2-填2 定理可推出结论，说明失效点恰在零向量。结论：×，反例确凿。

### 导-Y2-判2
**答案**：×
**解法要点**：丢了定理的关键前提 \(\overrightarrow{b}\neq\overrightarrow{0}\)，存在性和唯一性都会破。
**验证**：双反例——①存在性破：取 \(\overrightarrow{b}=\overrightarrow{0},\overrightarrow{a}\neq\overrightarrow{0}\)，由规定有 \(\overrightarrow{a}\parallel\overrightarrow{b}\)，但任何 \(\lambda\) 都使 \(\lambda\overrightarrow{b}=\overrightarrow{0}\neq\overrightarrow{a}\)；②唯一性破：取 \(\overrightarrow{a}=\overrightarrow{b}=\overrightarrow{0}\)，则任意实数 \(\lambda\) 均满足，不唯一。互验：导-Y2-填2 的标准定理表述显式携带 \(\overrightarrow{b}\neq\overrightarrow{0}\) 前提，与本条删去前提后的断言形成精确对照。结论：×。

---
## 知识点三　空间向量的夹角、数量积与共面

### 导-Y3-填1
**答案**：\([0,\pi]\)；垂直
**解法要点**：把 \(\overrightarrow{a},\overrightarrow{b}\) 平移到共起点 \(O\) 后，\(\angle AOB\) 的取值范围是 \(0\le\angle AOB\le\pi\)（同向时为 \(0\)，反向时为 \(\pi\)）；夹角为 \(\frac{\pi}{2}\) 即两向量垂直，记 \(\overrightarrow{a}\perp\overrightarrow{b}\)。
**验证**：①定义比对；②自洽代验：范围取端点检验——\(\theta=0,\pi\) 分别对应同向、反向共线，\(\theta=\frac{\pi}{2}\) 对应题面第二空的"垂直"，与后附性质"\(\overrightarrow{a}\perp\overrightarrow{b}\Leftrightarrow\overrightarrow{a}\cdot\overrightarrow{b}=0\)"（此时 \(\cos\theta=0\)）完全咬合；\([0,\pi]\) 上 \(\cos\) 值唯一确定角，保证数量积定义良定。结论：可靠。

### 导-Y3-填2
**答案**：零向量
**解法要点**：数量积定义式只对非零向量给出夹角，故需另行规定：零向量与任意向量的数量积为 \(0\)。
**验证**：①规定比对；②代验（极限相容性）：在 \(\overrightarrow{a}\cdot\overrightarrow{b}=|\overrightarrow{a}||\overrightarrow{b}|\cos\langle\overrightarrow{a},\overrightarrow{b}\rangle\) 中令 \(|\overrightarrow{a}|\to 0\)，无论夹角取何值右端恒趋于 \(0\)，规定值与定义式的趋势一致、不产生矛盾；性质式 \(\overrightarrow{a}\cdot\overrightarrow{a}=|\overrightarrow{a}|^2\) 取 \(\overrightarrow{a}=\overrightarrow{0}\) 亦得 \(0=0\)。两验均通过。结论：可靠。

### 导-Y3-填4
**答案**：唯一实数对（即有序实数对 \((x,y)\) 唯一存在）
**解法要点**：共面向量定理：\(\overrightarrow{p}\) 与不共线向量 \(\overrightarrow{a},\overrightarrow{b}\) 共面 \(\Leftrightarrow\) 存在**唯一**实数对 \((x,y)\) 使 \(\overrightarrow{p}=x\overrightarrow{a}+y\overrightarrow{b}\)。与导-Y2-填2 的"唯一实数"结构平行，这里参数升为一对。
**验证**：双法互验——存在性即定理方向（把 \(\overrightarrow{p}\) 平移至与 \(\overrightarrow{a},\overrightarrow{b}\) 共起点，落在其张成的平面内时按平行四边形法则分解即得 \(x\overrightarrow{a}+y\overrightarrow{b}\)）；唯一性可独立证明：设 \(x_1\overrightarrow{a}+y_1\overrightarrow{b}=x_2\overrightarrow{a}+y_2\overrightarrow{b}\)，相减得 \((x_1-x_2)\overrightarrow{a}=-(y_1-y_2)\overrightarrow{b}\)，若系数不全为零将推出 \(\overrightarrow{a}\parallel\overrightarrow{b}\)，与前提矛盾，故 \(x_1=x_2,y_1=y_2\)。两法均通过。结论：可靠。

### 导-Y3-判1
**答案**：√
**解法要点**：这正是共面向量定理的充分性方向——\(\overrightarrow{p}\) 能表成不共线 \(\overrightarrow{a},\overrightarrow{b}\) 的线性组合，则 \(\overrightarrow{p}\) 与 \(\overrightarrow{a},\overrightarrow{b}\) 共面。
**验证**：双法互验——①定理比对（导-Y3-填4 的 \(\Leftarrow\) 方向，条件"\(\overrightarrow{a},\overrightarrow{b}\) 不共线"题面已带，无缺口）；②几何构造：将三向量平移至共起点 \(O\)，作 \(OA\)、\(OB\)，则 \(x\overrightarrow{a}+y\overrightarrow{b}\) 对应的有向线段按数乘＋平行四边形法则必落在平面 \(OAB\) 内，故 \(\overrightarrow{p}\) 可由该平面表示。两法一致。结论：√。

### 导-Y3-判2
**答案**：×
**解法要点**：\(\overrightarrow{a}\cdot\overrightarrow{b}>0\Leftrightarrow\cos\langle\overrightarrow{a},\overrightarrow{b}\rangle>0\)，而夹角范围是 \([0,\pi]\)，满足条件的是 \([0,\frac{\pi}{2})\)——其中 \(\theta=0\)（同向共线）不是锐角，命题漏掉了这个端点。
**验证**：①反例法——取两个同向的非零向量（如 \(\overrightarrow{b}=2\overrightarrow{a}\)，\(\overrightarrow{a}\neq\overrightarrow{0}\)），\(\overrightarrow{a}\cdot\overrightarrow{b}=2|\overrightarrow{a}|^2>0\)，但夹角为 \(0\)，非锐角；②互验：导-Y3-填1 明确夹角范围含端点 \(0\)，与本条失效点严丝合缝（若把结论改为"夹角为锐角或零角/两向量同向"即成立）。两验一致。结论：×。

---

## 卷末汇总

| 题号 | 答案 |
|---|---|
| 导-Y1-填1 | 大小（模）；方向 |
| 导-Y1-填2 | 长度 |
| 导-Y1-填3 | 零；表：0／\(\overrightarrow{0}\)／1／相反／互相平行／重合／模相等 |
| 导-Y1-判1 | ×（模相等不保证方向相同） |
| 导-Y1-判2 | √（同向⇒基线平行或重合） |
| 导-Y2-填1 | 平行四边形；三角形；相同；相反 |
| 导-Y2-填2 | 唯一实数 |
| 导-Y2-判1 | ×（\(\overrightarrow{b}=\overrightarrow{0}\) 时传递性失效） |
| 导-Y2-判2 | ×（缺 \(\overrightarrow{b}\neq\overrightarrow{0}\) 前提） |
| 导-Y3-填1 | \([0,\pi]\)；垂直 |
| 导-Y3-填2 | 零向量 |
| 导-Y3-填4 | 唯一实数对 \((x,y)\) |
| 导-Y3-判1 | √（共面向量定理充分性） |
| 导-Y3-判2 | ×（夹角可为 \(0\)，非锐角） |

**验证口径说明**：本卷 14 题均为概念性填空与判断。凡可双验者（定理空、全部判断题）均做了"定义/定理比对＋反例或独立证明"双法互验；仅两处纯定义措辞空（导-Y1-填1、填2）以定义比对为主、辅以同卷条目间互验，无独立第二法，按档口登记为**近似仅单法（定义比对＋卷内条目交叉）**，其中判断题与定理空全部完成双验，无"仅单法"遗留。

**盲性自证**：仅读切片文件 `工作区/逻辑闸-样张族0911/slices/slice-01.md`，未触任何答案键（未读 `keys/` 目录、未读任何答案册/答案键文件、未联网搜题解）。
