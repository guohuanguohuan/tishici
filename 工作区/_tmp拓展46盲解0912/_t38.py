import numpy as np, math
# 14 charges on unit ring: 7 positive on upper semicircle (one at 90deg, 3 pairs symmetric about vertical),
# 7 negative mirrored about horizontal diameter.
d = math.radians(180/7)
pos_ang = [90 + k*d for k in range(-3,4)]
charges = [(math.cos(math.radians(a)), math.sin(math.radians(a)), 1.0) for a in pos_ang]
charges += [(math.cos(math.radians(a)), -math.sin(math.radians(a)), -1.0) for a in pos_ang]
charges = np.array(charges)
def E(p):
    tot = np.zeros(2)
    for x,y,q in charges:
        r = np.array(p)-np.array([x,y]); n = np.linalg.norm(r)
        tot += q*r/n**3
    return tot
s = 0.5
for name,p in [('a',(-s,0)),('b',(s,0)),('c',(0,s)),('d',(0,-s)),('O',(0,0))]:
    e = E(p); print(name, np.round(e,4), round(np.linalg.norm(e),4))
ys = np.linspace(-s,s,41)
mags = [np.linalg.norm(E((0,y))) for y in ys]
print('E along c->d min/max:', round(min(mags),4), round(max(mags),4), 'value at O:', round(mags[20],4))
xs = np.linspace(0.05,0.95,19)
print('E along x axis (y=0):', [round(np.linalg.norm(E((x,0))),3) for x in xs])
