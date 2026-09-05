# -*- coding: utf-8 -*-
"""②F_00_重置副本.py — ②-F 公式修复轮前置：清空 ②工具/副本/（②-D 作废态），
从同步盘（②-C 终态）复制 8 件修复对象（清单件两件不碰不复制）。
逐件超时重试（Resilio/RealTimeSync 瞬锁），落 MD5 对照表 → 报告/②F_00_副本重置_MD5.md"""
import sys, io, os, shutil, time, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SRC = os.path.join(ROOT, '高中数学', '高中数学同步')
BASE = os.path.join(ROOT, '工作区', '选必1成书修复-0905', '②工具')
DST = os.path.join(BASE, '副本')

NAMES = [
    '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx',
    '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
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


print('=== ① 清空旧副本（②-D 作废态，python shutil）===', flush=True)
if os.path.isdir(DST):
    for k in range(6):
        try:
            shutil.rmtree(DST)
            break
        except PermissionError as e:
            print('  清空瞬锁 att%d: %s' % (k, e), flush=True)
            time.sleep(6)
    else:
        raise RuntimeError('副本目录清空失败（持续锁）: ' + DST)
print('  已清空:', DST, flush=True)
os.makedirs(DST, exist_ok=True)

print('=== ② 逐件复制（每件最多 8 试、瞬锁退避 6s）===', flush=True)
rows = []
allok = True
for n in NAMES:
    s = os.path.join(SRC, n)
    d = os.path.join(DST, n)
    ok = False
    for att in range(1, 9):
        try:
            shutil.copy2(s, d)
            ok = True
            break
        except PermissionError as e:
            print('   %s att%d 瞬锁: %s' % (n[:24], att, e), flush=True)
            time.sleep(6)
    if not ok:
        allok = False
        print('  !! FAIL 复制失败:', n, flush=True)
        rows.append((n, 'FAIL', ''))
        continue
    ms, md = md5(s), md5(d)
    same = (ms == md)
    allok = allok and same
    print('  %s %s  %d B  md5=%s' % ('OK ' if same else '!!DIFF', n[:30], os.path.getsize(d), md[:12]), flush=True)
    rows.append((n, 'PASS' if same else 'DIFF', md))

out = os.path.join(BASE, '报告', '②F_00_副本重置_MD5.md')
with open(out, 'w', encoding='utf-8') as f:
    f.write('# ②F 副本重置（同步盘 ②-C 终态 → ②工具/副本）MD5 对照\n\n')
    f.write('- 时点：%s\n- 源＝同步盘 `高中数学\\高中数学同步\\`（②-C 终态，修复对象）\n' % time.strftime('%Y-%m-%d %H:%M:%S'))
    f.write('- 旧 ②-D 作废态副本整体清空（python shutil.rmtree）\n- 清单件两件 T5 零处置，不复制不碰\n')
    f.write('- 复制策略：每件最多 8 试、PermissionError 退避 6s（同步锁范式 300s×3 上限内）\n\n')
    f.write('| 件 | 复制＋MD5 一致 | 字节 | MD5 |\n|---|---|---|---|\n')
    for (n, st, md) in rows:
        f.write('| %s | %s | %d | %s |\n' % (n, st, os.path.getsize(os.path.join(DST, n)), md))
    f.write('\n结论：%s\n' % ('八件全部复制成功且源/副本 MD5 逐件一致 PASS' if allok else '存在失败/差异，见上表'))
print('=== 报告落盘:', out, flush=True)
print('SUMMARY allok=%s' % allok, flush=True)
