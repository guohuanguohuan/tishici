# ④轮 e2e 首页断言v3 复跑（2026-09-06，④轮新导出PDF硬链接；零COM）

== A) gen-mapping exit=0 ==
映射表已生成: 10 行
  清单1 条目号式 rev-check: .1-1．〔基〕空间向量｜反向校验:通过
  衔接1 条目号式 rev-check: ．平行线分线段成比例定理｜反向校验:通过
  上61 条目号式 rev-check: .1-1．〔基〕空间向量｜反向校验:通过
  下79 条目号式 rev-check: .2.5-1．〔基〕距离｜反向校验:通过
  清单2 条目号式 rev-check: 面上的两点间的距离公式．｜反向校验:通过
  衔接2 条目号式 rev-check: 1．一元二次方程的判别式｜反向校验:通过
  92 条目号式 rev-check: 面上的两点间的距离公式．｜反向校验:通过
  90 条目号式 rev-check: 基〕圆与圆位置关系的判定｜反向校验:通过
  68 条目号式 rev-check: 的差的绝对值等于非零常数｜反向校验:通过
  89 条目号式 rev-check: 个关于x的一元二次方程．｜反向校验:通过
== make-p1 exit=0 ==
== B) --run --mapping 锚点映射表v3.json（十件④轮PDF） exit=0 ==
Consider using the pymupdf_layout package for a greatly improved page layout analysis.
断言① PASS 10/10；阴性对照: ('FAIL', '首页正文区未见锚点块（块数=3 正文区行数=1）')
B) 断言① PASS 10/10；阴性对照=FAIL(期望FAIL, ok=True)

== 汇总 ==
SUMMARY_E2E_④: ①10/10=True 阴性对照FAIL=True → PASS
