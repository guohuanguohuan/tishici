# 对照六图.py —— 回退轮0910 条6：件内渲染 vs 原位图 同尺并排对照（300dpi）
import pymupdf
from PIL import Image, ImageDraw

BASE = 'C:/提示词/工作区/字替对照-0909/variantF/'
OUT = 'C:/提示词/工作区/字替对照-0909/回退轮0910/'
DPI = 300
SC = DPI / 72.0
doc = pymupdf.open(BASE + 'main.pdf')
FIGS = [('g1', 'image1.png', 3, 'g1-prism'), ('g2', 'image2.png', 3, 'g2-cubeE'),
        ('g3', 'image3.png', 5, 'g3-cube6'), ('g4', 'image4.png', 6, 'g4-dihedral'),
        ('g5', 'image5.png', 6, 'g5-fold'), ('g6', 'sub3_B_4.png', 2, 'g6-triple')]
PX = {'g1-prism': (691, 1159), 'g2-cubeE': (764, 764), 'g3-cube6': (521, 496),
      'g4-dihedral': (788, 424), 'g5-fold': (1798, 1350), 'g6-triple': (1408, 374)}

for tag, fn, pno, frag in FIGS:
    pg = doc[pno - 1]
    rect = None
    for info in pg.get_image_info():
        if (info['width'], info['height']) == PX[frag]:
            rect = pymupdf.Rect(info['bbox'])
    assert rect is not None, frag
    clip = pymupdf.Rect(rect.x0 - 6, rect.y0 - 6, rect.x1 + 6, rect.y1 + 6)
    pm = pg.get_pixmap(dpi=DPI, clip=clip)
    pm.save(OUT + '_tmpclip.png')
    piece = Image.open(OUT + '_tmpclip.png').convert('RGB')
    orig = Image.open(BASE + 'media/media/' + fn).convert('RGBA')
    bg = Image.new('RGBA', orig.size, (255, 255, 255, 255))
    orig = Image.alpha_composite(bg, orig).convert('RGB')
    w_px = int(round(rect.width * SC))
    h_px = int(round(rect.height * SC))
    orig = orig.resize((w_px, h_px), Image.LANCZOS)   # 同物理宽＝同尺
    W = max(piece.width, orig.width) + 24
    H = piece.height + orig.height + 74
    sheet = Image.new('RGB', (W, H), (245, 245, 245))
    d = ImageDraw.Draw(sheet)
    d.text((8, 4), '%s in-page render (%s @ %.1fmm wide, 300dpi)' % (tag, fn, rect.width / 72 * 25.4), fill='black')
    sheet.paste(piece, (10, 24))
    y2 = 24 + piece.height + 12
    d.text((8, y2), '%s original bitmap same scale (media/media/%s, native %dx%d px)'
           % (tag, fn, PX[frag][0], PX[frag][1]), fill='black')
    sheet.paste(orig, (10, y2 + 20))
    sheet.save(OUT + '对照位图-%s.png' % tag)
    print(tag, 'sheet', sheet.size, 'rect mm %.1fx%.1f' % (rect.width / 72 * 25.4, rect.height / 72 * 25.4))
