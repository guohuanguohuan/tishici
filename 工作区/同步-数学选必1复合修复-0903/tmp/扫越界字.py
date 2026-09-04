import fitz, glob, os, collections

# 越界字符定义：下标/上标数字、数学斜体字母、组合箭头等——这些在 TimesNewRoman 里不存在
def sus(ch):
    o = ord(ch)
    return (0x2080 <= o <= 0x2089) or (0x2090 <= o <= 0x209C) or (0x1D400 <= o <= 0x1D7FF) or (0x20D0 <= o <= 0x20F0)

base = r'C:\提示词\工作区\同步-数学选必1复合修复-0903\pages_406\pdf'
inv = collections.defaultdict(list)
for p in sorted(glob.glob(base + r'\*.pdf')):
    name = os.path.basename(p)[:-4]
    if name in ('导出记录',) or len(name) <= 3 and name.startswith(('F', 'S', 'M')): pass
    doc = fitz.open(p)
    for i in range(len(doc)):
        for blk in doc[i].get_text('dict')['blocks']:
            for line in blk.get('lines', []):
                for span in line['spans']:
                    fnt = span['font']
                    if 'CambriaMath' in fnt: continue
                    bad = [c for c in span['text'] if sus(c)]
                    if bad:
                        inv[name].append((i+1, fnt, ''.join(sorted(set(bad))), span['text'][:40]))
    doc.close()

for name, rows in sorted(inv.items()):
    print(f'=== {name}: {len(rows)} 处嫌疑span ===')
    for pg, fnt, bads, t in rows:
        print(f'  p{pg:03d} [{fnt}] 越界字={bads} 文本={t!r}')
if not inv:
    print('全 layer 无疑嫌疑span')
