# -*- coding: utf-8 -*-
# PDF逐页双断言：页眉节名=该页所属节标题、页脚节名=该页所属节标题（＋X/N顺带断言＋页眉=页脚）
# 节归属口径＝词典式跑头（公共规则§7实测注记⑤）：本页出现的第一个锚；无锚页取最近前锚。
# 锚定位＝1pt字号行（实测锚size=0.96pt，全文唯一——正文最小字号≥6.5pt，无混淆源）
# zone实测：页眉y0≤24.3｜正文≤771.8｜页脚≥786.2 → 阈值取40/780
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import fitz

CASES = [('X2挂载.pdf', 1, 4), ('B挂载.pdf', 1, 156), ('C挂载.pdf', 79, 156)]
HDR_Y, FTR_Y = 40, 780

def norm_keep_sep(s):
    return re.sub(r'[ \n\t\r]+', '', s)   # 剥ASCII空白（PyMuPDF数字汉字间伪迹），保留全角空格分隔符

def norm_all(s):
    return re.sub(r'\s+', '', s)          # 全空白剥（锚/节名匹配用）

fails, total_pages = [], 0
for path, start, n_total in CASES:
    print('=' * 66)
    print('##', path)
    doc = fitz.open(path)
    npages = doc.page_count
    anchor_pages, page_lines = {}, {}
    for i in range(npages):
        pno = i + 1
        anchors, hdr_parts, ftr_parts = [], [], []
        for b in doc[i].get_text('dict')['blocks']:
            if b.get('type') != 0:
                continue
            for ln in b['lines']:
                spans = sorted(ln['spans'], key=lambda s: s['bbox'][0])
                content = [s for s in spans if s['text'].strip()]
                if not content:
                    continue
                line_txt = ''.join(s['text'] for s in spans)
                if all(s['size'] < 3.0 for s in content):        # 1pt锚行
                    anchors.append(line_txt)
                elif ln['bbox'][1] < HDR_Y:
                    hdr_parts.append((ln['bbox'][1], ln['bbox'][0], line_txt))
                elif ln['bbox'][1] > FTR_Y:
                    ftr_parts.append((ln['bbox'][1], ln['bbox'][0], line_txt))
        anchor_pages[pno] = anchors
        page_lines[pno] = {
            'hdr': norm_keep_sep(''.join(t for _, _, t in sorted(hdr_parts))),
            'ftr': norm_keep_sep(''.join(t for _, _, t in sorted(ftr_parts))),
        }
    all_anchors = [a.strip() for p in sorted(anchor_pages) for a in anchor_pages[p]]
    print('  页数=%d | 锚行数=%d | 锚清单=%r' % (npages, len(all_anchors), all_anchors))

    def expected(pno):
        """词典式：本页出现的第一个锚；无锚页取最近前锚（本页最后/前页最后——文档序）。"""
        cur = [a for a in anchor_pages.get(pno, []) if a.strip()]
        if cur:
            return cur[0]
        for p in range(pno - 1, 0, -1):
            prev = [a for a in anchor_pages.get(p, []) if a.strip()]
            if prev:
                return prev[-1]
        return None

    bad = []
    for pno in range(1, npages + 1):
        exp = norm_all(expected(pno) or '')
        for zone in ('hdr', 'ftr'):
            line = page_lines[pno][zone].strip()
            # 全角空格在PyMuPDF提取中映射为普通空格并被剥除——分隔符容忍式匹配（锚定「（共N页）」与行尾「第X页」）
            m = re.fullmatch(r'(.+)（共(\d+)页）\s*(.+)\s*第(\d+)页', line)
            if not m:
                bad.append('p%d %s 同串形态异常: %r' % (pno, zone, line))
                continue
            got_sec = norm_all(m.group(3))
            if got_sec != exp:
                bad.append('p%d %s 节名=%r ≠ 期望%r' % (pno, zone, got_sec, exp))
            if int(m.group(4)) != start + pno - 1:
                bad.append('p%d %s X=%s ≠ %d' % (pno, zone, m.group(4), start + pno - 1))
            if int(m.group(2)) != n_total:
                bad.append('p%d %s N=%s ≠ %d' % (pno, zone, m.group(2), n_total))
        if page_lines[pno]['hdr'] != page_lines[pno]['ftr']:
            bad.append('p%d 页眉≠页脚同串: %r / %r' % (pno, page_lines[pno]['hdr'], page_lines[pno]['ftr']))
    # 3页抽样明细打印（规格要求：抽3页）——优先抽节边界页
    anchor_pnos = [p for p in range(1, npages + 1) if anchor_pages.get(p)]
    if len(anchor_pnos) >= 3:
        sample = sorted(set([anchor_pnos[1], anchor_pnos[len(anchor_pnos) // 2], anchor_pnos[-1]]))[:3]
    else:
        sample = [p for p in (1, npages // 2, npages) if 1 <= p <= npages]
    for pno in sample:
        print('  抽样p%d: 期望节名=%r' % (pno, expected(pno)))
        print('    页眉=%r' % page_lines[pno]['hdr'])
        print('    页脚=%r' % page_lines[pno]['ftr'])
    total_pages += npages
    print('  全页双断言：%d页×（页眉+页脚+X+N+同串） = %s' % (npages, 'ALL PASS' if not bad else 'FAIL %d项' % len(bad)))
    for x in bad[:12]:
        print('    -', x)
    fails.extend('%s %s' % (path, x) for x in bad)
    doc.close()

print('=' * 66)
print('PDF双断言总结：%d页全量 = %s' % (total_pages, 'ALL PASS' if not fails else 'FAIL %d项' % len(fails)))
sys.exit(0 if not fails else 1)
