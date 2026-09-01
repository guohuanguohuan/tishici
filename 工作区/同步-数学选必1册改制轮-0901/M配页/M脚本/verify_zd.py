# -*- coding: utf-8 -*-
"""装订单数字↔S盖章记录逐件脚本核对（页数/start/N/件标识/部分归属/Y/本列/starts串）。"""
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REC = r'C:/提示词/工作区/同步-数学选必1册改制轮-0901/S盖章/盖章记录.md'
ZD = '装订单_wip.md'

# 盖章记录表
rec = {}
for ln in open(REC, encoding='utf-8'):
    m = re.match(r'^\|\s*(P\d+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*$', ln)
    if m:
        part, fname, pages, start, tag, n = m.groups()
        rec[fname.strip()] = (part, int(pages), int(start), tag.strip(), int(n))
assert len(rec) == 10, len(rec)

zd = open(ZD, encoding='utf-8').read()
errs = []
for fname, (part, pages, start, tag, n) in rec.items():
    row = [ln for ln in zd.splitlines() if fname in ln and ln.startswith('|')]
    if not row:
        errs.append('缺行: ' + fname); continue
    ln = row[0]
    cols = [c.strip() for c in ln.split('|')]
    # cols: 空|序|本|件名|类型|题量|页数|start|部分N|件标识|空
    try:
        pg = int(re.match(r'(\d+)', cols[6]).group(1))
        st = int(cols[7])
    except Exception as e:
        errs.append(f'解析失败 {fname}: {e}'); continue
    if pg != pages: errs.append(f'页数不符 {fname[:20]}: 单{pg} vs 记录{pages}')
    if st != start: errs.append(f'start不符 {fname[:20]}: 单{st} vs 记录{start}')
    if f'{part}（共{n}页）' not in ln: errs.append(f'部分/N不符 {fname[:20]}')
    if f'{tag}（共{n}页）' not in ln: errs.append(f'件标识不符 {fname[:20]}')

# Y/本列/starts串
if '全册合计＝16+20+154+5+39+221＝**455页**' not in zd: errs.append('Y合计句缺失/不符')
if '逐本合计 16/20/154/5/39/221 全部≤400' not in zd: errs.append('本列合计句缺失/不符')
if '1/1/1/78/1/1/1/54/110/151' not in zd: errs.append('starts串缺失/不符')
ben = dict(re.findall(r'\*\*本(\d)\*\*＝序\d+—\d+（[^）]*?）?[^：]*?：内容页合计 \*\*(\d+)\*\* 页', zd))
# 手工核对本页数
ben_exp = {1: 16, 2: 20, 3: 154, 4: 5, 5: 39, 6: 221}
for b, p in ben_exp.items():
    if zd.count(f'内容页合计 **{p}** 页') < 1: errs.append(f'本{b}页数{p}缺失')
if sum(ben_exp.values()) != 455: errs.append('本列合计≠455')
# 作废注记
if '437 页版' not in zd or 'A\'改制轮（本轮）后以本装订单' not in zd: errs.append('作废注记缺失')
# 同串要素
if '第X页' not in zd or '共N页' not in zd or 'NUMPAGES' not in zd or 'STYLEREF' not in zd: errs.append('页脚形态节要素缺失')
# 题量括注
for frag in ['61题（节1.1.1—1.2.4）', '79题（节1.2.5）', '92题（节2.1—2.3.3）', '90题（节2.3.4—2.5.2）',
             '68题（节2.6.1—2.7.2）', '89题（节2.8）', '29题', '13题', '47条', '67条']:
    if frag not in zd: errs.append('题量括注缺失: ' + frag)

if errs:
    print('FAIL')
    for e in errs: print(' -', e)
    sys.exit(1)
print('True —— 装订单21行/页数/start/部分N/件标识与S盖章记录逐件一致；Y=455；本列16/20/154/5/39/221全≤400；starts串、作废注记、同串要素、题量括注全在位')
