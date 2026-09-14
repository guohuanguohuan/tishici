# -*- coding: utf-8 -*-
"""_s5lib.py — S5 试产臂共享库（写入仅限本目录；成卷件/工具只读）。"""
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import time

if not (getattr(sys.stdout, 'encoding', '') or '').lower().startswith('utf'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))          # C:/提示词
CJ = os.path.join(REPO, '工作区', 'M3-第2章量产0913', '成卷')
TOOL = os.path.join(REPO, '工具', '答案抽册器.py')

_spec = importlib.util.spec_from_file_location('ansbook_tool', TOOL)
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)

# 件序（册序＝产线片序；06B 随 06 之后）
PIAN_ORDER = ['衔接节'] + ['课时%02d' % i for i in range(1, 20)] + []
PIAN_ORDER = ['衔接节', '课时01', '课时02', '课时03', '课时04', '课时05',
              '课时06', '课时06B', '课时07', '课时08', '课时09', '课时10',
              '课时11', '课时12', '课时13', '课时14', '课时15', '课时16',
              '课时17', '课时18', '课时19']
GROUPS = [('导学件', '导学件'), ('练习件', '练习件'), ('拓展册', '拓展册')]


def pieces_of(jianxing):
    """件型 → [(片名, 件绝对目录)]（产线片序）。"""
    base = os.path.join(CJ, jianxing)
    by_pian = {}
    for name in os.listdir(base):
        p = os.path.join(base, name)
        if os.path.isdir(p) and os.path.exists(os.path.join(p, 'main.tex')):
            by_pian[T.pian_name(p)] = p
    out = []
    for pian in PIAN_ORDER:
        if pian in by_pian:
            out.append((pian, by_pian.pop(pian)))
    for pian in sorted(by_pian):                      # 未入表片兜底（如实续排）
        out.append((pian, by_pian[pian]))
    return out


def run_tool(piece_dir, out_dir):
    """逐件抽册（子进程，rc＋尾段留证）。"""
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    r = subprocess.run([sys.executable, TOOL, piece_dir, '--out', out_dir,
                        '--skip-png'], capture_output=True, text=True,
                       encoding='utf-8', errors='replace', cwd=REPO)
    dt = time.time() - t0
    tail = (r.stdout or '').strip().splitlines()[-14:]
    if r.returncode != 0:
        open(os.path.join(out_dir, '_stdout红.txt'), 'w', encoding='utf-8').write(
            (r.stdout or '') + '\n----stderr----\n' + (r.stderr or ''))
    return {'rc': r.returncode, '秒': round(dt, 1), '尾段': tail}


def load_readings(out_dir):
    p = os.path.join(out_dir, '抽册读数.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


# —— 泄漏补扫（拓展册题面库缺件→源件题面区替代口径，照工具门谱同折） ——
def fold(s):
    import unicodedata
    return unicodedata.normalize('NFKC', T.norm_ws(s or '')).replace('\u2212', '-')


def source_leakscan(piece_dir, out_dir):
    """源 main.tex 去 ansblock 体后逐行 ≥12字 run 为针，册双档 PDF 为 haystack，
    豁免＝全块 值+详解 剥离归一。返回 (红针列表, 针数)。"""
    src = T.read_text(os.path.join(piece_dir, 'main.tex'))
    lines = [ln.rstrip('\r') for ln in src.split('\n')]
    body, cur = [], False
    for ln in lines:                                   # 遮蔽 ansblock 体（豁免源）
        code = T.strip_comment(ln)
        if T.RE_BEGIN.match(code):
            cur = True
            continue
        if cur and T.RE_END.match(code):
            cur = False
            continue
        if not cur:
            body.append(ln)
    piece = T.parse_piece(piece_dir)
    allowed = fold(T.texstrip(''.join((b['val'] or '') + (b['note'] or '')
                                      for b in piece['blocks'])))
    runs = sorted(set(fold(r) for ln in body
                      for r in T.prose_runs(T.texstrip(ln))))
    reds = []
    for tag in ('true', 'false'):
        import fitz
        doc = fitz.open(os.path.join(out_dir, 'ansbook-%s.pdf' % tag))
        hay = fold('\n'.join(p.get_text() for p in doc))
        doc.close()
        reds += [r for r in runs if r in hay and r not in allowed]
    reds = sorted(set(reds))
    json.dump({'口径': '题面库缺件→源件题面区替代（≥12字run·NFKC+空白归一·−折连字；'
                       '豁免＝本件ansblock值+详解）',
               '针数': len(runs), '红针': reds[:8], '红针数': len(reds)},
              open(os.path.join(out_dir, '泄漏补扫.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    return reds, len(runs)
