import fitz

doc = fitz.open(r'C:\提示词\工作区\同步-数学选必1复合修复-0903\pages_406\pdf\B.pdf')
page = doc[1]
d = page.get_text('dict')
print('--- p002 含□/箭头 的 span ---')
for blk in d['blocks']:
    for line in blk.get('lines', []):
        for span in line['spans']:
            t = span['text']
            if '□' in t or '⃑' in t or '⃗' in t:
                bbox = [round(v) for v in span['bbox']]
                print(f"  字体={span['font']!r} 字号={round(span['size'],1)} bbox={bbox} 文本={t!r}")
print()
print('--- p002 页字体表（xref, 名, 类型, 编码）---')
for f in page.get_fonts(full=True):
    print('  ', f)
