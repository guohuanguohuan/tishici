# -*- coding: utf-8 -*-
"""②E_08_回写.py — ②-E 回写同步盘（十件〔盖章 N/start 变动〕＋册目录页〔重造〕＋装订单.md〔联动〕）。
逐件 3 轮×300s 预算抗锁 copy2（用户同步进程禁杀；轮间杀新生 WINWORD 孤儿）；MD5 逐件比对；
回写后 oMath 元素守恒（同步盘十件对 ②-F 锚，zip/XML 面——避开 COM 撞上传窗口）。
证据：报告/②E_08_回写.md、报告/②E_MD5_回写.md"""
import sys, io, os, re, time, shutil, hashlib, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SYNC = os.path.join(ROOT, '高中数学', '高中数学同步')
DST = os.path.join(HERE, '副本_②E')
RPT = os.path.join(HERE, '报告')

FILES = [
    ('清单1', '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx', 396),
    ('衔接1', '人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx', 882),
    ('上61', '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx', 3251),
    ('下79', '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx', 2876),
    ('清单2', '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx', 1156),
    ('衔接2', '人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx', 243),
    ('92', '人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx', 2705),
    ('90', '人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx', 2914),
    ('68', '人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx', 2359),
    ('89', '人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx', 4034),
    ('册目录页', '人教B版选必1·册目录页.docx', None),
    ('装订单', '人教B版选必1·装订单.md', None),
]
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

OUT = []
def say(m):
    print(m, flush=True)
    OUT.append(m)

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def kill_newest_winword():
    try:
        import psutil
        ws = [p for p in psutil.process_iter(['name', 'create_time'])
              if (p.info['name'] or '').upper() == 'WINWORD.EXE']
        ws.sort(key=lambda x: x.info['create_time'], reverse=True)
        if ws:
            ws[0].kill()
            say('   杀 WINWORD 孤儿 pid%d' % ws[0].pid)
    except Exception as e:
        say('   kill fail %s' % e)

say('=== ① 回写（副本_②E → 同步盘；12 件；逐件 3 轮×300s 抗锁；同步客户端禁杀） ===')
ok_wb = True
for sh, n, _ in FILES:
    s, d = os.path.join(DST, n), os.path.join(SYNC, n)
    done = False
    for rd in range(1, 4):
        t0 = time.time()
        att = 0
        while time.time() - t0 < 300:
            att += 1
            try:
                shutil.copy2(s, d)
                done = True
                break
            except PermissionError as e:
                say('   %s r%d a%d 瞬锁退避 %s' % (sh, rd, att, str(e)[:40]))
                time.sleep(6)
        if done:
            break
        kill_newest_winword()
        time.sleep(20)
    if not done:
        ok_wb = False
        say('  !! %s 回写失败（3 轮×300s）——停：后续件照写，末尾汇总非绿' % sh)
    else:
        say('  %s 回写 OK' % sh)

say('=== ② 防播散检查 ===')
baks = [f for f in os.listdir(SYNC) if ('栏顶' in f or '跨行护' in f or f.startswith('~$'))]
say('  同步盘 .bak_栏顶/.bak_跨行护/~$ 数 = %d %s' % (len(baks), 'PASS' if not baks else '!!' + str(baks)))

say('=== ③ MD5 逐件比对（副本 vs 同步盘） ===')
md5_rows = []
ok_md5 = True
for sh, n, _ in FILES:
    m1, m2 = md5(os.path.join(DST, n)), md5(os.path.join(SYNC, n))
    hit = m1 == m2
    ok_md5 = ok_md5 and hit
    md5_rows.append('| %s | %s | %s | %s |' % (sh, m1, m2, 'PASS' if hit else 'FAIL'))
    say('  %-6s %s %s' % (sh, m1, 'PASS' if hit else '!!FAIL sync=%s' % m2))
with open(os.path.join(RPT, '②E_MD5_回写.md'), 'w', encoding='utf-8') as f:
    f.write('# ②-E 回写 MD5（副本_②E 终态 vs 同步盘；十件＝盖章后态，册目录页/装订单＝②-E 重造态）\n\n'
            '| 件 | 副本 MD5 | 同步盘 MD5 | 判定 |\n|---|---|---|---|\n' + '\n'.join(md5_rows) + '\n')

say('=== ④ 回写后 oMath 元素守恒（同步盘十件，zip/XML 面，不涉 COM） ===')
ok_om = True
for sh, n, om in FILES[:10]:
    z = zipfile.ZipFile(os.path.join(SYNC, n))
    doc = etree.fromstring(z.read('word/document.xml'))
    z.close()
    c = sum(len(list(p.iter('{%s}oMath' % M))) for p in doc.iter('{%s}p' % W))
    hit = (c == om)
    ok_om = ok_om and hit
    say('  %-6s oMath=%5d 锚=%5d %s' % (sh, c, om, 'PASS' if hit else '!!FAIL'))

say('=== ⑤ 回写后同串抽查（页脚可见串，zip 面） ===')
ok_hf = True
for sh, n, _ in FILES[:10]:
    z = zipfile.ZipFile(os.path.join(SYNC, n))
    names = z.namelist()
    f = [x for x in names if re.fullmatch(r'word/footer\d+\.xml', x)][0]
    fv = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', z.read(f).decode('utf-8')))
    z.close()
    m = re.fullmatch(r'(.+)（共(\d+)页）·本(\d+)/共(\d+)本　(.+)　第(\d+)页', fv)
    hit = bool(m)
    ok_hf = ok_hf and hit
    say('  %-6s %s %s' % (sh, fv[:44], '串形OK' if hit else '!!串形异常'))

say('=== 汇总 ===')
ALLOK = (ok_wb and not baks and ok_md5 and ok_om and ok_hf)
say('SUMMARY_08 ALLOK=%s (wb=%s nospread=%s md5=%s oMath=%s hf=%s)'
    % (ALLOK, ok_wb, not baks, ok_md5, ok_om, ok_hf))
with open(os.path.join(RPT, '②E_08_回写.md'), 'w', encoding='utf-8') as f:
    f.write('```text\n' + '\n'.join(OUT) + '\n```\n')
sys.exit(0 if ALLOK else 2)
