# -*- coding: utf-8 -*-
r"""_权威实测-缩档臂0910.py —— 缩档轮·权威实测复验驱动（临时产物，落 缩档测量/）。

为什么要有这个驱动：口径源 工作区/_tmp取证0909c/片G/权威实测.py 的 MAP 表把「声明置宽 mm」
逐图写死（84.0/41.1/42.0/84.0/66.3/54.7），而本轮改件动的正是这些置宽。口径源不在本轮改件清单
（纪律：只动 body.tex／六片段／_测v4断言.py），故不改它一字——本驱动 importlib 原样载入口径源，
**只在运行时把 MAP 第 3 列换成缩档后端档**，其余（并簇、线框重放、标签认领、同比、窗值建议）
一字不动。素材侧与件内侧仍走同一函数，Δ／不变量口径与改件前完全可比。

用法：python -X utf8 _权威实测-缩档臂0910.py [new|old]      （new＝缩档后端档，默认）
      落产物：缩档后-权威实测.txt（由外层重定向，本脚本只写 stdout）
"""
import importlib.util
import sys

AUTH = 'C:/提示词/工作区/_tmp取证0909c/片G/权威实测.py'
NEW = {'g6-triple': 80.8, 'g1-prism': 41.1, 'g2-cubeE': 42.0,
       'g3-cube6': 36.3, 'g4-dihedral': 30.5, 'g5-fold': 28.2}


def load():
    spec = importlib.util.spec_from_file_location('_auth_qw_arm', AUTH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)               # __main__ 门控 → 导入不触发自跑
    return mod


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    arm = (sys.argv[1] if len(sys.argv) > 1 else 'new').lower()
    m = load()
    if arm == 'new':
        m.MAP = [t[:2] + (NEW[t[3]],) + t[3:] for t in m.MAP]
    print('#' * 132)
    print('# 本件由 _权威实测-缩档臂0910.py 驱动：口径源＝_tmp取证0909c/片G/权威实测.py（importlib 原样载入，'
          '未改一字）')
    print('# 运行时覆写＝仅 MAP 第 3 列「声明置宽 mm」→ 缩档后端档 %s（臂＝%s；口径源内置旧档 '
          '84.0/41.1/42.0/84.0/66.3/54.7 系改件前）' % (
              '/'.join('%.1f' % NEW[k] for k in ['g6-triple', 'g1-prism', 'g2-cubeE',
                                                 'g3-cube6', 'g4-dihedral', 'g5-fold']), arm))
    print('# 下方所有读数（含 md5 与「7 页」字样）均系口径源自带文案，md5 行为其硬编码列，不作数。')
    print('#' * 132)
    return m.main()


if __name__ == '__main__':
    sys.exit(main())
