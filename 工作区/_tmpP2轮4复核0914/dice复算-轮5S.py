# P2 轮5实验卷复核臂·独立 Dice 复算（3 对抽核）·0914
# 口径同先例：ast 抽取指纹 dict（不执行命制脚本代码）＋自实现 4-gram 去空白 Dice，不调脚本函数
import ast, re, os

BASE = r"C:/提示词/工作区"

def extract_dicts(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
            try:
                d = ast.literal_eval(node.value)
            except Exception:
                continue
            if d and all(isinstance(k, str) and isinstance(v, str) for k, v in d.items()):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        out[t.id] = d
    return out

def fp_from_file(path):
    txt = open(path, encoding="utf-8").read()
    return re.findall(r"〔防撞记｜指纹＝「([^」]+)」", txt)

# 新3：从轮5S脚本 ast 抽 new3（找含 R5S 键的 dict）
n5 = extract_dicts(os.path.join(BASE, "_tmpP2轮5实验卷0914", "防撞扫-轮5S.py"))
new3 = next(d for d in n5.values() if any(k.startswith("R5S") for k in d))
assert len(new3) == 3

# 库：自建（A 脚本 pool69/newA12/newM10 ast 抽；R4B13/R4K9/R4L9 行提取自三命制件）
A = extract_dicts(os.path.join(BASE, "_tmpP2轮4凭空0914", "防撞扫-批A.py"))
mz = os.path.join(BASE, "P2-第10章量产0914", "命制")
r4b = fp_from_file(os.path.join(mz, "轮4改编批B-0914.md"))
r4k = fp_from_file(os.path.join(mz, "轮4凭空批A-0914.md"))
r4l = fp_from_file(os.path.join(mz, "轮4凭空批B-0914.md"))
assert (len(A["pool"]), len(A["newA12"]), len(A["newM10"]), len(r4b), len(r4k), len(r4l)) == (69, 12, 10, 13, 9, 9)
library = {}
library.update(A["pool"]); library.update(A["newA12"]); library.update(A["newM10"])
library.update({f"R4B-{i:02d}": s for i, s in enumerate(r4b, 1)})
library.update({f"R4K-{i:02d}": s for i, s in enumerate(r4k, 1)})
library.update({f"R4L-{i:02d}": s for i, s in enumerate(r4l, 1)})
assert len(library) == 122, len(library)

def ngrams(s, n=4):
    s = "".join(ch for ch in s if not ch.isspace())
    return set(s[i:i + n] for i in range(len(s) - n + 1))

def dice(a, b):
    Ga, Gb = ngrams(a), ngrams(b)
    return 2 * len(Ga & Gb) / (len(Ga) + len(Gb)) if Ga and Gb else 0.0

for a, b, claimed in (("R5S-01", "R4B-07", "0.166"), ("R5S-01", "R5S-03", "0.122"), ("R5S-03", "R4K-09", "0.11")):
    fa, fb_ = new3[a], (new3[b] if b in new3 else library[b])
    print(f"{a}×{b}：本臂复算＝{dice(fa, fb_):.4f}（件载申报 {claimed}）")
