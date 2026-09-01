# -*- coding: utf-8 -*-
"""h_halfwidth.py — E6一次性脚本（§6裁决8）：H件2条半角讲部条目预归一
「1. 小题…」「2. 大题…」→「1．小题…」「2．大题…」（半角句点+半角空格→全角句点），
并剥整段加粗（§7加粗仅限结构标题与题号块；条目族与其他4条全角条目形态对齐：
号run底纹/不加粗由③题号块三段式.py完成，本脚本只做文字token与加粗归一）。
断言：恰好改写2段；改写段文本=期望；不触碰其他段落。
用法: python h_halfwidth.py <docx> [--json 报告.json]
"""
import sys, os, re, zipfile, json, time
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
def q(t): return '{%s}%s' % (W, t)

EXPECT = [('1．小题（选择题与填空题）：直接“秒杀”', '1. 小题（选择题与填空题）：直接“秒杀”'),
          ('2．大题（解答题）：不可直接引用，需“合法洗白”', '2. 大题（解答题）：不可直接引用，需“合法洗白”')]

def main():
    path = sys.argv[1]
    jp = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None
    zin = zipfile.ZipFile(path)
    members = zin.namelist()
    parts = {n: zin.read(n) for n in members}
    zin.close()
    doc = etree.fromstring(parts['word/document.xml'])
    log = {'改写段': [], '加粗剥除run数': 0}
    done = set()
    for el in doc.find(q('body')):
        if etree.QName(el).localname != 'p':
            continue
        txt = ''.join(t.text or '' for t in el.iter(q('t')))
        for new_t, old_t in EXPECT:
            if txt != old_t or new_t in done:
                continue
            hit = False
            for r in el.findall(q('r')):
                ts = r.findall(q('t'))
                if not ts:
                    continue
                rt = ''.join(t.text or '' for t in ts)
                mm = re.match(r'^(\d{1,2})\.\s(.*)$', rt, re.S)
                if mm and not hit:
                    ts[0].text = mm.group(1) + '．' + mm.group(2)
                    ts[0].set(XMLSPACE, 'preserve')
                    for t in ts[1:]:
                        t.text = ''
                    hit = True
            assert hit, '半角号run未命中: %r' % txt[:30]
            for r in el.findall(q('r')):
                rpr = r.find(q('rPr'))
                if rpr is None:
                    continue
                for tg in ('b', 'bCs'):
                    e = rpr.find(q(tg))
                    if e is not None:
                        rpr.remove(e)
                        log['加粗剥除run数'] += 1
            got = ''.join(t.text or '' for t in el.iter(q('t')))
            assert got == new_t, '改写后文本不符: %r' % got[:40]
            log['改写段'].append({'旧': old_t[:30], '新': got[:30]})
            done.add(new_t)
    assert len(done) == 2, '应恰好改写2段，实得 %d' % len(done)
    parts['word/document.xml'] = etree.tostring(doc, xml_declaration=True,
                                                encoding='UTF-8', standalone=True)
    tmp = path + '.tmphalf'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
        for n in members:
            zo.writestr(n, parts[n])
    for _ in range(12):
        try:
            os.replace(tmp, path)
            break
        except PermissionError:
            time.sleep(6)
    else:
        raise RuntimeError('locked: ' + path)
    if jp:
        json.dump(log, open(jp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(log, ensure_ascii=False))

if __name__ == '__main__':
    main()
