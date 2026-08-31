# -*- coding: utf-8 -*-
"""任务A回归：题号块三段式.py --qstart 补丁。
F卷副本（已改版完成，题号93..182，base模式）跑 --qstart 93 ＝ 幂等零改动；
X2副本（衔接件，题号1..13，linkage模式）跑默认qstart ＝ 幂等零改动。
判据：首跑全计数为0（幂等跳过＝题量）＋document.xml成员字节前后零变化＋二跑字节稳定。
"""
import os, sys, shutil, subprocess, zipfile, hashlib

WS = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(WS))), '工具', '题号块三段式.py')
SRC_F = os.path.join(WS, '..', 'W-F卷90', 'F卷90-步骤11自检后.docx')
SRC_X2 = os.path.join(WS, '..', 'W-X2衔接2', 'X2工作副本.docx')

def docxml_sha(path):
    with zipfile.ZipFile(path) as z:
        return hashlib.sha256(z.read('word/document.xml')).hexdigest()

def run_case(name, src, args, expect_q):
    dst = os.path.join(WS, '回归A-%s.docx' % name)
    md = os.path.join(WS, '回归A-%s-登记.md' % name)
    shutil.copyfile(src, dst)
    h0 = docxml_sha(dst)
    outs = []
    for k in (1, 2):
        r = subprocess.run([sys.executable, TOOL, dst, md] + args,
                           capture_output=True, text=True, encoding='utf-8',
                           env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
        assert r.returncode == 0, '%s 第%d跑退出码%d\n%s\n%s' % (name, k, r.returncode, r.stdout, r.stderr)
        outs.append(r.stdout.strip())
    h1 = docxml_sha(dst)
    print('== %s %s ==' % (name, args))
    for o in outs:
        print(o)
    print('document.xml sha256: 前=%s 跑1后=%s 跑2后=%s' % (h0[:16], h1[:16], h1[:16]))
    line1 = outs[0]
    assert ('幂等跳过 %d' % expect_q) in line1, '幂等跳过数不符: ' + line1
    for token in ('改写 0', '缩底纹 0', '退化 0', '重建run 0', '补底纹 0', '补加粗 0'):
        assert token in line1, '计数非零: ' + token + ' | ' + line1
    assert h1 == h0, '%s document.xml字节变化（零改动判据失败）' % name
    assert outs[0] == outs[1], '两跑stdout不一致'
    print('%s: PASS（幂等零改动，document.xml字节前后恒等）\n' % name)

run_case('F93', SRC_F, ['--qstart', '93'], 90)
run_case('X2', SRC_X2, ['--linkage'], 13)
print('任务A回归全部PASS')
