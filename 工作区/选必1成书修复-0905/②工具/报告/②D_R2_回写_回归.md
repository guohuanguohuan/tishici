```text
=== ① 回写（副本 → 同步盘；逐件 3 轮×300s 预算抗锁；同步客户端禁杀） ===
  清单1 回写 OK
  衔接1 回写 OK
  上61 回写 OK
  下79 回写 OK
  清单2 回写 OK
  衔接2 回写 OK
  92 回写 OK
  90 回写 OK
  68 回写 OK
  89 回写 OK
=== ② 防播散检查 ===
  同步盘 .bak_跨行护/.bak_栏顶 数 = 0 PASS
=== ③ MD5 逐件比对（副本 vs 同步盘） ===
  清单1    1834d9249e67cc5128239e831c55fb96 PASS
  衔接1    32fb9abc553bf4956e055b6c6bd89029 PASS
  上61    71edb6e640d3bcf90108f42a661cb3fa PASS
  下79    663a7b30e50036144a038a0ee2b09e91 PASS
  清单2    63fb9cc12aa4f4ce3297c70a38bd613b PASS
  衔接2    94baffb0a820be72764740c7b79f8ff6 PASS
  92     7f6ccc84fab546ba496c4b72c9d70f0d PASS
  90     13d05ec024ed09ecdb7bebd56169feca PASS
  68     fae93d4c76571213b665ae317940477b PASS
  89     d131d693477f4bba90d349fa01304cad PASS
=== ④ 同步盘幂等（四工具面 [0,0]）：T9 dry×2 ＋ T7 dry×2 ===
  T9 dry1 同步盘十件新挂全零 = True
  T9 dry2 同步盘十件新挂全零 = True
   杀 WINWORD 孤儿 pid11196
   杀 WINWORD 孤儿 pid2296
  !! T7 dry1 上61 失败
  T7 dry1 同步盘十件拟插符全零 = False
   杀 WINWORD 孤儿 pid2116
   杀 WINWORD 孤儿 pid10324
  !! T7 dry2 上61 失败
  T7 dry2 同步盘十件拟插符全零 = False
  T7 dry 两轮（拟插符,页数）全等 = False
=== ⑤ oMath 终验（同步盘十件＝②-F 锚） ===
  清单1    oMath=  396 锚=  396 PASS
  衔接1    oMath=  882 锚=  882 PASS
  上61    oMath= 3251 锚= 3251 PASS
  下79    oMath= 2876 锚= 2876 PASS
  清单2    oMath= 1156 锚= 1156 PASS
  衔接2    oMath=  243 锚=  243 PASS
  92     oMath= 2705 锚= 2705 PASS
  90     oMath= 2914 锚= 2914 PASS
  68     oMath= 2359 锚= 2359 PASS
  89     oMath= 4034 锚= 4034 PASS
=== ⑥ 页数三账（②C基线/T9后/T7后；fitz 独立清点遗留至 ②-E 全件 PDF 轮） ===
  页数三账落盘 报告/②D_R2_页数对照.md
=== 汇总 ===
SUMMARY ALLOK=False (wb=True nospread=True md5=True idem=False oMath=True pages=True)
```
