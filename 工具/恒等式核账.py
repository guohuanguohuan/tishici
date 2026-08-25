# -*- coding: utf-8 -*-
"""恒等式核账.py — 机械计数辅助：成品题块数 / 题目台账行数 / 删除台账行数 三方对账底稿
用法: python 恒等式核账.py <成品docx...> <题目台账.md> [删除台账.md]
只做机械计数与差异提示；恒等式的公式与判定按所在总控由会话完成（同步线§2.3/§6②、二轮§2 等），
本脚本不替代判定，只替代数数。"""
import sys, os
from dump_docx import body_elements, QNUM_RE, QNUM_MINLEN

def count成品(path):
    """题块＝全角「N．」起始且块内含【答案】（讲部分内部「1．xxx」编号条目不计，经验口径）。"""
    els = body_elements(path)
    starts = [i for i, tag, text in els
              if tag == 'p' and text and len(text.strip()) >= QNUM_MINLEN and QNUM_RE.match(text.strip())]
    n = 0
    for k, i in enumerate(starts):
        j = starts[k+1] - 1 if k + 1 < len(starts) else els[-1][0]
        block = '\n'.join(t for ii, tag, t in els if i <= ii <= j and t is not None)
        if '【答案】' in block:
            n += 1
    return n

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
    print('== 成品题块数 ==')
    total_c = 0
    for p in docx_files:
        c = count成品(p)
        total_c += c
        print('  %s : %d' % (os.path.basename(p), c))
    print('  合计: %d' % total_c)
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
          '各线恒等式公式以总控为准，本输出只提供计数。')

if __name__ == '__main__':
    main()
