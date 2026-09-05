# -*- coding: utf-8 -*-
"""④轮步骤7b：首页断言v3 端到端复跑（照 收尾B_03_e2e复跑.py 范式；零COM）。
e2e 目录 巡检_④：pdf/＝④轮新导出十件硬链接（改代号名）；首页PDF/＝工具 --make-p1 裁剪。
A) --gen-mapping（映射生成验证）；make-p1（首页裁剪）；
B) --run --mapping 报告/锚点映射表v3.json（权威注册表）＋阴性对照衔接2缺陷态。
   收口判据：断言① PASS 10/10＋阴性对照 FAIL(ok=True)。
证据：报告/④_e2e复跑.md＋④_e2e_B-v3注册表_首页断言结果.json／.md 快照。"""
import sys, io, os, re, json, subprocess, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
EXEC = os.path.join(ROOT, '工具', '首页断言集执行器.py')
SRC = os.path.join(HERE, 'PDF对比', '④轮PDF')
DOCX = os.path.join(HERE, '副本_④轮')
V3 = os.path.join(HERE, '报告', '锚点映射表v3.json')
NEG = os.path.join(ROOT, '工作区', '体系-双栏首页与PDFCreator主路径-0903', '阴性对照证据', '衔接2缺陷态.pdf')
E2E = os.path.join(HERE, '巡检_④')
OUT_MD = os.path.join(HERE, '报告', '④_e2e复跑.md')

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

def run(cmd, timeout=900):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=timeout, cwd=ROOT)
    return r.returncode, (r.stdout or '') + (('\n[stderr] ' + r.stderr) if r.stderr.strip() else '')

os.makedirs(os.path.join(E2E, 'pdf'), exist_ok=True)
pairs = []
for sh, name in TEN:
    dst = os.path.join(E2E, 'pdf', sh + '.pdf')
    if os.path.exists(dst):
        os.remove(dst)                      # ④轮新导出须替换旧链
    os.link(os.path.join(SRC, name + '.pdf'), dst)
    pairs.append('%s=%s' % (sh, os.path.join(DOCX, name + '.docx')))
L = ['# ④轮 e2e 首页断言v3 复跑（2026-09-06，④轮新导出PDF硬链接；零COM）', '']
rc, out = run([sys.executable, EXEC, '--gen-mapping', '--out', E2E] + pairs)
L.append('== A) gen-mapping exit=%d ==' % rc)
L.append(out.strip())
rc2, out2 = run([sys.executable, EXEC, '--make-p1', '--out', E2E] + pairs)
L.append('== make-p1 exit=%d ==' % rc2)
rc3, out3 = run([sys.executable, EXEC, '--run', '--out', E2E, '--mapping', V3,
                 '--negative', NEG, '--neg-code', '衔接2'] + pairs)
L.append('== B) --run --mapping 锚点映射表v3.json（十件④轮PDF） exit=%d ==' % rc3)
L.append(out3.strip()[-1200:])
hj = json.load(open(os.path.join(E2E, '首页断言结果.json'), encoding='utf-8'))
for f in ('首页断言结果.json', '首页断言报告.md'):
    shutil.copyfile(os.path.join(E2E, f), os.path.join(HERE, '报告', '④_e2e_B-v3注册表_' + f))
a1 = {k: v.get('a1', ('', ''))[0] for k, v in hj.items()}
npass = sum(1 for k, c in a1.items() if k not in ('阴性对照',) and c == 'PASS')
neg_ok = hj.get('阴性对照', {}).get('ok') is True
neg_verdict = a1.get('阴性对照')
L.append('B) 断言① PASS %d/10；阴性对照=%s(期望FAIL, ok=%s)' % (npass, neg_verdict, neg_ok))
allok = (npass == 10 and neg_ok)
L.append('')
L.append('== 汇总 ==')
L.append('SUMMARY_E2E_④: ①10/10=%s 阴性对照FAIL=%s → %s'
         % (npass == 10, neg_ok, 'PASS' if allok else 'FAIL'))
with open(OUT_MD, 'w', encoding='utf-8') as f:
    f.write('\n'.join(L) + '\n')
print('\n'.join(L[-4:]))
print('证据=%s' % OUT_MD)
sys.exit(0 if allok else 2)
