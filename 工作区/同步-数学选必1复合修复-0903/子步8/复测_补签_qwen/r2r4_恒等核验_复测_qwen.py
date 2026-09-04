# -*- coding: utf-8 -*-
"""R2/R4 恒等核验：读复跑后的 tmp dump json（原件在 原输出备份\）＋参照件，逐项 PASS/FAIL＋实测值。只读。"""
import sys, io, os, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

TMP = r'C:\提示词\工作区\同步-数学选必1复合修复-0903\子步8\tmp'
rows1 = json.load(open(os.path.join(TMP, 'dump_册目录页_收尾.json'), encoding='utf-8'))

print('===== R2 册目录页恒等保持 =====')
n = len(rows1)
ok_n = (n == 20)
print('%s 段落总数 实测=%d 期望=20' % ('PASS' if ok_n else 'FAIL', n))
cnt = {}
for r in rows1:
    cnt[r['type']] = cnt.get(r['type'], 0) + 1
exp_cnt = {'章行': 2, '件级行': 6, '节级行': 10, '小注行': 1, '未归类': 1}
ok_c = (cnt == exp_cnt)
print('%s 行型分解 实测=%s 期望=%s（合计=%d）' % ('PASS' if ok_c else 'FAIL', json.dumps(cnt, ensure_ascii=False), json.dumps(exp_cnt, ensure_ascii=False), sum(cnt.values())))

EXP_P = {'1.1': 1, '1.2': 17, '2.1': 1, '2.2': 2, '2.3': 25, '2.4': 60, '2.5': 73, '2.6': 112, '2.7': 134, '2.8': 156}
EXP_N = {'1.1': 24, '1.2': 116, '2.1': 1, '2.2': 38, '2.3': 61, '2.4': 19, '2.5': 63, '2.6': 36, '2.7': 32, '2.8': 89}
got = {}
for r in rows1:
    if r['type'] != '节级行':
        continue
    m = re.match(r'^(\d+\.\d+)\b.*?（(\d+)题）\s*P(\d+)', r['text'])
    if not m:
        print('  节级行解析失败:', r['text'])
        continue
    got[m.group(1)] = (int(m.group(3)), int(m.group(2)))
okp = all(k in got and got[k][0] == EXP_P[k] for k in EXP_P) and len(got) == 10
okn = all(k in got and got[k][1] == EXP_N[k] for k in EXP_N) and len(got) == 10
print('%s 节级行P值10个 实测=%s' % ('PASS' if okp else 'FAIL', {k: got[k][0] for k in sorted(got)}))
print('%s 括注题数10个 实测=%s' % ('PASS' if okn else 'FAIL', {k: got[k][1] for k in sorted(got)}))
# 与 子步7\节页码_子步8.json 定位值交叉核对（讲练件 section part_page）
loc = json.load(open(r'C:\提示词\工作区\同步-数学选必1复合修复-0903\子步7\节页码_子步8.json', encoding='utf-8'))
loc_p = {}
for f in loc['files']:
    if '讲练件' in f['name']:
        for s in f['sections']:
            no = s['no']
            if re.fullmatch(r'\d+\.\d+', no):
                loc_p[no] = s['part_page']
okx = all(EXP_P.get(k) == v for k, v in loc_p.items() if k in EXP_P)
print('%s 任务书所录定位值 ↔ 节页码_子步8.json(讲练件part_page) 实测=%s' % ('PASS' if okx and set(loc_p) >= set(EXP_P) else 'FAIL', {k: loc_p.get(k) for k in EXP_P}))
# 件级行底纹（dump口径旁证）
ok_shd = all(r['pshd'] == 'C9C9C9' for r in rows1 if r['type'] == '件级行')
print('%s 件级行段级 pshd（dump旁证）实测=%s' % ('PASS' if ok_shd else 'FAIL', [r['pshd'] for r in rows1 if r['type'] == '件级行']))

print('===== R4 使用说明改动逐字核验 =====')
rows2 = json.load(open(TMP + '\\dump_使用说明_收尾.json', encoding='utf-8'))
n2 = len(rows2)
print('%s 段落总数 实测=%d 期望=33（36−3空段）' % ('PASS' if n2 == 33 else 'FAIL', n2))

legend = json.load(open(r'C:\提示词\工作区\同步-数学选必1复合修复-0903\子步8\图例改造_子步8.json', encoding='utf-8'))
OLD_TAIL = '题号块底纹式样仅衔接件·清单件仍现行（下行即衔接件式样）。'
NEW_TAIL = '题型级题号块底纹仅衔接件·清单件仍现行（下行即衔接件式样）；讲练件讲部填空块题号（2.8-1型）随块挂C9C9C9、不加粗。'
EXP4 = legend['texts']['4'].replace(OLD_TAIL, NEW_TAIL)

def find(prefix):
    for r in rows2:
        if r['text'].startswith(prefix):
            return r
    return None

p4 = find('1.1.1.1-1．')
if p4 is None:
    print('FAIL 行4未找到')
else:
    exact = p4['text'] == EXP4
    must = ('题型级题号块底纹仅衔接件·清单件仍现行' in p4['text']) and p4['text'].endswith('讲练件讲部填空块题号（2.8-1型）随块挂C9C9C9、不加粗。')
    print('%s 行4逐字=报告§四新文 实测len=%d 期望len=%d exact=%s 必含句=%s' % ('PASS' if exact and must else 'FAIL', len(p4['text']), len(EXP4), exact, must))
    if not exact:
        i = next((j for j in range(min(len(p4['text']), len(EXP4))) if p4['text'][j] != EXP4[j]), min(len(p4['text']), len(EXP4)))
        print('  首个差异@%d: 实=%r 期=%r' % (i, p4['text'][max(0,i-8):i+12], EXP4[max(0,i-8):i+12]))
        print('  实测全文: %s' % p4['text'])

last = rows2[-1]
szs = sorted({x['sz'] for x in last['runs'] if x['t'].strip()})
print('%s 末段(行35)字号 实测sz=%s 期望=[24] 文本=%s' % ('PASS' if szs == ['24'] else 'FAIL', szs, last['text'][:50]))

KEYS = [('4', '1.1.1.1-1．'), ('5', '1.2.1.1-1．'), ('13', '【答案】'), ('14', '　块标签芯片'), ('15', '定义：在空间')]
idx_map = {'4': 4, '5': 5, '13': 13, '14': 14, '15': 15}
all5 = True
for key, pref in KEYS:
    r = find(pref)
    if r is None:
        print('FAIL 图例行%s(%s) 未找到' % (key, pref)); all5 = False; continue
    exp = EXP4 if key == '4' else legend['texts'][key]
    eq = r['text'] == exp
    all5 &= eq
    print('%s 图例行%s 段idx=%d 文本%s 实测len=%d 期望len=%d' % ('PASS' if eq else 'FAIL', key, r['i'], '逐字等' if eq else '不等', len(r['text']), len(exp)))
    if not eq:
        print('  实测: %s' % r['text'])
        print('  期望: %s' % exp)
print('%s 图例区5行↔json（行4尾句按§四新文）' % ('PASS' if all5 else 'FAIL'))
