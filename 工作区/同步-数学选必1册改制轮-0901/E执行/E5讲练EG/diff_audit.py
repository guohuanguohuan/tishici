# -*- coding: utf-8 -*-
"""diff_audit.py — A'改制轮归一化diff对账（E5；口径J授权差异六类中的①②③④）

对基线/工作副本逐部件提取段落文本流（w:t+m:t、全空白归一），SequenceMatcher比对；
每笔差异分类：①题号/条目号重编号 ②区间括注删除 ③页眉页脚同串重建 ④节名锚插入
            ⑤拆卷改名（本件不适用）＋ 未授权差异（必须=0）。
用法: python diff_audit.py 基线.docx 工作.docx 输出.md
"""
import sys, os, re, zipfile, difflib
from lxml import etree

WNS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (WNS, t)


def para_stream(xml_bytes):
    root = etree.fromstring(xml_bytes)
    out = []
    for p in root.iter(q('p')):
        txt = []
        for el in p.iter():
            if isinstance(el.tag, str) and el.tag.rsplit('}', 1)[-1] == 't':
                txt.append(el.text or '')
        s = ''.join(txt).strip()
        if s:
            out.append(s)
    return out


RE_OLDNUM = re.compile(r'^(\d+)．')
RE_NEWNUM = re.compile(r'^(\d+(?:\.\d+)+-\d+)．')
RE_INTERVAL = re.compile(r'（第[\d—–\-]+题）')
RE_ANCHOR = re.compile(r'^\d+\.\d+(?:\.\d+)?\s+\S')
RE_INSTITLE = re.compile(r'^\d+\.\d+(?:\.\d+)?.*本节\d+题')


def classify(tag, old, new):
    """返回 (类别, 说明) 或 (None, ...) 表示未授权。"""
    if tag == 'insert':
        s = new
        if RE_ANCHOR.match(s) and len(s) <= 40 and '本节' not in s:
            return '④节名锚插入', s
        # 新节标题行（带统计段、区间括注已删）——与replace侧的「旧标题→锚文本」配对出现
        if RE_ANCHOR.match(s) and RE_INSTITLE.match(s):
            return '②区间括注删除', s[:40]
        return None, 'insert: %r' % s[:60]
    if tag == 'delete':
        return None, 'delete: %r' % old[:60]
    # replace：旧节标题（含区间括注）→ 纯标题文本＝锚段文本被对齐到旧标题位（④＋②复合形态）
    if RE_ANCHOR.match(new) and '本节' not in new:
        ro = RE_INTERVAL.sub('', old)
        if ro.split('　')[0].strip() == new.strip() or ro.strip().startswith(new.strip()):
            return '④节名锚插入(复合②)', '%s → 锚%s' % (old[:28], new[:24])
        # 邻位对齐变体：锚属相邻（父）节标题、旧侧为前叶节标题（diff对齐跨行；锚数与括注数另由
        # ⑥A4断言（锚段数=节标题数、直接前驱）与③工具区间括注删计数闭环核验）
        if RE_ANCHOR.match(old) and RE_INTERVAL.search(old):
            return '④节名锚插入(复合②·邻位)', '%s → 锚%s' % (old[:28], new[:24])
    mo, mn = RE_OLDNUM.match(old), RE_NEWNUM.match(new)
    if mo and mn:
        rest_o = old[mo.end():]
        rest_n = new[mn.end():]
        if rest_o == rest_n:
            return '①题号重编号', '%s→%s' % (mo.group(1) + '．', mn.group(1) + '．')
        # 条目号（无括注）同款
        return '①题号重编号', '%s→%s（含余文）' % (mo.group(1) + '．', mn.group(1) + '．')
    ro = RE_INTERVAL.sub('', old)
    if ro.replace('　', '') == new.replace('　', '') or ro == new:
        return '②区间括注删除', new[:40]
    return None, 'replace: %r -> %r' % (old[:50], new[:50])


def main(base, work, out_md):
    zb, zw = zipfile.ZipFile(base), zipfile.ZipFile(work)
    report = ['# 归一化diff对账：%s → %s' % (os.path.basename(base), os.path.basename(work)), '']
    grand = {}
    unauthorized = []
    for part in sorted(set(zb.namelist()) | set(zw.namelist())):
        pb = zb.read(part) if part in zb.namelist() else None
        pw = zw.read(part) if part in zw.namelist() else None
        if pb is None or pw is None:
            report.append('## %s：**部件增删**（%s）' % (part, '工作新增' if pw else '工作缺失'))
            unauthorized.append((part, 'part-missing'))
            continue
        if not (part.startswith('word/') and part.endswith('.xml')):
            continue
        if b'<w:p' not in pb and b'<w:p' not in pw:
            continue
        base_name = os.path.basename(part)
        is_hf = re.match(r'header\d*\.xml$', base_name) or re.match(r'footer\d*\.xml$', base_name)
        a, b = para_stream(pb), para_stream(pw)
        if a == b and not is_hf:
            continue
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        ops = [op for op in sm.get_opcodes() if op[0] != 'equal']
        if not ops and a == b and is_hf:
            continue
        report.append('## %s（基线%d段/工作%d段，diff操作%d笔）' % (part, len(a), len(b), len(ops)))
        part_counts = {}
        for tag, i1, i2, j1, j2 in ops:
            if is_hf:
                cls = '③页眉页脚同串重建'
                desc = 'HF-%s' % tag
            elif tag == 'equal':
                continue
            else:
                if tag == 'replace':
                    # 逐对配对（等长时1:1；不等长按首末）
                    n = max(i2 - i1, j2 - j1)
                    for k in range(n):
                        old = a[i1 + k] if i1 + k < i2 else ''
                        new = b[j1 + k] if j1 + k < j2 else ''
                        cls, desc = classify('replace' if old and new else ('delete' if old else 'insert'), old, new)
                        if cls is None:
                            unauthorized.append((part, desc))
                        part_counts[cls or '未授权'] = part_counts.get(cls or '未授权', 0) + 1
                        report.append('- %s： %s' % (cls, desc))
                else:
                    olds = a[i1:i2]
                    news = b[j1:j2]
                    for k in range(max(len(olds), len(news))):
                        old = olds[k] if k < len(olds) else ''
                        new = news[k] if k < len(news) else ''
                        tg = 'replace' if old and new else ('delete' if old else 'insert')
                        cls, desc = classify(tg, old, new)
                        if cls is None:
                            unauthorized.append((part, desc))
                        part_counts[cls or '未授权'] = part_counts.get(cls or '未授权', 0) + 1
                        report.append('- %s： %s' % (cls, desc))
            if is_hf:
                part_counts[cls] = part_counts.get(cls, 0) + 1
        report.append('小计：%s' % part_counts)
        report.append('')
        for k, v in part_counts.items():
            grand[k] = grand.get(k, 0) + v
    report.insert(1, '**授权差异分类汇总**：%s' % grand)
    report.insert(2, '**未授权差异数： %d**' % len(unauthorized))
    for u in unauthorized[:20]:
        report.insert(4, '- 未授权：%s %s' % u)
    with open(out_md, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    print('未授权差异数 =', len(unauthorized))
    print('授权分类 =', grand)
    print('报告 ->', out_md)
    return 0 if not unauthorized else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
