# -*- coding: utf-8 -*-
"""桩C 题面库补档（器升制·工单 S5-W1 桩C／军师补强③口径反转明裁）：
拓展上/下册 md（题面侧＋答案侧）＋manifest 冻结入 成卷/题面库/。
- 题面侧＝拓展册 main.tex 题面区 原文照录（\\tuhao 行剥座标/难度标起，至 \\liubai 止；
  \\zux 组头不入题面体，登组头于头段源注）；
- 答案侧＝值取台账 items[].值（渲染形照录），详解＝件内 ansblock 指针（字段规范「亲算＝详解」别名同口径）；
- manifest 冻结＝键序（装配序）＋逐键哈希（题面/答案，照对号门 parse 口径）＋文件 sha256＋期望值；
- 键务三约束：纯增量片零动（21 片零触碰）、对号门 strict 21 片复跑恒 0、留痕另账段（总表追加两行）；
- 明裁登记：拓展册 125 键（上 45＋下 80，以实算为准）与课时片同键并存＝同题两印在案口径，
  勿误报双挂；泄漏门针源换题面库（撤「源件题面区替代」临时口径，照锁退役）。
写入域＝成卷/题面库/拓展新片（桩C 授权）。零 git。
"""
import datetime
import glob
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _s5lib import CJ, T  # noqa: E402

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TMUB = os.path.join(CJ, '题面库')
MANI = os.path.join(TMUB, 'manifest')
RE_TUHAO = re.compile(r'^\\tuhao\{([^{}]*)\}\s*(.*)$')
RE_ZUX = re.compile(r'^\\zux\{(.*)\}\s*%?\s*$')
RE_JIE = re.compile(r'^\\jietitle\{(.*)\}\s*%?\s*$')
RE_B = re.compile(r'^\\begin\{ansblock\}\[([^\]]+)\]')
RE_B_ANY = re.compile(r'\\begin\{ansblock\}\[([^\]]+)\]')


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_text(t):
    return hashlib.sha256(t.encode('utf-8')).hexdigest()


def now_stamp():
    return datetime.datetime.now().astimezone().isoformat(timespec='seconds')


def key_universe(jianxing):
    ks = set()
    for p in glob.glob(os.path.join(CJ, jianxing, '*', 'main.tex')):
        ks |= set(RE_B_ANY.findall(open(p, encoding='utf-8').read()))
    return ks


dao_k = key_universe('导学件')
lian_k = key_universe('练习件')

results = {}
for pian in ('上册', '下册'):
    pian_name = '拓展%s' % pian
    pdir = os.path.join(CJ, '拓展册', pian)
    main_path = os.path.join(pdir, 'main.tex')
    src = open(main_path, encoding='utf-8', newline='').read()
    lines = [ln.rstrip('\r') for ln in src.split('\n')]
    led = json.load(open(os.path.join(pdir, '值台账-%s.json' % pian), encoding='utf-8'))
    led_by_key = {it['key']: it for it in led['items']}
    # —— 题面区解析（\zux 组头｜\jietitle 节名｜\tuhao 起题面体） ——
    qrows = []  # (key, seat, form, jie, zux, diff, [body lines])
    jie = zux = ''
    i = 0
    while i < len(lines):
        ln = lines[i]
        mj = RE_JIE.match(ln.strip())
        if mj:
            jie = mj.group(1)
        mz = RE_ZUX.match(ln.strip())
        if mz:
            zux = mz.group(1)
        mt = RE_TUHAO.match(ln.strip())
        if mt:
            seat, rest = mt.group(1), mt.group(2)
            mdiff = ''
            mr = re.match(r'\\tieside\{([^{}]*)\}\s*(.*)$', rest)
            if mr:
                mdiff, rest = mr.group(1), mr.group(2)
            body = [rest] if rest.strip() else []
            j = i + 1
            while j < len(lines):
                s = lines[j].strip()
                if s.startswith('\\liubai') or RE_TUHAO.match(s) or \
                        RE_ZUX.match(s) or RE_JIE.match(s) or RE_B.match(s):
                    break
                if s:
                    body.append(lines[j])
                j += 1
            # 关联块键：向后找最近 ansblock
            k = j
            key = None
            while k < len(lines):
                mb = RE_B.match(lines[k].strip())
                if mb:
                    key = mb.group(1)
                    break
                if RE_TUHAO.match(lines[k].strip()) or RE_ZUX.match(lines[k].strip()):
                    break
                k += 1
            assert key, 'tuhao %s 未关联到 ansblock（行 %d）' % (seat, i + 1)
            it = led_by_key[key]
            assert it['seat'] == seat, 'seat 漂：%s %s≠%s' % (key, it['seat'], seat)
            qrows.append((key, seat, it.get('form', ''), jie, zux, mdiff, body))
            i = j
            continue
        i += 1
    assert len(qrows) == len(led['items']), \
        '题面块数 %d ≠台账 %d' % (len(qrows), len(led['items']))
    # 键序＝装配序（题面区序≡台账序）
    assert [r[0] for r in qrows] == [it['key'] for it in led['items']], '键序≠装配序'

    # —— 题面侧 md ——
    qkeyset = key_universe('导学件')  # noqa: F841 (dao_k 已有；此处防误用)
    n_dao = sum(1 for r in qrows if r[0] in dao_k)
    n_lian = sum(1 for r in qrows if r[0] in lian_k)
    n_multi = sum(1 for r in qrows if r[2] == '多选')
    L = []
    A = L.append
    A('# M3 第2章 题面库·%s（拓展册·拓区两印制）【题面侧·盲窗层】' % pian_name)
    A('')
    A('> 冻结：%s｜片＝拓展册%s｜manifest＝`manifest/%s.manifest.json`'
      % (now_stamp(), pian, pian_name))
    A('> 源件：`成卷/拓展册/%s/main.tex`（sha256 见 manifest 源件sha256；题面区原文照录，'
      'tex 形保真——\\(\\)/\\\\命令照源，泄漏门 texstrip 同折比对）' % pian)
    A('> 盲窗纪律：本件只有题面与无答案元数据；答案值与详解在「-答案侧」分文件，禁并读入盲解工位。')
    A('> 键式：`2章-拓-课时NN-<槽>`（照 canonical键名总表 §〇.1 拓键制）；'
      '片内键序＝拓展册装配序＝manifest 键序。')
    A('> 同键并存口径（明裁登记，勿误报双挂）：本片 %d 键中 %d 键与导学件课时片同键'
      '（同题两印在案——课时拓区一印、拓展册一印），键值字节各照本片源件；'
      '跨片同键非重复挂账，键务查重以「同键两印」口径放行。'
      % (len(qrows), n_dao))
    A('> 题面体口径：`\\tuhao` 行剥座标/难度标起，至 `\\liubai` 止；`\\zux` 组头不题面体'
      '（组头登于各键头段「组」注）；节名照 `\\jietitle`。')
    A('')
    for key, seat, form, jn, zx, df, body in qrows:
        A('### %s｜%s｜%s｜难度：%s｜组：%s｜源：拓展册%s main.tex 原文照录'
          % (key, form, jn, df or '未标', zx, pian))
        A('\n'.join(body))
        A('')
        A('---')
        A('')
    qp = os.path.join(TMUB, '%s.md' % pian_name)
    open(qp, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')

    # —— 答案侧 md ——
    L = []
    A = L.append
    A('# M3 第2章 答案侧·%s（拓展册·拓区两印制）【答案侧·盲窗层另一半】' % pian_name)
    A('')
    A('> 冻结：%s｜片＝拓展册%s｜manifest＝`manifest/%s.manifest.json`'
      % (now_stamp(), pian, pian_name))
    A('> 锚点契约：每键一行 `%% ans:<键>`（v2 新锚点，值快照/钉值门/对号断言按此扫描）。')
    A('> 值口径：照台账 items[].值 渲染形照录（值快照键型判模门落盘值）；'
      '值tex（器面钉值用）＝拓展册台账 v2 items[].值tex（照 main.tex 逐字），'
      '两形并行在案、各依其门。')
    A('> 详解口径：「亲算＝详解」别名（字段规范修订口径）：本片详解＝件内 ansblock '
      '`\\ansnote{详解}{…}` 全文指针。')
    A('')
    for key, _seat, _form, _jn, _zx, _df, _body in qrows:
        it = led_by_key[key]
        A('%% ans:%s' % key)
        A('值：%s' % it['值'])
        A('详解：→成卷/拓展册/%s/main.tex ansblock[%s] \\ansnote{{详解}}{{…}} 全文'
          % (pian, key))
        A('')
    ap = os.path.join(TMUB, '%s-答案侧.md' % pian_name)
    open(ap, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')

    # —— manifest 冻结（哈希照对号门 parse 口径计算） ——
    qtext_by_key = {}
    for (key, _s, _f, _j, _z, _d, body) in qrows:
        kept = [x for x in body if x.strip() and not x.startswith('【注】')]
        qtext_by_key[key] = '\n'.join(kept)
    # 与对号门 parse_questions/parse_answers 同口径本地复算（防口径漂；权威验证＝
    # 立片后 对号门 --strict 23 片子进程复跑）——不进程内 exec 对号门（其模块级
    # stdout 包装会关闭本脚本输出流）。
    def parse_questions_loc(path):
        out, cur = [], None
        for ln in open(path, encoding='utf-8', newline='').read().splitlines():
            if ln.startswith('### '):
                if cur:
                    out.append(cur)
                head = ln[4:]
                key = head.split('｜')[0].strip()
                kinds = [s for s in head.split('｜')[1:]
                         if s in ('单选', '多选', '填空', '解答')]
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
        return [(k, t, '\n'.join(b)) for k, t, b in out]

    def parse_answers_loc(path):
        out, cur = [], None
        for ln in open(path, encoding='utf-8', newline='').read().splitlines():
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

    qs = parse_questions_loc(qp)
    ans = parse_answers_loc(ap)
    assert [k for k, _, _ in qs] == [r[0] for r in qrows], 'parse_questions 键序漂'
    assert [k for k, _, _ in ans] == [r[0] for r in qrows], 'parse_answers 键序漂'
    for (k, _t, qt) in qs:
        assert qt == qtext_by_key[k], 'parse 口径差：%s' % k
    daov = {k: (v, d) for k, v, d in ans}
    mani = {
        '片': pian_name,
        '章': 'M3选必1第2章',
        '键式': '2章-拓-课时NN-<槽>（拓区两印制；与课时片同键并存＝同题两印在案）',
        '冻时戳': now_stamp(),
        '源件': '成卷/拓展册/%s/main.tex' % pian,
        '源件sha256': sha_bytes(open(main_path, 'rb').read()),
        '题面侧': '%s.md' % pian_name,
        '题面侧sha256': sha_bytes(open(qp, 'rb').read()),
        '答案侧': '%s-答案侧.md' % pian_name,
        '答案侧sha256': sha_bytes(open(ap, 'rb').read()),
        '键序': [r[0] for r in qrows],
        '逐键哈希': {r[0]: {'题面': sha_text(qtext_by_key[r[0]]),
                            '答案': sha_text(daov[r[0]][0] + '\n' + daov[r[0]][1])}
                     for r in qrows},
        '期望值': {
            '键数': len(qrows),
            '导学键数': n_dao,
            '练习键数': n_lian,
            '多选数': 0,
            '多选键': [],
            '对号门期望': '题面侧键集＝答案侧锚点集＝manifest键清单（%d=%d=%d，序一致零缺漏）；'
                        '多选门≤4（本片实多选 %d 道但全含「-拓-」照对号门拓键豁免计 0，合规）；'
                        '题面全文/答案块哈希逐一相符；片冻后不可变，变更→重冻→下游回冲；'
                        '同键并存两印口径勿误报双挂'
                        % (len(qrows), len(qrows), len(qrows), n_multi),
        },
    }
    mp = os.path.join(MANI, '%s.manifest.json' % pian_name)
    json.dump(mani, open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    results[pian_name] = {'键数': len(qrows), '导学同键': n_dao, '练习同键': n_lian,
                          '实多选': n_multi,
                          '题面侧': qp, '答案侧': ap, 'manifest': mp}
    print('%s：键 %d（导学同键 %d｜练习同键 %d｜实多选 %d→豁免计 0）立片毕'
          % (pian_name, len(qrows), n_dao, n_lian, n_multi))

# —— canonical键名总表 另账段追加两行（append-only，零动既录） —— nothing yet
