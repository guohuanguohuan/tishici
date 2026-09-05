# -*- coding: utf-8 -*-
"""②C_文本守恒.py — T6 三连共用的守恒断言工具（T6 只动属性不动文本）。

提供：
  snap(path)        → 逐段文本快照（body 文档序全部 w:p 的 w:t 串接）＋全文字符数＋
                      非 document.xml 部件逐件字节 MD5（证 T6 只改 word/document.xml）
  norm(s)           → 去空白归一化（含全角空格/制表/换行）
  compare(a, b)     → (strict_pass, norm_pass, diff_detail)
                      strict＝逐段字面全等；norm＝去空白归一化逐段零差异
用法（作为模块导入）：
  import ②C_文本守恒 as G   # 文件名含全角字符，用 importlib 载入见 ②C_02_T6a_exec.py
"""
import re, zipfile, hashlib, io, sys
from lxml import etree

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)

WS_RE = re.compile(r'[\s\u3000\u00a0\u200b\ufeff]+')


def norm(s):
    return WS_RE.sub('', s or '')


def snap(path):
    """返回 dict：paras＝逐段文本 list；chars＝全文字符数；others＝非 document.xml 部件 {名: md5}；
    docxml_md5＝word/document.xml 的 md5（改动指纹，不参与守恒判定）。"""
    z = zipfile.ZipFile(path)
    try:
        names = z.namelist()
        doc = etree.fromstring(z.read('word/document.xml'))
        others = {}
        for n in names:
            if n == 'word/document.xml':
                continue
            others[n] = hashlib.md5(z.read(n)).hexdigest()
        docxml_md5 = hashlib.md5(z.read('word/document.xml')).hexdigest()
    finally:
        z.close()
    paras = []
    for p in doc.iter(q('p')):
        paras.append(''.join(t.text or '' for t in p.iter(q('t'))))
    return {'paras': paras, 'chars': sum(len(x) for x in paras),
            'others': others, 'docxml_md5': docxml_md5,
            'nparts': len(names)}


def compare(a, b):
    """守恒判定：逐段文本 strict 全等＋去空白归一化零差异＋非 document.xml 部件全等。"""
    det = []
    pa, pb = a['paras'], b['paras']
    strict = True
    if len(pa) != len(pb):
        strict = False
        det.append('段落数变动 %d→%d' % (len(pa), len(pb)))
    ndiff_strict = 0
    ndiff_norm = 0
    for i in range(min(len(pa), len(pb))):
        if pa[i] != pb[i]:
            ndiff_strict += 1
            if norm(pa[i]) != norm(pb[i]):
                ndiff_norm += 1
                if len(det) < 12:
                    det.append('段%d 归一化差异: %r -> %r' % (i, pa[i][:60], pb[i][:60]))
            elif len(det) < 12:
                det.append('段%d 仅空白差异: %r -> %r' % (i, pa[i][:60], pb[i][:60]))
    if ndiff_strict:
        strict = False
    normok = (ndiff_norm == 0) and (len(pa) == len(pb))
    if a['chars'] != b['chars']:
        det.append('全文字符数变动 %d→%d' % (a['chars'], b['chars']))
        normok = False
    ok_oth = (a['others'] == b['others'])
    if not ok_oth:
        ka, kb = set(a['others']), set(b['others'])
        det.append('非 document.xml 部件变动：增%s 减%s 改%s'
                   % (sorted(kb - ka)[:3], sorted(ka - kb)[:3],
                      sorted(k for k in ka & kb if a['others'][k] != b['others'][k])[:3]))
    return {'strict': strict and ok_oth, 'norm': normok and ok_oth,
            'ndiff_strict': ndiff_strict, 'ndiff_norm': ndiff_norm,
            'others_same': ok_oth, 'detail': det,
            'docxml_changed': a['docxml_md5'] != b['docxml_md5']}
