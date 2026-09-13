# -*- coding: utf-8 -*-
r"""值复核批D补冻.py —— M3 S1 批D 课时14~17 G5 补冻 二十键 值↔定稿「导学 G5 补产」块 逐键比对＋存量 179 键零漂回归。

口径（值复核批E补冻.py 同法，值规范化禁自动生成）：
  定稿侧：解析 件末「导学 G5 补产」小节 块【1N-GK｜导学｜…】→ 块内【答案】行全文；
  题面库侧：对号门.parse_questions / parse_answers 同一提取约定。
  判全等：值 20 键逐键、题面 20 键逐字（15-G3/16-G3/17-G5 之注均在定稿【详解】后块尾、
          题面库侧不入题面主干，两不吃，题面主干逐字比对）。
  槽型构成：四片均 单选×3＋填空×2（补产报告 §一 核销表口径）；G5 详解指针域断言含「导学 G5 补产」。
  回归：存量 练+拓 全部键（66/31/45/37＝179）题面全文/答案块哈希 与补冻前 manifest 逐键哈希逐一相等
        （本件须跑于 冻manifest批D补冻.py 之前，方为真「补冻前」基线）。
跑法：python 值复核批D补冻.py
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
    '课时14': ('批D-课时14-2.6.2双曲线性质.md', r'^【14-G', '课时14-2.6.2双曲线性质', 66),
    '课时15': ('批D-课时15-2.7.1抛物线方程.md', r'^【15-G', '课时15-2.7.1抛物线方程', 31),
    '课时16': ('批D-课时16-2.7.2抛物线性质.md', r'^【16-G', '课时16-2.7.2抛物线性质', 45),
    '课时17': ('批D-课时17-2.8①压轴综合一.md', r'^【17-G', '课时17-2.8①压轴综合一', 37),
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
    for piece, (src, pat, title, base_n) in SRC.items():
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
            tag = '%s-G%d' % (piece[-2:], i)  # 定稿块标＝【14-G1｜…】，取课时号两位
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
            if not (daov[key][1].startswith('→定稿/') and '「导学 G5 补产」' in daov[key][1]):
                bad.append('%s 详解指针非 G5 补产域指向：%r' % (key, daov[key][1]))
        # 存量键零漂回归（对照补冻前 manifest 逐键哈希；基线＝23:12 初冻版，重冻前读取方为有效）
        mani = json.load(open(os.path.join(MANI, '%s.manifest.json' % piece), encoding='utf-8'))
        if len(mani['键序']) != base_n:
            bad.append('%s 补冻前 manifest 键数=%d≠%d（基线错位？）' % (piece, len(mani['键序']), base_n))
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
        print('  存量回归：%d 键中 %d 键哈希与补冻前 manifest 全等｜多选 %d（含拓区）'
              % (base_n, reg, len(multi)))
    print('合计：G5 值全等 %d/20｜题面逐字 %d/20｜存量零漂 %d/179' % (total_v, total_q, reg))
    if bad or total_v != 20 or total_q != 20 or reg != 179:
        print('不等清单：')
        for b in bad:
            print('  -', b)
        sys.exit(1)
    print('值复核批D补冻：20/20 全等＋存量 179/179 零漂 ✓（跑于重冻前，基线有效）')


if __name__ == '__main__':
    main()
