# -*- coding: utf-8 -*-
"""SA·主会话补充指令：全册十件幂等重盖（§7先内容后页码时序合规收口）。
流程：①快照十件全zip成员＋pre-mtime；②跑 工具/册级连续页码.py --parts S盖章\parts.json
（P1=17新值，P2=20/P3=154/P4=5/P5=39/P6=221，starts不变——工具COM实测复算）；
③逐件成员DIFF断言（预期十件全DIFF=0；任一≠0即停）；④盖章mtime>最近内容改动mtime逐件断言；
⑤新生成记录表与盖章记录.md现行表逐行比对。"""
import io, os, re, subprocess, sys, zipfile, json, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SG = os.path.dirname(HERE)
TOOL = r'C:\提示词\工具\册级连续页码.py'
CFG = os.path.join(SG, 'parts.json')          # S盖章现行十件全册配置
REC_NEW = os.path.join(HERE, '盖章记录_全册重盖.md')
REC_MASTER = os.path.join(SG, '盖章记录.md')
SNAP = os.path.join(HERE, 'snap_full')

cfg = json.load(open(CFG, encoding='utf-8-sig'))
files = [f for it in cfg['parts'] for f in it['files']]
assert len(files) == 10, 'parts.json件数=%d' % len(files)

def members(p):
    with zipfile.ZipFile(p) as z:
        return {n: z.read(n) for n in z.namelist()}

def mt(p):
    return os.stat(p).st_mtime

# ① 快照＋pre-mtime
os.makedirs(SNAP, exist_ok=True)
pre = {}
for i, f in enumerate(files):
    d = members(f)
    with open(os.path.join(SNAP, '%02d.zip' % i), 'wb') as fh:
        fh.write(json.dumps({k: len(v) for k, v in d.items()}).encode())  # 占位长度表
    # 直接存成员字节（独立子夹）
    sd = os.path.join(SNAP, '%02d' % i)
    os.makedirs(sd, exist_ok=True)
    for n, b in d.items():
        with open(os.path.join(sd, n.replace('/', '__')), 'wb') as fh:
            fh.write(b)
    pre[os.path.basename(f)] = mt(f)
print('① 快照完成（十件，%d成员/件级）｜pre-mtime：' % sum(len(members(f)) for f in files))
for k, v in pre.items():
    print('   %s  %s' % (datetime.datetime.fromtimestamp(v).strftime('%m-%d %H:%M:%S'), k[:44]))

# ② 全册重盖
r = subprocess.run([sys.executable, TOOL, '--parts', CFG, '--record', REC_NEW],
                   capture_output=True, text=True, encoding='utf-8')
print('② 重盖输出：')
print('\n'.join(('   ' + ln) for ln in (r.stdout or r.stderr).strip().splitlines()))
assert r.returncode == 0, '工具非零退出'

# ③ 逐件成员DIFF
fail = False
print('③ 幂等断言（逐件全zip成员DIFF）：')
post_mts = {}
for i, f in enumerate(files):
    d2 = members(f)
    sd = os.path.join(SNAP, '%02d' % i)
    names = sorted(os.listdir(sd))
    diffs = []
    for n in names:
        orig = os.path.join(sd, n)
        member = n.replace('__', '/')
        if member not in d2 or d2[member] != open(orig, 'rb').read():
            diffs.append(member)
    order_note = '(成员序由重打包保持)'
    post_mts[os.path.basename(f)] = mt(f)
    tag = 'DIFF=0 ✓' if not diffs else 'DIFF≠0: %r' % diffs
    if diffs:
        fail = True
    print('   %s | %s' % (os.path.basename(f)[:46], tag))

# ④ 时序断言：盖章mtime晚于最近内容改动mtime（pre-mtime即内容/前章落地时刻）
print('④ 先内容后页码时序断言：')
seq_ok = True
for f in files:
    b = os.path.basename(f)
    if post_mts[b] <= pre[b]:
        seq_ok = False
        fail = True
        print('   ✗ %s 盖章mtime≤内容mtime' % b)
print('   十件盖章mtime全部晚于各自pre-mtime（内容/前章落地）：%s（本次重盖时刻=%s）'
      % ('✓' if seq_ok else '✗',
         datetime.datetime.fromtimestamp(max(post_mts.values())).strftime('%m-%d %H:%M:%S')))

# ⑤ 新记录表 vs 盖章记录.md现行表逐行比对
rows_new = [ln for ln in open(REC_NEW, encoding='utf-8').read().splitlines()
            if re.match(r'\| P\d \|', ln)]
rows_mas = [ln for ln in open(REC_MASTER, encoding='utf-8').read().splitlines()
            if re.match(r'\| P\d \|', ln)]
same = rows_new == rows_mas
print('⑤ 记录表比对：新生成%d行 vs 现行%d行 逐行%s' % (len(rows_new), len(rows_mas), '相同✓' if same else '不同!'))
if not same:
    for a, b in zip(rows_new, rows_mas):
        if a != b:
            print('   新: %s\n   旧: %s' % (a, b))
    fail = True
eq_line_new = [ln for ln in open(REC_NEW, encoding='utf-8').read().splitlines() if ln.startswith('恒等式')][0]
print('   新恒等式行：%s' % eq_line_new[:80])
assert '456' in eq_line_new, '恒等式合计≠456'

json.dump({'pre_mtime': pre, 'post_mtime': post_mts, 'table_rows_equal': same,
           'idempotent': not fail},
          open(os.path.join(HERE, '全册重盖断言.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, default=str)
print('=== 全册幂等重盖：%s ===' % ('全绿（十件DIFF=0、时序合规、表一致）' if not fail else '存在失败项——已按指令停报'))
sys.exit(0 if not fail else 1)
