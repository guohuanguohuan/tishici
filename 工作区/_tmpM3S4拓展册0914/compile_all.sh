#!/bin/bash
X=/c/Users/28120/AppData/Roaming/TinyTeX/bin/windows/xelatex
BASE=/c/提示词/工作区/M3-第2章量产0913/成卷/拓展册
for vol in 上册 下册; do
  for sh in main-true main-false; do
    cd "$BASE/$vol" || exit 1
    for i in 1 2; do
      echo "=== $vol/$sh pass$i ==="
      "$X" -interaction=nonstopmode "$sh.tex" >/dev/null 2>&1
      echo "exit=$?"
    done
  done
done
echo ALLDONE
