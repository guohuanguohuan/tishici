# -*- coding: utf-8 -*-
r"""立manifest.py — S5-W4 阶段二·四卷 件manifest.json 立件（键序按各卷源件＝ansblock 键序）。
消费方＝工具/答案抽册器.py resolve_canonical（题面库 manifest 缺位时以 冻结manifest键序 为 canonical）。"""
import hashlib
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
B = r'C:/提示词/工作区/_tmp换装正装0914'
OUT = None

VOLS = [
    (r'M2测评滚动/测评卷', 'M2测评卷', 'qp-m3.sty', 19, '测',
     '单元素养测评卷（一）第一章 19 题；回流制 2/1 页；滚A/滚B 题不入卷口径随件头注承旧'),
    (r'M2测评滚动/滚动卷A', '滚动卷A', 'qp-m3.sty', 16, '滚A',
     '滚动测评卷（A）16 题（命制-滚A 全卷）；回流制 2/1 页'),
    (r'M2测评滚动/滚动卷B', '滚动卷B', 'qp-m3.sty', 16, '滚B',
     '滚动测评卷（B）16 题；回流制 2/1 页'),
    (r'P1测评本/测评卷', 'P1测评卷', 'qp-m3p-overlay.sty', 19, '测',
     'P1 第9章 静电场 单元素养测评卷（一）19 题；物理骨架 overlay；回流制 3/3 页；\\setcounter{page}{41} 承装配 G7 链'),
]

READINGS = {
    'M2测评卷': 'true 错0溢0缺字0 页2 ANSKEY=19 [答案]×19 [解析]×5；pure 错0溢0缺字0 页1 ANSKEY=19 零泄答',
    '滚动卷A': 'true 错0溢0缺字0(under1=题12括注行 hbox 微松，非门项) 页2 ANSKEY=16 [答案]×16 [解析]×4；pure 同 under1 页1 零泄答',
    '滚动卷B': 'true 错0溢0缺字0 页2 ANSKEY=16 [答案]×16 [解析]×4；pure 错0溢0缺字0 页1 零泄答',
    'P1测评卷': 'true 错0溢0缺字0 页3 ANSKEY=19 [答案]×19 [解析]×0；pure 错0溢0缺字0 页3 零泄答',
}

NOTES = {
    'M2测评卷': 'S5-W4 阶段二（0914）：\\jpthree 零高固定栏→\\juancols multicols 三栏回流；案B 附卷 19 块逐键内联题后；'
               '退役＝卷末附卷页／\\anskey 补偿发射 19 键／\\dabiao 速查表（定义随撤）。题面字符零改（举证 _M2P1/题面零改举证-M2测评卷.txt）；'
               '页数 案B true4/pure3 → 回流 true2/pure1。',
    '滚动卷A': 'S5-W4 阶段二（0914）：同回流制改造；退役 16 键补偿发射＋速查表＋附卷页。题面零改（举证 _M2P1/题面零改举证-滚动卷A.txt）；'
               '页数 案B true3/pure2 → 回流 true2/pure1。',
    '滚动卷B': 'S5-W4 阶段二（0914）：同回流制改造；退役 16 键补偿发射＋速查表＋附卷页。题面零改（举证 _M2P1/题面零改举证-滚动卷B.txt）；'
               '页数 案B true3/pure2 → 回流 true2/pure1。',
    'P1测评卷': 'S5-W4 阶段二（0914）：同回流制改造（qp-m3p-overlay 件型层 E′）；退役 19 键补偿发射＋速查表＋附卷页——'
               '附卷内 \\tailfill 尾块随附卷整页退役（装配层 M3-TAILFILL log 锚在本件消失，成书重装装配断言须随改）；'
               '\\setcounter{page}{41} 与 figs/ 源位图零动。题面零改（举证 _M2P1/题面零改举证-P1测评卷.txt）；'
               '页数 案B true4/pure3 → 回流 true3/pure3。腿3 断言用 _M2P1/断言三腿-卷件紧跟-P1页脚白名单.py'
               '（父目录正本签名带按数学卷 RJB 签写，物理页脚「高中物理/必修第三册/RJ」被误计体墨，副本仅扩页脚签，三腿判线零改）。',
}


def md5f(p):
    return hashlib.md5(io.open(p, 'rb').read()).hexdigest()


def sha256f(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()


for rel, tag, sty, n, pre, desc in VOLS:
    d = os.path.join(B, rel)
    keys = ['%s-%d' % (pre, i) for i in range(1, n + 1)]
    man = {
        '片': tag,
        '件型': '测评卷（8 开横放三栏·卷件三栏回流制 \\juancols·题后紧跟答案制）·单源双档 main.tex＋[pure] 壳',
        '卷式注记': desc,
        '冻结manifest': '题面库 manifest 缺位（M2 第一章卷件/P1 物理卷件未立题面库），本件 manifest 冻结键序即 canonical',
        '冻结manifest键序': keys,
        '源件sha256': {
            'main.tex.bak_w4（案B 底本·改前自存）': sha256f(os.path.join(d, 'main.tex.bak_w4')),
        },
        'toolchain锁': {
            'file': sty,
            'md5': md5f(os.path.join(d, sty)),
            '注记': '本地挂载副本，禁改保 md5' + ('；P1 骨架七件（物理样张0911/骨架/qp-*.tex）只读零动' if 'overlay' in sty else ''),
        },
        '件指纹': {
            'main.tex.md5': md5f(os.path.join(d, 'main.tex')),
            'main-true.pdf.md5': md5f(os.path.join(d, 'main.pdf')),
            'main-pure.pdf.md5': md5f(os.path.join(d, 'main-pure.pdf')),
            '编译': 'xelatex -interaction=nonstopmode -halt-on-error main.tex ×2 / main-pure.tex ×2（cwd＝卷目录）',
            '双档读数': READINGS[tag],
            '三腿断言': 'exit=0（腿1 锚连含序｜腿2 块数恒等·双档零泄答｜腿3 栏底＜267.6mm）＋ --selftest 反装被拦 exit=0'
                       + ('；读数 _M2P1/_断言三腿-%s.txt' % tag),
        },
        '键↔号': {k: i + 1 for i, k in enumerate(keys)},
        '变更注记': NOTES[tag],
    }
    p = os.path.join(d, '件manifest.json')
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(man, f, ensure_ascii=False, indent=1)
    print('立件：', p)
