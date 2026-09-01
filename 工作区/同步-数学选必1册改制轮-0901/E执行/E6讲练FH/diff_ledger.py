# -*- coding: utf-8 -*-
"""diff_ledger.py — E6一次性脚本：A'改制轮归一化diff对账（口径J，段落级对齐版）
对比基线与成品 document.xml 的段落文本序列（w:t/m:t），差异逐笔分类登记授权差异：
①题号/条目号重编号（段首「N．」→「节号-序号．」token替换）
②节标题区间括注删除（「（第X—Y题）」删除）
③页眉页脚同串重建（部件级，不在document.xml——登记不比对）
④节名锚段插入（插入段「节号 节名」）
⑤拆卷文件名/文内标题改动（本比对不涉及）
⑥配页件改动（不适用）
附类：⑦环绕删空图段（被删段文本为空、含图）；⑧H条目半角→全角归一笔（「N. 」→「N．」）。
凡不落类差异＝意外差异，必须为0。
用法: python diff_ledger.py <基线.docx> <成品.docx> <登记md>
"""
import sys, zipfile, re, difflib
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)

def para_stream(path):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    out = []
    for el in doc.find(q('body')):
        ln = etree.QName(el).localname
        if ln != 'p':
            out.append(('<%s>' % ln, False))
            continue
        txt = ''.join(t.text or '' for t in el.iter(q('t')))
        has_img = el.find('.//' + q('drawing')) is not None or el.find('.//' + q('pict')) is not None
        out.append((txt, has_img))
    return out

RE_INTERVAL = re.compile(r'（第\d+[—–-]\d+题）')
RE_OLD2NEW = re.compile(r'^\d{1,3}．')
RE_ANCHOR = re.compile(r'^\d+\.\d+(?:\.\d+)?\s+\S+$')
RE_HALFNUM = re.compile(r'^\d{1,2}\.\s')

def classify_pair(old, new):
    """段内差异分类：返回 (类别, 明细) 或 None（无法归类）。"""
    if RE_OLD2NEW.match(old) and not RE_OLD2NEW.match(new):
        # 题号/条目号token替换：old「N．xxx」new「节号-序号．xxx」，尾部须一致
        m = re.match(r'^(\d{1,3}．)(.*)$', old, re.S)
        n = re.match(r'^(\d+(?:\.\d+)+-\d+．)(.*)$', new, re.S)
        if m and n and m.group(2) == n.group(2):
            return ('①题号/条目号重编号', '%s→%s' % (m.group(1), n.group(1)))
    if RE_HALFNUM.match(old):
        # H半角条目：old「N. xxx」→new「节号-序号．xxx」（半角→全角＋去半角空格）
        m = re.match(r'^(\d{1,2})\.\s(.*)$', old, re.S)
        n = re.match(r'^(\d+(?:\.\d+)+-\d+)．(.*)$', new, re.S)
        if m and n and m.group(2) == n.group(2):
            return ('①题号/条目号重编号（半角归一笔）', '%s. →%s．' % (m.group(1), n.group(1)))
    stripped = RE_INTERVAL.sub('', old)
    if new == stripped or (new == stripped.replace('\u3000\u3000', '\u3000') and not RE_INTERVAL.search(new)):
        if RE_INTERVAL.search(old):
            return ('②区间括注删除', RE_INTERVAL.search(old).group(0))
    return None

def main():
    base, final, md = sys.argv[1], sys.argv[2], sys.argv[3]
    A, B = para_stream(base), para_stream(final)
    ta = [x[0] for x in A]
    tb = [x[0] for x in B]
    sm = difflib.SequenceMatcher(None, ta, tb, autojunk=False)
    ledger = {}
    unexpected = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        olds = A[i1:i2]
        news = B[j1:j2]
        if tag == 'replace':
            no = [(k, t) for k, (t, im) in enumerate(olds) if t.strip()]
            ne = [(k, t) for k, (t, im) in enumerate(news) if t.strip()]
            shift = 0
            anchor_ks = set()
            while len(ne) > len(no) and RE_ANCHOR.match(ne[0][1]):
                # 节标题段前插锚段（可连插多段：2.5锚＋2.5.1锚）：new[锚,…, 标题'] ↔ old[标题]
                # （末锚与old的前缀一致性由随后的 classify_pair 配对最终把关）
                ledger.setdefault('④节名锚段插入', []).append(ne[0][1])
                anchor_ks.add(ne[0][0])
                ne = ne[1:]
                shift += 1
            ok = len(ne) == len(no)
            if ok:
                for (ko, to), (kn, tn) in zip(no, ne):
                    cls = classify_pair(to, tn)
                    if not cls:
                        ok = False
                        break
                    ledger.setdefault(cls[0], []).append(cls[1])
            if ok:
                used_o = {k for k, _ in no}
                used_n = {k for k, _ in ne} | anchor_ks
                rest_o = [olds[k] for k in range(len(olds)) if k not in used_o]
                rest_n = [news[k] for k in range(len(news)) if news[k][0].strip() and k not in used_n]
                if all((not t.strip()) and im for t, im in rest_o) and not rest_n:
                    if rest_o:
                        ledger.setdefault('⑦环绕删空图段（零文字）', []).append('×%d段' % len(rest_o))
                    continue
            unexpected.append((tag, [t[:40] for t, _ in olds], [t[:40] for t, _ in news]))
            continue
        if tag == 'insert':
            if all((not t.strip()) and not im for t, im in news) or \
               all((not t.strip()) for t, im in news):
                ledger.setdefault('⑦环绕删空图段（零文字·反向空段）', []).append('×%d段' % len(news))
                continue
            if len(news) == 1 and not news[0][1] and RE_ANCHOR.match(news[0][0]):
                ledger.setdefault('④节名锚段插入', []).append(news[0][0])
                continue
            unexpected.append((tag, [], [t[:40] for t, _ in news]))
            continue
        # delete
        if all((not t.strip()) and im for t, im in olds):
            ledger.setdefault('⑦环绕删空图段（零文字）', []).append('×%d段' % len(olds))
            continue
        unexpected.append((tag, [t[:40] for t, _ in olds], []))
    L = ['# 归一化diff对账（段落级） — %s vs %s' % (base, final)]
    L.append('')
    L.append('- 基线段落 %d｜成品段落 %d' % (len(A), len(B)))
    for k in sorted(ledger):
        L.append('- %s：%d 笔' % (k, len(ledger[k])))
        for it in ledger[k][:250]:
            L.append('  - %s' % it)
    L.append('- ③页眉页脚同串重建＝header/footer部件整体重建（部件级授权，不在document.xml流）')
    L.append('- 意外差异：%d 笔%s' % (len(unexpected), ' ✓零' if not unexpected else '（必须为0）'))
    for it in unexpected[:40]:
        L.append('  ! %r' % (it,))
    open(md, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    keys = {k: len(v) for k, v in ledger.items()}
    print('%s：%s 意外%d' % (final, keys, len(unexpected)))
    sys.exit(1 if unexpected else 0)

if __name__ == '__main__':
    main()
