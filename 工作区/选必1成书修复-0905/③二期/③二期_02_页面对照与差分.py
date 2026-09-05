# -*- coding: utf-8 -*-
"""③二期 02 页面对照与差分：嵌回副本 PDF vs ②-E 基线 PDF。
1) 页数对照（预期 15/15/65/62 全等；有变即停跑信号）
2) 逐页像素差分：定位变化页；变化页上验证差分区域 ⊆ 图片框∪容差（文字零移动=像素级零回流）
"""
import io, os, json, sys
import pymupdf

OLD = r'C:/提示词/工作区/选必1成书修复-0905/②工具/巡检_②E/pdf'
NEW = r'C:/提示词/工作区/选必1成书修复-0905/②工具/巡检_③二期/pdf'
REPORT = r'C:/提示词/工作区/选必1成书修复-0905/②工具/报告'
EXPECT = {'清单1': 15, '清单2': 32, '上61': 65, '下79': 62}
DPI = 100
TOL_PT = 6  # 差分越界容差(pt)

def render(page, dpi=DPI):
    pm = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
    return pm.samples, pm.width, pm.height

out = {'pages': {}, 'changed_pages': {}, 'reflow_alerts': []}
allok = True
for code, expn in EXPECT.items():
    dold, dnew = pymupdf.open(os.path.join(OLD, f'{code}.pdf')), pymupdf.open(os.path.join(NEW, f'{code}.pdf'))
    n1, n2 = len(dold), len(dnew)
    ok = (n1 == n2 == expn)
    allok &= ok
    out['pages'][code] = {'old': n1, 'new': n2, 'expect': expn, 'ok': ok}
    print(f'{code}: {n1} vs {n2} (expect {expn}) {"OK" if ok else "PAGE-CHANGE!"}')
    changed = []
    if n1 != n2:
        allok = False
        continue
    for i in range(n1):
        s1, w, h = render(dold[i])
        s2, w2, h2 = render(dnew[i])
        if (w, h) != (w2, h2):
            changed.append(i + 1); out['reflow_alerts'].append(f'{code} p{i+1} 尺寸变化')
            continue
        diff = [k for k in range(0, len(s1), 2) if abs(s1[k] - s2[k]) > 6]
        if len(diff) < 8:
            continue
        # 逐像素归属：差分像素须落入本页图片框(∪,容差TOL_PT)内，否则＝文字/版面移动
        imgs = [tuple(v * DPI / 72 for v in it['bbox']) for it in dnew[i].get_image_info()]
        T = TOL_PT / 72 * DPI
        viol = []
        for k in diff:
            x, y = k % w, k // w
            if not any(bx0 - T <= x <= bx1 + T and by0 - T <= y <= by1 + T for (bx0, by0, bx1, by1) in imgs):
                viol.append((x, y))
        changed.append((i + 1, len(diff), len(viol)))
        if len(viol) > 50:
            xs = [v[0] for v in viol]; ys = [v[1] for v in viol]
            out['reflow_alerts'].append(f'{code} p{i+1} 越界差分像素{len(viol)} bbox=({min(xs):.1f},{min(ys):.1f},{max(xs):.1f},{max(ys):.1f})px@100dpi')
    out['changed_pages'][code] = changed
    print(f'  变化页: {[c[0] if isinstance(c, tuple) else c for c in changed]}')
    print(f'  越界告警: {[a for a in out["reflow_alerts"] if a.startswith(code)]}')

out['ALLOK'] = allok and not out['reflow_alerts']
json.dump(out, open(os.path.join(REPORT, '③二期_02_页面对照.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('SUMMARY_DIFF ALLOK =', out['ALLOK'])
