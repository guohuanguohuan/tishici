#!/bin/bash
# 目验修红0913：受影响六件 xelatex×2 三零读数（err / Overfull / Missing character）＋页数
set -u
ROOT="C:/提示词/工作区/M2-第1章量产0911/成卷"
OUT="C:/提示词/工作区/_tmp目验修红0913"
PIECES=(
  "导学件/课时03"
  "导学件/课时05"
  "导学件/课时06"
  "导学件/课时07"
  "导学件/衔接节-1.2.1前"
  "练习件/课时10"
)
: > "$OUT/compile2.log"
for pc in "${PIECES[@]}"; do
  d="$ROOT/$pc"
  cd "$d" || { echo "MISSING DIR $pc" | tee -a "$OUT/compile2.log"; continue; }
  xelatex -interaction=nonstopmode main.tex > _r1.log 2>&1
  xelatex -interaction=nonstopmode main.tex > _r2.log 2>&1
  err=$(grep -c '^! ' main.log)
  ovf=$(grep -c 'Overfull' main.log)
  mic=$(grep -c 'Missing character' main.log)
  und=$(grep -c 'Underfull' main.log)
  pg=$(python -c "import pymupdf;print(len(pymupdf.open('main.pdf')))" 2>/dev/null)
  echo "$pc | err=$err Overfull=$ovf MissingChar=$mic Underfull=$und pages=$pg" | tee -a "$OUT/compile2.log"
done
