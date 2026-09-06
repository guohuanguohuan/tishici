# -*- coding: utf-8 -*-
"""规则lint.py——全库规则件巡检工具（附则/规则巡检.md XJ-1a~1e 检查面逐字实现；⑩轮漏读治理任务B）。

巡检对象（XJ-1 清单原文口径）：公共规则.md／附则/*.md／*总控.md／00总纲.md／公共规则·目录摘要.md。

检查面：
- XJ-1a 超长行：>1000 字符警告、>2000 字符报错（恰等于阈值不触发；长度按 python len() 字符数、
  不含行尾 EOL；超 2000 者读文件工具按行截断读不全，本工具以脚本全量读并照常报告）；
- XJ-1b 引用断链：规则文内引用的文件路径（*.md／*.py，含「*总控.md」「附则/*.md」通配形态）
  与条款锚（ZH-n/K1/CB-n/XJ-n 等）目标存在性；解析序＝盘符绝对式→根／引用件同目录→未命中按
  尾段文件名全库寻获（剪 .git/logs/__pycache__，容错斜杠枚举式「A/名.md/名」、裸名引用与深层
  线上件）；通用豁免＝「▽」起首分句/行内的文件引用不做断链判定（留痕句提及已删/退役文件属
  合法存档引用）；《件名》式书名引用与 §n/Ln 节号行号引用不在检出面（L-n 驻《公共规则·目录摘要.md》
  且行号随拆段漂移，纳入时机待裁决）；
- XJ-1c 留痕缺标：含留痕关键词（留痕/废止/作废/不再适用/历史保留/转历史/出脑/退役）而无
  「▽」前缀的分句清单（分句界＝。；！？，、；A2 实测落点「▽」居「（」「，」之后，故分句内
  「▽」起之后视为已标、只查 ▽ 前的未标文头——与规格书 A2「幂等防护与 XJ-1c 判定对齐」同口径）；
- XJ-1d 占位符：「待回填」「TODO」类（白名单豁免制，白名单驻本文件头部常量 WHITELIST）；
- XJ-1e 日期异常：未来日期（警告）、非法格式（月日历法不成立／分隔符混排，报错）；
  未补零（2026-9-6）与「年月日」混排横杠式不在检出面（2026年9月6日 全角式合法）。

级别赋值：XJ-1a 两级为巡检附则原文；XJ-1b 文件断链＝报错、通配无命中与锚断链＝警告；
XJ-1c/1d＝警告；XJ-1e 未来＝警告、非法＝报错。锚断链从警告系因「已废止机制的叙事性提及」
（如 K3 升级通道）非真断链，留人工裁决。

锚存在性判定：锚在某规则件中「行首式（剥除 markdown 结构符后居行首）」或「后随 ｜:：」出现
即计为定义；扩展字母式（ZH-6c）按基锚（ZH-6）存在即认存在。

用法：
  python 工具/规则lint.py                      # 巡检库根（本文件上一级），报告打印 stdout
  python 工具/规则lint.py --out <报告.md>      # 报告另存（UTF-8／CRLF）
  python 工具/规则lint.py --root <目录>        # 指定巡检根（合成样例自测用）
  python 工具/规则lint.py --selftest [--keep-samples]  # 临时目录合成样例走查，验五面检出率
退出码：0＝无报错级命中；1＝有报错级命中；2＝运行异常。
"""
import calendar
import datetime
import fnmatch
import os
import re
import shutil
import sys
import tempfile
from collections import Counter, namedtuple
from functools import lru_cache
from pathlib import Path

# ===== XJ-1a 阈值（巡检附则原文：>1000 警告、>2000 报错） =====
LEN_WARN = 1000
LEN_ERROR = 2000

# ===== XJ-1c 留痕词集（⑩规格书 A2 判定词集；「覆盖」不在词集） =====
TRACE_KEYWORDS = ("留痕", "废止", "作废", "不再适用", "历史保留", "转历史", "出脑", "退役")

# ===== XJ-1d 占位词集（「待回填」「TODO」类） =====
PLACEHOLDER_PATTERNS = ("待回填", "TODO", "FIXME", "TBD", "待补", "待定")

# ===== 白名单（XJ-1d「白名单豁免制，白名单驻工具内」；XJ-1c/XJ-1b 同机制） =====
# 条目＝(文件通配, 内容片段, 作用域)。一律「文件＋内容片段」定位、禁用行号（⑩拆段漂移期）。
# 作用域：line＝该行本检查面全部命中豁免／clause＝仅含片段之分句豁免（限 XJ-1c，防同行连坐）／
#         ref＝仅被引用名含片段之断链豁免（限 XJ-1b 文件引用）。ref 作用域系模式匹配实现——
#         命名模式类按被引用名片段豁免，「单位名·」「册别·」系占位模式片段，覆盖现行四项与未来同型。
# 初值＝⑩规格书任务B：公共规则·目录摘要.md 与 附则/规则巡检.md 的词集枚举行（XJ-1c，常驻豁免；
#       目录摘要现行无枚举行，条目休眠——日后出现即自动豁免）。
# 2026-09-06 主会话裁决回填（⑩终报B§六.2 四组全采纳＋新增四行）：
#       XJ-1b/ref＝规则巡检「附则/xxx.md」定义示例行＋命名模式类；
#       XJ-1c＝公共规则「旧词族grep」定性条款行（行级）、讲练件底纹减法「减法清单（讲练件四类废止）」
#       标题行（行级）、00总纲「公共资产与退役文件」标题行（行级）、「旧打印本作废」句与
#       「产出文件夹副本废止」分句（分句级）；XJ-1d＝规则巡检「「待回填」「TODO」」词集定义行。
# K3 锚不豁免（主会话裁决：靠 A2 ▽标记豁免覆盖，复测仍命中再议）；真断链 3 项不入白名单（保持报错级）。
WHITELIST = {
    "XJ-1b": [
        ("附则/规则巡检.md", "附则/xxx.md", "ref"),
        ("00总纲.md", "两科各自的章节总台账.md", "ref"),
        ("公共规则.md", "单位名·", "ref"),
        ("公共规则.md", "册别·", "ref"),
        ("公共规则.md", "排版自检记录.md", "ref"),
    ],
    "XJ-1c": [
        ("公共规则·目录摘要.md", "留痕/废止/作废", "line"),
        ("附则/规则巡检.md", "留痕/废止/作废", "line"),
        ("公共规则.md", "旧词族grep", "line"),
        ("附则/讲练件底纹减法.md", "减法清单（讲练件四类废止）", "line"),
        ("00总纲.md", "公共资产与退役文件", "line"),
        ("公共规则.md", "旧打印本作废", "clause"),
        ("公共规则.md", "产出文件夹副本废止", "clause"),
    ],
    "XJ-1d": [
        ("附则/规则巡检.md", "「待回填」「TODO」", "line"),
    ],
}

# ===== XJ-1b 引用形态 =====
# 文件路径引用（*.md／*.py；支持盘符绝对路径与 /、\ 两种分隔；全角括号不入名类防吞散文；
# 前置 * 通配排除、由通配式另行接管）
FILE_REF_RE = re.compile(
    r"(?<![\w·/\\.\-*])"
    r"((?:[A-Za-z]:)?(?:[/\\]?[\w\u4e00-\u9fff·\-]+[/\\])*"
    r"[\w\u4e00-\u9fff·\-]+\.(?:md|py))"
    r"(?![\w.\-])"
)
# 通配引用（末段含 * 的路径式，兼容「*总控.md」「附则/*.md」「工具/六类*.py」三形态）
WILDCARD_REF_RE = re.compile(
    r"(?<![\w*])"
    r"((?:[\w\u4e00-\u9fff·\-]+[/\\])*"
    r"[\w\u4e00-\u9fff·\-]*\*[\w\u4e00-\u9fff·\-]*\.(?:md|py))"
    r"(?![\w*])"
)
# 条款锚：ZH-n／CB-n／XJ-n（可带字母后缀如 ZH-6c）与 K-n 式
HYPHEN_ANCHOR_RE = re.compile(r"(?<![A-Za-z])(ZH|CB|XJ)-(\d+)([A-Za-z]*)(?![0-9A-Za-z])")
K_ANCHOR_RE = re.compile(r"(?<![A-Za-z0-9])(K)(\d+)(?![0-9A-Za-z])")
# 锚定义判定：行首式前置可剥除的 markdown 结构符；或锚后紧随 ｜:：
ANCHOR_LEAD_CHARS = " \t#>*·|－—-「『【"
ANCHOR_DEF_FOLLOW = "｜:："

# ===== XJ-1e 日期形态：2026-09-06／2026.09.06／2026/09/06 与 2026年9月6日 =====
DATE_RE = re.compile(
    r"(?<!\d)(?:(?P<y>\d{4})(?P<s1>[-/.])(?P<m>\d{1,2})(?P<s2>[-/.])(?P<d>\d{1,2})"
    r"|(?P<y2>\d{4})年(?P<m2>\d{1,2})月(?P<d2>\d{1,2})日?)(?!\d)"
)

# ===== XJ-1c 分句界（。；！？，、——与 A2 留痕标注的分句粒度对齐） =====
SENT_DELIM_CHARS = "。；！？，、"
SENT_SPLIT_RE = re.compile("(?<=[" + re.escape(SENT_DELIM_CHARS) + "])")

Hit = namedtuple("Hit", "check level file line msg")

LEVEL_ERROR = "报错"
LEVEL_WARN = "警告"


def discover_rule_files(root: Path) -> list:
    """XJ-1 巡检对象：公共规则.md／附则/*.md／*总控.md／00总纲.md／公共规则·目录摘要.md。"""
    files = []
    for name in ("公共规则.md", "00总纲.md", "公共规则·目录摘要.md"):
        p = root / name
        if p.is_file():
            files.append(p)
    if (root / "附则").is_dir():
        files.extend(sorted((root / "附则").glob("*.md")))
    files.extend(sorted(root.glob("*总控.md")))
    seen, out = set(), []
    for p in files:
        key = p.resolve()
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out


def read_lines(path: Path) -> list:
    """全量读入并按行拆分；剥行尾 \\r（CRLF/LF 兼容），字符数口径不含 EOL。"""
    return [ln.rstrip("\r") for ln in path.read_text(encoding="utf-8").split("\n")]


def _wl_fragments(check: str, rel_posix: str, scope: str) -> list:
    """取该检查面下指定作用域、且文件通配匹配的全部白名单片段。"""
    out = []
    for file_pat, fragment, sc in WHITELIST.get(check, ()):
        if sc == scope and (
            fnmatch.fnmatch(rel_posix, file_pat) or fnmatch.fnmatch(Path(rel_posix).name, file_pat)
        ):
            out.append(fragment)
    return out


def _first_fragment(fragments: list, text: str):
    """返回首个命中片段（供豁免记录溯源），未命中返回 None。"""
    for frag in fragments:
        if frag in text:
            return frag
    return None


def whitelisted_line(check: str, rel_posix: str, line: str):
    return _first_fragment(_wl_fragments(check, rel_posix, "line"), line)


def whitelisted_clause(check: str, rel_posix: str, clause: str):
    return _first_fragment(_wl_fragments(check, rel_posix, "clause"), clause)


def whitelisted_ref(check: str, rel_posix: str, ref: str):
    return _first_fragment(_wl_fragments(check, rel_posix, "ref"), ref)


def _at_line_start(line: str, idx: int) -> bool:
    stripped = line.lstrip(ANCHOR_LEAD_CHARS)
    return idx == len(line) - len(stripped)


# 尾段按名寻获时剪除的瞬态/非库目录
_TRANSIENT_PARTS = {".git", "logs", "__pycache__"}


@lru_cache(maxsize=None)
def _find_by_basename(root_str: str, name: str) -> tuple:
    """全库按文件名寻获（os.walk 剪枝瞬态目录；结果按名缓存，一名一次走树）。"""
    out = []
    for dirpath, dirnames, filenames in os.walk(root_str):
        dirnames[:] = [d for d in dirnames if d not in _TRANSIENT_PARTS]
        if name in filenames:
            out.append(Path(dirpath) / name)
    return tuple(out)


def collect_defined_anchors(files_lines: dict) -> set:
    defined = set()
    for lines in files_lines.values():
        for line in lines:
            for m in HYPHEN_ANCHOR_RE.finditer(line):
                if _at_line_start(line, m.start(1)) or (m.end() < len(line) and line[m.end()] in ANCHOR_DEF_FOLLOW):
                    defined.add(f"{m.group(1)}-{m.group(2)}")
            for m in K_ANCHOR_RE.finditer(line):
                end = m.end()
                if _at_line_start(line, m.start(1)) or (end < len(line) and line[end] in ANCHOR_DEF_FOLLOW):
                    defined.add(f"K{m.group(2)}")
    return defined


def check_line_length(rel: str, lines: list) -> list:
    hits = []
    for i, line in enumerate(lines, 1):
        n = len(line)
        if n > LEN_ERROR:
            hits.append(Hit("XJ-1a", LEVEL_ERROR, rel, i,
                            f"行长 {n} 字符（>{LEN_ERROR} 报错——读文件工具按行截断 2000，须脚本全量读）｜行首：{line[:40]}…"))
        elif n > LEN_WARN:
            hits.append(Hit("XJ-1a", LEVEL_WARN, rel, i,
                            f"行长 {n} 字符（>{LEN_WARN} 警告）｜行首：{line[:40]}…"))
    return hits


def _ref_candidates(root: Path, path: Path, ref: str) -> list:
    """引用目标候选：盘符绝对式直取；相对式按 根／引用件同目录 解析；
    未命中再按尾段文件名全库寻获（剪除瞬态目录）——容错斜杠枚举式「A/名.md/名」、
    裸名引用与深层线上件（如各线目录下的台账/沿革件）。"""
    if re.match(r"^[A-Za-z]:", ref):
        return [Path(ref)]
    cands = [root / ref, path.parent / ref]
    last = re.split(r"[/\\]", ref)[-1]
    if last:
        cands.extend(_find_by_basename(str(root), last))
    return list(dict.fromkeys(cands))


def _in_marked_span(line: str, pos: int) -> bool:
    """引用是否位于「▽」起首之分句/行内（XJ-1b 通用豁免：留痕句提及已删/退役文件＝合法存档引用）。
    判定＝引用位置之前最近的「▽」与引用之间无分句界符（有界符则分属两分句、后句非▽起首）。"""
    q = line.rfind("▽", 0, pos)
    if q < 0:
        return False
    return not (set(line[q:pos]) & set(SENT_DELIM_CHARS))


def check_references(root: Path, rel: str, path: Path, lines: list, defined: set, exemptions: list) -> list:
    hits = []
    for i, line in enumerate(lines, 1):
        for m in FILE_REF_RE.finditer(line):
            ref = m.group(1)
            cands = _ref_candidates(root, path, ref)
            if any(c.exists() for c in cands):
                continue
            if _in_marked_span(line, m.start(1)):
                exemptions.append(("XJ-1b", rel, i, f"留痕句豁免（▽起首分句）→ {ref}"))
                continue
            rfrag = whitelisted_ref("XJ-1b", rel, ref)
            if rfrag:
                exemptions.append(("XJ-1b", rel, i, f"引用名豁免「{rfrag}」→ {ref}"))
                continue
            hits.append(Hit("XJ-1b", LEVEL_ERROR, rel, i,
                            f"文件引用断链：{ref}（{'、'.join(str(c) for c in cands)} 均不存在）"))
        for m in WILDCARD_REF_RE.finditer(line):
            pat = m.group(1).replace("\\", "/")
            if list(root.glob(pat)) or list(path.parent.glob(pat)):
                continue
            if _in_marked_span(line, m.start(1)):
                exemptions.append(("XJ-1b", rel, i, f"留痕句豁免（▽起首分句）→ {pat}"))
                continue
            hits.append(Hit("XJ-1b", LEVEL_WARN, rel, i, f"通配引用无命中：{pat}"))
        for m in HYPHEN_ANCHOR_RE.finditer(line):
            token = m.group(0)
            base = f"{m.group(1)}-{m.group(2)}"
            if base not in defined:
                note = f"（基锚 {base}）" if token != base else ""
                hits.append(Hit("XJ-1b", LEVEL_WARN, rel, i, f"条款锚断链：{token}{note}——全库规则件未见定义"))
        for m in K_ANCHOR_RE.finditer(line):
            token = f"K{m.group(2)}"
            if token not in defined:
                hits.append(Hit("XJ-1b", LEVEL_WARN, rel, i, f"条款锚断链：{token}——全库规则件未见定义"))
    return hits


def check_traceless(rel: str, lines: list, exemptions: list) -> list:
    hits = []
    for i, line in enumerate(lines, 1):
        if not any(k in line for k in TRACE_KEYWORDS):
            continue
        lfrag = whitelisted_line("XJ-1c", rel, line)
        if lfrag:
            exemptions.append(("XJ-1c", rel, i, f"行级豁免「{lfrag}」｜{line.strip()[:48]}"))
            continue
        for unit in SENT_SPLIT_RE.split(line):
            head, marked, _tail = unit.partition("▽")
            # 「▽」起之后视为 A2 已标（观测落点居「（」「，」之后），只查 ▽ 前的未标文头
            seg = head if marked else unit
            kws = [k for k in TRACE_KEYWORDS if k in seg]
            if not kws:
                continue
            cfrag = whitelisted_clause("XJ-1c", rel, unit)
            if cfrag:
                exemptions.append(("XJ-1c", rel, i, f"分句级豁免「{cfrag}」｜{unit.strip()[:48]}"))
                continue
            excerpt = seg.strip()[:80] + ("…" if len(seg.strip()) > 80 else "")
            hits.append(Hit("XJ-1c", LEVEL_WARN, rel, i, f"留痕词句未标▽：词={'/'.join(kws)}｜句：{excerpt}"))
    return hits


def check_placeholders(rel: str, lines: list, exemptions: list) -> list:
    hits = []
    for i, line in enumerate(lines, 1):
        found = [p for p in PLACEHOLDER_PATTERNS if p in line]
        if not found:
            continue
        lfrag = whitelisted_line("XJ-1d", rel, line)
        if lfrag:
            exemptions.append(("XJ-1d", rel, i, f"行级豁免「{lfrag}」｜{line.strip()[:48]}"))
            continue
        hits.append(Hit("XJ-1d", LEVEL_WARN, rel, i,
                        f"占位符「{'」「'.join(found)}」｜摘录：{line.strip()[:60]}"))
    return hits


def check_dates(rel: str, lines: list, today: datetime.date) -> list:
    hits = []
    for i, line in enumerate(lines, 1):
        for m in DATE_RE.finditer(line):
            if m.group("y"):
                y, mo, d = int(m.group("y")), int(m.group("m")), int(m.group("d"))
                s1, s2 = m.group("s1"), m.group("s2")
                if s1 != s2:
                    hits.append(Hit("XJ-1e", LEVEL_ERROR, rel, i, f"非法日期（分隔符混排 {s1}{s2}）：{m.group(0)}"))
                    continue
            else:
                y, mo, d = int(m.group("y2")), int(m.group("m2")), int(m.group("d2"))
            if not 1 <= mo <= 12:
                hits.append(Hit("XJ-1e", LEVEL_ERROR, rel, i, f"非法日期（月 {mo} 不在 1-12）：{m.group(0)}"))
                continue
            if not 1 <= d <= calendar.monthrange(y, mo)[1]:
                hits.append(Hit("XJ-1e", LEVEL_ERROR, rel, i, f"非法日期（{y}-{mo:02d} 月无 {d} 日）：{m.group(0)}"))
                continue
            dt = datetime.date(y, mo, d)
            if dt > today:
                hits.append(Hit("XJ-1e", LEVEL_WARN, rel, i, f"未来日期：{m.group(0)}（晚于运行日 {today.isoformat()}）"))
    return hits


def run_lint(root: Path):
    files = discover_rule_files(root)
    files_lines = {p: read_lines(p) for p in files}
    rel_of = {p: (p.relative_to(root).as_posix() if root in p.parents or p.parent == root else str(p)) for p in files}
    defined = collect_defined_anchors(files_lines)
    hits, exemptions = [], []
    for p in files:
        rel = rel_of[p]
        lines = files_lines[p]
        hits.extend(check_line_length(rel, lines))
        hits.extend(check_references(root, rel, p, lines, defined, exemptions))
        hits.extend(check_traceless(rel, lines, exemptions))
        hits.extend(check_placeholders(rel, lines, exemptions))
        hits.extend(check_dates(rel, lines, datetime.date.today()))
    hits.sort(key=lambda h: (h.check, h.file, h.line, h.msg))
    return hits, exemptions, files_lines


def render_report(root: Path, hits: list, exemptions: list, files_lines: dict) -> str:
    today = datetime.date.today().isoformat()
    L = []
    L.append("# 规则lint 报告（XJ-1a~1e）")
    L.append("")
    L.append(f"- 运行：{datetime.datetime.now().isoformat(timespec='seconds')}｜运行日基准：{today}"
             f"｜巡检根：{root}")
    L.append(f"- 工具：工具/规则lint.py（附则/规则巡检.md XJ-1a~1e 逐字实现；白名单驻工具头部常量）")
    L.append(f"- 扫描件数：{len(files_lines)}")
    L.append("")
    L.append("## 扫描清单")
    L.append("")
    L.append("| 文件 | 行数 |")
    L.append("|---|---|")
    for p, lines in files_lines.items():
        rel = p.name if p.parent == root else p.parent.name + "/" + p.name
        L.append(f"| {rel} | {len(lines)} |")
    L.append("")
    L.append("## 命中汇总")
    L.append("")
    L.append("| 检查面 | 报错级 | 警告级 |")
    L.append("|---|---|---|")
    for chk in ("XJ-1a", "XJ-1b", "XJ-1c", "XJ-1d", "XJ-1e"):
        e = sum(1 for h in hits if h.check == chk and h.level == LEVEL_ERROR)
        w = sum(1 for h in hits if h.check == chk and h.level == LEVEL_WARN)
        L.append(f"| {chk} | {e} | {w} |")
    L.append("")
    titles = {
        "XJ-1a": "XJ-1a 超长行（>1000 警告／>2000 报错）",
        "XJ-1b": "XJ-1b 引用断链（文件路径＋条款锚）",
        "XJ-1c": "XJ-1c 留痕缺标（含词集而无▽句首前缀）",
        "XJ-1d": "XJ-1d 占位符（待回填/TODO 类）",
        "XJ-1e": "XJ-1e 日期异常（未来／非法格式）",
    }
    for chk in ("XJ-1a", "XJ-1b", "XJ-1c", "XJ-1d", "XJ-1e"):
        L.append(f"## {titles[chk]}")
        L.append("")
        sub = [h for h in hits if h.check == chk]
        if not sub:
            L.append("无命中。")
        for h in sub:
            L.append(f"- [{h.level}] {h.file}:L{h.line}｜{h.msg}")
        L.append("")
    L.append("## 白名单豁免记录（本次实际豁免）")
    L.append("")
    if not exemptions:
        L.append("本次无豁免命中。")
    for chk, rel, ln, excerpt in exemptions:
        L.append(f"- {chk}｜{rel}:L{ln}｜{excerpt}")
    L.append("")
    L.append("## 口径附注")
    L.append("")
    L.append("- 级别赋值：XJ-1a 两级为巡检附则原文；XJ-1b 文件断链=报错、通配无命中/锚断链=警告；"
             "XJ-1c/1d=警告；XJ-1e 未来=警告、非法=报错。")
    L.append("- XJ-1b 检出面：*.md／*.py 路径式引用＋通配式＋ZH/K/CB/XJ 条款锚；《件名》书名式、"
             "§n 节号、L-n 行号引用不在检出面（L-n 纳入与否待裁决）。解析序＝盘符绝对式→"
             "根／引用件同目录→尾段文件名全库寻获（剪 .git/logs/__pycache__）。通用豁免＝"
             "「▽」起首分句/行内的文件引用不做断链判定（留痕句提及已删/退役文件＝合法存档引用）。")
    L.append("- XJ-1c 分句界＝。；！？，、；分句内「▽」起之后视为已标（A2 观测落点居「（」「，」后），"
             "只查 ▽ 前未标文头。命中属清单性质（供留痕标注轮逐句裁决语义），命中≠必标：语义非"
             "「该物已停用/被取代、仅存档备查」者不标。")
    L.append("- 白名单：一律「文件＋内容片段」定位、禁用行号（拆段漂移期）；作用域 line＝整行该面豁免／"
             "clause＝仅含片段分句豁免（限 XJ-1c）／ref＝被引用名含片段豁免（限 XJ-1b 文件引用；"
             "命名模式类系模式匹配，「单位名·」「册别·」占位片段覆盖同型）。K3 锚与真断链 3 项不豁免"
             "（2026-09-06 主会话裁决）。")
    L.append("- 退出码：" + ("1（有报错级命中）" if any(h.level == LEVEL_ERROR for h in hits) else "0（无报错级命中）"))
    return "\r\n".join(L)


# ================= 合成样例自测（--selftest；临时目录，不在生产规则件上练手） =================

SELFTEST_SAMPLES = {
    # 文件名刻意取 XJ-1 巡检对象形态（00总纲/*总控/公共规则/目录摘要/附则），顺带验证发现制
    "00总纲.md": [
        "超长行样例。",
        "A" * 1000,   # ≤1000：无命中
        "B" * 1001,   # 警告
        "C" * 2000,   # 警告（不 >2000）
        "D" * 2001,   # 报错
        "▽留痕：已退役并删除：旧提示词.md（全文存于 git 历史）。",
    ],
    "公共规则.md": [
        "现存路径引用：详见 附则/存在件.md 与 样例总控.md。",
        "断链路径引用：详见 附则/不存在件.md。",
        "通配无命中：全脚本见 工具/无此通配*.py。",
        "通配有命中：总控枚举见 *总控.md。",
        "锚存在：按 ZH-1 与 ZH-6c 与 K1 执行。",
        "锚断链：按 ZH-99 与 K9 执行。",
        "外部配置不扫：config.toml 与 settings.json 不入 .md/.py 扫描面。",
        "斜杠枚举容错：写权驻 公共规则/附则/样例引用目标总控.md/进度看板等件。",
        "括号不吞：样例总控（样例引用目标总控.md）。",
        "命名模式豁免对照：台账见 单位名·删除台账.md。",
        "▽留痕：旧件退役。现行件见 附则/存在件.md 与 附则/不存在件.md。",
    ],
    "样例总控.md": [
        "## ZH-1 样例锚",
        "## ZH-6 梯队样例锚",
        "## K1调用块",
        "## XJ-1 检查面样例锚",
    ],
    "公共规则·目录摘要.md": [
        "词集枚举行：留痕/废止/作废/不再适用/历史保留/转历史/出脑/退役。",
    ],
    "附则/留痕样例.md": [
        "旧方案已废止，改用新案。",
        "▽留痕：旧全式已退役，仅存档备查。",
        "首句正常。第二句含历史保留语义词集。",
        "▽留痕：首句出脑已标。第二句转历史未标。",
        "词集裸行不在豁免名单：关键词（留痕/废止/作废/不再适用/历史保留/转历史/出脑/退役）。",
        "- ▽留痕：列表项留痕已标。",
        "现行句保留（▽留痕：括注内旧机制废止）；",
        "钉档，▽留痕：旧钉档之议作废）尾注。",
        "旧制废止（▽留痕：详情存档）。",
    ],
    "附则/占位日期样例.md": [
        "此处待回填。",
        "TODO：冒烟。",
        "干净行无占位。",
        "非法月：2026-13-01。",
        "非法日：2026-02-30。",
        "未来：2099-01-01。",
        "分隔符混排：2026-09/06。",
        "合法：2026-09-06 与 2026年9月6日 与 2026.09.06。",
    ],
    "样例引用目标总控.md": ["样例总控空件。"],
    "附则/存在件.md": ["存在件。"],
    "附则/规则巡检.md": [
        "词集枚举行：留痕/废止/作废/不再适用/历史保留/转历史/出脑/退役。",
        "定义自身：占位词集「待回填」「TODO」（已裁决回填白名单——豁免验证）。",
        "检出面示例：附则/xxx.md。",
    ],
}

# 预期命中清单：(检查面, 文件, 行号, 级别)——与实际命中做多对多集合等值断言
SELFTEST_EXPECT = [
    ("XJ-1a", "00总纲.md", 3, LEVEL_WARN),
    ("XJ-1a", "00总纲.md", 4, LEVEL_WARN),
    ("XJ-1a", "00总纲.md", 5, LEVEL_ERROR),
    ("XJ-1b", "公共规则.md", 2, LEVEL_ERROR),
    ("XJ-1b", "公共规则.md", 3, LEVEL_WARN),
    ("XJ-1b", "公共规则.md", 6, LEVEL_WARN),
    ("XJ-1b", "公共规则.md", 6, LEVEL_WARN),
    ("XJ-1b", "公共规则.md", 11, LEVEL_ERROR),
    ("XJ-1c", "附则/留痕样例.md", 1, LEVEL_WARN),
    ("XJ-1c", "附则/留痕样例.md", 3, LEVEL_WARN),
    ("XJ-1c", "附则/留痕样例.md", 4, LEVEL_WARN),
    ("XJ-1c", "附则/留痕样例.md", 5, LEVEL_WARN),
    ("XJ-1c", "附则/留痕样例.md", 9, LEVEL_WARN),
    ("XJ-1d", "附则/占位日期样例.md", 1, LEVEL_WARN),
    ("XJ-1d", "附则/占位日期样例.md", 2, LEVEL_WARN),
    ("XJ-1e", "附则/占位日期样例.md", 4, LEVEL_ERROR),
    ("XJ-1e", "附则/占位日期样例.md", 5, LEVEL_ERROR),
    ("XJ-1e", "附则/占位日期样例.md", 6, LEVEL_WARN),
    ("XJ-1e", "附则/占位日期样例.md", 7, LEVEL_ERROR),
]


def selftest(keep: bool) -> int:
    tmp = Path(tempfile.mkdtemp(prefix="规则lint_自测_"))
    for rel, lines in SELFTEST_SAMPLES.items():
        p = tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")
    hits, exemptions, _ = run_lint(tmp)
    got = Counter((h.check, h.file, h.line, h.level) for h in hits)
    exp = Counter(SELFTEST_EXPECT)
    ok = True
    print("== 合成样例走查（临时目录：%s）==" % tmp)
    print("类型｜样例位置｜预期｜实测｜判定")
    for key in sorted(set(exp) | set(got), key=lambda k: (k[0], k[1], k[2])):
        e, g = exp.get(key, 0), got.get(key, 0)
        verdict = "PASS" if e == g else "FAIL"
        if e != g:
            ok = False
        print(f"{key[0]}｜{key[1]}:L{key[2]}｜{key[3]}×{e}｜×{g}｜{verdict}")
    # 白名单豁免断言：回填条目逐条验证（词集枚举行×2＋规则巡检占位定义行＋检出面示例 ref＋命名模式 ref）
    exp_exempt = {
        ("XJ-1c", "公共规则·目录摘要.md", 1),
        ("XJ-1c", "附则/规则巡检.md", 1),
        ("XJ-1d", "附则/规则巡检.md", 2),
        ("XJ-1b", "附则/规则巡检.md", 3),
        ("XJ-1b", "公共规则.md", 10),
        ("XJ-1b", "00总纲.md", 6),
    }
    got_exempt = {(chk, rel, ln) for chk, rel, ln, _ in exemptions}
    wb_ok = got_exempt == exp_exempt
    print(f"白名单豁免记录｜预期 {sorted(exp_exempt, key=lambda k: (k[1], k[2]))}｜实测 {sorted(got_exempt, key=lambda k: (k[1], k[2]))}｜{'PASS' if wb_ok else 'FAIL'}")
    if not wb_ok:
        ok = False
    n_error = sum(1 for h in hits if h.level == LEVEL_ERROR)
    print(f"走查结论：{'PASS（五类违规每类至少 1 检出、预期外命中为零）' if ok else 'FAIL'}；"
          f"总命中 {len(hits)}（报错级 {n_error}）；退出码 0")
    if keep:
        print(f"样例保留（--keep-samples）：{tmp}")
    else:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0 if ok else 1


def main(argv: list) -> int:
    args = argv[1:]
    keep = "--keep-samples" in args
    if "--selftest" in args:
        try:
            return selftest(keep)
        except Exception as exc:  # 运行异常与断言失败分码
            print(f"[FAIL] 自测异常：{exc!r}")
            return 2
    root = None
    out = None
    i = 0
    while i < len(args):
        if args[i] == "--root" and i + 1 < len(args):
            root = Path(args[i + 1])
            i += 2
        elif args[i] == "--out" and i + 1 < len(args):
            out = Path(args[i + 1])
            i += 2
        else:
            print(f"未知参数：{args[i]}")
            return 2
    if root is None:
        root = Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"[FAIL] 巡检根不存在：{root}")
        return 2
    try:
        hits, exemptions, files_lines = run_lint(root)
    except Exception as exc:
        print(f"[FAIL] 巡检异常：{exc!r}")
        return 2
    report = render_report(root, hits, exemptions, files_lines)
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        for attempt in range(3):  # 同步盘瞬时锁重试
            try:
                out.write_text(report, encoding="utf-8", newline="")
                break
            except OSError:
                if attempt == 2:
                    raise
        n_err = sum(1 for h in hits if h.level == LEVEL_ERROR)
        n_warn = sum(1 for h in hits if h.level == LEVEL_WARN)
        print(f"[规则lint] 报告已落盘：{out}")
        print(f"[规则lint] 扫描 {len(files_lines)} 件｜命中 {len(hits)}＝报错级 {n_err}＋警告级 {n_warn}"
              f"｜白名单豁免 {len(exemptions)}")
        print(f"[规则lint] 退出码 {'1（有报错级命中，不修不报喜）' if n_err else '0'}")
    else:
        print(report)
    return 1 if any(h.level == LEVEL_ERROR for h in hits) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
