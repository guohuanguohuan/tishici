# -*- coding: utf-8 -*-
r"""提分线迁移器.py — 2026-09-05 选必1成书修复路线·版式修订轮②·T2（工具先建后用）

口径（规格书T2）：从题号块括注剥离「提分线」（保60%/保80%/冲100%），迁至节级统计段末尾集中标注。
  实测（选必1十件 dry-run 结论）：提分线现行挂载形态＝讲练件逐题括注
  「（简单·保60%·卡壳看答案）」中的中段「·保60%」，档位↔提分线一一对应
  （简单→保60%、中档→保80%、难→冲100%）；衔接件括注「（衔接必会·卡壳看答案）」不含提分线；
  知识清单无题号块。故本器仅对讲练件生效，衔接件/清单件实测结论＝无提分线挂载，0 处置登记。
  节统计段追加串形（从简，规格书授权自定）：「　提分线：简单→保60%｜中档→保80%｜难→冲100%」，
  仅列本节实际出现的档位，档位按 简单→中档→难 序。
  题号块剥离后形态：「（中档·卡壳看答案）」（卡壳看答案的去除归 T1 题号块终态器）。

识别：节统计段＝节标题行内「　本节N题：…」（T3 拆分前）或节标题后紧跟的独立统计段
  「本节N题：…」（T3 拆分后）——两形兼容，幂等识别「提分线：」已挂跳过。
断言：剥离数＝含提分线括注题数（讲练件＝文件名题数）；追加节数＝有提分线题的节数；
      逐节断言：节内括注档位集合＝所挂提分线标注集合；零意外字符（逐段期望文本比对）。
模式：默认就地改写（留 .bak_提分线迁）；--dry-run 出分布报告不落盘。
用法:
  python 工具/提分线迁移器.py <docx...> [--dry-run] [--report r.md]
"""
import sys, io, os, re, zipfile, time
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
def q(t): return '{%s}%s' % (W, t)
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def pfill(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        return None
    sh = ppr.find(q('shd'))
    return sh.get(q('fill')) if sh is not None else None

NUM = r'(?:\d+(?:\.\d+)+-\d+|\d+)'
QBRACKET_RE = re.compile(r'^(%s)．（((?:简单|中档|难))·(保60%%|保80%%|冲100%%)(·卡壳看答案)?）' % NUM)
SEC_TTL_RE = re.compile(r'^(\d+\.\d+(?:\.\d+)?)[\s　]+\S')
SEC_STATS_RE = re.compile(r'　（?本节\d+题')          # 行内统计段起点（全角空格引导）
SEC_STATS_PARA_RE = re.compile(r'^本节\d+题')        # 独立统计段（T3 拆分后形态）
GRADE2LINE = {'简单': '保60%', '中档': '保80%', '难': '冲100%'}
GRADE_ORDER = ('简单', '中档', '难')
FN_Q_RE = re.compile(r'（(\d+)题')


def wt_nodes(p):
    return [t for t in p.iter(q('t'))]


def set_span(p, a, b, newtext):
    off = 0
    done = False
    for t in wt_nodes(p):
        txt = t.text or ''
        ta, tb = off, off + len(txt)
        off = tb
        if tb <= a or ta >= b:
            continue
        cs, ce = max(a - ta, 0), min(b - ta, len(txt))
        t.text = txt[:cs] + (newtext if not done else '') + txt[ce:]
        t.set(XMLSPACE, 'preserve')
        done = True
    assert done, 'set_span 区间未触任何 w:t'


def append_at_end(p, s):
    ts = wt_nodes(p)
    assert ts, '统计段无 w:t 可挂尾'
    t = ts[-1]
    t.text = (t.text or '') + s
    t.set(XMLSPACE, 'preserve')


def process(path, dry):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))
    els = list(body)

    fn_m = FN_Q_RE.search(os.path.basename(path))
    fn_q = int(fn_m.group(1)) if fn_m else None

    # ---- 节定位（节标题段＋行内/独立统计段挂点） ----
    # secs: [(节标题idx, 节号, 统计段所在idx或None, 是否已挂提分线)]
    secs = []
    for i, c in enumerate(els):
        if c.tag != q('p'):
            continue
        txt = ptext(c)
        if pfill(c) == 'ADC2DA' and SEC_TTL_RE.match(txt):
            m = re.match(r'^(\d+\.\d+(?:\.\d+)?)', txt)
            stat_idx = i if SEC_STATS_RE.search(txt) else None
            secs.append([i, m.group(1), stat_idx, False])
    # T3 后形态：节标题无行内统计段 → 看紧随其后是否独立统计段
    for k, (i, secno, stat_idx, _) in enumerate(secs):
        if stat_idx is not None:
            continue
        for j in range(i + 1, min(i + 3, len(els))):
            if els[j].tag != q('p'):
                break
            tj = ptext(els[j])
            if not tj.strip():
                continue
            if SEC_STATS_PARA_RE.match(tj.strip()):
                secs[k][2] = j
            break

    # ---- 扫描题号块：剥离提分线，逐节记档位 ----
    sec_grades = {}     # 节idx → set(档位)
    n_strip = 0
    cur_sec = None
    anomalies = []
    for i, c in enumerate(els):
        if c.tag != q('p'):
            continue
        txt = ptext(c)
        for k, (si, secno, _st, _f) in enumerate(secs):
            if si == i:
                cur_sec = si
                break
        m = QBRACKET_RE.match(txt)
        if not m:
            continue
        grade = m.group(2)
        if cur_sec is None:
            anomalies.append('题 %s 位于首节标题之前，提分线无节可挂（仍剥离）' % m.group(1))
        else:
            sec_grades.setdefault(cur_sec, set()).add(grade)
        # 剥离「·提分线」段
        line_tok = '·' + m.group(3)
        s = txt.find(line_tok, m.start(2))
        e = s + len(line_tok)
        before = ptext(c)
        set_span(c, s, e, '')
        assert ptext(c) == before[:s] + before[e:], '剥离后文本不符: %r' % ptext(c)[:60]
        n_strip += 1

    # ---- 节统计段末尾追加提分线标注 ----
    n_append = n_skip_hung = 0
    appended = []       # (节号, 标注)
    for si, secno, stat_idx, _f in secs:
        grades = sec_grades.get(si)
        if not grades:
            continue
        if stat_idx is None:
            anomalies.append('节%s 有提分线题但无节统计段可挂（跳过追加，交人工）' % secno)
            continue
        p = els[stat_idx]
        full = ptext(p)
        if '提分线：' in full:
            n_skip_hung += 1
            continue
        ann = '　提分线：' + '｜'.join('%s→%s' % (g, GRADE2LINE[g]) for g in GRADE_ORDER if g in grades)
        append_at_end(p, ann)
        assert ptext(p) == full + ann, '追加后文本不符: 节%s' % secno
        appended.append((secno, ann.strip()))
        n_append += 1

    # ---- 断言 ----
    assert_msg = []
    if fn_q is not None and n_strip and n_strip != fn_q:
        raise AssertionError('剥离数 %d ≠ 文件名题数 %d（%s）' % (n_strip, fn_q, os.path.basename(path)))
    expect_secs = len(sec_grades)
    if n_append + n_skip_hung + sum(1 for s in secs if sec_grades.get(s[0]) and s[2] is None) != expect_secs:
        raise AssertionError('提分线节处置数不符: 追加%d＋幂等%d＋无挂点异常 ≠ 有提分线节%d'
                             % (n_append, n_skip_hung, expect_secs))
    assert_msg.append('剥离 %d｜节追加 %d｜幂等 %d' % (n_strip, n_append, n_skip_hung))

    lines = []
    lines.append('## T2 提分线迁移器 — %s%s' % (os.path.basename(path), '（dry-run）' if dry else ''))
    if n_strip == 0:
        lines.append('实测结论：本件题号块无提分线挂载（衔接件/清单件或已迁移）——0 处置')
    else:
        lines.append('提分线分布：' + '；'.join('%s→%s' % (g, GRADE2LINE[g]) for g in GRADE_ORDER))
        lines.append('剥离题号块 %d 处｜节统计段追加 %d 节｜幂等跳过 %d 节' % (n_strip, n_append, n_skip_hung))
        for secno, ann in appended[:10]:
            lines.append('  节%s ← %s' % (secno, ann))
        if len(appended) > 10:
            lines.append('  …共 %d 节' % len(appended))
    lines.append('断言：' + '｜'.join(assert_msg) + ('｜文件名题数 %s' % (('%d PASS' % fn_q) if fn_q is not None else '无括注')))
    for a in anomalies:
        lines.append('  ! ' + a)
    lines.append('')

    if not dry and (n_strip or n_append):
        import shutil
        bak = path + '.bak_提分线迁'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
        tmp = path + '.t2tmp'
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
    assert argv, '用法: python 工具/提分线迁移器.py <docx...> [--dry-run] [--report r.md]'
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
