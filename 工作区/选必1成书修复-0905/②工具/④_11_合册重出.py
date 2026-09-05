# -*- coding: utf-8 -*-
"""④轮步骤8a：PDF合册 全粒度重出（照 ⑤轮口径——装订单＝⑤轮副本 19件口径，扉页不入册）。
输入区 PDF对比/④轮合册输入/＝④轮新导出 12 件（含改色后 SM/TOC）＋未动配页件 7 件
（封面＋6部分封面——自 成书交付/全件PDF 原样复制，MD5 与全件PDF 现件锚定）。
跑 工具/PDF合册.py --granularity all --output-dir PDF对比/④轮合册：
  预期＝⑤轮登记（分本/…/合册补白登记.json）逐项同值：整册 454＝430 内容＋10 配页＋14 补白、
  本1..6＝24/18/130/8/34/240、大分本 26/52/370、零 WARN。
落盘 报告/④_合册对照.json（新登记 json 逐项 vs ⑤轮登记 json 逐项）。"""
import io, sys, os, json, shutil, hashlib, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'C:\提示词\工作区\选必1成书修复-0905\②工具'
PDFO = os.path.join(BASE, 'PDF对比', '④轮PDF')
STAGE = os.path.join(BASE, 'PDF对比', '④轮合册输入')
OUTD = os.path.join(BASE, 'PDF对比', '④轮合册')
DELIV = r'C:\提示词\工作区\选必1成书修复-0905\成书交付'
SRC5 = os.path.join(DELIV, '全件PDF')
ORDER5 = os.path.join(DELIV, '_工作', 'docx源', '人教B版选必1·装订单.md')
REG5 = os.path.join(DELIV, '分本', '人教B版选必1·合册补白登记.json')
REP = os.path.join(BASE, '报告')
TOOL = r'C:\提示词\工具\PDF合册.py'
KEEP = ['人教B版选必1·封面.pdf',
        '人教B版选必1·部分封面（第1章 空间向量与立体几何·衔接）.pdf',
        '人教B版选必1·部分封面（第1章 空间向量与立体几何·清单）.pdf',
        '人教B版选必1·部分封面（第1章 空间向量与立体几何·讲练）.pdf',
        '人教B版选必1·部分封面（第2章 平面解析几何·衔接）.pdf',
        '人教B版选必1·部分封面（第2章 平面解析几何·清单）.pdf',
        '人教B版选必1·部分封面（第2章 平面解析几何·讲练）.pdf']

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

if os.path.isdir(STAGE):
    shutil.rmtree(STAGE)
os.makedirs(STAGE)
for f in os.listdir(PDFO):
    shutil.copyfile(os.path.join(PDFO, f), os.path.join(STAGE, f))
keep_md5 = {}
for f in KEEP:
    src = os.path.join(SRC5, f)
    shutil.copyfile(src, os.path.join(STAGE, f))
    keep_md5[f] = {'src_md5': md5(src), 'stage_md5': md5(os.path.join(STAGE, f))}
n = len(os.listdir(STAGE))
assert n == 19, '输入区 %d 件 ≠ 19' % n
print('输入区 19 件齐（12 ④轮新导出＋7 配页件原样，MD5 锚定 %d 件）' % len(KEEP), flush=True)
if os.path.isdir(OUTD):
    shutil.rmtree(OUTD)
r = subprocess.run([sys.executable, TOOL, '--order', ORDER5, '--input-dir', STAGE,
                    '--output-dir', OUTD, '--granularity', 'all'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
print(r.stdout)
if r.returncode != 0 or 'WARN' in (r.stdout or ''):
    print('STDERR:', (r.stderr or '')[:600])
    sys.exit(2)
reg_new_path = os.path.join(OUTD, '人教B版选必1·合册补白登记.json')
reg_old = json.load(open(REG5, encoding='utf-8'))
reg_new = json.load(open(reg_new_path, encoding='utf-8'))
ok_all = True
cmp = {}
for tag, o in reg_old['outputs'].items():
    n2 = reg_new['outputs'].get(tag)
    same_pages = n2 and n2['total_pages'] == o['total_pages']
    same_pieces = n2 and [(p['xu'], p['src_pages'], p['blanks']) for p in o['pieces']] \
        == [(p['xu'], p['src_pages'], p['blanks']) for p in n2['pieces']]
    ok = bool(same_pages and same_pieces)
    ok_all = ok_all and ok
    cmp[tag] = {'old': o['total_pages'], 'new': n2['total_pages'] if n2 else None,
                'pieces_same': same_pieces, 'ok': ok}
    print('%-12s %s → %s %s' % (tag, o['total_pages'], n2['total_pages'] if n2 else '缺',
                                'OK' if ok else '←≠'))
with open(os.path.join(REP, '④_合册对照.json'), 'w', encoding='utf-8') as f:
    json.dump({'keep_md5': keep_md5, 'cmp': cmp, 'ok': ok_all,
               'new_registry': reg_new_path}, f, ensure_ascii=False, indent=1)
print('④_11 合册对照 PASS＝%s' % ok_all)
sys.exit(0 if ok_all else 1)
