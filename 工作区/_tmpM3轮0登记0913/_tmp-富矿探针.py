# -*- coding: utf-8 -*-
"""富矿开卷探针：大单元作业设计 docx 逐件结构探查（题号/分节/难度/答案/图/字节）。
只读源文件，输出紧凑摘要到 stdout。复用 dump_docx.py 的段落提取思路。"""
import re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'

def tagof(el):
    return el.tag.split('}')[-1]

def para_text(p_el):
    parts = []
    def walk(el):
        for c in el:
            ct = tagof(c)
            if ct == 't' and c.tag.startswith(W):
                parts.append(c.text or '')
            elif ct in ('drawing', 'pict', 'object'):
                parts.append('【图】')
            else:
                walk(c)
    walk(p_el)
    return ''.join(parts)

SEC_RE = re.compile(r'^[一二三四五六七八九十]{1,3}\s*、')
QNUM_RE = re.compile(r'^(\d{1,3})\s*[．.、]\s*')
COEF_RE = re.compile(r'【难度】\s*([01](?:\.\d+)?)')

def census(path):
    doc = Document(path)
    # 全文档 w:p（含表格内），按文档顺序
    texts = [t for t in (para_text(p) for p in doc.element.body.iter(W + 'p')) if t.strip()]
    secs = [t.strip() for t in texts if SEC_RE.match(t.strip()) and len(t.strip()) < 30]
    qnums = []
    for t in texts:
        m = QNUM_RE.match(t.strip())
        if m and len(t.strip()) >= 8:
            qnums.append(int(m.group(1)))
    coefs = [float(m.group(1)) for t in texts for m in [COEF_RE.search(t)] if m]
    n_ans = sum(1 for t in texts if t.strip().startswith('【答案】') or t.strip().startswith('【解析】'))
    imgs = sum(t.count('【图】') for t in texts)
    # 题号序列：找最大连续递增段（区分正文卷与答案卷的重复编号）
    seqs = []
    cur = []
    for n in qnums:
        if cur and n == cur[-1] + 1:
            cur.append(n)
        elif cur and n == cur[-1]:
            continue
        else:
            if cur: seqs.append(cur)
            cur = [n]
    if cur: seqs.append(cur)
    seqs.sort(key=len, reverse=True)
    top = seqs[0] if seqs else []
    n_1 = sum(1 for n in qnums if n == 1)
    return dict(
        paras=len(texts), secs=secs[:12], qmark=len(qnums),
        maxlen=top[-1] if top else 0, maxrun=len(top),
        n_start1=n_1, n_ans=n_ans, imgs=imgs,
        n_coef=len(coefs), coef_avg=(sum(coefs)/len(coefs)) if coefs else None,
        coef_min=min(coefs) if coefs else None, coef_max=max(coefs) if coefs else None,
        size=os.path.getsize(path),
    )

if __name__ == '__main__':
    for p in sys.argv[1:]:
        try:
            r = census(p)
        except Exception as e:
            print('FAIL\t%s\t%s' % (os.path.basename(p), str(e)[:60]))
            continue
        print('== %s' % os.path.basename(p))
        ca = ('%.2f' % r['coef_avg']) if r['coef_avg'] is not None else '-'
        print('   段=%d 题号标记=%d 起始1×%d 最长连续段=%d(末号%d) 答案解析块=%d 图=%d 难度系数=%d个(均%s 域%s~%s) 字节=%d' % (
            r['paras'], r['qmark'], r['n_start1'], r['maxrun'], r['maxlen'], r['n_ans'], r['imgs'],
            r['n_coef'], ca, r['coef_min'], r['coef_max'], r['size']))
        print('   分节: %s' % ' | '.join(r['secs']))
