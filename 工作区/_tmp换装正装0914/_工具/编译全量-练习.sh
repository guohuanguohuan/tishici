#!/bin/bash
# 双档全量编译：12 件 × (true,pure) × 2 遍；汇总 exit 与 ！错数
cd "/c/提示词/工作区/_tmp换装正装0914/M2练习本" || exit 9
for piece in 课时01 课时02 课时03 课时04 课时05 课时06 课时07 课时08 课时09 课时10 上册 下册; do
  for mode in true pure; do
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
echo BATCH_DONE
