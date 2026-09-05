# -*- coding: utf-8 -*-
"""④轮步骤0：同步盘 12 件字节复制入 副本_④轮，改前 MD5 双向锚定（FX-4：不碰同步盘原件写路径）。
输出：报告/④_改前锚定.json（同步盘 md5/副本 md5/字节等 assert）＋脚本逐件打印。"""
import hashlib, json, os, shutil, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SYNC = r'C:\提示词\高中数学\高中数学同步'
DST = r'C:\提示词\工作区\选必1成书修复-0905\②工具\副本_④轮'
REP = r'C:\提示词\工作区\选必1成书修复-0905\②工具\报告'
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

os.makedirs(DST, exist_ok=True)
os.makedirs(REP, exist_ok=True)
out = {}
ok = True
for name in FILES:
    src = os.path.join(SYNC, name)
    dst = os.path.join(DST, name)
    shutil.copyfile(src, dst)
    m1, m2 = md5(src), md5(dst)
    same = (m1 == m2)
    ok = ok and same
    out[name] = {'sync_md5': m1, 'copy_md5': m2, 'equal': same}
    print('%-52s %s %s' % (name[:52], m1[:16], 'OK' if same else '←≠'))
with open(os.path.join(REP, '④_改前锚定.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('合计 %d 件，全部字节一致＝%s' % (len(FILES), ok))
sys.exit(0 if ok else 1)
