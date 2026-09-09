# -*- coding: utf-8 -*-
"""取证B组·全品裁片：p04/p05 目标式子高清裁片（写本目录），供定位与量隙。"""
from PIL import Image
import os

HERE = os.path.dirname(os.path.abspath(__file__))
D = r"C:\提示词\工作区\全品结构提取\数学选必一\导学案页图"

CROPS = [
    # (页, 名, x0,y0,x1,y1)
    ("p04", "qp_p04表_a=b",    900, 3220, 1350, 3420),
    ("p04", "qp_p04表_a∥b",    900, 3600, 1350, 3820),
    ("p04", "qp_p04判断3_∥",  1400, 1690, 2350, 1880),
    ("p05", "qp_p05条目2_b∥a", 1480, 320, 1780, 510),
    ("p05", "qp_p05判断2_∥=λ", 1480, 1450, 2450, 1640),
    ("p05", "qp_p05例1A_=b",  1480, 2230, 2400, 2420),
    ("p05", "qp_p05判断3_和式", 200, 1830, 1300, 2020),
]
for pg, name, x0, y0, x1, y1 in CROPS:
    im = Image.open(os.path.join(D, pg + ".png"))
    im.crop((x0, y0, x1, y1)).save(os.path.join(HERE, name + ".png"))
    print(name, "saved", x1 - x0, "x", y1 - y0)
