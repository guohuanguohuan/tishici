# -*- coding: utf-8 -*-
"""⑤_00_净场锚定.py — ⑤轮起点锚定：同步盘终态 19 件 docx 字节复制进工作区＋MD5 清单（FX-2）。"""
import sys, io, os, shutil, hashlib, json, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SYNC = r"C:\提示词\高中数学\高中数学同步"
WORK = r"C:\提示词\工作区\选必1成书修复-0905\成书交付"
SRC_DIR = os.path.join(WORK, "_工作", "docx源")

FILES = [
    "人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx",
    "人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx",
    "人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx",
    "人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx",
    "人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx",
    "人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx",
    "人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx",
    "人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx",
    "人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx",
    "人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx",
    "人教B版选必1·封面.docx",
    "人教B版选必1·使用说明.docx",
    "人教B版选必1·册目录页.docx",
    "人教B版选必1·部分封面（第1章 空间向量与立体几何·衔接）.docx",
    "人教B版选必1·部分封面（第1章 空间向量与立体几何·清单）.docx",
    "人教B版选必1·部分封面（第1章 空间向量与立体几何·讲练）.docx",
    "人教B版选必1·部分封面（第2章 平面解析几何·衔接）.docx",
    "人教B版选必1·部分封面（第2章 平面解析几何·清单）.docx",
    "人教B版选必1·部分封面（第2章 平面解析几何·讲练）.docx",
    "人教B版选必1·装订单.md",
]


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    os.makedirs(SRC_DIR, exist_ok=True)
    rows, ok = [], True
    for name in FILES:
        s, d = os.path.join(SYNC, name), os.path.join(SRC_DIR, name)
        if not os.path.exists(s):
            print(f"MISSING 源缺失：{name}")
            ok = False
            continue
        shutil.copy2(s, d)
        m1, m2 = md5(s), md5(d)
        same = m1 == m2
        ok = ok and same
        rows.append({"file": name, "md5_sync": m1, "md5_copy": m2, "size": os.path.getsize(d), "equal": same})
        print(f"{'OK ' if same else 'DIFF'} {m1} {os.path.getsize(d):>9} {name}")
    man = {"time": datetime.datetime.now().isoformat(timespec="seconds"),
           "sync_dir": SYNC, "copy_dir": SRC_DIR, "files": rows, "all_equal": ok}
    with open(os.path.join(WORK, "_工作", "⑤_00_锚定.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=1)
    with open(os.path.join(WORK, "_工作", "⑤_00_锚定.md"), "w", encoding="utf-8") as f:
        f.write("# ⑤_00 净场锚定（同步盘终态→工作区字节复制，FX-2）\n\n")
        f.write(f"时点：{man['time']}　源：{SYNC}\n\n")
        f.write("| MD5 | 字节 | 件 |\n|---|---|---|\n")
        for r in rows:
            f.write(f"| {r['md5_sync']}{'（＝副本）' if r['equal'] else '（≠副本 DIFF！）'} "
                    f"| {r['size']} | {r['file']} |\n")
        f.write(f"\n全件等值：{ok}\n")
    print("ALL_EQUAL =", ok)


if __name__ == "__main__":
    main()
