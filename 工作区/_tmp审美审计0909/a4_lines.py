# -*- coding: utf-8 -*-
"""行级标点检查：行首/行尾标点、悬挂、每行字距统计。我方 PDF 用 rawdict line 分组。"""
import collections, json
import pymupdf as fitz

PDF = r'mine-snapshot.pdf'
doc = fitz.open(PDF)
PUNCT = set('。，、；：！？）】》”’…—')
HALF = set(',.;:!?)]')
OPEN = set('（【《“‘([')

LCOL = (49.8, 49.8 + 82.8 / 25.4 * 72)          # 17.575mm .. +82.8mm
RCOL = (595.28 - 49.8 - 82.8 / 25.4 * 72, 595.28 - 49.8)
print('LCOL', LCOL, 'RCOL', RCOL)

stats = dict(head_punct=[], tail_punct=[], hang=[], lines=0, line_pitch={})
pitch_by_line = []
for pno in range(doc.page_count):
    page = doc[pno]
    d = page.get_text('rawdict')
    for block in d['blocks']:
        if block.get('type') != 0:
            continue
        for line in block['lines']:
            chars = []
            for span in line['spans']:
                for ch in span['chars']:
                    chars.append((ch['c'], ch['bbox'], span['size'], span['font'], ch['origin']))
            if not chars:
                continue
            stats['lines'] += 1
            # 行首/行尾（按字符 bbox x0 排序）
            chars.sort(key=lambda t: t[1][0])
            first_c, first_bb, first_sz, _, _ = chars[0]
            last_c, last_bb, last_sz, _, _ = chars[-1]
            if first_c in PUNCT or first_c in HALF:
                stats['head_punct'].append((pno + 1, first_c, round(first_bb[0], 1)))
            if last_c in PUNCT or last_c in HALF:
                # 判断是否悬挂：行尾标点 bbox.x1 超过栏右界
                col = LCOL if first_bb[0] < 300 else RCOL
                over = last_bb[2] - col[1]
                stats['tail_punct'].append((pno + 1, last_c, round(last_bb[2], 1), round(over, 2)))
                if over > 0.5:
                    stats['hang'].append((pno + 1, last_c, round(over, 2)))
            # 行内字距（相邻全角字）
            ps = []
            for (c1, b1, s1, f1, o1), (c2, b2, s2, f2, o2) in zip(chars, chars[1:]):
                if abs(o1[1] - o2[1]) > 0.3:
                    continue
                adv = o2[0] - o1[0]
                if s1 > 9 and adv > 0.8 * s1 and adv < 3 * s1:
                    ps.append(adv / s1)
            if len(ps) >= 5:
                pitch_by_line.append((pno + 1, round(sum(ps) / len(ps), 4),
                                      round(min(ps), 4), round(max(ps), 4), len(ps)))

print('总行数', stats['lines'])
print('行首标点', len(stats['head_punct']))
for t in stats['head_punct'][:15]:
    print('  ', t)
print('行尾标点', len(stats['tail_punct']))
for t in stats['tail_punct'][:15]:
    print('  ', t)
print('悬挂(超栏右界>0.5pt)', len(stats['hang']), stats['hang'][:10])
import statistics
m = [x[1] for x in pitch_by_line]
print('行内字距/em: 行数=%d 均值=%.4f 中位=%.4f 最小=%.4f 最大=%.4f' % (len(m), statistics.mean(m), statistics.median(m), min(m), max(m)))
wide = [x for x in pitch_by_line if x[3] > 1.2]
print('含拉伸>1.2em 的行数', len(wide), wide[:10])
