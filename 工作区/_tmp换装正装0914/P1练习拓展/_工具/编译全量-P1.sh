#!/bin/bash
# 基线＋压测补编译：5 件 × main.src（预迁移快照基线）× 2 遍 ＋ 拓 压测A/B/C × 2；汇总 exit 与错数
# （主双档 true/pure 已于 编译全量-P1.sh 首跑全三零；本件只补 src 基线与拓压测三变体）
cd "/c/提示词/工作区/_tmp换装正装0914/P1练习拓展" || exit 9
for piece in 9.1电荷 9.2库仑定律 9.3电场电场强度 9.4静电的防止与利用 拓展册; do
  (cd "$piece" || exit 9
   xelatex -interaction=nonstopmode "main.src.tex" > "_run_src.1.txt" 2>&1; e1=$?
   xelatex -interaction=nonstopmode "main.src.tex" > "_run_src.2.txt" 2>&1; e2=$?
   err=$(grep -c '^!' "main.src.log" 2>/dev/null)
   ovf=$(grep -c 'Overfull' "main.src.log" 2>/dev/null)
   miss=$(grep -c 'Missing character' "main.src.log" 2>/dev/null)
   echo "$piece main.src exit=$e1,$e2 err=$err overfull=$ovf misschar=$miss")
done
for v in 压测A-三栏灰底 压测B-两栏括线 压测C-三栏括线; do
  (cd "拓展册" || exit 9
   xelatex -interaction=nonstopmode "$v-true.tex" > "_run_$v.1.txt" 2>&1; e1=$?
   xelatex -interaction=nonstopmode "$v-true.tex" > "_run_$v.2.txt" 2>&1; e2=$?
   err=$(grep -c '^!' "$v-true.log" 2>/dev/null)
   ovf=$(grep -c 'Overfull' "$v-true.log" 2>/dev/null)
   miss=$(grep -c 'Missing character' "$v-true.log" 2>/dev/null)
   echo "拓展册 $v exit=$e1,$e2 err=$err overfull=$ovf misschar=$miss")
done
echo BATCH_DONE
