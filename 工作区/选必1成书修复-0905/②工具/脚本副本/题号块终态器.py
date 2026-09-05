# -*- coding: utf-8 -*-
r"""题号块终态器.py — 2026-09-05 选必1成书修复路线·版式修订轮②·T1（工具先建后用）

口径（2026-09-05 用户拍板版式新规则；规格书T1）：
  讲练件题号块括注各现行形态 → 终态「（简单）／（中档）／（难）」；
  衔接件「（衔接必会·卡壳看答案）」→「（衔接必会）」。
  实测现行形态（选必1十件）：「（简单·保60%·卡壳看答案）」「（中档·保80%·卡壳看答案）」
  「（难·冲100%·卡壳看答案）」「（衔接必会·卡壳看答案）」，及 T2 提分线迁移器 剥离后的
  中间形「（简单·卡壳看答案）」等；映射规则＝括注以档位词起头即归并为该档位终态单词。
  未识别括注形态不猜写，登记异常清单交人工。

识别：段首「题型号-序号．（括注）」（NUM．（…））；知识清单件无题号块（放行0命中登记）。
断言：改写题号块数＋幂等跳过数＝该件题数（文件名括注（N题）；衔接件同）。
      文字流除授权括注改写外零变更（逐段期望文本比对）；元素计数仅 w:t 文本变化。
模式：
  默认        就地改写（自动留 .bak_题号终态，已存在不覆盖）
  --dry-run   全形态枚举＋改写映射表＋逐件计数预演，不落盘
报告：--report <txt/md> 落盘（可多次调用追加；缺省仅 stdout）。
用法:
  python 工具/题号块终态器.py <docx...> [--dry-run] [--report r.md]
"""
import sys, io, os, re, zipfile, time
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
def q(t): return '{%s}%s' % (W, t)
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))

NUM = r'(?:\d+(?:\.\d+)+-\d+|\d+)'
QBRACKET_RE = re.compile(r'^(%s)．（([^】）]*)）' % NUM)
GRADES = ('简单', '中档', '难', '衔接必会')
FN_Q_RE = re.compile(r'（(\d+)题')


def wt_nodes(p):
    return [t for t in p.iter(q('t'))]


def set_span(p, a, b, newtext):
    """段内 w:t 文本流 [a,b) 区间替换为 newtext（首触 w:t 承接全文，区间内其余清空）。"""
    off = 0
    done = False
    for t in wt_nodes(p):
        txt = t.text or ''
        ta, tb = off, off + len(txt)
        off = tb
        if tb <= a or ta >= b:
            continue
        cs, ce = max(a - ta, 0), min(b - ta, len(txt))
        if not done:
            t.text = txt[:cs] + newtext + txt[ce:]
            done = True
        else:
            t.text = txt[:cs] + txt[ce:]
        t.set(XMLSPACE, 'preserve')
    assert done, 'set_span 区间未触任何 w:t'


def terminal_of(content):
    """括注内容 → 终态档位词；已终态返回原词；未识别返回 None。"""
    for g in GRADES:
        if content == g:
            return g
    for g in GRADES:
        if content.startswith(g + '·') or content.startswith(g):
            return g
    return None


def process(path, dry):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))

    fn_m = FN_Q_RE.search(os.path.basename(path))
    fn_q = int(fn_m.group(1)) if fn_m else None

    forms = {}          # 括注原形态 → 计数
    mapping = {}        # 原形态 → 终态形态
    anomalies = []
    n_rewrite = n_keep = 0
    rewrites = []       # (号, 前, 后)

    for p in body.iter(q('p')):
        txt = ptext(p)
        m = QBRACKET_RE.match(txt)
        if not m:
            continue
        content = m.group(2)
        forms[content] = forms.get(content, 0) + 1
        tgt = terminal_of(content)
        if tgt is None:
            anomalies.append('未识别括注形态（跳过）: 段首 %s' % txt[:48])
            continue
        new_bracket = '（%s）' % tgt
        old_bracket = '（%s）' % content
        mapping[content] = tgt
        if content == tgt:
            n_keep += 1
            continue
        before = ptext(p)
        set_span(p, len(m.group(1)) + 1, m.end(), new_bracket)   # 「N．」长＝号+全角句点
        exp = before[:len(m.group(1)) + 1] + new_bracket + before[m.end():]
        assert ptext(p) == exp, '改写后文本不符: %r' % ptext(p)[:60]
        n_rewrite += 1
        rewrites.append((m.group(1), old_bracket, new_bracket))

    total = sum(forms.values())
    assert_msg = ''
    if fn_q is not None:
        if total != fn_q:
            raise AssertionError('题号块认定 %d ≠ 文件名题数 %d（%s）——漏认/多认，终止'
                                 % (total, fn_q, os.path.basename(path)))
        assert_msg = '题数恒等 %d＝文件名%d PASS' % (total, fn_q)
    else:
        assert_msg = '文件名无题数括注（知识清单/配页面），认定题号块 %d 处' % total

    lines = []
    lines.append('## T1 题号块终态器 — %s%s' % (os.path.basename(path), '（dry-run）' if dry else ''))
    lines.append('形态枚举：' + ('；'.join('「%s」×%d' % (k, v) for k, v in sorted(forms.items(), key=lambda x: -x[1])) or '（无题号块）'))
    lines.append('映射表：' + ('；'.join('「%s」→「%s」' % (k, mapping[k]) for k in sorted(mapping)) or '—'))
    lines.append('改写 %d｜幂等跳过 %d｜异常 %d｜%s' % (n_rewrite, n_keep, len(anomalies), assert_msg))
    for a in anomalies[:20]:
        lines.append('  ! ' + a)
    if dry and rewrites:
        lines.append('样例（前5）：' + '；'.join('%s %s→%s' % r for r in rewrites[:5]))
    lines.append('')

    if not dry and n_rewrite:
        bak = path + '.bak_题号终态'
        if not os.path.exists(bak):
            import shutil
            shutil.copy2(path, bak)
        new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
        tmp = path + '.t1tmp'
        with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = new_xml if item.filename == 'word/document.xml' else zin.read(item.filename)
                zout.writestr(item, data)
        for k in range(12):
            try:
                os.replace(tmp, path)
                break
            except PermissionError:
                time.sleep(6)
        else:
            raise RuntimeError('locked: ' + path)
    return '\n'.join(lines)


def main():
    argv = sys.argv[1:]
    dry = '--dry-run' in argv
    argv = [a for a in argv if a != '--dry-run']
    report = None
    if '--report' in argv:
        k = argv.index('--report'); report = argv[k + 1]; del argv[k:k + 2]
    assert argv, '用法: python 工具/题号块终态器.py <docx...> [--dry-run] [--report r.md]'
    out = []
    for path in argv:
        r = process(path, dry)
        out.append(r)
        print(r)
    if report:
        with open(report, 'a', encoding='utf-8') as f:
            f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
