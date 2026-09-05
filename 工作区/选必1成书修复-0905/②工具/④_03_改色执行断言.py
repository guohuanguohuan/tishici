# -*- coding: utf-8 -*-
"""④轮步骤3：灰底改色 C9C9C9→C7C7C7 执行＋三重断言（副本_④轮 12 件）。
①白名单零diff（YS-2）：逐 zip 成员比对——构造性证明 前态.replace('w:fill="C9C9C9"','w:fill="C7C7C7"')＝后态，
  其余逐字节一致；成员名清单全等。
②YS-1 三族守恒：w:t／m:oMath＋m:t＋m:oMathPara／w:drawing（wp:inline、wp:anchor 分记）改前改后全等。
③幂等：改后再跑工具 --dry-run，C9C9C9 计数＝0。
计数对账：逐件改色数与 dry-run 报告（④_改色_dryrun.txt）逐件全等。落盘 ④_改色_执行对账.json。"""
import io, sys, os, re, json, subprocess, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'C:\提示词\工作区\选必1成书修复-0905\②工具'
DST = BASE + r'\副本_④轮'
REP = BASE + r'\报告'
TOOL = r'C:\提示词\工具\灰底改色.py'
FILES = [
    ('I1清单1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', 1353),
    ('X1衔接1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', 245),
    ('B讲练1上', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', 880),
    ('C讲练1下', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', 466),
    ('I2清单2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', 1085),
    ('X2衔接2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', 150),
    ('E讲练92', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', 354),
    ('F讲练90', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', 340),
    ('G讲练68', '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', 347),
    ('H讲练89', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', 67),
    ('SM使用说明', '人教B版选必1·使用说明.docx', 7),
    ('TOC册目录页', '人教B版选必1·册目录页.docx', 0),
]
OLD = b'w:fill="C9C9C9"'
NEW = b'w:fill="C7C7C7"'

def fam_counts(path):
    z = zipfile.ZipFile(path)
    c = {'w:t': 0, 'm:oMath': 0, 'm:t': 0, 'm:oMathPara': 0, 'wp:inline': 0, 'wp:anchor': 0}
    pats = {k: re.compile((('<%s' % k) + r'(?:\s[^>]*)?>').encode()) for k in c}
    for n in z.namelist():
        if not (n.startswith('word/') and n.endswith('.xml')):
            continue
        b = z.read(n)
        for k, p in pats.items():
            c[k] += len(p.findall(b))
    z.close()
    return c

def snapshot(path):
    z = zipfile.ZipFile(path)
    data = {n: z.read(n) for n in z.namelist()}
    z.close()
    return data

ok_all = True
report = {}
for code, fn, dry_expect in FILES:
    p = os.path.join(DST, fn)
    pre = snapshot(p)
    fam_pre = fam_counts(p)
    r = subprocess.run([sys.executable, TOOL, 'C9C9C9', 'C7C7C7', p],
                       capture_output=True, text=True, encoding='utf-8')
    tool_line = (r.stdout or '').strip().splitlines()[-1] if r.stdout else ''
    post = snapshot(p)
    # ①成员清单全等＋白名单零diff
    names_ok = (sorted(pre) == sorted(post))
    diff_members, replaced_total, byte_ok = [], 0, names_ok
    for n in pre:
        if pre[n] == post[n]:
            continue
        diff_members.append(n)
        cnt = pre[n].count(OLD)
        replaced_total += cnt
        construct = pre[n].replace(OLD, NEW)
        if construct != post[n]:
            byte_ok = False
    # ②三族守恒
    fam_post = fam_counts(p)
    fam_ok = (fam_pre == fam_post)
    # ③幂等（dry-run 旧值=0）
    r2 = subprocess.run([sys.executable, TOOL, 'C9C9C9', 'C7C7C7', p, '--dry-run'],
                        capture_output=True, text=True, encoding='utf-8')
    idem_ok = 'C9C9C9→C7C7C7 0 处' in (r2.stdout or '')
    cnt_ok = (replaced_total == dry_expect)
    ok = names_ok and byte_ok and fam_ok and idem_ok and cnt_ok
    ok_all = ok_all and ok
    report[code] = {'file': fn, 'dry_expect': dry_expect, 'replaced': replaced_total,
                    'diff_members': diff_members, 'names_ok': names_ok, 'byte_ok': byte_ok,
                    'fam_pre': fam_pre, 'fam_post': fam_post, 'fam_ok': fam_ok,
                    'idem_ok': idem_ok, 'cnt_ok': cnt_ok, 'ok': ok, 'tool_line': tool_line}
    print('%-10s 换色 %4d（期望 %4d）｜成员全等 %s｜白名单零diff %s｜三族守恒 %s｜幂等 %s｜%s'
          % (code, replaced_total, dry_expect, names_ok, byte_ok, fam_ok, idem_ok,
             'PASS' if ok else '←FAIL'))
with open(os.path.join(REP, '④_改色_执行对账.json'), 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print('合计 12 件全PASS＝%s' % ok_all)
sys.exit(0 if ok_all else 1)
