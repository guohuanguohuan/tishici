# -*- coding: utf-8 -*-
"""片规.py — M3 S2 波1 补位臂3·三片共用常量表（交接自 _tmpM3S2波1臂4_0914/门谱）。
补位臂3 任务面＝补值台账＋门谱全项复跑验证；本目录脚本为唯一新增写件源。
"""
import os

M3ROOT = 'C:/提示词/工作区/M3-第2章量产0913'
DAO = os.path.join(M3ROOT, '成卷/导学件')
TMK = os.path.join(M3ROOT, '成卷/题面库/manifest')

PIECES = {
    '09': {
        'dir': '课时09-圆与圆的位置关系',
        'nkey': 21,
        'sty_md5': '7c3930362be8a0a2bdf21bbf8ac16573',
        '侧件': '课时09-圆与圆的位置关系-答案侧.md',
        '题面件': '课时09-圆与圆的位置关系.md',
    },
    '14': {
        'dir': '课时14-2.6.2双曲线性质',
        'nkey': 71,
        'sty_md5': '7c3930362be8a0a2bdf21bbf8ac16573',
        '侧件': '课时14-2.6.2双曲线性质-答案侧.md',
        '题面件': '课时14-2.6.2双曲线性质.md',
    },
    '15': {
        'dir': '课时15-2.7.1抛物线方程',
        'nkey': 36,
        'sty_md5': '7c3930362be8a0a2bdf21bbf8ac16573',
        '侧件': '课时15-2.7.1抛物线方程-答案侧.md',
        '题面件': '课时15-2.7.1抛物线方程.md',
    },
}


def piece(k):
    p = dict(PIECES[k])
    p['key'] = k
    p['piece'] = os.path.join(DAO, p['dir'])
    p['mani'] = os.path.join(TMK, f'课时{k}.manifest.json')
    p['side'] = os.path.join(M3ROOT, '成卷/题面库', p['侧件'])
    p['tikumian'] = os.path.join(M3ROOT, '成卷/题面库', p['题面件'])
    here = os.path.dirname(os.path.abspath(__file__))
    p['draft'] = os.path.join(here, f'值台账底稿-课时{k}.json')
    p['keytable'] = os.path.join(here, f'键表-课时{k}.txt')
    return p
