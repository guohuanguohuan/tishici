# SW任务1证据：allowOverlap全件0化（2026-09-01）

## 改前勘察（勘察_anchor与导航表.py，产出文件夹只读实测）

[X1] anchor总计=42 已0=42 需改1=0 缺省/他值=0（E1返工§6.2已0化——计数确认，跳过手术）
[I1] anchor=9 全部="1"
[B]  anchor=60 全部="1"
[C]  anchor=64 全部="1"
[X2] anchor=0（无anchor件，无事可做）
[I2] anchor=30 全部="1"
[E]  anchor=39 全部="1"
[F]  anchor=43 全部="1"
[G]  anchor=31 全部="1"
[H]  anchor=34 全部="1"
十件合计 anchor=352 已0=42 需改1=310（无缺省/他值形态；全部anchor均显式携带属性）
anchor仅存在于word/document.xml（headers/footers等部件无anchor）。

## 手术实跑（allowOverlap归零.py，SW工作副本）

[I1] anchor=9 改写1→0=9 | 断言全过
[B] anchor=60 改写1→0=60 | 断言全过
[C] anchor=64 改写1→0=64 | 断言全过
[I2] anchor=30 改写1→0=30 | 断言全过
[E] anchor=39 改写1→0=39 | 断言全过
[F] anchor=43 改写1→0=43 | 断言全过
[G] anchor=31 改写1→0=31 | 断言全过
[H] anchor=34 改写1→0=34 | 断言全过
8件合计 anchor=310 改写=310（其中缺省补挂0）

断言B1/B2/B3逐件全过：
- B1 anchor计数前=后（310不改数）；
- B2 改后重开落盘件全部anchor allowOverlap="0"；
- B3 零副作用证明——原文将allowOverlap="1"全文替换为"0"后的字节流与手术输出逐字节相等（改动面仅该属性值）；其余zip成员原样透传。

## 终态复核（check-only二跑，幂等确认）

SW任务1_终态计数.txt：8件anchor=310 改写=0 已0=310（幂等；X1另计42已0）。
十件终态：352个anchor全部allowOverlap="0"（310本次＋42 X1前轮）。
