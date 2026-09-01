# -*- coding: utf-8 -*-
import fitz, sys, os
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
PDF = r'C:\提示词\工作区\同步-数学选必1册改制轮-0901\R审计\PDF'
FOOT = fitz.Rect(40, 782, 540, 804)
def strip(pn, redact=False):
    doc = fitz.open(os.path.join(PDF, code + '.pdf'))
    page = doc[pn-1]
    if redact:
        page.add_redact_annot(FOOT)
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE,
                              graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                              text=fitz.PDF_REDACT_TEXT_NONE)
    pix = page.get_pixmap(matrix=fitz.Matrix(4,4), clip=FOOT, colorspace=fitz.csRGB)
    img = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    doc.close()
    return img
for code, pn in [('B',47), ('E',50), ('X1',5)]:
    a = strip(pn)
    b = strip(pn, redact=True)
    w, h = a.size
    canvas = Image.new('RGB', (w, h*2+8), 'white')
    canvas.paste(a, (0,0)); canvas.paste(b, (0,h+8))
    canvas.save(os.path.join(PDF, '%s_footer_p%d_对比.png' % (code, pn)))
    print('saved', code, pn)
