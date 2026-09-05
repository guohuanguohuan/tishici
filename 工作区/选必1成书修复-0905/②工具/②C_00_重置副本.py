# -*- coding: utf-8 -*-
"""②C_00_重置副本.py — ②-C 阶段前置：弃 ②-B 已跑副本（改名留档），
从同步盘（②-B 回写终态）重新复制十件进 ②工具/副本/。
逐件超时重试（Resilio/RealTimeSync 双客户端瞬锁），落 MD5 对照表。"""
import sys, io, os, shutil, time, hashlib, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SRC = os.path.join(ROOT, '高中数学', '高中数学同步')
BASE = os.path.join(ROOT, '工作区', '选必1成书修复-0905', '②工具')
DST = os.path.join(BASE, '副本')
ARCH = os.path.join(BASE, '副本_②B留档')

NAMES = [
    '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
    '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx',
    '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx',
]


def md5(p, tries=6):
    for k in range(tries):
        try:
            h = hashlib.md5()
            with open(p, 'rb') as f:
                for chunk in iter(lambda: f.read(1 << 20), b''):
                    h.update(chunk)
            return h.hexdigest()
        except PermissionError:
            time.sleep(5)
    return 'LOCKED'


print('=== ① 旧副本留档 ===', flush=True)
if os.path.isdir(ARCH):
    print('  留档目录已存在，跳过改名（不覆盖）:', ARCH, flush=True)
elif os.path.isdir(DST):
    shutil.move(DST, ARCH)
    print('  %s -> %s' % (DST, ARCH), flush=True)
else:
    print('  无旧副本目录', flush=True)
os.makedirs(DST, exist_ok=True)
print('  新副本目录就绪:', DST, flush=True)

print('=== ② 逐件复制（每件最多 8 试、瞬锁退避 6s）===', flush=True)
rows = []
allok = True
for n in NAMES:
    s = os.path.join(SRC, n)
    d = os.path.join(DST, n)
    ok = False
    for att in range(1, 9):
        try:
            if os.path.exists(d):
                os.remove(d)
            shutil.copy2(s, d)
            ok = True
            break
        except PermissionError as e:
            print('   %s att%d 瞬锁: %s' % (n[:24], att, e), flush=True)
            time.sleep(6)
    if not ok:
        allok = False
        print('  !! FAIL 复制失败:', n, flush=True)
        rows.append((n, 'FAIL', '', ''))
        continue
    ms, md = md5(s), md5(d)
    same = (ms == md)
    allok = allok and same
    print('  %s %s  %d B  src=%s dst=%s' % ('OK ' if same else '!!DIFF', n[:30],
                                            os.path.getsize(d), ms[:12], md[:12]), flush=True)
    rows.append((n, 'PASS' if same else 'DIFF', ms, md))

out = os.path.join(BASE, '报告', '②C_副本重置_MD5.md')
with open(out, 'w', encoding='utf-8') as f:
    f.write('# ②C 副本重置（同步盘→②工具/副本）MD5 对照\n\n')
    f.write('- 时点：%s\n- 源＝同步盘 `高中数学\\高中数学同步\\`（②-B 回写终态）\n' % time.strftime('%Y-%m-%d %H:%M:%S'))
    f.write('- 旧 ②-B 已跑副本改名留档 `副本_②B留档\\`（不再参与本轮）\n- 复制策略：每件最多 8 试、PermissionError 退避 6s（Resilio/RealTimeSync 瞬锁）\n\n')
    f.write('| 件 | 复制＋MD5 一致 | 字节 | MD5（源＝副本） |\n|---|---|---|---|\n')
    for (n, st, ms, md) in rows:
        sz = os.path.getsize(os.path.join(DST, n)) if os.path.exists(os.path.join(DST, n)) else 0
        f.write('| %s | %s | %d | %s |\n' % (n, st, sz, ms))
    f.write('\n结论：%s\n' % ('十件全部复制成功且源/副本 MD5 逐件一致 PASS' if allok else '存在失败/差异，见上表'))
print('=== 报告落盘:', out, flush=True)
print('SUMMARY allok=%s' % allok, flush=True)
