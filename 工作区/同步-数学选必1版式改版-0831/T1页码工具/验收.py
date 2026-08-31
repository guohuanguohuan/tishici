# -*- coding: utf-8 -*-
"""T1验收主脚本（编排器，自身不做进程内COM——COM阶段各自独立短生命周期子进程，COM拆解噪音互不传染）：
P3+P6盖章跑通（不动点收敛）→XML断言→幂等二跑成员级diff→阶段4子进程（页数源+3页抽查）→节页码定位5组测试
→阶段6子进程（手工抽查2节）→N11签名单元测试。一切只在T1子文件夹副本上做，输出全部实测数字。"""
import subprocess, sys, os, io, zipfile, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

BASE = os.path.dirname(os.path.abspath(__file__))
TOOL_A = r'C:\Users\28120\Desktop\提示词\工具\册级连续页码.py'
TOOL_B = r'C:\Users\28120\Desktop\提示词\工具\节页码定位.py'

EXPECT = {  # 副本路径: (盖章收敛后页数[COM实测], 期望start, tag, N)
    # T1实测发现：旧件页脚21半点→9pt(18半点)后正文区微增，B临界repaginate 79→78页（footer距边=下边距=850缇
    # 零余量、页脚行高参与正文区计算）；工具内已做不动点迭代收敛。以下为收敛终值（P3=154页）。
    'P3/B.docx': (78, 1, '第1章·讲练', 154),
    'P3/C.docx': (76, 79, '第1章·讲练', 154),
    'P6/E.docx': (50, 1, '第2章·讲练', 205),
    'P6/F.docx': (53, 51, '第2章·讲练', 205),
    'P6/G.docx': (38, 104, '第2章·讲练', 205),
    'P6/H.docx': (64, 142, '第2章·讲练', 205),
}

def run(cmd):
    p = subprocess.run([sys.executable] + cmd, capture_output=True, cwd=BASE)
    return p.returncode, p.stdout.decode('utf-8', 'replace'), p.stderr.decode('utf-8', 'replace')

def word_pids():
    p = subprocess.run(['tasklist', '/FO', 'CSV'], capture_output=True)
    out = p.stdout.decode('gbk', 'replace')
    return {ln.split('","')[1] for ln in out.splitlines() if ln.startswith('"WINWORD.EXE')}

def sweep_word(before):
    """子进程结束后清扫：新出现的WINWORD＝本编排器子进程残留（自己的实例），逐个结束。"""
    new = word_pids() - before
    for pid in new:
        subprocess.run(['taskkill', '/PID', pid, '/F'], capture_output=True)
        print('  [残留清查] 结束本编排器拉起的Word实例 PID=%s' % pid)
    return not new

def members(path):
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}

def check_one(rel):
    path = os.path.join(BASE, rel)
    base_pages, start, tag, N = EXPECT[rel]
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        footers = [n for n in names if re.fullmatch(r'word/footer\d+\.xml', n)]
        f = z.read('word/footer1.xml').decode('utf-8')
        d = z.read('word/document.xml').decode('utf-8')
        s = z.read('word/settings.xml').decode('utf-8')
    a = []
    a.append(('唯一页脚部件数=1', len(footers) == 1, 'footers=%s' % footers))
    vis = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', f))
    exp_vis = '%s（共%d页）　第%d页' % (tag, N, start)
    a.append(('页脚可见文本=件标识（共N页）＋全角空格＋第start页', vis == exp_vis, '%r' % vis))
    a.append(('PAGE复杂域唯一（begin=end=separate=1）',
              f.count('fldCharType="begin"') == 1 and f.count('fldCharType="end"') == 1
              and f.count('fldCharType="separate"') == 1,
              'b/e/s=%d/%d/%d' % (f.count('fldCharType="begin"'), f.count('fldCharType="end"'),
                                  f.count('fldCharType="separate"'))))
    a.append(('instrText含PAGE', ' PAGE ' in f, ''))
    a.append(('无fldSimple', 'fldSimple' not in f, ''))
    a.append(('无NUMPAGES域', 'NUMPAGES' not in f, ''))
    a.append(('页码18半点(9pt)且无他值', set(re.findall(r'<w:sz w:val="(\d+)"/>', f)) == {'18'},
              'sz集合=%s' % sorted(set(re.findall(r'<w:sz w:val="(\d+)"/>', f)))))
    a.append(('中文字体宋体西文TNR', 'w:eastAsia="宋体"' in f and 'Times New Roman' in f, ''))
    a.append(('页脚左对齐jc=left', '<w:jc w:val="left"/>' in f, ''))
    a.append(('sectPr pgNumType start=%d' % start,
              re.findall(r'<w:pgNumType w:start="(\d+)"/>', d) == [str(start)],
              '实=%s' % re.findall(r'<w:pgNumType w:start="(\d+)"/>', d)))
    a.append(('pgMar footer=850', 'w:footer="850"' in d and not re.search(r'w:footer="(?!850")\d+"', d),
              '实=%s' % re.findall(r'w:footer="(\d+)"', d)))
    a.append(('无titlePg', '<w:titlePg' not in d, ''))
    a.append(('settings含updateFields', '<w:updateFields' in s, ''))
    bad = [name for name, ok, ev in a if not ok]
    for name, ok, ev in a:
        if not ok:
            print('  ✗ %s | %s | %s' % (rel, name, ev))
    return len(a), len(a) - len(bad)

print('====== 阶段1：盖章（P3两件＋P6四件，一次跑，含skip_files跳过行＋不动点收敛）======')
before = word_pids()
rc, out, err = run([TOOL_A, '--parts', '验收parts.json', '--record', '盖章记录.md'])
sweep_word(before)
print(out.strip())
if err.strip():
    print('stderr:', err.strip())
assert rc == 0, '盖章退出码=%d' % rc
assert '跳过配页件' in out and '配页件_封面副本.docx' in out, 'skip_files跳过行缺失'
assert '收敛' in out, '不动点收敛行缺失'

print('====== 阶段2：XML断言（6件×13项）======')
tot = ok = 0
for rel in EXPECT:
    t, o = check_one(rel)
    tot += t; ok += o
    print('  %s: %d/%d' % (rel, o, t))
assert ok == tot, 'XML断言 %d/%d' % (ok, tot)
print('  XML断言合计 %d/%d 全绿' % (ok, tot))

print('====== 阶段3：幂等二跑（zip成员级diff）======')
snap1 = {rel: members(os.path.join(BASE, rel)) for rel in EXPECT}
before = word_pids()
rc, out2, err2 = run([TOOL_A, '--parts', '验收parts.json', '--record', '盖章记录.md'])
sweep_word(before)
assert rc == 0, '二跑退出码=%d' % rc
diff_total = 0
for rel in EXPECT:
    m2 = members(os.path.join(BASE, rel))
    m1 = snap1[rel]
    same_set = set(m1) == set(m2)
    diffs = [n for n in m1 if m1.get(n) != m2.get(n)] + [n for n in m2 if n not in m1]
    diff_total += len(diffs)
    print('  %s: 成员数=%d 集合一致=%s 内容差异成员=%d %s'
          % (rel, len(m1), same_set, len(diffs), diffs[:4] if diffs else ''))
assert diff_total == 0, '幂等失败：差异成员合计=%d' % diff_total
print('  幂等铁证：6件全部zip成员逐字节DIFF=0（含document/footer1/settings等）')

print('====== 阶段4：COM实测页数为源＋缓存值抽查3页（独立子进程）======')
before = word_pids()
rc, out, err = run([os.path.join(BASE, '阶段4_缓存抽查.py')])
sweep_word(before)
print(out.strip())
if '全过' not in out:
    print('stderr:', err.strip())
    raise SystemExit('阶段4未通过')
res4 = json.load(open(os.path.join(BASE, '阶段4结果.json'), encoding='utf-8'))
assert len(res4) == 6, '阶段4结果件数=%d' % len(res4)

print('====== 阶段5：节页码定位——B副本重测＋0命中批量修复＋strict＋record补齐＋parts.json直传 ======')
# 5a 单件模式（B，start=1）
rc, out, err = run([TOOL_B, 'P3/B.docx', '1', '--name', 'B讲上'])
assert rc == 0, '5a退出码=%d %s' % (rc, err)
rows = [r for r in out.splitlines() if r and not r.startswith('#')]
print('  5a 单件模式: 退出码0 节行数=%d 首行=%s 末行=%s' % (len(rows), rows[0][:56], rows[-1][:56]))
open(os.path.join(BASE, '5a行.tsv'), 'w', encoding='utf-8').write('\n'.join(rows) + '\n')
for r in rows:
    c = r.split('\t')
    assert int(c[4]) == int(c[3]) + 1 - 1, '5a行异常 %r' % r
print('  5a 恒等: 部分内页码=件内页+start−1 全部成立（start=1，%d节）' % len(rows))
# 5b 批量模式：B(记录补start)＋X1衔接(0命中)＋I1清单(0命中) → 警告跳过、退出码0
open(os.path.join(BASE, '批量配置.tsv'), 'w', encoding='utf-8').write(
    'P3/B.docx\t\tB讲上\nX1衔接副本.docx\t1\tX1衔接\nI1清单副本.docx\t1\tI1清单\n')
rc, out, err = run([TOOL_B, '@批量配置.tsv', '--record', '盖章记录.md'])
b_rows = [r for r in out.splitlines() if r.startswith('B讲上\t') and r.count('\t') == 4]
print('  5b 批量(记录补start): 退出码=%d B节行数=%d X1/I1跳过警告数=%d' % (rc, len(b_rows), err.count('0命中')))
assert rc == 0, '5b退出码=%d（0命中不应阻断整批）' % rc
assert err.count('0命中') == 2 and len(b_rows) == len(rows), '5b行为异常'
# 5c 同配置 --strict → 非零退出（旧口径恢复）
rc3, out3, err3 = run([TOOL_B, '@批量配置.tsv', '--record', '盖章记录.md', '--strict'])
print('  5c --strict: 退出码=%d（预期非零）' % rc3)
assert rc3 != 0, '5c strict应非零退出'
# 5d 缺start且无record → 报错退出2
open(os.path.join(BASE, '无record配置.tsv'), 'w', encoding='utf-8').write('P3/C.docx\t\tC讲下\n')
rc4, out4, err4 = run([TOOL_B, '@无record配置.tsv'])
print('  5d 缺start无record: 退出码=%d（预期2）' % rc4)
assert rc4 == 2, '5d应退出2'
# 5e parts.json直传＋record（M2同源接驳）
rc5, out5, err5 = run([TOOL_B, '@验收parts.json', '--record', '盖章记录.md'])
lv = [r for r in out5.splitlines() if r and not r.startswith('#') and r.count('\t') == 2]
print('  5e parts.json直传: 退出码=%d 件级行=%d starts=%s' % (rc5, len(lv), [r.split('\t')[1] for r in lv]))
assert rc5 == 0 and len(lv) == 6
assert [r.split('\t')[1] for r in lv] == ['1', '79', '1', '51', '104', '142'], '5e starts级联与record不符'

print('====== 阶段6：手工抽查2节（独立子进程，不走路由正则）======')
before = word_pids()
rc, out, err = run([os.path.join(BASE, '阶段6_手工抽查.py')])
sweep_word(before)
print(out.strip())
if '完成' not in out:
    print('stderr:', err.strip())
    raise SystemExit('阶段6未通过')
res6 = json.load(open(os.path.join(BASE, '阶段6结果.json'), encoding='utf-8'))
assert len(res6['picked']) == 2

print('====== 阶段7：N11签名单元测试（独立子进程）======')
rc, out, err = run([os.path.join(BASE, '阶段7_签名单测.py')])
print(out.strip())
if '阶段7完成' not in out:
    print('stderr:', err.strip())
    raise SystemExit('阶段7未通过')

print('====== 阶段8：页脚域拆除单测（独立子进程）======')
rc, out, err = run([os.path.join(BASE, '阶段8_域拆除单测.py')])
print(out.strip())
if '阶段8完成' not in out:
    print('stderr:', err.strip())
    raise SystemExit('阶段8未通过')
print('全部验收阶段（1-8）完成。')
