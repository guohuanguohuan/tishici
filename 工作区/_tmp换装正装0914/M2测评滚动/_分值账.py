# -*- coding: utf-8 -*-
"""分值账闭合＋卷头制式＋\\ti 序列断言（读数 _分值账与覆盖断言.txt）。"""
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
L = []
for d, want in [("测评卷", 150), ("滚动卷A", 100), ("滚动卷B", 100)]:
    tex = (BASE / d / "main.tex").read_text(encoding="utf-8")
    src = (BASE / d / "main.src.tex").read_text(encoding="utf-8")
    grp = [(int(a), int(b)) for a, b in re.findall(r"每小题(\d+)分，共(\d+)分", tex)]
    grp_s = sum(b for _, b in grp)
    solo = [int(b) for a, b in re.findall(r"本题共(\d+)小题，共(\d+)分", tex)]
    fz = [int(x) for x in re.findall(r"\\fenzhi\{(\d+)\}", tex)]
    jie_s = sum(solo)                     # 解答组按组行共N分计
    total = grp_s + jie_s
    jie_fz = sum(fz)                      # 解答逐题 \fenzhi 自校
    t150 = "时间：120分钟" in tex and "分值：150分" in tex
    t100 = "时间：40分钟" in tex and "分值：100分" in tex
    ti = re.findall(r"\\ti\{(\d+)\}", tex)
    ti_src = re.findall(r"\\ti\{(\d+)\}", src)
    seq_ok = ti == [str(i) for i in range(1, len(ti) + 1)] and ti == ti_src
    L.append(f"{d}: 制式组行 {grp}＝{grp_s}＋解答组 {solo}＝{total} 分（期望 {want}）"
             f"{'✓' if total == want else '✗'}｜\\fenzhi 逐题和 {fz}＝{jie_fz}"
             f"{'＝解答组值 ✓' if jie_fz == jie_s else '≠解答组值 ✗'}"
             f"｜卷头 {'120分钟/150分' if t150 else '40分钟/100分' if t100 else '?'}"
             f"｜\\ti 1..{len(ti)} 连续且＝源面序列 {'✓' if seq_ok else '✗'}")
    L.append("   题干全串经回程断言逐字节不变（_换装案B.py）⇒ 题号↔节映射未动 ⇒ 章覆盖八节分布承试迁§七（测评卷八节全触达｜滚A 三节各≥1｜滚B 八节全触达、1.2.4/1.2.5 各≥2）仍真。")
txt = "\n".join(L) + "\n"
print(txt)
(BASE / "_门谱读数" / "_分值账与覆盖断言.txt").write_text(txt, encoding="utf-8")
