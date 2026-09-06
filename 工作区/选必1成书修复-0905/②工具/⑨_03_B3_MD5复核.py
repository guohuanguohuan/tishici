# -*- coding: utf-8 -*-
"""⑨轮 B3：12件docx MD5改后复核 vs ⑨_12件MD5锚定.json；结果落 报告/⑨_B3_MD5复核.json。"""
import hashlib, json, os

ROOT = r'C:/提示词'
with open(ROOT + '/工作区/选必1成书修复-0905/②工具/报告/⑨_12件MD5锚定.json', encoding='utf-8') as f:
    anchor = json.load(f)
res, allok = {}, True
for code, info in anchor.items():
    p = ROOT + '/' + info['path']
    h = hashlib.md5()
    with open(p, 'rb') as f:
        h.update(f.read())
    now = h.hexdigest()
    same = (now == info['md5'])
    allok = allok and same
    res[code] = {'改前': info['md5'], '改后': now, '对平': same,
                 'bytes_改前': info['bytes'], 'bytes_改后': os.path.getsize(p)}
out = ROOT + '/工作区/选必1成书修复-0905/②工具/报告/⑨_B3_MD5复核.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
for code, r in res.items():
    print('%-3s %s %s' % (code, '对平' if r['对平'] else '!!漂移!!', r['改后']))
print('B3-MD5 汇总: %s → %s' % ('12/12 对平' if allok else '存在漂移', out))
