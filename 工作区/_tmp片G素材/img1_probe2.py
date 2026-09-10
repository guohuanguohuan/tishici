# -*- coding: utf-8 -*-
"""Component + dot analysis for image1.png (ink in alpha channel)."""
import numpy as np
import cv2

ink = np.load("img1_ink.npy")
H, W = ink.shape

# --- connected components: figure vs glyphs ---
n, lab, stats, cent = cv2.connectedComponentsWithStats(ink, 8)
print("components:", n - 1)
comps = []
for i in range(1, n):
    x, y, w, h_, area = (stats[i, 0], stats[i, 1], stats[i, 2], stats[i, 3], stats[i, 4])
    comps.append((area, x, y, w, h_, i))
comps.sort(reverse=True)
for a, x, y, w, h_, i in comps[:24]:
    print("comp id=%d area=%d bbox x %d-%d y %d-%d (w%d h%d)" % (i, a, x, x + w - 1, y, y + h_ - 1, w, h_))

# --- dot detection via disk density ---
r = 5
k = np.zeros((2 * r + 1, 2 * r + 1), np.uint8)
cv2.circle(k, (r, r), r, 1, -1)
dens = cv2.filter2D(ink.astype(np.float32), -1, k.astype(np.float32)) / k.sum()
mask = (dens > 0.985).astype(np.uint8)
nn, ll, ss, cc = cv2.connectedComponentsWithStats(mask, 8)
print("dot centers (disk r=5 density>0.985):")
pts = []
for i in range(1, nn):
    pts.append((cc[i][0], cc[i][1], ss[i, 4]))
for cx, cy, a in sorted(pts, key=lambda t: t[1]):
    print("  dot cx=%.1f cy=%.1f area=%d" % (cx, cy, a))

# label glyph bboxes: components excluding figure (largest)
print("likely glyph comps:")
for a, x, y, w, h_, i in comps:
    if a < 3000 and max(w, h_) > 12:
        print("  glyph area=%d bbox x %d-%d y %d-%d (w%d h%d) centroid (%.1f,%.1f)" % (a, x, x + w - 1, y, y + h_ - 1, w, h_, cent[i][0], cent[i][1]))
