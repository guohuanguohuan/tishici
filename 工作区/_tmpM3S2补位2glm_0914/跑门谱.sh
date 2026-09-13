#!/bin/bash
# 门谱批跑 — 补位臂2(glm) 0914。用法: bash 跑门谱.sh <04|05|06>
# 零 git；只写本过程件目录与片目录编译产物。
set -u
TAG="$1"
ROOT='C:/提示词/工作区/M3-第2章量产0913'
PIECE="$ROOT/成卷/导学件"
case "$TAG" in
  04) DIR="$PIECE/课时04-点斜式与斜截式";;
  05) DIR="$PIECE/课时05-两点式与一般式";;
  06) DIR="$PIECE/课时06-两条直线的位置关系";;
  *) echo "件须∈{04,05,06}"; exit 2;;
esac
GATES='C:/提示词/工作区/_tmpM3S2补位2glm_0914/门谱'
TOOL='C:/提示词/工具'
LOGD='C:/提示词/工作区/_tmpM3S2补位2glm_0914'
cd "$DIR" || exit 2
echo "=== [$TAG] 编译 main-true ×2 ==="
xelatex -interaction=nonstopmode main-true.tex > "$LOGD/c$TAG-t1.log" 2>&1
xelatex -interaction=nonstopmode main-true.tex > "$LOGD/c$TAG-t2.log" 2>&1
echo "=== [$TAG] 编译 main-false ×2 ==="
xelatex -interaction=nonstopmode main-false.tex > "$LOGD/c$TAG-f1.log" 2>&1
xelatex -interaction=nonstopmode main-false.tex > "$LOGD/c$TAG-f2.log" 2>&1
echo "=== [$TAG] 三零/ANSKEY 读数 ==="
for L in main-true.log main-false.log; do
  echo "-- $L: err=$(grep -c '^!' $L) over=$(grep -c 'Overfull' $L) under=$(grep -c 'Underfull' $L) miss=$(grep -c 'Missing character' $L) anskey=$(grep -c '^M3-ANSKEY:' $L)"
done
python -c "import fitz,sys;d1=fitz.open('main-true.pdf');d2=fitz.open('main-false.pdf');print('pages true=%d false=%d ok=%s'%(d1.page_count,d2.page_count,d2.page_count<=d1.page_count))"
echo "=== [$TAG] 门-守恒对号 ==="
python "$GATES/门-守恒对号.py" "$TAG"; echo "exit=$?"
echo "=== [$TAG] 门-值快照键型判模 ==="
python "$GATES/门-值快照键型判模.py" "$TAG"; echo "exit=$?"
echo "=== [$TAG] 门-回流+CJK ==="
python "$GATES/门-回流.py" "$TAG"; echo "exit=$?"
echo "=== [$TAG] 键账对平门 ==="
python "$TOOL/键账对平门.py" --piece "片=$DIR/main.tex" --ledger "台账=$DIR/值台账-课时$TAG.json" --expect "manifest键序=$GATES/键表-课时$TAG.txt"; echo "exit=$?"
echo "=== [$TAG] 槽宽门 zero-fp ==="
python "$TOOL/makebox槽宽门.py" "$DIR" --mode zero-fp; echo "exit=$?"
echo "=== [$TAG] 槽宽门 strict ==="
python "$TOOL/makebox槽宽门.py" "$DIR" --mode strict; echo "exit=$?"
echo "=== [$TAG] 门谱毕 ==="
