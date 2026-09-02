# -*- coding: utf-8 -*-
"""恒等式核账.py — 机械计数辅助：成品题块数 / 题目台账行数 / 删除台账行数 三方对账底稿
用法: python 恒等式核账.py <成品docx...> [题目台账.md] [删除台账.md]
只做机械计数与差异提示；恒等式的公式与判定按所在总控由会话完成（同步线§2.3/§6②、二轮§2 等），
本脚本不替代判定，只替代数数。
2026-09-01 升级（A'改制轮·工具债③·T3）——层级制恒等式（公共规则§7⑦编号核验·同步线）：
  · 题号/条目号双形态识别：「N．」（旧全局）与「节号-序号．」（层级制，如「1.1.1-5．」）；
    题块＝号起段且块内含【答案】（讲部条目/清单条目不计题）；条目＝号起段且块内无【答案】。
  · 层级制核验：各节内题号/条目号序列连续无重复＋全件总数恒等＝文件名题量/条目数
    （文件名「（N题）」「（N条）」「（N题M条）」自动解析断言；清单件无条数时人工对规格书数）。
  · 旧全局号照跑：1..N 全件连续提示（原口径不变）。
2026-09-02 升级（A''成品轮·工具债）——题族前缀＝题型号「题型号-节内序号．」（组内起点＝节内
  累进值，题族起始≠1属预期、仅条目族报告）；新增题型统计段恒等核验（§7⑦/§7排版①）：
  ①各题型组统计段题数之和＝文件名题量；②「本节N题」各行之和＝文件名题量；③统计段区间端点
  与题数一致。"""
import sys, os, re
from dump_docx import body_elements, QNUM_RE, QNUM_MINLEN

HNUM_RE = re.compile(r'^(\d{1,3}(?:\.\d{1,3}){1,3})-(\d{1,3})．')   # 层级制「前缀-序号．」（A''题族前缀＝题型号）
FN_Q_RE = re.compile(r'（(\d+)题')
FN_E_RE = re.compile(r'（(\d+)条')
GRPCNT_RE = re.compile(r'　(\d+)题：((?:\d+(?:\.\d+)+-\d+)(?:～(?:\d+(?:\.\d+)+-\d+))?)')
SECSTAT_RE = re.compile(r'本节(\d+)题')

def count统计段(path):
    """A''题型统计段核验：返回 (组统计列表, 节统计列表, 问题清单)。"""
    els = body_elements(path)
    grp_stats, sec_stats, probs = [], [], []
    for i, tag, text in els:
        if tag != 'p' or not text:
            continue
        for m in GRPCNT_RE.finditer(text):
            n = int(m.group(1)); rng = m.group(2)
            a = rng.split('～')[0]
            b = rng.split('～')[-1]
            oa = int(a.rsplit('-', 1)[1]); ob = int(b.rsplit('-', 1)[1])
            if ob - oa + 1 != n:
                probs.append('题型统计段区间%s与题数%d不符' % (rng, n))
            grp_stats.append((text[:24], n))
        m2 = SECSTAT_RE.search(text)
        if m2:
            sec_stats.append(int(m2.group(1)))
    return grp_stats, sec_stats, probs

def _is_numstart(text):
    """号起段（双形态）→ ('hier', 节号, 序号) / ('old', None, N) / None。"""
    t = (text or '').strip()
    if len(t) < QNUM_MINLEN:
        return None
    m = HNUM_RE.match(t)
    if m:
        return ('hier', m.group(1), int(m.group(2)))
    m = QNUM_RE.match(t)
    if m:
        return ('old', None, int(m.group(1)))
    return None

def count成品(path):
    """返回 (题块数, 条目数, 层级制各节序列dict, 旧全局序列list, 问题清单)。
    题块＝号起段且块内含【答案】；条目＝号起段且块内无【答案】（经验口径：讲块内部「1．xxx」不计题）。"""
    els = body_elements(path)
    starts = []
    for i, tag, text in els:
        if tag != 'p':
            continue
        info = _is_numstart(text)
        if info:
            starts.append((i, info))
    n = q = e = 0
    hier = {}
    oldseq = []
    probs = []
    for k, (i, info) in enumerate(starts):
        j = starts[k+1][0] - 1 if k + 1 < len(starts) else els[-1][0]
        block = '\n'.join(t for ii, tag, t in els if i <= ii <= j and t is not None)
        kind, sec, o = info
        if '【答案】' in block:
            q += 1
            if kind == 'hier':
                hier.setdefault(('题', sec), []).append(o)
            else:
                oldseq.append((o, '题'))
        else:
            e += 1
            if kind == 'hier':
                hier.setdefault(('条', sec), []).append(o)
            else:
                oldseq.append((o, '条'))
    for (fam, sec), seq in hier.items():
        for k in range(1, len(seq)):
            if seq[k] != seq[k-1] + 1:
                probs.append('%s族节%s 序列断点：%d→%d' % (fam, sec, seq[k-1], seq[k]))
        if seq and seq[0] != 1 and fam == '条':
            probs.append('条族节%s 起始=%d（≠1；跨卷续号件属预期，须配续卷口径核对）' % (sec, seq[0]))
        # 题族A''形态：组内起点＝节内累进值，起始≠1属预期不入probs
    return q, e, hier, oldseq, probs

def fn_counts(path):
    b = os.path.basename(path)
    mq = FN_Q_RE.search(b)
    me = FN_E_RE.search(b)
    return (int(mq.group(1)) if mq else None, int(me.group(1)) if me else None)

def count台账行(md_path):
    """返回 (总数据行, {小节标题: 行数})；小节=「## 」行；跳过表头（含题号/原位置/首句字样）与分隔行。"""
    total, secs, cur = 0, {}, ''
    with open(md_path, encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if s.startswith('## '):
                cur = s[3:].strip(); secs.setdefault(cur, 0)
            elif s.startswith('|') and '---' not in s:
                if any(h in s for h in ('题号', '原位置', '首句(36字)', '判别特征')):
                    continue
                total += 1
                if cur:
                    secs[cur] += 1
    return total, secs

def count删除原因(md_path):
    """删除台账行按原因分组：优先扫行内关键词，其次继承「## 」小节标题（分节式台账）。"""
    grp = {}
    KEYS = ('超纲', '前序内容', '后续内容', '高度重复', '组合内让位', '跨卷让位', '多源合并让位', '转投暂存消费', '其它淘汰')
    cur = ''
    with open(md_path, encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if s.startswith('## '):
                cur = s
                continue
            if not s.startswith('|') or '---' in s or '原位置' in s:
                continue
            key = '未知'
            for k in KEYS:
                if (cur and k in cur) or k in s:
                    key = k; break
            grp[key] = grp.get(key, 0) + 1
    return grp

def main():
    args = sys.argv[1:]
    docx_files = [a for a in args if a.lower().endswith('.docx')]
    md_files = [a for a in args if a.endswith('.md')]
    print('== 成品题块数/条目数（层级制恒等式） ==')
    total_c = total_e = 0
    for p in docx_files:
        q, e, hier, oldseq, probs = count成品(p)
        total_c += q
        total_e += e
        f_q, f_e = fn_counts(p)
        q_id = ('文件名题量 %s %s' % (f_q, 'PASS' if f_q == q else 'FAIL≠%d' % q)) if f_q is not None else '文件名无题量（清单件属正常）'
        e_id = ('文件名条数 %s %s' % (f_e, 'PASS' if f_e == e else 'FAIL≠%d' % e)) if f_e is not None else '文件名无条数'
        print('  %s : 题 %d｜条目 %d｜%s｜%s' % (os.path.basename(p), q, e, q_id, e_id))
        if hier:
            fams = {}
            for (fam, sec), seq in hier.items():
                fams.setdefault(fam, []).append('节%s:%d..%d(%d)' % (sec, seq[0], seq[-1], len(seq)))
            for fam, lst in fams.items():
                print('    [%s族·层级制] %s' % (fam, '；'.join(sorted(lst))))
            print('    层级制核验: %s' % ('节内连续无重复 全过' if not probs else '；'.join(probs[:8])))
        elif oldseq:
            nums = [o for o, fam in oldseq if fam == '题']
            cont = [nums[k] for k in range(1, len(nums)) if nums[k] != nums[k-1] + 1]
            print('    [旧全局号] 题 %d..%d 连续性: %s' % (nums[0] if nums else 0, nums[-1] if nums else 0,
                                                           '连续' if not cont else '断点%s' % cont[:5]))
        # A''：题型统计段恒等核验（§7⑦/§7排版①）
        try:
            gstats, sstats, gprobs = count统计段(p)
            if gstats:
                gs = sum(n for _t, n in gstats)
                print('    [题型统计段] %d组 Σ%d题 %s%s' % (
                    len(gstats), gs, 'PASS' if gs == q and not gprobs else 'CHECK',
                    '' if not gprobs else '（' + '；'.join(gprobs[:4]) + '）'))
            if sstats:
                ss = sum(sstats)
                print('    [节标题统计段] 本节N题行%d行 Σ%d %s' % (
                    len(sstats), ss, 'PASS' if ss == q else 'FAIL≠题量%d' % q))
        except Exception as ex:
            print('    [题型统计段] 核验异常: %s' % ex)
    print('  合计: 题 %d｜条目 %d' % (total_c, total_e))
    if md_files:
        t, secs = count台账行(md_files[0])
        print('== 题目台账（%s）数据行合计: %d ==' % (os.path.basename(md_files[0]), t))
        for k, v in secs.items():
            print('  [%s] %d' % (k, v))
    if len(md_files) > 1:
        t2, _ = count台账行(md_files[1])
        print('== 删除台账（%s）数据行合计: %d ==' % (os.path.basename(md_files[1]), t2))
        for k, v in sorted(count删除原因(md_files[1]).items(), key=lambda x: -x[1]):
            print('  [%s] %d' % (k, v))
    print('== 提示 ==')
    print('  常用核对：成品题数 ≟ 题目台账行数−删除台账行数（本轮基线口径）；'
          '层级制件＝各节内序列连续无重复＋全件总数＝文件名题量/条目数（§7⑦）；'
          '各线恒等式公式以总控为准，本输出只提供计数。')

if __name__ == '__main__':
    main()
