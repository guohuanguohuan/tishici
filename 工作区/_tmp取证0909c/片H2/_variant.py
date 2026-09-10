# -*- coding: utf-8 -*-
"""片H2 变体矩阵驱动 v4：scale / dfrac / 串连字符 / 脚本档 / medmuskip 开关 → 构建。
用法：python _variant.py <tag> <scale> <dfrac0|1> <strh0|1> <sms0|1> "<medmu>|off"
  medmu 例："2mu"、"2mu plus 2mu minus 4mu"、"off"（=撤本档，回 TeX 默认 4mu±）"""
import os
import re
import subprocess
import sys

VF = r'C:/提示词/工作区/字替对照-0909/variantF'
OUT = r'C:/提示词/工作区/_tmp取证0909c/片H2'
LAYOUT = os.path.join(VF, 'qp-layout.tex')
POST = os.path.join(VF, 'postproc_daoxue.py')
MED_RE = re.compile(r'\n\\medmuskip=[^\n]*')
MED_OFF = '\n' + chr(92) + 'medmuskip=0mu'   # 占位（不在正文生效；off 时整行替换为注释）


def patch_layout(scale, dfrac, sms, medmu):
    s = open(LAYOUT, encoding='utf-8').read()
    s = re.sub(r'(\\setmathfont\{texgyretermes-math\.otf\}\[Scale=)[0-9.]+', r'\g<1>' + scale, s)
    on, off = '\\let\\frac\\dfrac', '%\\let\\frac\\dfrac'
    if on not in s and off not in s:
        s = s.replace('\\medmuskip=0mu', '\\medmuskip=0mu\n' + on, 1)
    s = s.replace(off, on)
    if not dfrac:
        s = s.replace(on, off)
    DMS = chr(92) + 'DeclareMathSizes'
    s = s.replace(chr(10) + '%' + DMS, chr(10) + DMS)
    if not sms:
        s = s.replace(chr(10) + DMS, chr(10) + '%' + DMS)
    # medmuskip 归一（注释行不动）
    assert MED_RE.search(s), '未找到 \\medmuskip 生效行'
    if medmu == 'off':
        rep = chr(10) + '%' + chr(92) + 'medmuskip=2mu'
    else:
        rep = chr(10) + chr(92) + 'medmuskip=' + medmu
    s = MED_RE.sub(lambda m: rep, s, count=1)
    open(LAYOUT, 'w', encoding='utf-8').write(s)


def patch_post(strh):
    s = open(POST, encoding='utf-8').read()
    open(POST, 'w', encoding='utf-8').write(s)


def build(tag):
    r = subprocess.run(['bash', os.path.join(OUT, '_build.sh'), tag], capture_output=True, text=True)
    return r.stdout


if __name__ == '__main__':
    tag, scale, dfrac, strh, sms, medmu = sys.argv[1:7]
    patch_layout(scale, dfrac == '1', sms == '1', medmu)
    out = build(tag)
    print(out.strip().splitlines()[-1])
