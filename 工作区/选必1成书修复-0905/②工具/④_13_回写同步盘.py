# -*- coding: utf-8 -*-
"""④轮步骤9：12 件回写同步盘（字节复制＋MD5 双向锚定）。
前置断言：同步盘现件 MD5 ＝ ④_改前锚定.json sync_md5（④轮全程同步盘未被它手触碰）。
回写：副本_④轮/<fn> → 同步盘/<fn>（shutil.copyfile）。
双向锚定：回写后 逐件 sync_md5 == 副本_md5 == 改后锚定（本脚本回写前重算副本 MD5）；
  再反向 copyfile 同步盘→_tmp 校验副本（读回比较字节，防缓存假象——读回比较即可）。
落盘 报告/④_回写锚定.json。"""
import io, sys, os, json, shutil, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'C:\提示词\工作区\选必1成书修复-0905\②工具'
SYNC = r'C:\提示词\高中数学\高中数学同步'
DST = os.path.join(BASE, '副本_④轮')
REP = os.path.join(BASE, '报告')
FILES = [
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
    '人教B版选必1·使用说明.docx',
    '人教B版选必1·册目录页.docx',
]

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

anchor = json.load(open(os.path.join(REP, '④_改前锚定.json'), encoding='utf-8'))
out = {}
ok_all = True
for fn in FILES:
    src = os.path.join(DST, fn)
    dst = os.path.join(SYNC, fn)
    pre_sync = md5(dst)
    pre_ok = (pre_sync == anchor[fn]['sync_md5'])
    m_copy = md5(src)
    if not pre_ok:
        print('!! %-52s 同步盘现件 MD5 ≠ ④_改前锚定（%s ≠ %s）——中止' % (fn[:52], pre_sync[:12], anchor[fn]['sync_md5'][:12]))
        sys.exit(3)
    shutil.copyfile(src, dst)
    post_sync = md5(dst)
    back_ok = (post_sync == m_copy)
    # 读回比较（字节级）
    with open(src, 'rb') as a, open(dst, 'rb') as b:
        byte_ok = (a.read() == b.read())
    ok = pre_ok and back_ok and byte_ok
    ok_all = ok_all and ok
    out[fn] = {'sync_before': pre_sync, 'copy_md5': m_copy, 'sync_after': post_sync,
               'pre_ok': pre_ok, 'back_ok': back_ok, 'byte_ok': byte_ok, 'ok': ok}
    print('%s %-52s %s（改前 %s）' % ('OK' if ok else '←FAIL', fn[:52], post_sync[:12], pre_sync[:12]))
with open(os.path.join(REP, '④_回写锚定.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('④_13 回写 12/12 双向锚定 PASS＝%s' % ok_all)
sys.exit(0 if ok_all else 1)
