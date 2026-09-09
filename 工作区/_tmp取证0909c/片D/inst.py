# -*- coding: utf-8 -*-
"""片D 0909c：从 AlimamaFangYuanTi-VF.ttf 实例化变式标签双字重档（沿 E 轮 calibrate.py 先例）。
产物落 variantF/fonts/（gitignore 已挡）；本脚本/日志为临时产物，只落 _tmp取证0909c/片D/。"""
import os, subprocess, hashlib

VF = r"C:/提示词/工作区/字替对照-0909/fonts/候选字体/AlimamaFangYuanTi-VF.ttf"
OUT = r"C:/提示词/工作区/字替对照-0909/variantF/fonts"
os.makedirs(OUT, exist_ok=True)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return r.returncode, (r.stdout + r.stderr)[-800:]

for w in (700, 450, 500):
    out = f"{OUT}/FY-w{w}BEVL100.ttf"
    if os.path.exists(out):
        print(f"skip existing {out}")
    else:
        rc, msg = run(f'python -m fontTools.varLib.instancer "{VF}" wght={w} BEVL=100 -o "{out}"')
        print(f"wght={w} BEVL=100 rc={rc}")
        if rc:
            print(msg); raise SystemExit(1)

for w in (700, 450, 500):
    p = f"{OUT}/FY-w{w}BEVL100.ttf"
    h = hashlib.md5(open(p, 'rb').read()).hexdigest()
    print(f"FY-w{w}BEVL100.ttf  {os.path.getsize(p)} bytes  MD5={h}")

# 真身核验
from fontTools.ttLib import TTFont
for w in (700, 450, 500):
    f = TTFont(f"{OUT}/FY-w{w}BEVL100.ttf")
    print(f"FY-w{w}BEVL100: fvar={'fvar' in f} usWeightClass={f['OS/2'].usWeightClass} name4={f['name'].getDebugName(4)!r}")
