# -*- coding: utf-8 -*-
"""跑批S5.py — A 逐件抽册 44 件＋B 拓展册泄漏补扫。写读数 → 逐件汇总.json"""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _s5lib import HERE, pieces_of, run_tool, load_readings, source_leakscan


def one(job):
    jianxing, pian, pdir = job
    out = os.path.join(HERE, '%s-%s' % (jianxing, pian))
    r = run_tool(pdir, out)
    rd = load_readings(out)
    return {'件型': jianxing, '片': pian, '目录': out.replace('\\', '/'),
            'rc': r['rc'], '秒': r['秒'], '尾段': r['尾段'],
            '键数': (rd or {}).get('键数'), 'canonical来源': (rd or {}).get('canonical来源'),
            '红': (rd or {}).get('红'), '页数': (rd or {}).get('页数'),
            '源md5': (rd or {}).get('源件md5'), 'sty_md5': (rd or {}).get('sty_md5'),
            '台账': (rd or {}).get('台账')}


def main():
    jobs = []
    for jianxing, _ in (('导学件', 0), ('练习件', 0), ('拓展册', 0)):
        for pian, pdir in pieces_of(jianxing):
            jobs.append((jianxing, pian, pdir))
    print('件域 %d 件' % len(jobs))
    results = []
    warm, rest = jobs[:1], jobs[1:]                    # 首件暖机（字体缓存）后并行×3
    r0 = one(warm[0])
    results.append(r0)
    print('暖机 %s rc=%d %.1fs' % (r0['片'], r0['rc'], r0['秒']))
    with ThreadPoolExecutor(max_workers=3) as ex:
        for i, r in enumerate(ex.map(one, rest)):
            results.append(r)
            print('[%02d/%02d] %s-%s rc=%d 键=%s 红=%s %.1fs'
                  % (i + 2, len(jobs), r['件型'], r['片'], r['rc'],
                     r['键数'], len(r['红'] or []), r['秒']))
    # B：拓展册泄漏补扫——桩C（0914）题面库拓展上/下册立片后撤「源件题面区替代」
    # 临时口径（照锁退役，留证＝备份-值台账-*与 泄漏补扫.json 旧读数）；针源自此
    # ＝题面库拓展上册.md/拓展下册.md（抽册器 build_leakset 门内针，已在 A 段门谱生效）。
    for jianxing, pian, pdir in jobs:
        if jianxing == '拓展册':
            for r in results:
                if r['件型'] == '拓展册' and r['片'] == pian:
                    r['补扫'] = '撤（桩C 0914：针源换题面库 %s.md，临时口径照锁退役）' % pian
            print('补扫 %s：撤（针源换题面库，照锁退役）' % pian)
    json.dump(results, open(os.path.join(HERE, '逐件汇总.json'), 'w',
                            encoding='utf-8'), ensure_ascii=False, indent=1)
    nred = sum(1 for r in results if r['rc'] != 0 or r['红'])
    print('== 跑批完：44 件，rc红/门红件数=%d ==' % nred)


if __name__ == '__main__':
    main()
