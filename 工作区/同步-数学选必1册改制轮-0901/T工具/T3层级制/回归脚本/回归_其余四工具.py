# -*- coding: utf-8 -*-
"""回归_其余四工具.py — extract_structure / 节页码定位 / 恒等式核账 / 题目台账预填 回归
（A'改制轮·工具债③·T3；全部在工作区副本上跑，禁止触碰产出文件夹）
① extract_structure：合并统计段行「1.1.1 …　本节10题：…」判 section 不误判 group（看板债）；
   层级制题号题块识别＋各节序列；旧全局号件 1..N 连续。
② 节页码定位：批量模式含0命中件（I1清单）→ 逐件独立报告（件级行＋!0命中注记）、退出码0；
   层级制新式节标题（无区间括注）与旧式双签名命中。
③ 恒等式核账：层级制各节序列连续无重复＋文件名题量恒等 PASS；旧全局号回退口径。
④ 题目台账预填：层级制题号入骨架（节分组序列行在位）。"""
import sys, os, subprocess, importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
D = os.path.join(ROOT, '测试副本')
ok = True
def gate(cond, msg):
    global ok
    print(('  PASS ' if cond else '  FAIL ') + msg)
    ok = ok and cond

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def sh(*args):
    return subprocess.run(list(args), capture_output=True, text=True, encoding='utf-8',
                          errors='replace', cwd=D)

def main():
    # ① extract_structure
    sys.path.insert(0, r'C:\提示词\工具')
    es = load('es', r'C:\提示词\工具\extract_structure.py')
    s_new = es.structure(os.path.join(D, 'B讲练上（61题）.docx'))     # 已层级制
    s_old = es.structure(os.path.join(D, 'B旧式对照（61题）.docx'))   # 旧全局号原态
    stats_line = next(x for x in s_old['items'] if x['text'].startswith('1.1.1 '))
    gate(stats_line['kind'] == 'section', '①合并统计段行判section（旧式「1.1.1 …（第1—10题）　本节10题：…」不误判题型）')
    gate(len(s_old['questions']) == 61 and s_old['questions'][0]['no'] == '1'
         and s_old['questions'][-1]['no'] == '61', '①旧全局号：题块61（1..61）')
    gate(len(s_new['questions']) == 61 and s_new['questions'][0]['no'] == '1.1.1-1'
         and s_new['questions'][-1]['no'] == '1.2.4-13' and s_new['questions'][0]['sec'] == '1.1.1',
         '①层级制题号识别：1.1.1-1..1.2.4-13（sec字段在位）')
    bysec, probs = es.hier_check(s_new['questions'])
    gate(not probs and sum(len(v) for v in bysec.values()) == 61 and len(bysec) == 7,
         '①层级制核验：7节61题节内连续无重复')

    # ② 节页码定位（批量：新式B＋旧式B＋0命中I1）
    cfg = os.path.join(D, '批量配置.tsv')
    r2 = sh(sys.executable, r'C:\提示词\工具\节页码定位.py', '@' + cfg)
    out = r2.stdout
    gate(r2.returncode == 0, '②批量含0命中件退出码0（逐件独立报告，不整批退出）')
    gate('I1清单\t!0命中\t—\t—\t—' in out and 'I1清单\t99' in out,
         '②0命中件照常出件级行＋!0命中注记行')
    gate(out.count('\nB新式\t1.1.') + out.count('B旧式\t1.1.') >= 2 and 'B新式\t1.1.1\t1.1.1 空间向量及其运算　本节10题' in out,
         '②层级制新式节标题（无区间括注、纯统计段）命中')
    gate('（第1—10题）' in out, '②旧式（第X—Y题）区间括注签名兼容命中')

    # ③ 恒等式核账
    r3 = sh(sys.executable, r'C:\提示词\工具\恒等式核账.py',
            os.path.join(D, 'B讲练上（61题）.docx'), os.path.join(D, 'I1知识清单.docx'),
            os.path.join(D, 'B旧式对照（61题）.docx'))
    o3 = r3.stdout
    gate('B讲练上（61题）.docx : 题 61｜条目 2｜文件名题量 61 PASS' in o3
         and '层级制核验: 节内连续无重复 全过' in o3,
         '③层级制恒等：题61/条目2＋文件名61 PASS＋节内连续无重复')
    gate('[条族·层级制] 节1.1.1:1..9(9)' in o3, '③清单件条目族47逐节序列（1.1.1=9起）')
    gate('[旧全局号] 题 1..61 连续性: 连续' in o3, '③旧全局号回退口径照跑')

    # ④ 题目台账预填
    r4 = sh(sys.executable, r'C:\提示词\工具\题目台账预填.py',
            os.path.join(D, 'B讲练上（61题）.docx'), '-o', os.path.join(D, 'R4_台账骨架.md'))
    body = open(os.path.join(D, 'R4_台账骨架.md'), encoding='utf-8').read()
    gate(r4.returncode == 0 and '题块合计=63' in r4.stdout,
         '④层级制骨架：63块（61题＋2讲部条目，条目带⚠人工判定标记）')
    gate('| B讲练上（61题）.docx | 1.1.1-1 |' in body and '节1.1.1：1.1.1-1、1.1.1-2、1.1.1-3' in body,
         '④题号列层级制照出＋逐节序列行在位')
    print('回归结论：' + ('通过' if ok else '不通过'))
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
