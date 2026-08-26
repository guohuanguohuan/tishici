# -*- coding: utf-8 -*-
"""空位公式扫描：检测「行内公式掉位堆积」缺陷（2026-08-26 欧拉线题缺陷家族）。

缺陷签名（交错流层面，非纯文本层面）：
  1) 双逗空位——段落线性化（文字＋⟦公式⟧交错）中出现两个全角逗号相邻、中间无任何公式，
     说明该处本应内联的公式不在句中（多半被堆积到段尾）；
  2) 段尾公式簇——段落以 ≥2 个 oMath 结尾且其前的文字段以「（ ）」等收尾。
签名 1 是主判据（对「a，b，」这类两公式夹一逗号的正确内联不误报——它们之间有 ⟦⟧）。
命中＝红旗，必须定位核验（对照源文件交错顺序），禁止以「扫描误报」为由放过。

用法：python 空位公式扫描.py <docx> [docx ...]
     （扫描全部成品时可直接递归传入；本工具只读不改。）
"""
import sys
import zipfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'


def paragraph_seq(p):
    """段落交错序列 [(kind, text)]，kind='t' 文字 / 'm' 公式线性化。"""
    seq = []
    for child in p.iter():
        qn = etree.QName(child)
        if qn.namespace == W and qn.localname == 't' and child.text:
            seq.append(('t', child.text))
        elif qn.namespace == M and qn.localname == 'oMath':
            lin = ''.join(t.text or '' for t in child.iter(f'{{{M}}}t'))
            seq.append(('m', lin))
    return seq


def scan_file(path):
    with zipfile.ZipFile(path) as z:
        root = etree.fromstring(z.read('word/document.xml'))
    hits = []
    for pi, p in enumerate(root.iter(f'{{{W}}}p')):
        seq = paragraph_seq(p)
        if not any(k == 'm' for k, _ in seq):
            continue
        joined = ''.join(f'⟦{s}⟧' if k == 'm' else s for k, s in seq)
        # 签名1：双逗空位（两全角逗号之间只有空白、没有公式）
        if '，，' in joined.replace('， ,', '，，') and any(
                seg.strip('，, ') == '' or True for seg in [joined]):
            import re
            if re.search(r'，[^\S⟦]{0,4}，', joined):
                hits.append((pi, '双逗空位', joined))
                continue
        # 签名2：段尾公式簇（≥2 个公式收尾且文字以（ ）类收束）——弱签名，仅供人工复核
        j = len(seq) - 1
        while j >= 0 and seq[j][0] == 'm':
            j -= 1
        cluster = sum(1 for k, _ in seq[j + 1:] if k == 'm')
        tail_text = seq[j][1] if j >= 0 and seq[j][0] == 't' else ''
        if cluster >= 2 and tail_text.rstrip().endswith(('）', ')')):
            hits.append((pi, '段尾公式簇', joined))
    return hits


def main():
    out = sys.stdout
    total = 0
    for path in sys.argv[1:]:
        try:
            hits = scan_file(path)
        except Exception as e:
            print(f'ERR {path}: {e}', file=out)
            continue
        for pi, kind, joined in hits:
            total += 1
            print(f'{kind} | {path} | p#{pi} | {joined[:200]}', file=out)
    print(f'TOTAL {total}', file=out)


if __name__ == '__main__':
    main()
