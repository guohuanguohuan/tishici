# -*- coding: utf-8 -*-
r"""T3执行_底纹减法.py（子步2一次性执行脚本）——六讲练件执行减法＋独立复核＋写回。
逐件：复制原件入 执行/ → 底纹去除器执行（fail-closed）→ 独立核验（文字流diff=0／容器成员／
计数工具旧签名留痕）→ 写回产出文件夹覆盖 → sha256 登记。全部数字落盘 T3执行结果.json。
"""
import sys, io, os, re, zipfile, json, shutil, hashlib, subprocess
if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def q(t): return '{%s}%s' % (W, t)
def qm(t): return '{%s}%s' % (M, t)

PROD = r'C:\提示词\高中数学\高中数学同步'
TOOL = r'C:\提示词\工具\底纹去除器.py'
COUNT7 = r'C:\提示词\工具\六类底纹计数.py'
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, '执行')
os.makedirs(WORK, exist_ok=True)

FILES = {
    'B': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    'C': '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    'E': '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    'F': '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    'G': '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    'H': '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
}

TEXT_TAGS = {q('t'), qm('t')}

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

def stream_counts(path):
    z = zipfile.ZipFile(path)
    doc = etree.fromstring(z.read('word/document.xml'))
    names = [i.filename for i in z.infolist()]
    hashes = {n: hashlib.sha256(z.read(n)).hexdigest() for n in names}
    z.close()
    s = ''.join((el.text or '') for el in doc.iter() if el.tag in TEXT_TAGS)
    c = {
        'w:p': len(doc.findall('.//' + q('p'))),
        'w:tbl': len(doc.findall('.//' + q('tbl'))),
        'w:r': len(doc.findall('.//' + q('r'))),
        'w:t': len(doc.findall('.//' + q('t'))),
        'm:r': len(doc.findall('.//' + qm('r'))),
        'm:t': len(doc.findall('.//' + qm('t'))),
        'm:oMath': len(doc.findall('.//' + qm('oMath'))),
        'w:drawing': len(doc.findall('.//' + q('drawing'))),
        'sectPr': len(doc.findall('.//' + q('sectPr'))),
        'w:shd': len(doc.findall('.//' + q('shd'))),
    }
    return s, c, names, hashes

def count7_key_lines(path, rpt):
    """计数工具旧签名留痕：返回关键行文本（题号块/芯片/答案值/条目/题干底纹/标题两色/结论）。"""
    r = subprocess.run([sys.executable, COUNT7, path, rpt],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    out = r.stdout
    keep = []
    for ln in out.splitlines():
        if re.search(r'题号块 |块标签run|答案值/需背|条目号run|第一子层run|⑦题干底纹 段级|标题整行底纹 段级|^结论', ln):
            keep.append(ln.strip())
    return keep

if __name__ == '__main__':
    results = {}
    for code, fn in FILES.items():
        src = os.path.join(PROD, fn)
        orig = os.path.join(WORK, code + '_减前.docx')
        fixed = os.path.join(WORK, code + '_减后.docx')
        rpt = os.path.join(WORK, code + '_执行报告.txt')
        c7rpt = os.path.join(WORK, code + '_减后_七类计数留痕.txt')
        shutil.copy2(src, orig)
        pre_sha = sha(orig)
        s0, c0, n0, h0 = stream_counts(orig)
        # 执行（fail-closed：断言不过退出码3且不写）
        r = subprocess.run([sys.executable, TOOL, orig, fixed, '--report', rpt],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        if r.returncode != 0 or not os.path.exists(fixed):
            results[code] = {'verdict': 'TOOL_REFUSE', 'stderr': r.stderr[-400:], 'stdout_tail': r.stdout[-400:]}
            print('[%s] 工具拒写/异常，未写回！' % code)
            continue
        s1, c1, n1, h1 = stream_counts(fixed)
        diff_members = [n for n in n0 if h0[n] != h1.get(n)]
        rec = {
            'pre_sha12': pre_sha[:12], 'post_sha12': sha(fixed)[:12],
            'stream_eq': s0 == s1,
            'stream_len': (len(s0), len(s1)),
            'member_list_eq': n0 == n1,
            'changed_members': diff_members,
            'counts_eq': {k: (c0[k], c1[k], c0[k] == c1[k]) for k in c0},
            'shd_delta': c0['w:shd'] - c1['w:shd'],
            'bytes': (os.path.getsize(orig), os.path.getsize(fixed)),
        }
        rec['count7_lines'] = count7_key_lines(fixed, c7rpt)
        ok = (rec['stream_eq'] and rec['member_list_eq'] and diff_members == ['word/document.xml']
              and all(v[2] for k, v in rec['counts_eq'].items() if k != 'w:shd'))
        rec['verdict'] = 'PASS' if ok else 'CHECK'
        if ok:
            shutil.copy2(fixed, src)          # 写回产出文件夹
            rec['written_back'] = True
            rec['final_sha12'] = sha(src)[:12]
        else:
            rec['written_back'] = False
        results[code] = rec
        print('[%s] %s｜文字流diff=0:%s｜变更成员=%s｜w:shd减%d｜写回=%s｜%s→%s'
              % (code, rec['verdict'], rec['stream_eq'], diff_members, rec['shd_delta'],
                 rec['written_back'], rec['pre_sha12'], rec['post_sha12']))
    dst = os.path.join(HERE, 'T3执行结果.json')
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print('落盘:', dst)
