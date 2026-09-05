# -*- coding: utf-8 -*-
r"""公式元素还原器.py — ②-F 公式修复轮（T5 丢失 oMath 元素外科还原）

事故：②-B 期 T5（标签行独立成段器）拆「【答案】 公式　【知识点】」类混行段时，
把可视文本全空白但含 m:oMath 的 content 段整段丢弃（T5 守恒断言只看 w:t）。

机制（本工具）：
  donor＝preT5 留档（*.docx.bak_标签行），cur＝现态（②-C 终态）。
  ① 全文去空白 w:t 流逐字对齐（k＝该位置前去空白 w:t 字符数；donor/cur 归一流全文相等为前提断言）；
  ② 数学单元实例＝段直接子级中含 m:oMath 后代者（深拷贝插入保 rPr 与内部结构）；
  ③ 同 k 组内按文档序配对，donor 剩余＝丢失集（元素级 diff 重建，不依赖摘要）；
  ④ 插入点＝k 在 cur 流中的精确位置：段内 run 级（跳过界点上既有零宽单元）或段尾（前段末，
     与 T5 零宽归属规则「标签起界归前段（内容尾）」一致）；
  ⑤ 题块锚定：报告行附 donor 侧最近题号段文本（^\d+(\.\d+)*-\d+．）作人工核对锚。

硬断言（缺一即 FAIL 停跑）：
  a) 元素守恒：修复后逐件 oMath 总数（含 oMathPara 内层与嵌套段）对平 donor preT5 总数；
  b) 文本守恒：w:t 拼接（raw 与去空白归一化双口径）前＝后；
  c) 白名单外零 diff：撤除全部插入单元后 document.xml 序列化字节＝修复前；
     非 document.xml 部件 MD5 全等；
  d) XML well-formed＋zip 完整（testzip）＋无悬空 rId（document.xml 引用 ⊆ rels）；
  e) 幂等：修复产物上二跑 k 配对丢失集＝0、0 改写。

模式：默认就地改写（不改同步盘；本轮修复态留 ②工具\副本 待主脑抽审）；--dry-run 预演不落盘。
用法:
  python 工具/公式元素还原器.py <docx...> [--dry-run] [--report r.md]
"""
import sys, io, os, re, zipfile, time, hashlib, copy
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)
def qr(t): return '{%s}%s' % (R, t)
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
WS_RE = re.compile(r'[\s　\xa0​]+')
ANCHOR_RE = re.compile(r'^\d+(?:\.\d+)*-\d+．')
def norm(s): return WS_RE.sub('', s)
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def wlen(el): return sum(len(t.text or '') for t in el.iter(q('t')))
def n_om(el): return sum(1 for _ in el.iter(qm('oMath')))


def load(path):
    z = zipfile.ZipFile(path)
    tree = etree.fromstring(z.read('word/document.xml'))
    parts = [(i.filename, z.read(i.filename)) for i in z.infolist()]
    z.close()
    return tree, parts


def fp(el):
    """数学内容指纹（m: 子树标签序列＋m:t 文本；对 w: 格式属性漂移免疫）。"""
    out = []
    for e in el.iter():
        en = etree.QName(e).namespace
        ln = etree.QName(e).localname
        if en == M:
            out.append(ln)
            if ln == 't':
                out.append(e.text or '')
    return '|'.join(out)


class MidChildError(Exception):
    pass


def instances(tree):
    """[(k, n_om, el, para, para_idx, para_text)]，文档序。k＝单元前全局去空白 w:t 字符数。"""
    body = tree.find(q('body'))
    out = []
    nk = 0
    for pi, p in enumerate(body.iter(q('p'))):
        txt = ptext(p)
        off = 0
        for ch in p:
            if n_om(ch):
                out.append((nk + len(norm(txt[:off])), n_om(ch), ch, p, pi, txt))
            off += wlen(ch)
        nk += len(norm(txt))
    return out


def pair_lost(D, C):
    """同 k 组内按文档序配对 → (lost, n_collide_cur)。lost＝donor 剩余实例。"""
    from collections import defaultdict
    dk, ck = defaultdict(list), defaultdict(list)
    for inst in D:
        dk[inst[0]].append(inst)
    for inst in C:
        ck[inst[0]].append(inst)
    lost = []
    for k in sorted(dk):
        dd, cc = dk[k], ck.get(k, [])
        n = min(len(dd), len(cc))
        lost += dd[n:]
    return lost


def locate(cur_tree, k):
    """k → (para, child_index)；段尾边界归前段末（index=len(children)）。
    段内界点上跳过既有零宽子级（插其后，保 donor 文档序）。k 落非零宽子级内部 → MidChildError。"""
    body = cur_tree.find(q('body'))
    nk = 0
    for p in body.iter(q('p')):
        children = list(p)
        pending = None
        for ci, ch in enumerate(children):
            nw = len(norm(''.join(t.text or '' for t in ch.iter(q('t')))))
            if nw == 0:
                if nk == k:
                    pending = ci + 1
                continue
            if k <= nk:
                return p, (pending if pending is not None else ci)
            if k < nk + nw:
                raise MidChildError('k=%d 落入非零宽子级内部（%s，段文 %r）'
                                    % (k, etree.QName(ch).localname, ptext(p)[:60]))
            nk += nw
            pending = None
        if nk == k:
            return p, len(children)
    raise MidChildError('k=%d 超出 cur 文本流末端' % k)


def apply_ops(ops):
    """ops＝[(para, orig_idx, el)]（同 para 按 orig_idx 升序）：实际位＝orig_idx＋同段前序操作数。"""
    from collections import defaultdict
    byp = defaultdict(list)
    for op in ops:
        byp[id(op[0])].append(op)
    for plist in byp.values():
        plist.sort(key=lambda o: o[1])
        for i, (p, oi, el) in enumerate(plist):
            p.insert(oi + i, el)


def revert_ops(ops):
    for p, oi, el in ops:
        p.remove(el)


def anchors(donor_tree):
    """donor 段序 → 每段最近前序题号锚文本。"""
    body = donor_tree.find(q('body'))
    out = []
    cur_anchor = '—'
    for p in body.iter(q('p')):
        t = ptext(p).strip()
        if ANCHOR_RE.match(t):
            cur_anchor = t[:42]
        out.append(cur_anchor)
    return out


def rids_referenced(tree):
    ids = set()
    for e in tree.iter():
        for attr in (qr('id'), qr('embed'), qr('link')):
            v = e.get(attr)
            if v:
                ids.add(v)
    return ids


def process(path, donor_path, dry):
    tree, parts = load(path)
    dtree, _ = load(donor_path)
    s_before = etree.tostring(tree)
    wt_before = ''.join(t.text or '' for t in tree.iter(q('t')))
    om_before = sum(1 for _ in tree.iter(qm('oMath')))
    om_donor = sum(1 for _ in dtree.iter(qm('oMath')))
    norm_before = norm(wt_before)

    D, C = instances(dtree), instances(tree)
    # 前提断言：donor/cur 全文归一流相等（k 配对地基）
    dtxt = ''.join(ptext(p) for p in dtree.find(q('body')).iter(q('p')))
    ctxt = ''.join(ptext(p) for p in tree.find(q('body')).iter(q('p')))
    assert norm(dtxt) == norm(ctxt), '前提不成立：donor/cur 全文去空白流不等，k 配对失效'

    lost = pair_lost(D, C)
    n_lost_el = sum(x[1] for x in lost)
    anch = anchors(dtree)

    # 插入点解算（dry 亦全量解算，作 fail-fast 探针）
    ops = []
    detail = []
    for (k, nom, del_, _dp, dpi, dtxt_) in lost:
        p, idx = locate(tree, k)
        ops.append((p, idx, del_))
        detail.append((k, nom, dpi, dtxt_, ptext(p), idx))
    from collections import defaultdict
    byp = defaultdict(list)
    for op in ops:
        byp[id(op[0])].append(op)
    n_para_touched = len(byp)

    lines = []
    lines.append('## 公式元素还原器 — %s%s' % (os.path.basename(path), '（dry-run）' if dry else ''))
    lines.append('donor=%s' % os.path.basename(donor_path))
    lines.append('oMath：donor %d ｜ 现态 %d ｜ 丢失实例 %d（元素 %d，落 %d 段）'
                 % (om_donor, om_before, len(lost), n_lost_el, n_para_touched))
    for (k, nom, dpi, dtxt_, ctxt_, idx) in detail[:14]:
        lines.append('  还原 k=%d om%d donor[p%d]锚:%s ｜donor段 %r → cur段@%d %r'
                     % (k, nom, dpi, anch[dpi][:30], dtxt_[:46], idx, ctxt_[:46]))
    if len(detail) > 14:
        lines.append('  …共 %d 处' % len(detail))

    if dry:
        pred = om_before + n_lost_el
        lines.append('预演：预测修复后 oMath %d ｜ 元素守恒预测 %s'
                     % (pred, 'PASS' if pred == om_donor else 'FAIL'))
        lines.append('')
        return '\n'.join(lines), n_lost_el

    # ── 执行插入＋断言 ──
    # b) raw 文本快照已取（wt_before）；c) s_before 已取
    apply_ops(ops)
    s_mid = etree.tostring(tree)
    revert_ops(ops)
    s_back = etree.tostring(tree)
    assert s_back == s_before, '断言c前哨：撤除插入后字节不等于修复前（存在白名单外改动）'
    apply_ops(ops)                      # 重放（同批元素对象）
    assert etree.tostring(tree) == s_mid, '断言c前哨：重放后字节不等（插入不确定）'
    wt_after = ''.join(t.text or '' for t in tree.iter(q('t')))
    assert wt_after == wt_before, '断言b(raw) FAIL：w:t 拼接前≠后'
    assert norm(wt_after) == norm_before, '断言b(norm) FAIL：去空白归一前≠后'

    om_after_tree = sum(1 for _ in tree.iter(qm('oMath')))
    assert om_after_tree == om_donor, '断言a(树) FAIL：%d ≠ donor %d' % (om_after_tree, om_donor)

    # rId 前置核对（引用 ⊆ rels）
    rels = None
    for name, data in parts:
        if name == 'word/_rels/document.xml.rels':
            rels = etree.fromstring(data)
    rel_ids = set()
    if rels is not None:
        for rel in rels:
            rid = rel.get('Id')
            if rid:
                rel_ids.add(rid)
    dangling = rids_referenced(tree) - rel_ids
    assert not dangling, '断言d前哨：悬空 rId %s' % sorted(dangling)

    # 写盘（其余部件原字节复制）
    new_xml = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
    tmp = path + '.fxtmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, data in parts:
            zout.writestr(name, new_xml if name == 'word/document.xml' else data)
    for k in range(12):
        try:
            os.replace(tmp, path)
            break
        except PermissionError:
            time.sleep(6)
    else:
        raise RuntimeError('locked: ' + path)

    # ── 落盘后复验（d/a/b/c·部件面/e 幂等）──
    tree2, parts2 = load(path)
    assert tree2.find(q('body')) is not None
    om2 = sum(1 for _ in tree2.iter(qm('oMath')))
    assert om2 == om_donor, '断言a(盘) FAIL：%d ≠ donor %d' % (om2, om_donor)
    wt2 = ''.join(t.text or '' for t in tree2.iter(q('t')))
    assert wt2 == wt_before and norm(wt2) == norm_before, '断言b(盘) FAIL'
    md5_ok = all(hashlib.md5(a).hexdigest() == hashlib.md5(b).hexdigest()
                 for (na, a), (nb, b) in zip(sorted(parts), sorted(parts2)) if na != 'word/document.xml')
    assert md5_ok, '断言c(部件) FAIL：非 document.xml 部件 MD5 不等'
    # zip 完整
    z = zipfile.ZipFile(path)
    assert z.testzip() is None, '断言d FAIL：zip 损坏'
    z.close()
    # e) 幂等：产物上重跑丢失集＝0
    D2, C2 = instances(dtree), instances(tree2)
    lost2 = pair_lost(D2, C2)
    assert not lost2, '断言e FAIL：产物二跑仍有 %d 丢失实例' % len(lost2)

    lines.append('断言：a 元素守恒 %d=donor%d PASS ｜ b 文本守恒(raw+norm) PASS ｜ c 白名单外零diff(回退字节+部件MD5) PASS'
                 % (om2, om_donor))
    lines.append('　　　d well-formed+zip完整+无悬空rId PASS ｜ e 幂等(二跑丢失集0) PASS ｜ 写盘 %d B' % os.path.getsize(path))
    lines.append('')
    return '\n'.join(lines), n_lost_el


def main():
    argv = sys.argv[1:]
    dry = '--dry-run' in argv
    argv = [a for a in argv if a != '--dry-run']
    report = None
    if '--report' in argv:
        kk = argv.index('--report'); report = argv[kk + 1]; del argv[kk:kk + 2]
    assert argv, '用法: python 工具/公式元素还原器.py <docx...> [--dry-run] [--report r.md]'
    base = os.path.dirname(os.path.abspath(__file__))          # 工具/
    root = os.path.dirname(base)                               # C:\提示词
    donor_dir = os.path.join(root, '工作区', '选必1成书修复-0905', '②工具', '副本_②B留档')
    out = []
    tot = 0
    for path in argv:
        dp = os.path.join(donor_dir, os.path.basename(path) + '.bak_标签行')
        if not os.path.exists(dp):
            raise RuntimeError('donor 缺失: ' + dp)
        r, n = process(path, dp, dry)
        tot += n
        out.append(r)
        print(r, flush=True)
    head = '=== 公式元素还原器 %s：八件丢失实例合计 %d ===\n' % ('（DRY）' if dry else '（EXEC）', tot)
    print(head, flush=True)
    if report:
        with open(report, 'a', encoding='utf-8') as f:
            f.write(head + '\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
