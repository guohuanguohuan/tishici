# -*- coding: utf-8 -*-
#
# 收编：2026-08-29 节序号底纹收口轮（来源：桌面一次性脚本 同步-数学选必1第2章清单-0828回扫/节序号底纹.py
#       升级收编为常驻工具；升级点见 docstring「2026-08-29 收编注记」）
#
"""节标题序号底纹.py — 教材节标题序号挂 C9C9C9 底纹＋加粗（可复用，幂等）

口径注记（效力序见公共规则§7「题号难度块底纹」条款内「节标题序号底纹」扩展）：
  · 2026-08-27 用户拍板「节标题序号底纹」（用户成品截图反馈教材节标题序号无底纹、开头层次感不足）：
    教材节标题序号（章号＋节号，如「1.1.1」）加同款 C9C9C9 结构底纹＋加粗——结构锚加粗
    （与条目号 2026-08-29「不加粗」口径相区分）；底纹只盖序号字符（含尾随半角空格）、
    不盖标题文字；序号与标题文字同 run 时先拆出独立 run 再挂。
  · 2026-08-28 用户拍板「知识清单件跟进」：知识清单件的教材节标题序号同款跟进（存量件回扫债）。
  · 父级节标题（如「2.5」「9.1」二级）与叶节同款挂——选必1先例（讲练件终态 F2 补父级＋E1 复测、
    试点件父级 1.1/1.2 同款）：父级与叶节同挂，恒等式「节标题序号底纹 run 数＝节标题总数」，
    节标题数以 extract_structure 判定 section 为源（含二级与三级）。
  · 条目题名行「N．」全角句点起段，与 N.N(.N) 半角点分序号天然不同形——条目号不属节标题口径
    （其底纹按 2026-08-29 条目号底纹新口径另由 工具/条目号底纹.py 处置，本工具不碰条目题名行）。
  · 2026-08-29 收编注记（节序号底纹收口轮）：①试点脚本的反向断言「条目号段不许挂底纹」已随
    2026-08-29 条目号底纹拍板废止，改登记「条目号底纹 run 数改前后守恒」断言（不碰条目题名行的
    实证）；②新增节标题段内「标题文字 run 剥遗留底纹」归一（存量件旧构建整行铺灰形态——
    2026-08-28 标题字号梯子拍板「层级靠字号、整行灰冗余」，底纹只盖序号口径的存量归一），
    剥除数逐处登记；③工具内断言全文 w:t 字符序列改前后恒等（零字符铁律）。

判定与行为：
  · 节标题源＝extract_structure 判定的 section 段（body 级段落，段首 N.N(.N) 半角点分序号＋
    空白＋标题文字）；本工具仅处置序号匹配 ^\\d+(\\.\\d+){1,2} 的二/三级节标题——一级章号
    「N 标题」不属节标题口径，跳过并逐处登记（条目题名行「N．」全角句点天然排除，另设断言）；
  · 序号 run 文本终态＝「N.N(.N) 」（尾随半角空格随灰底，与试点件同款）；
  · 已挂（序号独立 run 已 C9C9C9）→ 幂等跳过，仍补加粗（缺才补）；
  · 序号 run 已有其他 fill 底纹 → 报错人工处置（不静默覆盖）；
  · 节标题段内其他 run 带 C9C9C9（遗留铺灰）→ 剥除并计数（标题文字无底纹口径）；
  · 修改的 w:t 一律置 xml:space="preserve" 防吞空格。
输出：登记 md（节号→节标题，含父级/叶级与逐处处置）＋stdout 恒等式断言
（节标题序号底纹 run 数＝节标题数＝新挂＋幂等跳过）。

用法: python 节标题序号底纹.py <docx> <登记md>
"""
import sys, os, re, zipfile, time, copy, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_structure import structure   # 注：该模块导入时会自重包 stdout
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
def q(t): return '{%s}%s' % (W, t)
def tag(e): return etree.QName(e).localname

FILL = 'C9C9C9'
SECTNUM_RE = re.compile(r'^\d+(?:\.\d+){1,2} ?$')      # 序号 run 终态文本（尾随半角空格随灰底）
SECHEAD_RE = re.compile(r'^(\d+(?:\.\d+){1,2})( ?)')   # 二/三级节序号＋至多一个尾随半角空格
ENT_RE = re.compile(r'^\d+．')                          # 条目题名行（全角句点，天然排除）

def para_runs(p):
    return [c for c in p if tag(c) == 'r']

def run_text(r):
    return ''.join(t.text or '' for t in r.findall(q('t')))

def set_run_text(r, s):
    ts = r.findall(q('t'))
    ts[0].text = s
    ts[0].set(XMLSPACE, 'preserve')
    for t in ts[1:]:
        t.text = ''

def shd_of(r):
    rpr = r.find(q('rPr'))
    return rpr.find(q('shd')) if rpr is not None else None

def doc_text(doc):
    return ''.join(t.text or '' for t in doc.iter(q('t')))

def ent_shaded_count(doc):
    """条目号底纹 run 数（body 级条目题名行的独立「N．」C9C9C9 run，与条目号底纹.py/四类计数同源口径）。"""
    n = 0
    body = doc.find(q('body'))
    for p in body:
        if p.tag != q('p'):
            continue
        for r in p.findall(q('r')):
            tx = run_text(r)
            if tx and re.match(r'^\d+．$', tx):
                shd = shd_of(r)
                if shd is not None and shd.get(q('fill')) == FILL:
                    n += 1
    return n

def ensure_anchor_rpr(r):
    """序号 run 补加粗＋底纹 C9C9C9（各自缺才补）。返回 (是否新挂底纹, 是否补加粗)。"""
    rpr = r.find(q('rPr'))
    if rpr is None:
        rpr = etree.Element(q('rPr')); r.insert(0, rpr)
    bold_added = False
    if rpr.find(q('b')) is None:
        b = etree.Element(q('b'))
        rf = rpr.find(q('rFonts'))
        rpr.insert(list(rpr).index(rf) + 1 if rf is not None else 0, b)
        bold_added = True
    shd = rpr.find(q('shd'))
    if shd is not None and shd.get(q('fill')) == FILL:
        return False, bold_added
    if shd is None:
        shd = etree.Element(q('shd'))
        shd.set(q('val'), 'clear'); shd.set(q('color'), 'auto'); shd.set(q('fill'), FILL)
        rpr.append(shd)  # rPr 内 shd 序靠后（bdr 之后），追加即合法
        return True, bold_added
    raise RuntimeError('序号run已有其他底纹 fill=%s，需人工处置' % shd.get(q('fill')))

def isolate_and_shade(p, numlen):
    """把段首 [0,numlen) 字符隔离为独立 run 并挂底纹（缺才挂，幂等）。
    返回 (序号run元素, 是否新挂底纹, 是否补加粗, 序号run文本)。"""
    runs = para_runs(p)
    off = 0
    target = None
    for r in runs:
        txt = run_text(r)
        a, b = off, off + len(txt)
        if a == 0 and b >= numlen and txt:
            target = r
            if b > numlen:
                # 序号与标题文字同 run：拆分为 [序号]＋[其余]（其余 run 剥底纹，标题文字不盖灰）
                rest = txt[numlen:]
                set_run_text(r, txt[:numlen])
                nr = copy.deepcopy(r)
                set_run_text(nr, rest)
                nrpr = nr.find(q('rPr'))
                if nrpr is not None:
                    nshd = nrpr.find(q('shd'))
                    if nshd is not None:
                        nrpr.remove(nshd)
                r.addnext(nr)
            break
        off = b
        if off >= numlen:
            break
    assert target is not None, '序号未落在首个文本run内（序号跨多 run 需人工归并）'
    assert run_text(target) and len(run_text(target)) == numlen
    shd_added, bold_added = ensure_anchor_rpr(target)
    return target, shd_added, bold_added, run_text(target)

def main(path, regmd):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    before_text = doc_text(doc)
    ent_before = ent_shaded_count(doc)

    st = structure(path)
    secs = []      # (body索引, 节号, numlen)
    skipped = []   # 一级章号等非节标题口径段（登记不处置）
    for x in st['items']:
        if x['kind'] != 'section':
            continue
        m = SECHEAD_RE.match(x['text'])
        if not m:
            skipped.append(x['text'][:30])
            continue
        assert not ENT_RE.match(x['text']), '条目题名行误入节标题口径: %r' % x['text'][:30]
        secs.append((x['el'], m.group(1), m.end()))

    body = doc.find(q('body'))
    els = list(body)
    secnums = [num for _, num, _ in secs]

    rows = []
    n_new = n_already = n_strip = n_bold = 0
    for eli, num, numlen in secs:
        p = els[eli]
        full = ''.join(t.text or '' for t in p.iter(q('t')))
        m = SECHEAD_RE.match(full)
        assert m and m.group(1) == num, '节标题序号复检不一致: %r' % full[:30]
        level = '父级' if any(sn != num and sn.startswith(num + '.') for sn in secnums) else '叶级'
        target, shd_added, bold_added, rt = isolate_and_shade(p, numlen)
        assert SECTNUM_RE.match(rt), '序号run文本形态异常: %r' % rt
        n_new += (1 if shd_added else 0)
        n_already += (0 if shd_added else 1)
        n_bold += (1 if bold_added else 0)
        # 标题文字 run 剥遗留底纹（底纹只盖序号口径；序号 run 本身除外）
        stripped = 0
        for r in p.iter(q('r')):
            if r is target:
                continue
            shd = shd_of(r)
            if shd is not None and shd.get(q('fill')) == FILL:
                shd.getparent().remove(shd)
                stripped += 1
        n_strip += stripped
        title = full[len(m.group(0)):].strip() or full.strip()
        rows.append((num, level, title, rt, shd_added, bold_added, stripped))

    # 恒等式断言：每节标题段底纹 run 恰为序号 run 一个，总数＝节标题数
    total_shaded = 0
    for eli, num, numlen in secs:
        p = els[eli]
        shd_runs = [run_text(r) for r in p.iter(q('r'))
                    if shd_of(r) is not None and shd_of(r).get(q('fill')) == FILL]
        assert len(shd_runs) == 1 and SECTNUM_RE.match(shd_runs[0]), \
            '节标题 b#%d 底纹run异常: %r' % (eli, shd_runs)
        total_shaded += 1
    n_secs = len(secs)
    ok = (total_shaded == n_secs == n_new + n_already)
    # 零字符铁律断言＋条目号底纹守恒断言
    assert doc_text(doc) == before_text, '零字符铁律被破坏（w:t 字符序列变化）'
    ent_after = ent_shaded_count(doc)
    assert ent_after == ent_before, '条目号底纹 run 数变化 %d->%d（本工具不得碰条目题名行）' % (ent_before, ent_after)

    # 落盘 docx（仅替换 word/document.xml，其余成员原样回写；占用重试禁杀进程）
    new_xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    fd, tmp = tempfile.mkstemp(suffix='.docx', dir=os.path.dirname(os.path.abspath(path)) or '.')
    os.close(fd)
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

    # 登记 md
    lines = []
    lines.append('# 节标题序号底纹登记 — %s' % os.path.basename(path))
    lines.append('')
    lines.append('轮次：节序号底纹收口轮 2026-08-29（公共规则§7节标题序号底纹——2026-08-27 用户拍板＋')
    lines.append('2026-08-28 知识清单件跟进的存量回扫；工具/节标题序号底纹.py 2026-08-29 收编，')
    lines.append('选必1先例：父级与叶节同挂，恒等式＝节标题序号底纹 run 数＝节标题数；结构锚加粗、')
    lines.append('底纹只盖序号含尾随半角空格、不盖标题文字；条目号「N．」不属本口径不碰）')
    lines.append('')
    lines.append('节标题数 %d｜新挂 %d｜幂等跳过 %d｜补加粗 %d｜标题文字剥遗留底纹 %d｜'
                 '恒等式（挂底纹 run 数 %d＝节标题数）%s｜零字符断言 通过｜条目号底纹守恒 %d＝%d 通过'
                 % (n_secs, n_new, n_already, n_bold, n_strip, total_shaded,
                    '成立' if ok else '不成立!!', ent_before, ent_after))
    lines.append('')
    lines.append('| 节号 | 级别 | 节标题 | 序号run | 处置 |')
    lines.append('|---|---|---|---|---|')
    for num, level, title, rt, shd_added, bold_added, stripped in rows:
        disp = '新挂' if shd_added else '已挂（幂等跳过）'
        extra = []
        if bold_added:
            extra.append('补加粗')
        if stripped:
            extra.append('剥标题文字遗留底纹%d处' % stripped)
        if extra:
            disp += '（' + '＋'.join(extra) + '）'
        lines.append('| %s | %s | %s | 「%s」 | %s |' % (num, level, title.replace('|', '\\|'), rt, disp))
    if skipped:
        lines.append('')
        lines.append('非节标题口径跳过段（一级章号等，登记不处置）：%s' % '；'.join(skipped))
    lines.append('')
    open(regmd, 'w', encoding='utf-8').write('\n'.join(lines))
    print('节标题数 %d｜新挂 %d｜幂等跳过 %d｜补加粗 %d｜剥标题文字遗留底纹 %d；'
          '恒等式（%d＝%d）%s；零字符断言通过；条目号底纹守恒 %d＝%d'
          % (n_secs, n_new, n_already, n_bold, n_strip, total_shaded, n_secs,
             '成立 PASS' if ok else '不成立 CHECK', ent_before, ent_after))
    print('登记md -> %s' % regmd)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
