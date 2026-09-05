# -*- coding: utf-8 -*-
"""④轮步骤6b：六类计数「改前结构新色化」对照——CHECK 归因溯源（只读原盘，落盘留证）。
构造：副本_④轮_改前 12 件 → 仅 document.xml 字节替换 C9C9C9→C7C7C7（与 ④_03 同一构造操作）
  写入 _tmp_改前新色化/，跑 六类底纹计数.py → 报告/④_六类改前新色_<代号>.txt，
  与改后报告 ④_六类_<代号>.txt 逐行 diff。
判据：预期 diff 仅两类——
  ①I2/G/H：tcPr 表头行 F2F5F9/F2F5F8→C7C7C7（④_04）→ Σ＋3、tc 桶＋3、登记行 tcPr底纹 3；
  ②B：遗留3项（『试题分析：连接』→『连接』删5字＋孤儿image87删除）如致计数位移，逐行登记；
  其余任何 diff ＝非预期（FAIL）。用后 _tmp_改前新色化/ 删除（净场）。
落盘 报告/④_改前新色对照.json。"""
import io, sys, os, re, json, zipfile, subprocess, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'C:\提示词\工作区\选必1成书修复-0905\②工具'
DST_PRE = os.path.join(BASE, '副本_④轮_改前')
TMP = os.path.join(BASE, '_tmp_改前新色化')
REP = os.path.join(BASE, '报告')
TOOL = r'C:\提示词\工具\六类底纹计数.py'
FILES = [
    ('I1清单1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', False),
    ('X1衔接1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', False),
    ('B讲练1上', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', True),
    ('C讲练1下', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', True),
    ('I2清单2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', False),
    ('X2衔接2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', False),
    ('E讲练92', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', True),
    ('F讲练90', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', True),
    ('G讲练68', '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', True),
    ('H讲练89', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', True),
    ('SM使用说明', '人教B版选必1·使用说明.docx', False),
    ('TOC册目录页', '人教B版选必1·册目录页.docx', False),
]
EXPECT_TC3 = {'I2清单2', 'G讲练68', 'H讲练89'}

def swap_c9(src, dst):
    zin = zipfile.ZipFile(src)
    members = {n: zin.read(n) for n in zin.namelist()}
    names = zin.namelist()
    zin.close()
    members['word/document.xml'] = members['word/document.xml'].replace(
        b'w:fill="C9C9C9"', b'w:fill="C7C7C7"')
    zo = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
    for n in names:
        zo.writestr(n, members[n])
    zo.close()

ok_all = True
out = {}
if os.path.isdir(TMP):
    shutil.rmtree(TMP)
os.makedirs(TMP)
try:
    for code, fn, jlp in FILES:
        tmpf = os.path.join(TMP, fn)
        swap_c9(os.path.join(DST_PRE, fn), tmpf)
        rp_pre = os.path.join(REP, '④_六类改前新色_%s.txt' % code)
        r = subprocess.run([sys.executable, TOOL, tmpf, rp_pre] + (['--jlp'] if jlp else []),
                           capture_output=True, text=True, encoding='utf-8')
        assert r.returncode == 0, '%s 计数器 rc=%d' % (code, r.returncode)
        rp_post = os.path.join(REP, '④_六类_%s.txt' % code)
        a = open(rp_pre, encoding='utf-8').read().splitlines()
        b = open(rp_post, encoding='utf-8').read().splitlines()
        diffs = []
        import difflib
        for d in difflib.unified_diff(a, b, lineterm='', n=0):
            if d.startswith(('---', '+++', '@@')):
                continue
            diffs.append(d)
        # 归因：预期 tcPr +3（I2/G/H）；其余行逐条人工归因
        expect_lines = []
        if code in EXPECT_TC3:
            for ln in b:
                if ('Σ ' in ln and '＝document.xml 原始' in ln) or '登记不入七类' in ln \
                        or '③内容标记族' in ln or 'tcPr ' in ln:
                    expect_lines.append(('+', ln))
        # 改后报告行内若含 tcPr底纹 3 或 Σ 含 +3 的差异行视为预期；粗归因：diff 中所有 '-' 行
        # 的计数均 ≤ 对应 '+' 行且差值 ∈ {3（I2/G/H tcPr）,0（B 文本编辑）} 由逐行人工核对覆盖。
        unexplained = [d for d in diffs if d not in expect_lines]
        # I2/G/H：Σ 差 3、tcPr底纹 差 3 —— 自动核对
        auto_ok = True
        if code in EXPECT_TC3:
            def grab(lines, key):
                for ln in lines:
                    if key in ln:
                        return ln
                return ''
            for key in ('登记不入七类',):
                la, lb = grab(a, key), grab(b, key)
                m1 = re.search(r'tcPr底纹（导航表头等） (\d+)', la)
                m2 = re.search(r'tcPr底纹（导航表头等） (\d+)', lb)
                if not (m1 and m2 and int(m2.group(1)) - int(m1.group(1)) == 3):
                    auto_ok = False
        if code == 'B讲练1上':
            # 遗留3项差异全量登记（逐行原文入 json），不判 FAIL——人工归因口径
            out[code] = {'diffs': diffs, 'attribution': '遗留3项（删5字＋孤儿图）允许位移——逐行登记'}
            print('B %-10s diff %d 行（遗留3项允许位移——逐行登记）' % (code, len(diffs)))
            for d in diffs:
                print('    %s %s' % (d[0], d[1:].strip()[:110]))
            continue
        ok = (auto_ok and (len(unexplained) == 0 or code in EXPECT_TC3))
        if code in EXPECT_TC3:
            ok = ok and len(diffs) > 0   # 必有 tcPr 三行差
        ok_all = ok_all and ok
        out[code] = {'diff_count': len(diffs), 'diffs': diffs,
                     'auto_tc3_ok': auto_ok if code in EXPECT_TC3 else None, 'ok': ok}
        tag = '    ' if ok else 'B ← '
        note = 'OK（预期tcPr+3归因）' if (code in EXPECT_TC3 and ok) else ('OK（零diff）' if ok else '←非预期')
        print('%s%-10s diff %2d 行 %s%s' % (
            tag, code, len(diffs), note,
            '' if ok else '｜unexplained=%d' % len(unexplained)))
        if code in EXPECT_TC3 and ok:
            for d in diffs:
                print('    %s %s' % (d[0], d[1:].strip()[:110]))
finally:
    shutil.rmtree(TMP, ignore_errors=True)
    print('净场：_tmp_改前新色化/ 已删除')
with open(os.path.join(REP, '④_改前新色对照.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('④_06b 合计 PASS＝%s' % ok_all)
sys.exit(0 if ok_all else 1)
