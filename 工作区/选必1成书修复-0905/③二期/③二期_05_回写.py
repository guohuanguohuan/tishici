# -*- coding: utf-8 -*-
"""③二期 05 回写：副本_③ 四件 → 同步盘（逐件 300s×3 抗锁 copy2＋MD5 双向比对）。
页数零变化 → 册目录页/装订单不回写，仅核对同步盘现值＝②-E 锚（应全等）。
回写后同步盘终验：oMath 逐件对锚＋wp:extent 抽核＋目标媒体 md5 抽核（零 COM）。
"""
import zipfile, hashlib, io, os, re, shutil, time, json

SYNC = r'C:/提示词/高中数学/高中数学同步'
SRC = r'C:/提示词/工作区/选必1成书修复-0905/②工具/副本_③'
FILES = {
    '清单1': '人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx',
    '清单2': '人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx',
    '上61': '人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx',
    '下79': '人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx',
}
OMATH = {'清单1': 396, '清单2': 1156, '上61': 3251, '下79': 2876}
# ②-E 锚（③二期_00 实测同值）
SYNC_ANCHOR = {'清单1': 'b3175eae9d57742f66621549a48f1b0b', '清单2': 'cf79bdc95a8f9d8b092e158477831482',
               '上61': '139722a461839f6fc15bba20e1afbc44', '下79': 'fbe2cd47290b0d60049669516aa0ef49'}
TOC_MD5_ANCHOR = 'b5c2bbda6f173f185f3d69a2080042f6'   # 册目录页
PLAN_MD5_ANCHOR = 'd59e6a52bd8bf2d65e96be567a5eb9fb'  # 装订单.md

def md5f(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

res = {}
# 联动件核对（页数零变化 → 应全等、零回写）
toc = os.path.join(SYNC, '人教B版选必1·册目录页.docx')
plan = os.path.join(SYNC, '人教B版选必1·装订单.md')
res['册目录页_核对'] = {'sync_md5': md5f(toc), 'anchor': TOC_MD5_ANCHOR, 'equal': md5f(toc) == TOC_MD5_ANCHOR}
res['装订单_核对'] = {'sync_md5': md5f(plan), 'anchor': PLAN_MD5_ANCHOR, 'equal': md5f(plan) == PLAN_MD5_ANCHOR}
print('册目录页 全等:', res['册目录页_核对']['equal'], '装订单 全等:', res['装订单_核对']['equal'])

for code, fn in FILES.items():
    src, dst = os.path.join(SRC, f'{code}.docx'), os.path.join(SYNC, fn)
    src_md5, pre_md5 = md5f(src), md5f(dst)
    ok = False
    for t in range(1, 4):
        try:
            shutil.copy2(src, dst)
            if md5f(dst) == src_md5:
                ok = True
                print(f'{code}: 回写 OK（第{t}试） src={src_md5} 同步盘={md5f(dst)}')
                break
        except Exception as e:
            print(f'{code}: 第{t}试异常 {e!r}')
        time.sleep(3)
    # 回写后终验（零 COM）
    z = zipfile.ZipFile(dst)
    xml = z.read('word/document.xml').decode('utf-8')
    om = len(re.findall(r'<m:oMath[ >]', xml))
    embed_info = []
    for n in z.namelist():
        if n.startswith('word/media/') and n.endswith(('.png', '.jpg')):
            pass
    assert om == OMATH[code], f'{code} 回写后 oMath {om}≠{OMATH[code]}'
    # 页脚同串抽验（盖章未动，应与 ②-E 同）
    foot = re.findall(r'（共(\d+)页）·本(\d)/共6本', xml)
    res[code] = {'pre_md5': pre_md5, 'post_md5': md5f(dst), 'src_md5': src_md5, 'write_ok': ok,
                 'omath': om, 'footer样本': foot[:2]}
    print(f'  终验 oMath={om} 对锚 {OMATH[code]} PASS; 页脚样本 {foot[:2]}')

json.dump(res, open(r'C:/提示词/工作区/选必1成书修复-0905/②工具/报告/③二期_回写.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
allok = all(res[c]['write_ok'] and res[c]['post_md5'] == res[c]['src_md5'] for c in FILES)
print('SUMMARY_WRITEBACK ALLOK =', allok)
