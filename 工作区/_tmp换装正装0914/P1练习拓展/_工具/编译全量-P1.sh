#!/bin/bash
# 双档＋基线全量编译：P1 波4b 5 件 × (true,pure,src基线) × 2 遍 ＋ 拓 压测A/B/C × 2；汇总 exit 与错数
cd "/c/提示词/工作区/_tmp换装正装0914/P1练习拓展" || exit 9
for piece in 9.1电荷 9.2库仑定律 9.3电场电场强度 9.4静电的防止与利用 拓展册; do
  for mode in true pure src; do
    d="$piece"
    (cd "$d" || exit 9
     xelatex -interaction=nonstopmode "main-$mode.tex" > "_run_$mode.1.txt" 2>&1; e1=$?
     xelatex -interaction=nonstopmode "main-$mode.tex" > "_run_$mode.2.txt" 2>&1; e2=$?
     err=$(grep -c '^!' "main-$mode.log" 2>/dev/null)
     ovf=$(grep -c 'Overfull' "main-$mode.log" 2>/dev/null)
     miss=$(grep -c 'Missing character' "main-$mode.log" 2>/dev/null)
     echo "$piece main-$mode exit=$e1,$e2 err=$err overfull=$ovf misschar=$miss")
  done
done
for v in 压测A-三栏灰底 压测B-两栏括线 压测C-三栏括线; do
  (cd "拓展册" || exit 9
   xelatex -interaction=nonstopmode "main-$v-true.tex" > "_run_$v.1.txt" 2>&1; e1=$?
   xelatex -interaction=nonstopmode "main-$v-true.tex" > "_run_$v.2.txt" 2>&1; e2=$?
   err=$(grep -c '^!' "main-$v-true.log" 2>/dev/null)
   ovf=$(grep -c 'Overfull' "main-$v-true.log" 2>/dev/null)
   miss=$(grep -c 'Missing character' "main-$v-true.log" 2>/dev/null)
   echo "拓展册 $v exit=$e1,$e2 err=$err overfull=$ovf misschar=$miss")
done
echo BATCH_DONE
