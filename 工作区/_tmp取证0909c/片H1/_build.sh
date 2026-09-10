#!/bin/bash
# 片H1 构建＋三0计数：用法 bash _build.sh <档名>
# 产出：variantF/main.pdf（＋快照 _tmp取证0909c/片H1/档_<档名>.pdf）
set -u
VF="C:/提示词/工作区/字替对照-0909/variantF"
OUT="C:/提示词/工作区/_tmp取证0909c/片H1"
TAG="${1:-run}"
cd "$VF" || exit 1
echo "=== [$TAG] postproc ==="
python postproc_daoxue.py > "$OUT/_build_${TAG}_postproc.log" 2>&1
pp=$?
if [ $pp -ne 0 ]; then echo "postproc FAILED ($pp)"; tail -5 "$OUT/_build_${TAG}_postproc.log"; exit 1; fi
echo "postproc ok"
for i in 1 2; do
  xelatex -interaction=nonstopmode main.tex > "$OUT/_build_${TAG}_xelatex${i}.log" 2>&1
done
cp main.pdf "$OUT/档_${TAG}.pdf"
echo "=== [$TAG] 三0计数 ==="
e=$(grep -c "^! " main.log)
ov=$(grep -c "Overfull \\\\hbox" main.log)
un=$(grep -c "Underfull \\\\hbox" main.log)
mc=$(grep -ci "missing character" main.log)
pg=$(grep -o "Output written on main.pdf ([0-9]* pages" main.log | grep -o "[0-9]*")
echo "error=$e overfull=$ov underfull=$un missingchar=$mc pages=$pg"
