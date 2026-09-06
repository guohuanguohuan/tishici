# -*- coding: utf-8 -*-
# ⑩轮任务A3：公共规则·目录摘要.md 行号重算。
# 规则：全部L号按A1映射表机械重算（拆段旧行的条目改行号区间，保证覆盖断言无空洞）；
# 条目概括文字不变（仅L19/L20/L21三条按主会话附言一新文刷新）；头部源文件行字节数/行数按实况更新；
# 生成日期行追加⑩轮注记；空行覆盖条目按拆段后实况重算；文末覆盖自检数字重算。
# 例外保留（历史记述不改）：生成日期行既有外移轮L号；「两轮修订…内容行（L1-216）行号零漂移」句。
import pathlib, re, json, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
APPLY = (len(sys.argv) > 1 and sys.argv[1] == 'apply')

mp = json.loads((ROOT / '工作区/体系-漏读治理-0906/⑩_拆段映射.json').read_text(encoding='utf-8'))['mapping']['公共规则.md']
# old->(new_start,new_end)；未拆行 new=n+cum
splits = {int(k): v for k, v in mp.items() if len(v) > 1}
def rng(n):
    if n in splits:
        return splits[n][0], splits[n][-1]
    c = sum(len(v) - 1 for k, v in splits.items() if k < n)
    return n + c, n + c

src = ROOT / '公共规则.md'
sb = src.read_bytes()
stext = sb.decode('utf-8')
slines = stext.split('\r\n')
N = len(slines)                      # split口径（含尾空行）
BYTES = len(sb)
empt = [i for i, L in enumerate(slines, 1) if L == '']
nonempty = N - len(empt)

p = ROOT / '公共规则·目录摘要.md'
raw = p.read_bytes()
assert raw.count(b'\r\n') == raw.count(b'\n'), '摘要非纯CRLF'
t = raw.decode('utf-8')
lines = t.split('\r\n')

REFRESH = {  # 锚名 -> 附言一新概括（主会话拍板文，逐字采用）
    '多智能体模式': '默认生效；主会话五件事；执行一律子代理；子代理＝平台原生（[secondary_model] 绑定）；阅读默认索引精读制',
    '多智能体派发纪律': '索引＋条款ID精读＋纪律短版五句＋⑥通读举证门（无举证视同未读）',
    '主会话上下文与调度纪律': '摘要回传/规格书先行/抽验不重做/互斥切分/代理粒度/⑥阅读制（默认索引精读、涉面宽升级全文通读）/⑦分片轮换',
}

out, stats = [], {'entry': 0, 'refresh': 0, 'range': 0}
for ln in lines:
    m = re.match(r'^- L(\d+)｜(.*)$', ln)
    if m:
        old = int(m.group(1)); rest = m.group(2)
        anchor = rest.split('｜')[1] if rest.count('｜') >= 1 else ''
        if old in (19, 20, 21) and anchor in REFRESH:
            parts = rest.split('｜')
            parts[2] = REFRESH[anchor]          # parts[0]=§归属 parts[1]=锚名 parts[2]=概括
            rest = '｜'.join(parts)
            stats['refresh'] += 1
        a, b = rng(old)
        if a != b:
            out.append(f'- L{a}-{b}｜{rest}')
            stats['range'] += 1
        else:
            out.append(f'- L{a}｜{rest}')
        stats['entry'] += 1
        continue
    if ln.startswith('## ') or ln.startswith('- ') or ln.startswith('用途：') or True:
        # 生成日期行：追加⑩轮注记（既有历史L号不动）
        if ln.startswith('- 生成日期：'):
            ln = ln + '；2026-09-06 ⑩轮漏读治理拆段刷新（15超长行拆段重排行号、L19/L20/L21概括按拍板刷新、源文件行按实况更新）'
        else:
            # 历史零漂移句排除
            if '行号零漂移' in ln:
                pass  # 历史记述，L号保持原样
            else:
                def sub(mo):
                    a = int(mo.group(1)); b = int(mo.group(2) or mo.group(1))
                    a2, b2 = rng(a)[0], rng(b)[1]
                    return f'L{a2}' if a2 == b2 else f'L{a2}-{b2}'
                ln = re.sub(r'L(\d+)(?:-(\d+))?', sub, ln)
        # N值口径行
        ln = ln.replace('1..218 无空洞', f'1..{N} 无空洞')
    out.append(ln)

t2 = '\r\n'.join(out)

# 空行覆盖条目重算
def rebuild_blank(mo):
    body = mo.group(0)
    lst = '·'.join(str(x) for x in empt)
    body = re.sub(r'L[\d·]+｜', f'L{lst}｜', body, count=1)
    body = re.sub(r'（\d+行，含文件尾空行L\d+，', f'（{len(empt)}行，含文件尾空行L{empt[-1]}，', body, count=1)
    return body
t2 = re.sub(r'- L2·[\d·]+｜全文各处｜空行｜[^\r\n]*', rebuild_blank, t2, count=1)

# 头部源文件行
t2 = re.sub(r'（[\d,]+ 字节，CRLF；\d+ 行〔编辑器/split 口径，末行 L\d+ 为文件尾空行；wc -l 口径 \d+〕，单行极长）',
            f'（{BYTES:,} 字节，CRLF；{N} 行〔编辑器/split 口径，末行 L{N} 为文件尾空行；wc -l 口径 {N-1}〕，超长行已于⑩轮拆段）', t2, count=1)

# 文末覆盖自检数字
t2 = t2.replace('条目行号并集＝L1..L218，无空洞。✅ 通过（2026-09-05 对照现行源文逐行重核，脚本实算）',
                f'条目行号并集＝L1..L{N}，无空洞。✅ 通过（2026-09-05 对照现行源文逐行重核，脚本实算；2026-09-06 ⑩轮拆段后脚本重算通过）')
t2 = t2.replace('内容条款条目覆盖全部 181 个非空行', f'内容条款条目覆盖全部 {nonempty} 个非空行')
t2 = re.sub(r'（L2·[\d·]+）；(\d+)＋(\d+)＝(\d+)＝源文总行数',
            lambda mo: f'（L{"·".join(map(str,empt))}）；{nonempty}＋{len(empt)}＝{N}＝源文总行数', t2, count=1)
t2 = t2.replace('wc -l 计 217（换行符数），split/编辑器视图计 218（末行 L218 为文件尾空行）；本索引采用 218 口径',
                f'wc -l 计 {N-1}（换行符数），split/编辑器视图计 {N}（末行 L{N} 为文件尾空行）；本索引采用 {N} 口径')

# 覆盖断言：条目行号并集＝1..N 无空洞
cov = set()
for ln in t2.split('\r\n'):
    m = re.match(r'^- L[\d]', ln)
    if not m:
        continue
    if '｜全文各处｜空行｜' in ln:
        seg = ln[2:ln.index('｜全文各处')]
        cov.update(int(x) for x in re.findall(r'\d+', seg))
        continue
    for mm in re.finditer(r'L(\d+)(?:-(\d+))?', ln):
        a = int(mm.group(1)); b = int(mm.group(2) or mm.group(1))
        cov.update(range(a, b + 1))
holes = sorted(set(range(1, N + 1)) - cov)
overs = sorted(x for x in cov if x > N)
assert not holes and not overs, f'覆盖断言失败 holes={holes[:10]} overs={overs[:10]}'
print('覆盖断言通过: 1..%d 无空洞, 条目%d(区间%d/刷新%d)' % (N, stats['entry'], stats['range'], stats['refresh']))
print('源文: %d字节 %d行(空行%d) 尾空行L%d' % (BYTES, N, len(empt), empt[-1]))

if APPLY:
    p.write_bytes(t2.encode('utf-8'))
    print('APPLIED')
else:
    print('DRYRUN')
