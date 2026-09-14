# 丙臂独立 Dice 复算器（凭空批A/B）·自实现 4-gram Dice，不调命制脚本函数·0914
# 用 ast 抽取命制脚本内指纹 dict（不执行其代码），本臂自实现 Dice 复算抽核 5 对＋库一致性断言
import ast

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

A = extract_dicts(r"C:/提示词/工作区/_tmpP2轮4凭空0914/防撞扫-批A.py")
B = extract_dicts(r"C:/提示词/工作区/_tmpP2轮4凭空0914/防撞扫批B.py")

def ngrams(s, n=4):
    s = "".join(ch for ch in s if not ch.isspace())
    return set(s[i:i + n] for i in range(len(s) - n + 1))

def dice(a, b):
    Ga, Gb = ngrams(a), ngrams(b)
    return 2 * len(Ga & Gb) / (len(Ga) + len(Gb)) if Ga and Gb else 0.0

def fp(libs, key):
    hits = [(name, v) for name, d in libs.items() for k, v in d.items()
            if k == key or k.startswith(key + "(")]
    if not hits:
        raise KeyError(key)
    assert len(hits) == 1, f"{key} 非唯一：{[h[0] for h in hits]}"
    return hits[0]

# ---- 库一致性断言（指纹库逐字拷贝核）----
pa, pb = A.get("pool"), B.get("pool")
na, nb = A.get("newA12"), B.get("newA12")
print(f"pool(69) 批B≡批A 逐字相等：{pa == pb}（|批A|={len(pa)}，|批B|={len(pb)}）")
print(f"newA12 批B≡批A 逐字相等：{na == nb}（|批A|={len(na)}，|批B|={len(nb)}）")
print(f"批B new9 规模＝{len(B.get('new9', {}))}；批A new9 规模＝{len(A.get('new9', {}))}")

# ---- 抽核 5 对（申报值 vs 本臂复算）----
# 键名映射：批B 件内 R4K-0N ≡ R4L-0N（勘定置换前跑数留痕）
pairs = [
    ("A", "R4K-07", "R4A-09", 0.169, "批A库面max"),
    ("A", "R4K-03", "R4K-04", 0.154, "批A批内max"),
    ("B", "R4K-09", "批B-13", 0.20,  "批B全表max（键名映射 R4L-09）"),
    ("B", "R4K-05", "R4K-08", 0.19,  "批B批内max（映射 R4L-05×R4L-08）"),
    ("B", "R4K-06", "批B-12", 0.03,  "批B疏密族人工判读数（映射 R4L-06，重跑top3未显形待核）"),
]
for lib, k1, k2, want, tag in pairs:
    src = A if lib == "A" else B
    _, f1 = fp(src, k1)
    _, f2 = fp(src, k2)
    got = dice(f1, f2)
    ok = "合" if abs(got - want) <= 0.005 + 1e-9 else "不合"
    print(f"[{lib}] {k1}×{k2}＝{got:.3f}（申报 {want}，{tag}）→ {ok}")
