"""精测：从 image2.png 提取全部几何量（子像素），输出 geom.json"""
from PIL import Image
import numpy as np, json
from scipy import ndimage

P = r"C:\提示词\工作区\字替对照-0909\variantF\media\media\image2.png"
im = Image.open(P).convert("L")
a = np.array(im).astype(float)
ink = 1.0 - a/255.0
b = a < 128

def centroid_col(x0, x1, y):          # 竖线：某一行上的 x 质心
    w = ink[y, x0:x1]; return (w*np.arange(x0,x1)).sum()/w.sum(), w.sum()
def centroid_row(y0, y1, x):          # 横线：某一列上的 y 质心
    w = ink[y0:y1, x]; return (w*np.arange(y0,y1)).sum()/w.sum(), w.sum()

def fit_line(samples):                # samples: [(t, c)] 沿 t 采样、c 为垂直坐标质心
    t = np.array([s[0] for s in samples], float); c = np.array([s[1] for s in samples], float)
    A = np.vstack([t, np.ones_like(t)]).T
    m, k = np.linalg.lstsq(A, c, rcond=None)[0]
    return float(m), float(k)         # c = m*t + k

def inter_h_v(hor, ver):              # hor: (m,k) y=mx+k ; ver: (m2,k2) x=m2*y+k2
    m,k = hor; m2,k2 = ver
    y = (m*k2 + k)/(1 - m*m2); x = m2*y + k2; return (x,y)
def inter_gen(l1, l2):               # 一般：线段方向 (ux,uy) 与点 p
    (p1,d1),(p2,d2) = l1,l2
    A = np.array([[d1[0], -d2[0]],[d1[1], -d2[1]]], float)
    t = np.linalg.solve(A, np.array([p2[0]-p1[0], p2[1]-p1[1]]))
    return (p1[0]+t[0]*d1[0], p1[1]+t[0]*d1[1])

G = {}
# --- 竖直边：A-A1 (x~108.5), B-B1 (x~527.5), C-C1 (x~682.5)
for name, x0, x1, ys in [("AA1", 95, 125, [300,400,500,600]), ("BB1", 515, 545, [300,400,500,600]), ("CC1", 668, 700, [200,330,470])]:
    s = [(y, centroid_col(x0,x1,y)[0]) for y in ys]
    m,k = fit_line(s); G[name] = {"m":m, "k":k, "vert": True, "samples":s}
    print(name, "x = %.4f*y + %.4f" % (m,k), "thick≈%.2f" % np.mean([centroid_col(x0,x1,y)[1] for y in ys]))
# --- 水平边：A-B (y~671.5), A1-B1 (y~253.5), D1-C1 (y~96.5)
for name, y0, y1, xs in [("AB", 660, 685, [150,250,350,450]), ("A1B1", 240, 266, [150,250,350,450]), ("D1C1", 84, 112, [300,400,500,620])]:
    s = [(x, centroid_row(y0,y1,x)[0]) for x in xs]
    m,k = fit_line(s); G[name] = {"m":m, "k":k, "horiz": True, "samples":s}
    print(name, "y = %.4f*x + %.4f" % (m,k), "thick≈%.2f" % np.mean([centroid_row(y0,y1,x)[1] for x in xs]))
# --- 斜边 45°：B-C, A1-D1, B1-C1（按行采样）
for name, xs in [("BC", [540,570,600,630,660]), ("A1D1", [130,160,190,220,245]), ("B1C1", [550,580,610,640,665])]:
    s = [(x, centroid_row( 0,764, x)[0]) for x in []]; s=[]
    for x in xs:
        w = ink[:, x]; # 找该列中属于这条斜边的 run（用形态：附近行搜索）
        s.append((x, centroid_col(0,1,x)[0]))
    G[name] = {"xs":xs}
print("（斜边稍后用连通域法定位）")
json.dump(G, open("geom_raw.json","w"), ensure_ascii=False, indent=1)
