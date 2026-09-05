# -*- coding: utf-8 -*-
"""收尾B_03_e2e复跑.py — 2026-09-06 收尾-B 步3：经生产工具 端到端复跑 v3 断言①。
e2e 目录：pdf/＝十件终态全件PDF硬链接（改代号名）；首页PDF/＝工具--make-p1裁剪。
跑法：A) --gen-mapping（验证定族更正后十行族）；B) --run --mapping 锚点映射表v3.json
（权威注册表，含阴性对照）；C) --run 无 --mapping（诊断：docx自产表对题名内嵌公式件的局限）。
零 COM；证据落 ②工具\\报告\\收尾B_e2e复跑.md。"""
import sys, io, os, re, json, subprocess, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
EXEC = os.path.join(ROOT, '工具', '首页断言集执行器.py')
SRC = os.path.abspath(os.path.join(HERE, '..', '成书交付', '全件PDF'))
DOCX = os.path.join(HERE, '副本_②E')
V3 = os.path.join(HERE, '报告', '锚点映射表v3.json')
NEG = os.path.join(ROOT, '工作区', '体系-双栏首页与PDFCreator主路径-0903', '阴性对照证据', '衔接2缺陷态.pdf')
E2E = os.path.join(HERE, '收尾B_e2e')
OUT_MD = os.path.join(HERE, '报告', '收尾B_e2e复跑.md')

TEN = [
    ('清单1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）'),
    ('衔接1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）'),
    ('上61', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）'),
    ('下79', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）'),
    ('清单2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）'),
    ('衔接2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）'),
    ('92', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）'),
    ('90', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）'),
    ('68', '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）'),
    ('89', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）'),
]

def say(lines, m):
    print(m, flush=True)
    lines.append(m)

def run(cmd, timeout=900):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=timeout, cwd=ROOT)
    return r.returncode, (r.stdout or '') + (('\n[stderr] ' + r.stderr) if r.stderr.strip() else '')

def main():
    os.makedirs(os.path.join(E2E, 'pdf'), exist_ok=True)
    pairs = []
    for sh, name in TEN:
        dst = os.path.join(E2E, 'pdf', sh + '.pdf')
        if not os.path.exists(dst):
            os.link(os.path.join(SRC, name + '.pdf'), dst)      # 硬链接：零拷贝、同卷
        pairs.append('%s=%s' % (sh, os.path.join(DOCX, name + '.docx')))
    L = ['# 收尾B e2e 复跑（2026-09-06，生产工具＋终态全件PDF硬链接；零COM）', '']
    # A) gen-mapping：定族更正验证
    rc, out = run([sys.executable, EXEC, '--gen-mapping', '--out', E2E] + pairs)
    say(L, '== A) gen-mapping（定族更正验证） exit=%d ==' % rc)
    say(L, out.strip())
    # 首页PDF裁剪（幂等）
    rc2, out2 = run([sys.executable, EXEC, '--make-p1', '--out', E2E] + pairs)
    say(L, '== make-p1 exit=%d ==' % rc2)
    # B) --run --mapping v3（权威注册表）＋阴性对照
    rc3, out3 = run([sys.executable, EXEC, '--run', '--out', E2E, '--mapping', V3,
                     '--negative', NEG, '--neg-code', '衔接2'] + pairs)
    say(L, '== B) --run --mapping 锚点映射表v3.json（十件终态PDF） exit=%d ==' % rc3)
    say(L, out3.strip()[-1200:])
    hj = json.load(open(os.path.join(E2E, '首页断言结果.json'), encoding='utf-8'))
    for f in ('首页断言结果.json', '首页断言报告.md'):   # B 跑证据快照（防 C 跑覆盖）
        shutil.copyfile(os.path.join(E2E, f), os.path.join(HERE, '报告', '收尾B_e2e_B-v3注册表_' + f))
    a1 = {k: v.get('a1', ('', ''))[0] for k, v in hj.items()}
    npass = sum(1 for k, c in a1.items() if k not in ('阴性对照',) and c == 'PASS')
    neg_ok = hj.get('阴性对照', {}).get('ok') is True
    say(L, 'B) 断言① PASS %d/10；阴性对照=%s(期望FAIL, ok=%s)' % (npass, a1.get('阴性对照'), neg_ok))
    # C) 诊断：docx 自产表（定族更正后）——验证其局限
    rc4, out4 = run([sys.executable, EXEC, '--run', '--out', E2E] + pairs)
    hj2 = json.load(open(os.path.join(E2E, '首页断言结果.json'), encoding='utf-8'))
    for f in ('首页断言结果.json', '首页断言报告.md'):   # C 跑（诊断）证据快照
        shutil.copyfile(os.path.join(E2E, f), os.path.join(HERE, '报告', '收尾B_e2e_C-自产表诊断_' + f))
    a1b = {k: v.get('a1', ('', ''))[0] for k, v in hj2.items()}
    failb = [k for k, c in a1b.items() if k != '阴性对照' and c != 'PASS']
    say(L, '== C) 诊断 --run（docx自产表，定族更正后） exit=%d ==' % rc4)
    say(L, 'C) 断言① FAIL=%s（预期：题名内嵌公式件〔89等〕docx自产锚点含文字层不可见串→假阴性；'
           '证注册表--mapping为权威源）' % failb)
    # 汇总
    allokb = (npass == 10 and neg_ok)
    say(L, '')
    say(L, '== 汇总 ==')
    say(L, 'SUMMARY_E2E mapping_v3: ①10/10=%s 阴性对照FAIL=%s → %s'
        % (npass == 10, neg_ok, 'PASS' if allokb else 'FAIL'))
    md = '\n'.join(L) + '\n'
    with open(OUT_MD, 'w', encoding='utf-8') as f:
        f.write(md)
    print('\n证据=%s' % OUT_MD)
    sys.exit(0 if allokb else 2)

if __name__ == '__main__':
    main()
