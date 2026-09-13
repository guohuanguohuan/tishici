# -*- coding: utf-8 -*-
r"""冻manifest批C.py —— M3 S1 批C 四片冻结器（工序件，跑于 _tmpM3S1批C0913/；克隆 _tmpM3S1首批0913/冻manifest.py）。

口径（S1 题面库代理·批C 轮；提取规则与 对号门.py 单一约定）：
  对每片：解析 题面侧/答案侧 → 键序（canonical 位）＋逐键哈希（题面全文 sha256／答案块 sha256）
  ＋文件级哈希＋源件（定稿）哈希 → 写 `成卷/题面库/manifest/<片>.manifest.json`；另加 `批`／`备注` 字段。
    题面侧：`### <键>｜…` 起块；题面全文＝块内除【注】行、空行、`---` 分隔行外全部行。
    答案侧：`% ans:<键>` 锚点行；`值：` 行取规范化值；`详解：` 行取详解指针；答案块哈希＝值+"\n"+详解行。
  冻结纪律：片冻后不可变；单点变更→重冻该片→下游回冲。
跑法：python 冻manifest批C.py [--stamp 2026-09-14T00:05:11+0800] [片名 ...]
"""
import hashlib
import io
import json
import os
import re
import sys
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', 'M3-第2章量产0913'))
TMUB = os.path.join(ROOT, '成卷', '题面库')
MANI = os.path.join(TMUB, 'manifest')
DING = os.path.join(ROOT, '定稿')

SLICES = {
    '课时10': ('2.4曲线与方程',        '定稿/批C-课时10-2.4曲线与方程.md'),
    '课时11': ('2.5.1椭圆的标准方程',  '定稿/批C-课时11-2.5.1椭圆的标准方程.md'),
    '课时12': ('2.5.2椭圆的几何性质',  '定稿/批C-课时12-2.5.2椭圆的几何性质.md'),
    '课时13': ('2.6.1双曲线的标准方程', '定稿/批C-课时13-2.6.1双曲线的标准方程.md'),
}
MULTI_EXP = {'课时10': 0, '课时11': 1, '课时12': 1, '课时13': 0}

REMARKS = {
    '课时10': [
        '拓区读数（照件内§5/§9.5/§9.6 区末恒等）：素材域36＝正文16＋G5 5＋拓展14＋删除1（净域35）；拓展席＝拓2~拓15 实产14（拓1 撤位登记席不设题不占键）。',
        '拓1 撤席让位（0913案2令1，成品②2.4.2.2-2 真双列）：该题唯一活位＝本片 2章-导-课时10-G1；防双收B22；拓1 号跳号留痕不设 frozen 键。',
        '0913 批C置换入槽：原中5/6/7 三席挤出→拓展册 10-拓13/14/15（件7-#29／教材B⑦／成品2.4.2.2-3）；正文简8~简10＝命制10-命1改/命2/命3改（照录）；置换净零。',
        '10-填2 备位销（教材8→7，A④复核闸未过不顶补，件内§1/§8.2 认账）。',
        '槽型口径：2章-练-课时10-难1（成品②2.4.3-15，答案BCD）槽型标「多结论选择」——源卷与件内均未标多选，汇总§十一课时10行多选＝0 维持，不计多选门；S4 如按多选排版须回改§十一并重冻本片。难2＝填空（序号②④）。',
        '件内块号对照：件内 §9.1 即 G1~G5；简7／中1~中4 为 §4 定稿核录指针席，题面照 §4【定稿2.4-新N】全文转录（详解指针亦指 §4）。',
    ],
    '课时11': [
        '拓区读数（照件内§5/§9.5/§9.6 区末恒等）：素材域37＝正文16＋G5 5＋拓展16（无删除）；拓展席＝拓1＋拓3~拓17 实产16（拓2 撤位登记席不设题不占键）。',
        '拓2 撤席让位（0913案2令2，成品②2.5.1.2.2-3×件3-#21 真双列，成品版留正文）：该题唯一活位＝本片 2章-练-课时11-简7（源号翻归件3-#21）；防双收B21；拓2 号跳号留痕。',
        '0913 批C置换入槽：原中5/6/7 三席挤出→11-拓15/16/17（成品2.5.1.3.1-11/2.5.1.4.1-13/2.5.1.6-21）；正文简8~简10＝命制11-命1/命2/命3（§九9.2原案照录）。',
        '前引注记：简10/难2 题面设问词「离心率」系2.5.2概念前引（成品照录不改）——S4 装配换问口径随行。',
        '件内块号对照：件内 §9.1~§9.4 即 G1~G5＋简/中/难席，一一对应。',
    ],
    '课时12': [
        '拓区读数（照件内§9 区末自查恒等）：本区题块63＝G5 5＋正文16＋拓展42（拓展拓1~拓42 连续无缺号）；域64＝63＋件4-#7（转投2.7槽，不在本域）。',
        '件内块号对照：冻结键 G1~G5 ↔ 件内 12-单1~单3＋12-填1~填2（G1=单1、G2=单2、G3=单3、G4=填1、G5=填2，照件内§9 定稿号编排）；练习键与件内同号块一一对应。',
        '12-拓6（成品②2.5.2.8.1-12）↔ 12-拓27（3章件4-#10）互斥注记键：题面答案全同，S4 装配拓展册二选一/分册，勿同卷并出（前置闸条件②/R5 落地，件内区末注记1）。',
        '蒙日族件内 S4 组合≤2 口径随行；R1~R3 前置闸整改已落盘（拓28/拓31 头标【简】、§5 成品26枚举含-35/-36、件4-#19＝0.85）。',
        '档位偏差注随行：简6（件4-#6）源标0.65记简档；G2（件4-#28）源标0.85/总表亲算0.94 同属简档。',
    ],
    '课时13': [
        '拓区读数（照件内§5/§9.五/区末自查恒等）：本区题块27＝G5 5＋正文16＋拓展6（域27，无删除）；拓展席＝拓1~拓6（成品-7/-14/-16＋件8-#8＋0913置换入拓5/拓6）。任务括号「26」与件内不符（实排6；台账§一与挤出指令单§二同证批C拓区78＝14＋16＋42＋6）——照件内落盘，差异入 canonical 更新指令单。',
        '件内块号对照：冻结键 G1~G5 ↔ 件内 13-单1~单3＋13-填1~填2；练习键与件内同号块一一对应（简9/简10＝0913 命制入槽照录）。',
        '0913 批C置换入槽：原中5/6 两席挤出→13-拓5/拓6（成品③2.6.1.7-10／2.6.1.9-13）；原中5 多选随拓不计正文门——汇总§十一课时13行多选 1→0，本片多选＝0。',
        '难2＝件13-#25 借入难位（0.4难+档，件内§6 借入登记）；简1 与教材习题2-4C②同文防双收（教材侧不收）。',
        '双曲线闸：13-中2 源主解焦半径公式路线已改第一定义＋等积法（件内【口径注】），答案 16/5 不变。',
    ],
}


def sha(t):
    if isinstance(t, bytes):
        return hashlib.sha256(t).hexdigest()
    return hashlib.sha256(t.encode('utf-8')).hexdigest()


def parse_questions(path):
    """题面侧 → [(键, 槽型, 题面全文)]，保持文件序。"""
    text = open(path, encoding='utf-8', newline='').read()
    out, cur = [], None
    for ln in text.splitlines():
        if ln.startswith('### '):
            if cur:
                out.append(cur)
            head = ln[4:]
            key = head.split('｜')[0].strip()
            kinds = [s for s in head.split('｜')[1:] if s in ('单选', '多选', '填空', '解答')]
            cur = [key, kinds[0] if kinds else '', []]
        elif cur is not None:
            if ln.strip() == '---':
                out.append(cur)
                cur = None
            elif ln.startswith('【注】') or not ln.strip():
                continue
            else:
                cur[2].append(ln)
    if cur:
        out.append(cur)
    return [(k, t, '\n'.join(body)) for k, t, body in out]


def parse_answers(path):
    """答案侧 → [(键, 值, 详解指针)]，保持文件序。"""
    text = open(path, encoding='utf-8', newline='').read()
    out, cur = [], None
    for ln in text.splitlines():
        m = re.match(r'^% ans:(\S+)\s*$', ln)
        if m:
            if cur:
                out.append(cur)
            cur = [m.group(1), '', '']
        elif cur is not None:
            if ln.startswith('值：'):
                cur[1] = ln[2:].strip()
            elif ln.startswith('详解：'):
                cur[2] = ln[3:].strip()
    if cur:
        out.append(cur)
    return out


def freeze(slice_name, spec, stamp=None):
    title, src_rel = spec
    qp = os.path.join(TMUB, '%s-%s.md' % (slice_name, title))
    ap = os.path.join(TMUB, '%s-%s-答案侧.md' % (slice_name, title))
    sp = os.path.join(DING, os.path.basename(src_rel))
    for p in (qp, ap, sp):
        assert os.path.exists(p), '缺件：%s' % p
    qs, ans = parse_questions(qp), parse_answers(ap)
    qkeys = [k for k, _, _ in qs]
    akeys = [k for k, _, _ in ans]
    assert qkeys == akeys, '%s 键序不等：题面侧%d vs 答案侧%d\n缺%s\n多%s' % (
        slice_name, len(qkeys), len(akes), sorted(set(qkeys) - set(akes))[:6], sorted(set(akes) - set(qkeys))[:6])
    daov = dict((k, (v, d)) for k, v, d in ans)
    per = {}
    for k, _, qtext in qs:
        v, d = daov[k]
        assert v, '%s 空值' % k
        assert d, '%s 缺详解锚点' % k
        per[k] = {'题面': sha(qtext), '答案': sha(v + '\n' + d)}
    multi = [k for k, t, _ in qs if t == '多选']
    exp = {
        '键数': len(qkeys),
        '导学键数': sum(1 for k in qkeys if '-导-' in k),
        '练习键数': sum(1 for k in qkeys if '-练-' in k),
        '多选数': len(multi),
        '多选键': multi,
        '对号门期望': '题面侧键集＝答案侧锚点集＝manifest键清单（%d=%d=%d，序一致零缺漏）；'
                  '多选门≤4（本片%d，%s）；题面全文/答案块哈希逐一相符；片冻后不可变，变更→重冻→下游回冲'
                  % (len(qkeys), len(akeys), len(qkeys), len(multi),
                     '触顶合规' if MULTI_EXP[slice_name] == 4 and len(multi) == 4 else '合规'),
    }
    assert exp['导学键数'] == 5 and exp['练习键数'] == 16, '%s 导学/练习键数异常：%d/%d' % (
        slice_name, exp['导学键数'], exp['练习键数'])
    assert exp['多选数'] == MULTI_EXP[slice_name], '%s 多选数 %d ≠ 期望 %d' % (
        slice_name, exp['多选数'], MULTI_EXP[slice_name])
    stamp = stamp or datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z')
    mani = {
        '片': slice_name,
        '章': 'M3选必1第2章',
        '批': '批C',
        '键式': '2章-<册>-课时<NN>-<槽>',
        '冻时戳': stamp,
        '源件': src_rel.replace('定稿/', ''),
        '源件sha256': sha(open(sp, 'rb').read()),
        '题面侧': os.path.basename(qp),
        '题面侧sha256': sha(open(qp, 'rb').read()),
        '答案侧': os.path.basename(ap),
        '答案侧sha256': sha(open(ap, 'rb').read()),
        '键序': qkeys,
        '逐键哈希': per,
        '期望值': exp,
        '备注': REMARKS[slice_name],
    }
    out = os.path.join(MANI, '%s.manifest.json' % slice_name)
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(mani, f, ensure_ascii=False, indent=1)
    print('%s 冻结 ✓｜键%d（导%d＋练%d）｜多选%d｜manifest→%s'
          % (slice_name, exp['键数'], exp['导学键数'], exp['练习键数'], exp['多选数'], os.path.relpath(out, ROOT)))


def main():
    args = sys.argv[1:]
    stamp = None
    if '--stamp' in args:
        i = args.index('--stamp')
        stamp = args[i + 1]
        args = args[:i] + args[i + 2:]
    names = args or list(SLICES)
    for n in names:
        freeze(n, SLICES[n], stamp)


if __name__ == '__main__':
    main()
