# -*- coding: utf-8 -*-
r"""_注记扫描.py —— 答案册·内部注记卫生门（P1 注释卫生门同构，目验修红0913 派生）。

射程：组装S5.py 数据源的**印面**全量——即 body.tex 将印给学生的每一行（V 表值串＋解析串＋
build_body/build_body_rest 静态行）。纯 Python 注释／工具串（断言语、门表注）非印面，不扫。
判据：内部过程语模式电池（日期串／义务代号／钉-N／勘正挂账呈报／主会话主脑／逻辑闸改字义务／
亲算盲解 numpy sympy／源详解源件讲部／台账批次基准表／撤下撤销／S·P 代号／键指称·快照·对号／
排版编辑过程语（补分隔·删法·重标·随册·口径等）／§档引用）。随册拍板语（两制并存、钝制/取锐
值面）不在电池——属内容非过程语。
跑法：python _注记扫描.py   → 逐条列 行号·键·模式·片段；全净 exit 0，有残留 exit 1（门态）。
零写盘；不触 body.tex／值快照；键值与数学内容零改动（本门只读）。
"""
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import 组装S5 as z

# 内部注记模式电池（名, 正则）
BATTERY = [
    ('日期串', r'20\d{2}[-年]\d{1,2}'),
    ('义务代号', r'义[0-9A-ZＡ-Ｚ]+[-－]\d+'),
    ('钉N', r'钉-?\d'),
    ('勘误更正', r'勘正|勘误|衍字|已正|误算|应作'),
    ('挂账呈报', r'挂账|呈报|待钉|待裁|保持待'),
    ('主会话主脑', r'主会话|主脑'),
    ('逻辑闸改字', r'逻辑闸|逻辑撤销|改字义务'),
    ('亲算验证', r'亲算|盲解|numpy|sympy|批验|三重验证'),
    ('源件勘语', r'源详解|源件|讲部|详解栏|答案栏按'),
    ('台账批次', r'台账|批\d|基准表|判例'),
    ('撤下撤销', r'撤下|撤销|已撤'),
    ('SP代号', r'(?<![0-9A-Za-z])[SP]\d(?![0-9])'),
    ('键指称', r'键\s?[A-Za-z]|键值|快照|对号|pair'),
    ('装配器语', r'组装|body\.tex|值快照|骨架'),
    ('档位引用', r'§\s*\d'),
    ('排版过程语', r'补分隔|等号后|分隔：|印钝制|排版'),
    ('编辑过程语', r'删法|仅留|重建|重标|回填|注销|随册|拍板|口径|冻结|在案'),
]


def build_surface():
    """印面全行＝body 产出行（与 main() 写盘内容同源；vskip 微胶行不入印面账）。"""
    L = z.build_body()
    z.build_body_rest(L)
    return L


def scan():
    L = build_surface()
    hits = []
    key = '(册首)'
    for i, ln in enumerate(L, 1):
        m = re.match(r'^%\s*pair:(\S+)', ln)
        if m:
            key = m.group(1)
            continue
        if not ln or ln.startswith('%'):
            continue
        for name, pat in BATTERY:
            for mm in re.finditer(pat, ln):
                s = max(0, mm.start() - 12)
                hits.append((i, key, name, mm.group(), ln[s:mm.end() + 18]))
    return hits


def main():
    hits = scan()
    if not hits:
        print('注记扫描：印面全净——内部过程语 0 残留 ✓')
        sys.exit(0)
    print('注记扫描：残留 %d 处 ✗' % len(hits))
    for i, key, name, tok, ctx in hits:
        print(' L%-5d %-14s %-8s 命中「%s」 …%s…' % (i, key, name, tok, ctx.replace('\n', ' ')))
    sys.exit(1)


if __name__ == '__main__':
    main()
