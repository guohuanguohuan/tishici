# -*- coding: utf-8 -*-
r"""值复核批E补冻.py —— M3 S1 批E G5 补冻 十键 值↔定稿「导学 G5 补产」块 逐键比对＋存量 32 键零漂回归。

口径（值复核批E.py 同法，值规范化禁自动生成）：
  定稿侧：解析 件末「导学 G5 补产」小节 块【1N-GK｜导学｜源｜难度】→ 块内【答案】行全文；
  题面库侧：对号门.parse_questions / parse_answers 同一提取约定。
  判全等：值 10 键逐键、题面 10 键逐字（19-G3 源订正注题面库侧走【注】行不入题面全文，
          定稿侧订正注在【详解】后块尾，两不吃，题面主干逐字比对）。
  回归：存量 练01~16×2 片 题面全文/答案块哈希 与补冻前 manifest 逐键哈希逐一相等
        （本件须跑于 冻manifest批E补冻.py 之前，方为真「补冻前」基线）。
跑法：python 值复核批E补冻.py
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', 'M3-第2章量产0913'))
DING = os.path.join(ROOT, '定稿')
TMUB = os.path.join(ROOT, '成卷', '题面库')
MANI = os.path.join(TMUB, 'manifest')
sys.path.insert(0, TMUB)
import 对号门  # noqa: E402  （复用同一提取约定；其 import 时统一包 stdout UTF-8）

SRC = {
    '课时18': ('批E-课时18-2.8②压轴综合二.md', r'^【18-G', '课时18-2.8②压轴综合二'),
    '课时19': ('批E-课时19-章末总结与复习.md', r'^【19-G', '课时19-章末总结与复习'),
}


def parse_g(path_rel, pat):
    blocks, cur = {}, None
    for ln in open(os.path.join(DING, path_rel), encoding='utf-8').read().splitlines():
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


def sha_text(t):
    return hashlib.sha256(t.encode('utf-8')).hexdigest()


def main():
    bad = []
    total_v = total_q = reg = 0
    for piece, (src, pat, title) in SRC.items():
        ding = parse_g(src, pat)
        qp = os.path.join(TMUB, '%s.md' % title)
        ap = os.path.join(TMUB, '%s-答案侧.md' % title)
        qs_rows = 对号门.parse_questions(qp)
        ans_rows = 对号门.parse_answers(ap)
        qs = dict((k, t) for k, _, t in qs_rows)
        daov = dict((k, (v, d)) for k, v, d in ans_rows)
        assert len(ding) == 5, '%s 定稿 G5 块数=%d≠5' % (piece, len(ding))
        kinds = dict((k, t) for k, t, _ in qs_rows)
        gkeys = ['2章-导-%s-G%d' % (piece, i) for i in range(1, 6)]
        gs = [kinds[k] for k in gkeys]
        print('【%s】G5 槽型：%s（期望 单选×3＋填空×2）' % (piece, '＋'.join(gs)))
        if not (gs.count('单选') == 3 and gs.count('填空') == 2):
            bad.append('%s G5 槽型构成异常：%s' % (piece, gs))
        for i, key in enumerate(gkeys, 1):
            tag = '%s-G%d' % (piece[-2:], i)  # 定稿块标＝【18-G1｜…】，取课时号两位
            blk = ding.get(tag)
            if blk is None or key not in qs or key not in daov:
                bad.append('%s：键 %s 三方缺一（定稿块/题面/答案）' % (piece, key))
                continue
            if qs[key] != '\n'.join(blk['面']):
                bad.append('%s 题面漂移（逐字不等）：%s' % (key, tag))
            else:
                total_q += 1
            dv = blk['答'] or ''
            if daov[key][0] != dv:
                bad.append('%s 值不等：库=%r 定稿=%r' % (key, daov[key][0], dv))
            else:
                total_v += 1
            if not daov[key][1].startswith('→定稿/'):
                bad.append('%s 详解指针非定稿指向' % key)
        # 存量键零漂回归（对照补冻前 manifest 逐键哈希）
        mani = json.load(open(os.path.join(MANI, '%s.manifest.json' % piece), encoding='utf-8'))
        if len(mani['键序']) != 16:
            bad.append('%s 补冻前 manifest 键数=%d≠16（基线错位？）' % (piece, len(mani['键序'])))
        for k, _, qtext in qs_rows:
            if '-导-' in k:
                if k in mani['逐键哈希']:
                    bad.append('%s 已在补冻前 manifest（预期外）' % k)
                continue
            h = mani['逐键哈希'].get(k)
            if not h:
                bad.append('%s 补冻前 manifest 缺存量键哈希' % k)
                continue
            v, d = daov[k]
            if sha_text(qtext) != h['题面']:
                bad.append('%s 存量题面哈希漂移（补冻误伤）' % k)
            elif sha_text(v + '\n' + d) != h['答案']:
                bad.append('%s 存量答案块哈希漂移（补冻误伤）' % k)
            else:
                reg += 1
        multi = [k for k, t, _ in qs_rows if t == '多选']
        for k in multi:
            if list(daov[k][0]) != sorted(daov[k][0]):
                bad.append('%s 多选未按字母序：%s' % (k, daov[k][0]))
        print('  存量回归：16 键中 %d 键哈希与补冻前 manifest 全等｜多选 %d' % (reg, len(multi)))
    print('合计：G5 值全等 %d/10｜题面逐字 %d/10｜存量零漂 %d/32' % (total_v, total_q, reg))
    if bad or total_v != 10 or total_q != 10 or reg != 32:
        print('不等清单：')
        for b in bad:
            print('  -', b)
        sys.exit(1)
    print('值复核批E补冻：10/10 全等＋存量 32/32 零漂 ✓（跑于重冻前，基线有效）')


if __name__ == '__main__':
    main()
