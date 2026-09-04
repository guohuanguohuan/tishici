# -*- coding: utf-8 -*-
"""子步10 COM驱动（§〇⑥bis形态）：逐件一子进程、90s全程帽、JSONL已有结果只读不重跑、
挂→差分击杀自建WINWORD→换新实例续跑；讲练1上(B)0次直开强制副本（§〇⑦）；
其余9件各1次直开机会，挂/报错即降级副本、禁原地重试。
sha不等或拷贝失败＝标「未测＋需裁决」跳下一件，禁用任何非全等手段。"""
import hashlib, json, os, shutil, subprocess, sys, time, datetime

BASE = r"C:\提示词\高中数学\高中数学同步"
TMP = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步10\tmp"
COPYDIR = os.path.join(TMP, "原件全同副本")
WORKER = os.path.join(TMP, "com_worker_子步10.py")
JSONL = os.path.join(TMP, "实测_逐件.jsonl")
EVENTS = os.path.join(TMP, "com事件_子步10.jsonl")
SHAJSON = os.path.join(TMP, "t10_sha比对.json")
STARTJSON = os.path.join(TMP, "t10_start采集.json")
CAP = 90  # 秒，覆盖单件全程 Open→Repaginate→ComputeStatistics→Close

FILES = [  # 短名, 实名, 强制副本?
    ("X1", "人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx", False),
    ("I1", "人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx", False),
    ("B", "人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx", True),
    ("C", "人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx", False),
    ("X2", "人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx", False),
    ("I2", "人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx", False),
    ("E", "人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx", False),
    ("F", "人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx", False),
    ("G", "人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx", False),
    ("H", "人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx", False),
]

def ev(kind, **kw):
    rec = {"t": datetime.datetime.now().isoformat(timespec="milliseconds"),
           "事件": kind, **kw}
    with open(EVENTS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("[EV]", json.dumps(rec, ensure_ascii=False), flush=True)

def winword_pids():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id"],
                         capture_output=True, text=True, timeout=30).stdout
    return {int(x) for x in out.split() if x.strip().isdigit()}

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def make_copy(name, orig_sha):
    """字节拷贝→sha复核与原件全等并回显。返回副本路径或None。"""
    src = os.path.join(BASE, name)
    dst = os.path.join(COPYDIR, name)
    shutil.copyfile(src, dst)
    csha = sha(dst)
    eq = (csha == orig_sha == sha(src))
    ev("副本sha复核", 件=name, 副本=dst, 副本sha=csha, 原件sha=orig_sha, 全等=eq)
    return dst if eq else None

def run_worker(path, name, form, osha, sinfo):
    """一次worker子进程（90s帽）。返回 'ok'|'挂'|'报错'。"""
    before = winword_pids()
    t0 = time.time()
    ev("open_start", 件=name, 形态=form, 路径=path)
    try:
        r = subprocess.run([sys.executable, WORKER, path, name, form, osha,
                            json.dumps(sinfo, ensure_ascii=False), JSONL],
                           capture_output=True, text=True, timeout=CAP)
        if r.returncode == 0 and "WORKER-OK" in r.stdout:
            ev("测成", 件=name, 形态=form, 全程耗时=round(time.time() - t0, 2))
            return "ok"
        ev("报错", 件=name, 形态=form, 退出码=r.returncode,
           stderr=(r.stderr or "")[-500:], 全程耗时=round(time.time() - t0, 2))
        return "报错"
    except subprocess.TimeoutExpired:
        ev("挂", 件=name, 形态=form, 帽=CAP)
        after = winword_pids()
        new = sorted(after - before)
        for pid in new:
            subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                           capture_output=True, timeout=20)
        ev("差分击杀自建WINWORD", 件=name, 击杀PID=new, 跑前=sorted(before))
        return "挂"

def main():
    os.makedirs(COPYDIR, exist_ok=True)
    with open(SHAJSON, encoding="utf-8") as f:
        shas = {r["件"]: r["sha256"] for r in json.load(f)["逐件"]}
    with open(STARTJSON, encoding="utf-8") as f:
        sinfos = {r["件"]: r for r in json.load(f)}
    done = set()
    if os.path.exists(JSONL):
        with open(JSONL, encoding="utf-8") as f:
            for ln in f:
                if ln.strip():
                    done.add(json.loads(ln)["件名"])
    ev("驱动启动", 已有结果件=sorted(done))
    results = {}
    for key, name, forced_copy in FILES:
        if name in done:
            ev("跳过重跑", 件=name)
            continue
        osha, sinfo = shas[name], sinfos[name]
        if forced_copy:
            ev("强制副本路径", 件=name, 依据="§〇⑦讲练1上禁直开")
            dst = make_copy(name, osha)
            if dst is None:
                ev("未测需裁决", 件=name, 原因="副本sha不等或拷贝失败")
                results[name] = "未测"
                continue
            st = run_worker(dst, name, "副本降级（强制）", osha, sinfo)
            results[name] = st if st == "ok" else "未测"
            if st != "ok":
                ev("未测需裁决", 件=name, 原因=f"副本路径{st}")
            continue
        # 其余9件：1次直开机会
        st = run_worker(os.path.join(BASE, name), name, "原件直开", osha, sinfo)
        if st == "ok":
            results[name] = "ok"
            continue
        ev("降级触发", 件=name, 触发=st)
        dst = make_copy(name, osha)
        if dst is None:
            ev("未测需裁决", 件=name, 原因="副本sha不等或拷贝失败")
            results[name] = "未测"
            continue
        st2 = run_worker(dst, name, f"副本降级（{st}）", osha, sinfo)
        results[name] = st2 if st2 == "ok" else "未测"
        if st2 != "ok":
            ev("未测需裁决", 件=name, 原因=f"副本路径{st2}")
    ev("驱动收尾", 结果=results)
    print("RESULTS " + json.dumps(results, ensure_ascii=False))

if __name__ == "__main__":
    main()
