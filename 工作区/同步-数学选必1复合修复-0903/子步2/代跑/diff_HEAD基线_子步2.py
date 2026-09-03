# -*- coding: utf-8 -*-
r"""diff_HEAD基线_子步2.py（子步2代跑③一次性脚本）——X2/B文本流diff复测。
基线＝git 18af5f6（修复前态；派发语「HEAD~1」时义＝b1f043d之父，因复审计提交181ced1落栈，
现 HEAD~1=b1f043d=修复后态，故取18af5f6——提交链证据落报告）。
口径同 子步1/diff_文本流.py：w:t/m:t 文档序字符流；B＝导航表子树流单独比对＋剔除后主流比对；
容器级＝zip成员清单一致＋document.xml以外成员逐字节恒等；计数对账八项。
"""
import sys, io, os, zipfile, hashlib, json, subprocess, re
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)
def ptext(p): return ''.join(t.text or '' for t in p.iter(q('t')))
def nospc(s): return re.sub(r'[\s　]+', '', s or '')
def is_navtbl(tbl):
    tr = tbl.find(q('tr'))
    if tr is None: return False
    cells = [nospc(ptext(tc)) for tc in tr.findall(q('tc'))]
    return any('节名' in c for c in cells) and any('题量' in c for c in cells) and any('题型组数' in c for c in cells)

TEXT_TAGS = {q('t'), qm('t')}
BASE_REPO = r'C:\提示词'
PROD = r'C:\提示词\高中数学\高中数学同步'
REV = '18af5f6'
HERE = os.path.dirname(os.path.abspath(__file__))

FILES = {
    'X2': ('人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', False),
    'B':  ('人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', True),
}

def stream(root, skip_el=None):
    parts = []
    for el in root.iter():
        if skip_el is not None and el is skip_el:
            parts.append('⟪NAVTABLE_SKIPPED⟫')
            continue
        if el.tag in TEXT_TAGS:
            parts.append(el.text or '')
    return ''.join(parts)

def counts(root):
    return {
        'w:p': len(root.findall('.//' + q('p'))),
        'w:tbl': len(root.findall('.//' + q('tbl'))),
        'w:t': len(root.findall('.//' + q('t'))),
        'm:t': len(root.findall('.//' + qm('t'))),
        'm:oMath': len(root.findall('.//' + qm('oMath'))),
        'w:drawing': len(root.findall('.//' + q('drawing'))),
        'sectPr': len(root.findall('.//' + q('sectPr'))),
        'w:shd': len(root.findall('.//' + q('shd'))),
    }

def one(code, orig, fixed, nav_split):
    zo, zf = zipfile.ZipFile(orig), zipfile.ZipFile(fixed)
    names_o = [i.filename for i in zo.infolist()]
    names_f = [i.filename for i in zf.infolist()]
    member_eq = names_o == names_f
    others_eq = True
    diff_members = []
    for n in names_o:
        ho = hashlib.sha256(zo.read(n)).hexdigest()
        hf = hashlib.sha256(zf.read(n)).hexdigest()
        if ho != hf:
            diff_members.append(n)
            if n != 'word/document.xml':
                others_eq = False
    ro = etree.fromstring(zo.read('word/document.xml'))
    rf = etree.fromstring(zf.read('word/document.xml'))
    zo.close(); zf.close()
    bo, bf = ro.find(q('body')), rf.find(q('body'))
    res = {'member_list_eq': member_eq, 'non_document_members_eq': others_eq,
           'changed_members': diff_members}
    if nav_split:
        nav_o = next((el for el in bo if etree.QName(el).localname == 'tbl' and is_navtbl(el)), None)
        nav_f = next((el for el in bf if etree.QName(el).localname == 'tbl' and is_navtbl(el)), None)
        res['nav_present'] = (nav_o is not None, nav_f is not None)
        so = stream(bo, skip_el=nav_o); sf = stream(bf, skip_el=nav_f)
        res['main_stream_eq_ex_nav'] = so == sf
        res['nav_stream_eq'] = stream(nav_o) == stream(nav_f)
        res['main_stream_len'] = (len(so), len(sf))
    else:
        so, sf = stream(bo), stream(bf)
        res['stream_eq'] = so == sf
        res['stream_len'] = (len(so), len(sf))
        if so != sf:
            k = next((i for i in range(min(len(so), len(sf))) if so[i] != sf[i]), min(len(so), len(sf)))
            res['first_diff_at'] = k
            res['diff_ctx'] = (so[max(0, k - 20):k + 20], sf[max(0, k - 20):k + 20])
    co, cf = counts(ro), counts(rf)
    res['counts_orig'] = co; res['counts_fixed'] = cf
    res['counts_eq'] = {k: (co[k], cf[k], co[k] == cf[k]) for k in co}
    return res

if __name__ == '__main__':
    out = {}
    for code, (fn, nav) in FILES.items():
        rel = '高中数学/高中数学同步/' + fn
        base_path = os.path.join(HERE, code + '_修复前_18af5f6.docx')
        raw = subprocess.run(['git', '-C', BASE_REPO, 'show', '%s:%s' % (REV, rel)],
                             capture_output=True, check=True).stdout
        open(base_path, 'wb').write(raw)
        cur = os.path.join(PROD, fn)
        r = one(code, base_path, cur, nav)
        r['baseline_bytes'] = len(raw)
        r['current_bytes'] = os.path.getsize(cur)
        r['current_sha256_12'] = hashlib.sha256(open(cur, 'rb').read()).hexdigest()[:12]
        out[code] = r
        ok = r['member_list_eq'] and r['non_document_members_eq'] and \
            (r.get('stream_eq') if not nav else (r['main_stream_eq_ex_nav'] and r['nav_stream_eq']))
        print('[%s] 文本流diff=0判定: %s | 变更成员=%s | 字节 %d→%d | 现件sha256前12=%s'
              % (code, 'PASS' if ok else 'FAIL', r['changed_members'],
                 r['baseline_bytes'], r['current_bytes'], r['current_sha256_12']))
        if not nav and not r.get('stream_eq', True):
            print('   首差异@%s: %r vs %r' % (r.get('first_diff_at'), r['diff_ctx'][0], r['diff_ctx'][1]))
        ce = {k: v for k, v in r['counts_eq'].items() if not v[2]}
        print('   计数差异项: %s' % (ce if ce else '全等'))
    dst = os.path.join(HERE, 'diff_HEAD基线实测.json')
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('落盘:', dst)
