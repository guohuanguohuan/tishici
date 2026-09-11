# -*- coding: utf-8 -*-
# 字体下载器（字替对照-0909）：直连优先 → Clash 127.0.0.1:7897 代理 → 放弃该项并记录。
# 只收 TTF/OTF/TTC 与许可文本；成功才由 .part 落位改名（全程不用 rm）。
import os, sys, time, json, urllib.request, urllib.error

WORK = r"C:/提示词/工作区/字替对照-0909/fonts"
PROXY = "http://127.0.0.1:7897"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) curl-font-fetch"}
LOG = os.path.join(WORK, "download.log")

def log(msg):
    line = msg
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def fetch(url, out, timeout=240):
    """return True if file saved (>=8KB or license >=1KB)"""
    minsize = 1024 if out.lower().endswith((".txt", ".md", ".license")) else 8192
    for mode in ("direct", "proxy"):
        handlers = []
        if mode == "proxy":
            handlers.append(urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}))
        else:
            handlers.append(urllib.request.ProxyHandler({}))
        opener = urllib.request.build_opener(*handlers)
        req = urllib.request.Request(url, headers=UA)
        part = out + ".part"
        t0 = time.time()
        try:
            with opener.open(req, timeout=timeout) as r, open(part, "wb") as f:
                while True:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
            sz = os.path.getsize(part)
            if sz >= minsize:
                os.replace(part, out)
                log(f"OK   [{mode}] {sz}B {time.time()-t0:.1f}s {url} -> {os.path.basename(out)}")
                return True
            log(f"SHORT [{mode}] {sz}B < {minsize}B {url}")
        except Exception as e:
            log(f"ERR  [{mode}] {type(e).__name__}: {e} {url}")
        time.sleep(1)
    log(f"GIVEUP {url}")
    return False

NOTO_BASE = "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/SubsetOTF/SC/"
results = {}

# ---------- 1) 思源黑体(Noto Sans SC) 静态 OTF ----------
noto = ["NotoSansSC-Light.otf", "NotoSansSC-Regular.otf", "NotoSansSC-Medium.otf",
        "NotoSansSC-Bold.otf", "NotoSansSC-Black.otf"]
for f in noto:
    results[f] = fetch(NOTO_BASE + f, os.path.join(WORK, f))
results["NOTO-LICENSE-OFL.txt"] = fetch(
    "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/LICENSE",
    os.path.join(WORK, "LICENSE-NotoSansSC-OFL.txt"))

# ---------- 2) free-font 仓库树定位（普惠体/HarmonyOS/方圆体镜像候选） ----------
tree_paths = []
for br in ("master", "main"):
    api = f"https://api.github.com/repos/wordshub/free-font/git/trees/{br}?recursive=1"
    try:
        handlers = [urllib.request.ProxyHandler({})]
        opener = urllib.request.build_opener(*handlers)
        req = urllib.request.Request(api, headers=UA)
        with opener.open(req, timeout=60) as r:
            data = json.load(r)
        tree_paths = [t["path"] for t in data.get("tree", []) if t["type"] == "blob"]
        log(f"TREE ok branch={br} blobs={len(tree_paths)}")
        break
    except Exception as e:
        log(f"TREE err branch={br}: {type(e).__name__}: {e}")

def pick(keywords, exts=(".ttf", ".otf", ".ttc")):
    hits = []
    for p in tree_paths:
        lp = p.lower()
        if any(k in lp for k in keywords) and lp.endswith(exts):
            hits.append(p)
    return hits

raw_base = "https://raw.githubusercontent.com/wordshub/free-font/master/"

# 阿里妈妈方圆体
fy = pick(["方圆体", "fangyuan"])
log("方圆体 hits: " + json.dumps(fy, ensure_ascii=False))
for p in fy[:6]:
    name = "FangYuanTi__" + os.path.basename(p).replace(" ", "_")
    if fetch(raw_base + urllib.request.quote(p), os.path.join(WORK, name)):
        break

# 阿里巴巴普惠体
ph = pick(["普惠体", "puhui"])
log("普惠体 hits: " + json.dumps(ph, ensure_ascii=False))
got = 0
# 先取 Bold/Heavy/Medium/Regular 各一档
want = ["bold", "heavy", "medium", "regular"]
for w in want:
    for p in ph:
        if w in os.path.basename(p).lower():
            name = "PuHuiTi__" + os.path.basename(p).replace(" ", "_")
            if fetch(raw_base + urllib.request.quote(p), os.path.join(WORK, name)):
                got += 1
                break
    if got >= 4:
        break

# HarmonyOS Sans SC
hm = pick(["harmonyos"])
log("HarmonyOS hits: " + json.dumps(hm, ensure_ascii=False))
got = 0
for w in ["bold", "medium", "regular"]:
    for p in hm:
        lp = p.lower()
        if w in os.path.basename(lp) and ("sc" in lp or "sc" in lp.replace("_", "")):
            name = "HarmonyOS__" + os.path.basename(p).replace(" ", "_")
            if fetch(raw_base + urllib.request.quote(p), os.path.join(WORK, name)):
                got += 1
                break
    if got >= 3:
        break

log("=== SUMMARY ===")
for k, v in results.items():
    log(f"{v and 'GOT ' or 'MISS'} {k}")
for f in sorted(os.listdir(WORK)):
    if not f.endswith((".py", ".log")):
        log(f"FILE {f} {os.path.getsize(os.path.join(WORK, f))}")
log("=== END ===")
