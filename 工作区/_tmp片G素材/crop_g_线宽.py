# -*- coding: utf-8 -*-
import numpy as np, math
bw = np.load("_bw.npy")
H,W = bw.shape
def runlen_vertical(x, y_lo, y_hi):
    col = bw[y_lo:y_hi, x]; runs=[]; c=0
    for v in col:
        if v: c+=1
        elif c: runs.append(c); c=0
    if c: runs.append(c)
    return runs
def runlen_horizontal(y, x_lo, x_hi):
    row = bw[y, x_lo:x_hi]; runs=[]; c=0
    for v in row:
        if v: c+=1
        elif c: runs.append(c); c=0
    if c: runs.append(c)
    return runs
print("== vertical cuts through near-horizontal lines EF(y~205), AB(y~74), DC(y~346) ==")
for x in (120, 200, 260, 320, 380, 500, 560, 620, 660):
    print(f" x={x:3d} EFruns={runlen_vertical(x,190,225)} ABruns={runlen_vertical(x,60,95)} DCruns={runlen_vertical(x,330,365)}")
print("== horizontal cuts through near-vertical-ish lines EA, FB, ED, FC, DB ==")
for y in (110, 140, 170, 250, 280, 310):
    print(f" y={y:3d} runs={runlen_horizontal(y,0,W)}")
