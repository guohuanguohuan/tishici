import fitz, sys, glob

pdf = glob.glob(r'C:\提示词\工作区\同步-数学选必1复合修复-0903\pages_406\pdf\*B*.pdf')
print('pdf候选:', pdf)
doc = fitz.open(pdf[0])
page = doc[1]  # p002
d = page.get_text('dict')
for blk in d['blocks']:
    for line in blk.get('lines', []):
        for span in line['spans']:
            t = span['text']
            if any(c in t for c in 'OABab+=') or '□' in t or '' in t:
                pass
# 直接找含 "a+b" 或 OA/AB/OB 的 span
print('--- p002 相关span ---')
for blk in d['blocks']:
    for line in blk.get('lines', []):
        for span in line['spans']:
            t = span['text'].strip()
            if t and ('OA' in t or 'AB' in t or 'OB' in t or 'a' == t or 'b' == t or '+' == t or '=' == t or '□' in t or '' in t):
                print(f"  字体={span['font']!r} 字号={round(span['size'],1)} 文本={t!r}")
print('--- p002 内嵌字体表 ---')
for f in page.get_fonts():
    print('  ', f)
