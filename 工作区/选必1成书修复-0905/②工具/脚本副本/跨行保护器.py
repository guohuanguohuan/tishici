# -*- coding: utf-8 -*-
r"""跨行保护器.py — 2026-09-05 选必1成书修复路线·版式修订轮②·T9（工具先建后用）

口径（规格书T9）：
  a) 行内【×】芯片标签字符间插 U+2060（WORD JOINER）防断行：「【答案】」→「【⁠答⁠案⁠】」
     （括号与字间全插）；幂等＝芯片内已含 U+2060 跳过。全部【…】（内文 1~16 字）一律处置，
     〔基〕〔进〕非【】不属本项。
  b) 节/题型/讲部标题段挂 w:keepLines（防标题折行拆词）。识别（T6b 撤底纹前后两形兼容）：
     节标题＝段级底纹 ADC2DA＋节号 pattern；讲部＝「N.N… 知识讲解｜/方法讲解｜」；
     题型＝父链续层编号（深度≥3）起段＋（C6D4E3 底纹 或 左侧竖条 pBdr 或 全角冒号）。
  c) 行内 OMML 公式跨行断裂保护——调研结论：Word 行内 m:oMath 对象在栏内折行时为原子整体
     （不拆公式本体），断裂风险在「短公式密集段被跨栏/跨页撕开」；可行形态＝含 oMath 且
     可视长 ≤60（约一栏两行内）的段挂 keepLines；＞60 的长段若整段 keepLines 会引发病态
     排布（整段推下一栏留大白），不挂并登记数量——替代方案即长段任其自然折行（公式本体
     不撕裂，行内断点落在文字处，符合阅读习惯）。WJ 围公式方案经调研不取：U+2060 对
     oMath 对象邻接断行无 Word 保证语义，且污染文本流，弃用。
断言：a) 插符芯片数＝新增 U+2060 组数（逐芯片核验）；b)/c) keepLines 命中段数登记、幂等跳过
      计数；零意外字符（a 仅插 U+2060，b/c 仅 pPr 属性）。
模式：默认就地改写（留 .bak_跨行护）；--dry-run 出分布不落盘。
用法:
  python 工具/跨行保护器.py <docx...> [--dry-run] [--report r.md]
"""
import sys, io, os, re, zipfile, time
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def pfill(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        return None
    sh = ppr.find(q('shd'))
    return sh.get(q('fill')) if sh is not None else None

WJ = '⁠'
CHIP_RE = re.compile(r'【[^】]{1,16}】')
SEC_TTL_RE = re.compile(r'^\d+\.\d+(?:\.\d+)?[\s　]+\S')
LECT_RE = re.compile(r'^\d+(?:\.\d+)*\s*(?:方法讲解|知识讲解)[｜|]')
GRP_RE = re.compile(r'^\d+(?:\.\d+){2,}[\s　]+\S')
OM_SHORT_LIMIT = 60


def eff_len(s):
    return sum(1.0 if ord(c) > 0x2E7F else 0.5 for c in s)


def add_keeplines(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        ppr = etree.Element(q('pPr'))
        p.insert(0, ppr)
    if ppr.find(q('keepLines')) is not None:
        return False
    kl = etree.Element(q('keepLines'))
    for c in ppr:
        if etree.QName(c).localname not in ('pStyle', 'keepNext'):
            c.addprevious(kl)
            break
    else:
        ppr.append(kl)
    return True


def has_left_bar(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        return False
    pb = ppr.find(q('pBdr'))
    return pb is not None and pb.find(q('left')) is not None


def process(path, dry):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    body = doc.find(q('body'))

    # ---- a) 芯片 WJ ----
    n_chip = n_chip_done = 0
    for t in body.iter(q('t')):
        txt = t.text or ''
        if '【' not in txt:
            continue
        def repl(m):
            nonlocal n_chip, n_chip_done
            chip = m.group(0)
            if WJ in chip:
                n_chip_done += 1
                return chip
            n_chip += 1
            return chip[0] + WJ + WJ.join(chip[1:-1]) + WJ + chip[-1]
        new = CHIP_RE.sub(repl, txt)
        if new != txt:
            t.text = new
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')

    # ---- b) 标题段 keepLines ----
    n_b = n_b_keep = 0
    n_b_sec = n_b_grp = n_b_lect = 0
    for p in body.iter(q('p')):
        t = ptext(p)
        kind = None
        if pfill(p) == 'ADC2DA' and SEC_TTL_RE.match(t):
            kind = '节'
        elif LECT_RE.match(t):
            kind = '讲部'
        elif GRP_RE.match(t) and (pfill(p) == 'C6D4E3' or has_left_bar(p) or '：' in t[:60]):
            kind = '题型'
        if kind is None:
            continue
        if add_keeplines(p):
            n_b += 1
            if kind == '节':
                n_b_sec += 1
            elif kind == '讲部':
                n_b_lect += 1
            else:
                n_b_grp += 1
        else:
            n_b_keep += 1

    # ---- c) oMath 短段 keepLines ----
    n_c = n_c_keep = n_c_long = 0
    for p in body.iter(q('p')):
        if not list(p.iter(qm('oMath'))):
            continue
        if eff_len(ptext(p)) > OM_SHORT_LIMIT:
            n_c_long += 1
            continue
        if add_keeplines(p):
            n_c += 1
        else:
            n_c_keep += 1

    lines = []
    lines.append('## T9 跨行保护器 — %s%s' % (os.path.basename(path), '（dry-run）' if dry else ''))
    lines.append('a) 芯片插WJ %d 处（幂等 %d）｜b) 标题keepLines 新挂 %d（节%d/讲部%d/题型%d，幂等 %d）｜'
                 'c) oMath短段keepLines 新挂 %d（幂等 %d；长段 %d 登记不挂）'
                 % (n_chip, n_chip_done, n_b, n_b_sec, n_b_lect, n_b_grp, n_b_keep, n_c, n_c_keep, n_c_long))
    lines.append('')

    if not dry and (n_chip or n_b or n_c):
        import shutil
        bak = path + '.bak_跨行护'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
        tmp = path + '.t9tmp'
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
    assert argv, '用法: python 工具/跨行保护器.py <docx...> [--dry-run] [--report r.md]'
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
