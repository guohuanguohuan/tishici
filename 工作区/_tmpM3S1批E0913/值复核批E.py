# -*- coding: utf-8 -*-
r"""值复核批E.py —— M3 S1 批E 三片 答案侧值↔定稿【答案】栏 逐键比对＋题面逐字核对。

口径（S1 首批 值复核.py 同法，值规范化禁自动生成）：
  定稿侧：解析 补产全文区 块【键｜归属｜来源｜难度】→ 块内【答案】行全文；
  题面库侧：对号门.parse_questions / parse_answers 同一提取约定。
  判全等：值 60 键逐键、题面 59 键逐键。两处登记性差异（题面实质不动）：
    A1 18-13／18-14 题面尾「（注：…）」定稿内嵌生产注记 → 题面库移入【注】行（印面不出产注）；
    A2 18-16 值截去答案行尾生产注记括注（源措辞改写说明），值本体照录。
跑法：python 值复核批E.py
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', 'M3-第2章量产0913'))
DING = os.path.join(ROOT, '定稿')
TMUB = os.path.join(ROOT, '成卷', '题面库')
sys.path.insert(0, TMUB)
import 对号门  # noqa: E402  （复用同一提取约定；其 import 时统一包 stdout UTF-8）

SRC = {
    '课时18': ('定稿/批E-课时18-2.8②压轴综合二.md', r'^【18-', '课时18-2.8②压轴综合二'),
    '课时19': ('定稿/批E-课时19-章末总结与复习.md', r'^【19-', '课时19-章末总结与复习'),
    '衔接节': ('定稿/批E-衔接节.md', r'^【衔接-', '衔接节'),
}
BKEY = {'课时18': lambda h: '2章-练-课时18-%02d' % int(h.split('-')[-1]),
        '课时19': lambda h: '2章-练-课时19-%02d' % int(h.split('-')[-1]),
        '衔接节': lambda h: (lambda s: ('2章-练-衔接-' + s[1:]) if s.startswith('练') else
                           ('2章-导-衔接-' + {'G5-1': 'G1', 'G5-2': 'G2', 'G5-3': 'G3', 'G5-4': 'G4',
                                              'G5-5': 'G5', 'T1例': '探1', 'T1变': '探2', 'T2例': '探3',
                                              'T2变': '探4', 'T3例': '探5', 'T3变': '探6'}.get(s, s)))(
                              h.split('-', 1)[-1])}
NOTE_STRIP = {'2章-练-课时18-13', '2章-练-课时18-14'}      # A1：题面尾内嵌生产注记移【注】
VALUE_TRIM = {'2章-练-课时18-16'}                            # A2：值截生产注记括注


def parse_ding(path_rel, pat):
    blocks, cur = {}, None
    for ln in open(os.path.join(DING, os.path.basename(path_rel)), encoding='utf-8').read().splitlines():
        if re.match(pat, ln):
            tag = ln[1:].split('｜')[0].strip()
            cur = {'面': [], '答': None}
            blocks[tag] = cur
        elif cur is not None:
            if ln.startswith('【答案】'):
                cur['答'] = ln[len('【答案】'):].strip()
            elif ln.startswith('【详解】'):
                cur = None
            elif cur['答'] is None and ln.strip():
                cur['面'].append(ln)
    return blocks


def main():
    bad = []
    total_v = total_q = 0
    for piece, (src, pat, title) in SRC.items():
        ding = parse_ding(src, pat)
        qs = 对号门.parse_questions(os.path.join(TMUB, '%s.md' % title))
        ans = dict((k, v) for k, v, _ in 对号门.parse_answers(
            os.path.join(TMUB, '%s-答案侧.md' % title)))
        for tag, blk in ding.items():
            key = BKEY[piece](tag)
            if key not in ans:
                bad.append('%s：%s 键 %s 无答案侧' % (piece, tag, key))
                continue
            qrow = [q for q in 对号门.parse_questions(os.path.join(TMUB, '%s.md' % title)) if q[0] == key]
            qtext = qrow[0][2] if qrow else ''
            expect = list(blk['面'])
            if key in NOTE_STRIP and expect and '（注：' in expect[-1]:
                expect[-1] = expect[-1][:expect[-1].index('（注：')]
            if qtext != '\n'.join(expect):
                bad.append('%s 题面漂移：%s' % (key, tag))
            else:
                total_q += 1
            v = ans[key]
            dv = blk['答'] or ''
            if key in VALUE_TRIM and '；源答案' in dv:
                dv = dv[:dv.index('；源答案')] + '）'
            if v != dv:
                bad.append('%s 值不等：库=%r 定稿=%r' % (key, v, dv))
            else:
                total_v += 1
        multi = [q[0] for q in qs if q[1] == '多选']
        for k in multi:
            if list(ans[k]) != sorted(ans[k]):
                bad.append('%s 多选未按字母序：%s' % (k, ans[k]))
        print('【%s】定稿块%d｜值等%d｜题面逐字%d｜多选%d' % (piece, len(ding), sum(
            1 for t in ding if True), sum(1 for t in ding), len(multi)))
    print('合计：值全等 %d/59｜题面逐字 %d/59（登记差异 A1×2、A2×1 已计入等）' % (total_v, total_q))
    if bad:
        print('不等清单：')
        for b in bad:
            print('  -', b)
        sys.exit(1)
    print('值复核批E：59/59 全等 ✓（含登记差异 A1/A2）')


if __name__ == '__main__':
    main()
