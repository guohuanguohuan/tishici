import fitz

doc = fitz.open(r'C:\提示词\工作区\同步-数学选必1复合修复-0903\pages_406\pdf\B.pdf')
page = doc[1]
d = page.get_text('dict')
print('--- p002 y∈[690,790] 全部span（含空）---')
for blk in d['blocks']:
    for line in blk.get('lines', []):
        for span in line['spans']:
            y = span['bbox'][1]
            if 690 <= y <= 790:
                bbox = [round(v) for v in span['bbox']]
                t = span['text']
                print(f"  y={round(y)} x={bbox[0]}-{bbox[2]} 字体={span['font']!r} 文本={t!r} chars={len(span.get('chars', [])) if 'chars' in span else '?'}")
# rawdict 看字符级（含无法映射的glyph）
print()
print('--- rawdict 同带 ---')
d2 = page.get_text('rawdict')
for blk in d2['blocks']:
    for line in blk.get('lines', []):
        for span in line['spans']:
            y = span['bbox'][1]
            if 690 <= y <= 790:
                chars = span.get('chars', [])
                s = ''.join(c['c'] for c in chars)
                print(f"  y={round(y)} 字体={span['font']!r} 文本={s!r} glyph数={len(chars)}")
