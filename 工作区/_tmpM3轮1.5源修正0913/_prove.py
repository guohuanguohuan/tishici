# -*- coding: utf-8 -*-
"""精确重构证明：修前流按「指定子串整段删除/单字符替换」= 修后流（逐字节相等）"""
import sys
sys.path.insert(0, '工具')
from dxml import Document, qn
W, M = qn('w:t'), qn('m:t')

def stream(p):
    d = Document(p)
    return ''.join((n.text or '') for n in d.element.body.iter() if n.tag in (W, M))

D = sys.argv[1]; S = sys.argv[2]

# --- 卷④：三次整段删除（按现文实际子串） ---
o = stream(D + '.bak_轮15源修正0913'); n = stream(D)
ops = [('，焦点弦情形Q落在准线', 1),
       ('其中，当 P 点为左 (右) 焦点时，Q 点位于左 (右) 准线上.（可用极点极线来求）', 1),
       ('其中，当 P 点为左 (右) 焦点时，Q 点位于左 (右) 准线上.', 1)]
cur = o
for pat, exp in ops:
    c = cur.count(pat)
    assert c >= exp, 'D 模式命中不足 %r -> %d' % (pat[:12], c)
    cur = cur.replace(pat, '', 1) if False else cur
    print('D 模式 %r 在修前流命中 %d 处' % (pat[:16] + '…', o.count(pat)))
# 逐条按序删一次
cur = o
for pat, _ in ops:
    i = cur.find(pat)
    assert i >= 0
    cur = cur[:i] + cur[i + len(pat):]
print('D 重构==现流 ?', cur == n, '（长度 %d vs %d）' % (len(cur), len(n)))

# --- 大招2源：本轮 C1 单字符替换（相对轮1.5修后态 = 上一轮留证转储） ---
so = stream(S + '.bak_轮15源修正0913'); sn = stream(S)
pat_old = '(a+2)/(a−1)'; pat_new = '(a+2)/(a−2)'
print('S 修前(原始备份) %r 命中 %d；现件 %r 命中 %d' % (pat_old, so.count(pat_old), pat_new, sn.count(pat_new)))
i = sn.find('得(x+2)/(y−2)=(a+2)/(a−2)')
print('S 现文片段=%r' % sn[i:i+60])
j = so.find('(a+2)/(a−1)')
print('S 备份件片段=%r' % so[j-20:j+50])
