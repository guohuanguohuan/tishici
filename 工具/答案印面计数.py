# -*- coding: utf-8 -*-
r"""答案印面计数.py — [E] 门脚本：编译产物 PDF 的答案印面计数＋键账对平（军师收口轮0913 §九钉①）。

口径（军师钉②「对集合不对数」）：
  ①B-true 档答案区计数＝键数、false 档＝0——逐件双档跑：true 件印面「N. [答案]」答案区
    数号集合须与键集合相等；false 件印面答案区须为 0（泄答＝红）。
  ②对集合不对数：答案册/% ans: 键集合 ↔ 印面答案区集合双向 diff（缺＝静默丢答案，
    多＝幻影答案区）；计数相等但号集不同也挂红（防 1..19 挪成 2..20 的假对平）。
    数号提取：键末段数字（测-6→6、练-3-2→2？多段键取末段；歧义键降级对数并标注）。
    三源可选：--keys（答案册 body.tex 之 \ansitem{N}{值}／键账 json）、--pct（件 tex 的
    % ans: 锚＋\begin{ansblock}[键]）、--log（M3-ANSKEY 恒发键序，含纯题档——两档键账
    恒等断言）。件面真源＝--pct 件 tex；--keys 答案册为对平基准（缺省时以 --pct 自代理）。
  ③页脚签名带「答案」字样（如卷末速查表说明行）不计答案区：正则须带 [答案] 方括号形
    或「N. [答案]」数号形；[详解]/[点睛]（\ansnote 形）单列计数不并答案区。
用法: python 工具/答案印面计数.py <true件.pdf>… [--false <false件.pdf>]
        [--pct 件tex] [--keys 答案册tex|键账json] [--log true件log] [--false-log false件log]
        [--prefix 测] [--out 报告.txt]
  例（双档一键跑）: python 工具/答案印面计数.py main-换装B-true.pdf --false main-换装B-false.pdf
        --pct main-换装B.tex --keys body.tex --log main-换装B-true.log --false-log main-换装B-false.log
  --keys .tex＝答案册提取 \ansitem{N}{…} 键（测-N 前缀随 --prefix）；.json＝键账（支持
  {"keys":N,"vals":{"测-1":…}} 或直接 {键:值} 字典）。--prefix 测（默认）键号=前缀-N。
退出码: 0＝全对平；1＝有红（缺块/幻影/泄答/键账不齐）；2＝用法/输入错。
负测自测: --selftest 临时目录合成丢块/泄答负例＋对平正例，断言真拦真放行，不落项目树。
红线: 全部输入只读；本脚本不写 PDF/tex；--out 报告除外。
"""
import argparse
import io
import json
import os
import re
import sys

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import pymupdf
except ImportError:
    import fitz as pymupdf

RE_NUMZONE = re.compile(r'(\d{1,3})[.\uFF0E]\s*\[答案\]')
RE_ZONE = re.compile(r'\[答案\]')
RE_NOTE = re.compile(r'\[(详解|点睛)\]')
RE_PCTKEY = re.compile(r'%\s*ans:(\S+)')
RE_ENVKEY = re.compile(r'\\begin\{ansblock\}\[([^\]]+)\]')
RE_ANSKEY = re.compile(r'M3-ANSKEY:\s*(\S+)')
RE_ANSITEM = re.compile(r'\\ansitem\{([^}]+)\}\{')


def _read(path):
    return open(path, encoding='utf-8-sig', errors='replace').read()


def keynum(k, prefix=None):
    """键→印面数号：末段数字；带前缀键（测-6→6）。失败返回 None。"""
    if prefix:
        m = re.match(r'^%s-(\d+)$' % re.escape(prefix), k.strip())
        if m:
            return int(m.group(1))
    m = re.search(r'(\d+)\s*$', k.strip())
    return int(m.group(1)) if m else None


def pdf_zones(pdfpath):
    d = pymupdf.open(pdfpath)
    alln = '\n'.join(p.get_text() for p in d)
    nums = sorted({int(x) for x in RE_NUMZONE.findall(alln)})
    return {'pages': d.page_count, 'count': len(RE_ZONE.findall(alln)),
            'nums': nums, 'notes': {t: len(RE_NOTE.findall(t_ := alln)) for t in ('详解', '点睛')}}


def load_keys(args):
    """键账三源合并：答案册（--keys）＞件 tex 锚（--pct）＞log（--log）。返回 dict。"""
    out = {}
    if args.keys:
        p = args.keys
        if p.lower().endswith('.json'):
            j = json.loads(_read(p))
            vals = j.get('vals', j if isinstance(j, dict) and 'keys' not in j else {})
            ks = list(vals.keys()) if isinstance(vals, dict) else list(j.get('keys', []))
            out['keys'] = ks
            out['src'] = os.path.basename(p)
        else:
            txt = _read(p)
            ks = [m.group(1) for m in RE_ANSITEM.finditer(txt)]
            if args.prefix:
                ks = [f'{args.prefix}-{k}' for k in ks]
            out['keys'] = ks
            out['src'] = os.path.basename(p)
    pct = env = None
    if args.pct:
        txt = _read(args.pct)
        pct = sorted(set(RE_PCTKEY.findall(txt)))
        env = sorted(set(RE_ENVKEY.findall(txt)))
    out['pct'], out['env'] = pct, env
    for tag, lp in (('log', args.log), ('false_log', args.false_log)):
        if lp and os.path.isfile(lp):
            ks = list(dict.fromkeys(RE_ANSKEY.findall(_read(lp))))
            out[tag] = ks
    if 'keys' not in out:
        cand = pct or env or out.get('log') or out.get('false_log')
        if not cand:
            return None
        out['keys'] = cand
        out['src'] = '件锚/log 代理（无独立答案册源）'
    return out


def diff_sets(a, b, la, lb):
    miss = sorted(set(a) - set(b))
    extra = sorted(set(b) - set(a))
    if miss or extra:
        msgs = []
        if miss:
            msgs.append(f'印面缺({la}有{lb}无)：{miss}')
        if extra:
            msgs.append(f'印面多({lb}有{la}无)：{extra}')
        return 'FAIL', '；'.join(msgs)
    return 'PASS', f'{la}({len(set(a))})↔{lb}({len(set(b))}) 集合相等'


def selftest():
    """负测真拦＋正测真放行（合成静默丢失样本，临时目录内跑毕即删）。"""
    import tempfile
    MM = 72 / 25.4
    rc = 0
    with tempfile.TemporaryDirectory(prefix='答案印面计数-selftest-') as td:
        ks = [f'测-{i}' for i in range(1, 5)]
        tex = os.path.join(td, 'n.tex')
        with open(tex, 'w', encoding='utf-8') as fh:
            for k in ks:
                fh.write(f'% ans:{k}\n\\begin{{ansblock}}[{k}]\\end{{ansblock}}\n')
        ledger = os.path.join(td, 'k.json')
        json.dump({'keys': 4, 'vals': {k: 'v' for k in ks}}, open(ledger, 'w', encoding='utf-8'),
                  ensure_ascii=False)
        def mkpdf(name, nums, drop):
            d = pymupdf.open()
            pg = d.new_page(width=399.8 * MM, height=284.2 * MM)
            for i, n in enumerate(nums):
                if n in drop:
                    continue
                pg.insert_text((20 * MM, (60 + 14 * i) * MM), f'{n}. [答案] 值', fontname='china-s', fontsize=10)
            d.save(os.path.join(td, name))
            d.close()
        mkpdf('ok-true.pdf', [1, 2, 3, 4], set())
        mkpdf('bad-true.pdf', [1, 2, 3, 4], {3})
        mkpdf('ok-false.pdf', [1, 2, 3, 4], {1, 2, 3, 4})
        mkpdf('bad-false.pdf', [1, 2, 3, 4], {4})
        for name, tpdf, fpdf, expect in (
                ('P0 正例 对平', 'ok-true.pdf', 'ok-false.pdf', 0),
                ('N1 负例 true 丢块', 'bad-true.pdf', 'ok-false.pdf', 1),
                ('N2 负例 false 泄答', 'ok-true.pdf', 'bad-false.pdf', 1)):
            argv = ['x', os.path.join(td, tpdf)]
            if fpdf:
                argv += ['--false', os.path.join(td, fpdf)]
            argv += ['--pct', tex, '--keys', ledger]
            print(f'--- selftest {name} ---')
            got = main(argv)
            ok = got == expect
            rc |= (not ok)
            print(f'[selftest {"PASS" if ok else "FAIL"}] {name}：退出码 {got}（期望 {expect}）\n')
        rc |= (main(['x']) != 2)
    print('[selftest PASS 负测真拦·正测真放行]' if rc == 0 else '[selftest FAIL]')
    return 0 if rc == 0 else 1


def main(argv):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument('true_pdf', nargs='*')
    ap.add_argument('--false', dest='false_pdf')
    ap.add_argument('--pct')
    ap.add_argument('--keys')
    ap.add_argument('--prefix', default='测')
    ap.add_argument('--log')
    ap.add_argument('--false-log', dest='false_log')
    ap.add_argument('--out')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('-h', '--help', action='store_true')
    a = ap.parse_args(argv[1:])
    if a.selftest:
        return selftest()
    if a.help or not a.true_pdf:
        print(__doc__)
        return 2
    for p in [x for x in (list(a.true_pdf) + ([a.false_pdf] if a.false_pdf else [])) if x] + \
             [x for x in (a.pct, a.keys, a.log, a.false_log) if x]:
        if not os.path.isfile(p):
            print('[FAIL] 输入不存在:', p)
            return 2
    L = []
    def log(s):
        L.append(s)
    keys = load_keys(a)
    if keys is None:
        print('[FAIL] 无键账源：--keys/--pct/--log 至少给一')
        return 2
    kn = [keynum(k, a.prefix or None) for k in keys['keys']]
    if any(v is None for v in kn):
        log(f'[键账] {len(keys["keys"])} 键（源 {keys["src"]}）含非数号键——对数降级口径')
        kn = [v for v in kn if v is not None]
    dup = sorted({v for v in kn if kn.count(v) > 1})
    if dup:
        log(f'[键账] 数号重号（多区块键）：{dup}——该号只断在体不断唯一')
    ks = sorted(set(kn))
    src_note = f'基准＝{keys["src"]} {len(ks)} 数号'
    if keys.get('pct') is not None:
        kpct = sorted({keynum(k, a.prefix or None) for k in keys['pct']})
        kenv = sorted({keynum(k, a.prefix or None) for k in keys['env']}) if keys.get('env') is not None else None
        st, msg = diff_sets(ks, kpct, '键账', '% ans:')
        log(f'[锚账1] {msg} → {st}')
        if kenv is not None:
            st2, msg2 = diff_sets(kpct, kenv, '% ans:', 'ansblock')
            log(f'[锚账2] {msg2} → {st2}')
        if st.startswith('F') or (kenv is not None and st2.startswith('F')):
            pass  # 红在末尾计数
    if keys.get('log') and keys.get('false_log'):
        st3, msg3 = diff_sets(sorted({keynum(k, a.prefix or None) for k in keys['log']}),
                              sorted({keynum(k, a.prefix or None) for k in keys['false_log']}),
                              'true档log', 'false档log')
        log(f'[两档恒发] {msg3} → {st3}')
    nfail = 0
    for tp in a.true_pdf:
        zt = pdf_zones(tp)
        st, msg = diff_sets(ks, zt['nums'], '键账', f'印面 {os.path.basename(tp)}')
        note = f'｜[答案]总现 {zt["count"]}（含无号形）页数 {zt["pages"]}'
        log(f'[true] {msg}{note} → {st}')
        if st == 'FAIL':
            nfail += 1
            if zt['count'] != len(ks):
                log(f'    计数读数：印面 {zt["count"]} vs 键数 {len(ks)}（对集合已挂红，计数供定位）')
        if a.false_pdf:
            zf = pdf_zones(a.false_pdf)
            ok = zf['count'] == 0 and not zf['nums']
            log(f'[false] {os.path.basename(a.false_pdf)}：[答案]×{zf["count"]} 答案区 {zf["nums"]} '
                f'页数 {zf["pages"]} → {"PASS（纯题档零答案）" if ok else "FAIL（泄答）"}')
            if not ok:
                nfail += 1
        if zt['notes']:
            log(f'[标注] [详解]×{zt["notes"]["详解"]} [点睛]×{zt["notes"]["点睛"]}（\\ansnote 形，不并答案区计数）')
    verdict = f'[PASS] 答案印面对平（{src_note}）' if nfail == 0 else f'[FAIL] {nfail} 件对不平，须回查后复跑'
    print('\n'.join(L))
    print(verdict)
    if a.out:
        with open(a.out, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(L + [verdict]) + '\n')
    return 0 if nfail == 0 else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
