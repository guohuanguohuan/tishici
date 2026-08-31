# -*- coding: utf-8 -*-
"""任务B回归：字号双档改版.py exempt_ids GC假失败修复（持活引用）。
E卷副本（已改版完成，题号1..92，曾实测首跑3/复跑10处假失败）连跑3次：
判据＝退出码0（断言零假失败）＋zip成员级DIFF=0（幂等零改动，工具docstring幂等铁证口径）。
"""
import os, sys, shutil, subprocess, zipfile, hashlib

WS = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(WS))), '工具', '字号双档改版.py')
SRC = os.path.join(WS, '..', 'W-E卷92', 'E卷92-工作副本.docx')

def member_digest(path):
    with zipfile.ZipFile(path) as z:
        return {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}

cur = os.path.join(WS, '回归B-E卷-in.docx')
shutil.copyfile(SRC, cur)
prev_digest = member_digest(cur)
for k in (1, 2, 3):
    nxt = os.path.join(WS, '回归B-E卷-跑%d.docx' % k)
    r = subprocess.run([sys.executable, TOOL, cur, nxt, '--qcount', '92'],
                       capture_output=True, text=True, encoding='utf-8',
                       env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    print('第%d跑 退出码=%d' % (k, r.returncode))
    print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr[-3000:])
        raise SystemExit('第%d跑断言失败（假失败未修复或新缺陷）' % k)
    cur_digest = member_digest(nxt)
    diff = [n for n in cur_digest if cur_digest[n] != prev_digest.get(n)] + \
           [n for n in prev_digest if n not in cur_digest]
    print('zip成员级DIFF: %s（%d成员）' % (diff if diff else '0=幂等', len(cur_digest)))
    assert not diff, '第%d跑非幂等: %s' % (k, diff)
    prev_digest = cur_digest
    cur = nxt
print('任务B回归PASS：3连跑退出码全0＋断言零假失败＋成员级DIFF=0')
