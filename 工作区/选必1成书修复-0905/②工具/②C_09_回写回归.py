# -*- coding: utf-8 -*-
"""②C_09_回写回归.py — ②-C 副本→同步盘回写＋回归。
①十件 副本→高中数学\\高中数学同步 逐件复制（Resilio/RealTimeSync 瞬锁退避：最多 8 试、退避 6s），
  同步盘不落 .bak（防 Resilio 播散）；回写前先留同步盘现态 MD5（＝②-B 终态，即回滚锚）。
②回写后 MD5 逐件比对 副本 vs 同步盘。
③回归：T6a/T6b/T6c 三工具对同步盘成品各连跑两次 dry 至不动点（0 命中）；
  另默认模式 --only c dry（审计回落 54/0、讲练件复核 0、清单 0）。
④结果落 报告/②C_回写_回归.md。
纪律：禁 git；同步客户端为用户进程禁杀（FX-4）；锁冲突仅退避重试。"""
import sys, io, os, time, hashlib, shutil, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DST = os.path.join(HERE, '副本')
SYNC = os.path.join(ROOT, '高中数学', '高中数学同步')
RPT = os.path.join(HERE, '报告', '②C_回写_回归.md')
TOOL = os.path.join(ROOT, '工具', '底纹批量器.py')

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
SHORT = ['清单1', '衔接1(29)', '上(61)', '下(79)', '清单2', '衔接2(13)', '92', '90', '68', '89']


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def copy_retry(src, dst, tries=8, backoff=6):
    for att in range(1, tries + 1):
        try:
            shutil.copy2(src, dst)
            return True
        except PermissionError as e:
            print('   att%d PermissionError %s，退避%ds' % (att, str(e)[:60], backoff), flush=True)
            time.sleep(backoff)
        except OSError as e:
            print('   att%d OSError %s，退避%ds' % (att, str(e)[:60], backoff), flush=True)
            time.sleep(backoff)
    return False


def run_tool(args, tries=3, timeout=300):
    for att in range(1, tries + 1):
        try:
            p = subprocess.run(['python', TOOL] + args, capture_output=True, text=True,
                               encoding='utf-8', timeout=timeout, cwd=ROOT)
        except subprocess.TimeoutExpired:
            print('    timeout att%d' % att, flush=True)
            time.sleep(15)
            continue
        if p.returncode == 0 and 'Traceback' not in (p.stderr or ''):
            return p.stdout.strip()
        print('    fail att%d rc=%d %s' % (att, p.returncode, (p.stderr or '')[-200:]), flush=True)
        time.sleep(15)
    return None


def main():
    L = []
    L.append('# ②C 回写同步盘＋回归\n')
    L.append('- 时点：%s\n' % time.strftime('%Y-%m-%d %H:%M:%S'))
    L.append('- 方向：`②工具\\副本\\` → `高中数学\\高中数学同步\\`（仅十件 docx；配页件不触；同步盘不落 .bak）\n')
    # ① 回写前同步盘现态 MD5（脚本可重入：若此前已回写过，此表为 ②-C 终态；
    #    真回写锚＝首轮执行前独立核验「同步盘十件 MD5＝②C_副本重置_MD5.md（②-B 终态）」逐件 PASS，见终报）
    L.append('\n## 一、同步盘现态 MD5（重入时点；真回写锚见终报「执行前独立核验」）\n')
    L.append('| 件 | 同步盘前 MD5 | 副本(post-②C) MD5 |')
    L.append('|---|---|---|')
    pre = {}
    for n in NAMES:
        pre[n] = md5(os.path.join(SYNC, n))
        L.append('| %s | %s | %s |' % (n, pre[n], md5(os.path.join(DST, n))))
    # ② 回写
    print('== 回写 ==', flush=True)
    L.append('\n## 二、回写（逐件重试范式）\n')
    wb = {}
    for n, sh in zip(NAMES, SHORT):
        ok = copy_retry(os.path.join(DST, n), os.path.join(SYNC, n))
        wb[n] = ok
        print('  %-10s %s' % (sh, 'OK' if ok else '!!FAIL'), flush=True)
        L.append('- %s：%s' % (sh, 'OK' if ok else '!!FAIL（8 试仍锁，需人工查同步客户端）'))
    allok = all(wb.values())
    # ③ 回写后 MD5
    print('== 回写后 MD5 ==', flush=True)
    L.append('\n## 三、回写后 MD5 逐件比对（副本 vs 同步盘）\n')
    L.append('| 件 | 副本 MD5 | 同步盘后 MD5 | 一致 |')
    L.append('|---|---|---|---|')
    for n, sh in zip(NAMES, SHORT):
        a = md5(os.path.join(DST, n))
        b = md5(os.path.join(SYNC, n))
        r = (a == b) and wb[n]
        allok = allok and r
        print('  %-10s %s %s' % (sh, a, 'PASS' if r else '!!FAIL'), flush=True)
        L.append('| %s | %s | %s | %s |' % (sh, a, b, 'PASS' if r else '**FAIL**'))
    # ④ 三工具 dry×2 至不动点（对同步盘成品）
    L.append('\n## 四、回归：三工具对同步盘成品 dry 各连跑两次（不动点断言）\n')
    L.append('| 件 | T6a×2 | T6b×2 | T6c(--xj-clear)×2 | 默认c审计回落 | 判定 |')
    L.append('|---|---|---|---|---|')
    import re
    for n, sh in zip(NAMES, SHORT):
        f = os.path.join(SYNC, n)
        res = {}
        for key, extra in [('a', ['--only', 'a']), ('b', ['--only', 'b']),
                           ('c', ['--only', 'c', '--xj-clear']), ('def', ['--only', 'c'])]:
            vals = []
            for _ in range(2):
                o = run_tool([f] + extra + ['--dry-run'])
                v = None
                if o:
                    if key == 'a':
                        m = re.search(r'a\) E0E0E0→F2F2F2：(\d+) 处', o)
                    elif key == 'b':
                        m = re.search(r'撤 C6D4E3＋挂左竖条：(\d+)', o)
                    elif key == 'c':
                        m = re.search(r'解析区剥除 (\d+) 处', o) or re.search(r'剥除：(\d+) 处', o) \
                            or re.search(r'：(\d+) 处登记', o)
                    else:
                        m = re.search(r'审计（非讲练件不剥，附则适用面）：(\d+) 处登记', o)
                        v = ('复核0' if '复核＝0' in o else None) if not m else int(m.group(1))
                        vals.append(v)
                        continue
                    v = int(m.group(1)) if m else -1
                vals.append(v)
            res[key] = vals
        defs = [0 if v == '复核0' else v for v in res['def']]
        okf = (all(v == 0 for v in res['a']) and all(v == 0 for v in res['b'])
               and all(v == 0 for v in res['c'])
               and all(v == (54 if sh == '衔接2(13)' else 0) for v in defs))
        allok = allok and okf
        print('  %-10s a%s b%s c%s def%s %s' % (sh, res['a'], res['b'], res['c'], res['def'],
                                                'PASS' if okf else '!!FAIL'), flush=True)
        L.append('| %s | %s | %s | %s | %s | %s |' % (sh, res['a'], res['b'], res['c'], res['def'],
                                                      'PASS' if okf else '**FAIL**'))
    L.append('\n## 五、结论\n')
    L.append('%s\n' % ('**全绿**：十件回写成功且 MD5 逐件一致；三工具对同步盘成品 dry 连跑两次全 0（不动点）；'
                       '默认模式审计回落衔接2=54／衔接1=0、讲练件复核0、清单件0——块界定剥除恰为解析区、'
                       '块外灰底全部仍在。②-C 可收口。'
                       if allok else '**存在未通过项**，见上表，②-C 不得收口。'))
    with open(RPT, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n')
    print('REPORT ->', RPT, flush=True)
    print('SUMMARY allok=%s' % allok, flush=True)


if __name__ == '__main__':
    main()
