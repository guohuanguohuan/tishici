# -*- coding: utf-8 -*-
"""S4 印前处置·值台账/件manifest 回冲：改动片指纹刷新＋知识点/图债字段落账＋变更注记。
依赖 复编读数S4.json（插桩后双档页数）。写入域＝涉片 值台账/件manifest。零 git。
"""
import hashlib, io, json, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CJ = r'C:/提示词/工作区/M3-第2章量产0913/成卷'
HERE = r'C:/提示词/工作区/_tmpM3印前处置0914'
recs = json.load(open(os.path.join(HERE, '复编读数S4.json'), encoding='utf-8'))
pages = {(r['树'], r['片']): (r['true页'], r['false页']) for r in recs}
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()


def pdir(tree, pid):
    base = os.path.join(CJ, tree)
    for d in os.listdir(base):
        if d == pid or d.startswith(pid + '-'):
            return os.path.join(base, d)
    raise SystemExit(pid)


NOTE_ZSD = ('S4 印前回核（0914，键联法全片扫描）：知识点 N 照导学件落盘切分逐题回核，'
            '%s 处改号（%s）；改后键联对读 16/16 相符，门谱复跑全绿（门谱S4/）。')

PRACTICE_NOTE = {
    '课时01': dict(field='知识点口径', value=NOTE_ZSD % ('1 席', '题10 二→三（导学席变式13 贴 知识点三，坐标法域）')),
    '课时02': dict(field='知识点预排注记', value=(
        '难度词照题面侧头标第4字段逐字；知识点 N 预排切分（一倾斜角/二斜率/三互求）经 S4 印前回核'
        '（0914，键联法）与导学件落盘分册逐席对读：切分同构，4 席按落盘贴标改号'
        '（题3 二→三、题8 三→二、题9 三→一、题16 三→一）；改后键联对读 16/16 相符，门谱复跑全绿（门谱S4/）。')),
    '课时06': dict(field='知识点预排注记', value=(
        '知识点 N 预排（一平行判定/二垂直判定/三交点与综合）与导学件06 落盘分册确有异动，'
        'S4 印前回核（0914，键联法逐题 16 席）：6 席按落盘切分改号（题4/6/11/14→知识点一，题9/15→知识点二）；'
        '题1（S3 同域候选）键联对读取符不改；改后 16/16 相符，门谱复跑全绿（门谱S4/）。')),
    '课时07': dict(field='知识点口径', value=(
        '照导学件 zsd 知识导学口径：一＝圆的标准方程、二＝点与圆位置关系、三＝一般方程与表圆条件；'
        'zsd 与 tjdnr 异序（登记在案）。S4 印前回核（0914，键联法）：题9 一→二（圆上点到直线最值，'
        '落盘 tjdnr 一 点与圆位置 → zsd 二）；改后 16/16 合 zsd 口径，门谱复跑全绿（门谱S4/）。')),
    '课时08': dict(field='知识点口径', value=(
        '照导学件 zsd 知识导学口径：一＝直线与圆的位置关系、二＝圆的切线、三＝弦长与圆心角。'
        'S4 印前回核（0914，键联法）：原贴系 tjdnr 讲练节序（二弦长/三切线），与 zsd 二/三互易，'
        '11 席按 zsd 改号（题1~4 二→三；题6/7/9/10/14/15 三→二；题16 一→二）；'
        '改后 16/16 合 zsd 口径，门谱复跑全绿（门谱S4/）。')),
}

FIG_NOTE = {
    '课时02': 'E1 国旗五星坐标图已于 0914 印前插桩销案（图资源/02-E1.png，卷①段58 rId10 提取；题面「如图」处 \\ansfig，练习件/导学件双面）',
    '课时12': '题15（12-难1）椭圆构形图已于 0914 印前插桩销案（图资源/12-难1.png，卷②段1283 rId151 提取；导学侧〔图注〕行随真图换除）',
    '课时13': '题16（13-难2）猫捉老鼠建系图已于 0914 印前插桩销案（图资源/13-难2.png，富矿件13-#25 段503 提取；导学侧〔图注〕行随真图换除）',
    '课时15': ('题16（15-16）隧道断面图已于 0914 印前插桩销案（图资源/15-16.png，富矿件18-#26 段465_0 提取；'
               '题面〔图注：…〕/（图注：…）随真图摘除、详解「由图注」改「由图」，双面）；'
               '题13「如图1/图2」装饰图按裁定免图销案（文字自足，不回补）'),
    '课时18': '题12(2)（18-12）抛物线弦构形图、题14（18-14）拼接曲线图已于 0914 印前插桩销案（图资源/18-12.png、18-14.png 提取；双面 \\ansfig）',
    '课时19': '题10（19-10）焦点三角形图、题16（19-16）双抛物线图已于 0914 印前插桩销案（图资源/19-10.png、19-16.png 重绘图；双面 \\ansfig）',
}

for tree, pids in (('练习件', ['课时01', '课时02', '课时06', '课时07', '课时08', '课时12', '课时13', '课时15', '课时18', '课时19']),
                   ('导学件', ['课时02', '课时12', '课时13', '课时15', '课时17', '课时18', '课时19'])):
    for pid in pids:
        d = pdir(tree, pid)
        if tree == '练习件':
            fp = [f for f in os.listdir(d) if f.startswith('值台账') and f.endswith('.json')][0]
            j = json.load(open(os.path.join(d, fp), encoding='utf-8'))
            kn = PRACTICE_NOTE.get(pid)
            if kn:
                j[kn['field']] = kn['value']
            if pid in FIG_NOTE:
                j['图债'] = FIG_NOTE[pid]
            tp, fpages = pages[(tree, pid)]
            j['指纹'] = {
                'main.tex.md5': md5(os.path.join(d, 'main.tex')),
                'main-true.pdf.md5': md5(os.path.join(d, 'main-true.pdf')),
                'main-false.pdf.md5': md5(os.path.join(d, 'main-false.pdf')),
                '编译': 'xelatex -interaction=nonstopmode main-true.tex ×2 / main-false.tex ×2（cwd＝片目录）',
                '双档读数': 'true 0错0溢0under0缺字 ANSKEY=16 %d页；false 同 %d页（S4 印前 0914 复编）' % (tp, fpages),
            }
            j['变更注记'] = ('S4 印前处置（0914）：' + ('知识点N 键联回核改号；' if kn else '') +
                          ('图债插桩回冲；' if pid in FIG_NOTE else '') +
                          '值台账指纹/读数刷新（本字段）；门谱复跑全绿见 工作区/_tmpM3印前处置0914/门谱S4/。')
            out = fp
        else:
            fp = '件manifest.json'
            out = fp
            j = json.load(open(os.path.join(d, fp), encoding='utf-8'))
            fz = j.get('件指纹', {})
            for k in list(fz):
                if k.endswith('.md5'):
                    name = k[:-4]
                    p = os.path.join(d, name)
                    if os.path.exists(p):
                        fz[k] = md5(p)
            j['件指纹'] = fz
            j['变更注记'] = ('S4 印前处置（0914）：' +
                          ('拓17-01 三行 \\lxopt 数值回源（A 4/5、B 6/5、C 8/5）＋详解尾括注摘除；' if pid == '课时17' else '') +
                          ('图债插桩回冲（\\ansfig，题面「如图」处）；' if pid != '课时17' else '') +
                          '件指纹刷新（本字段）；复编译三零承证见 工作区/_tmpM3印前处置0914/复编读数S4.json。')
        json.dump(j, open(os.path.join(d, out), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('回冲 %s/%s ← %s' % (tree, pid, out))
print('done')
