# -*- coding: utf-8 -*-
# qwen臂 建副本脚本：自进程字节拷贝10件原件 -> tmp\原件全同副本\，逐件复核sha256并回显
import hashlib, os, shutil, sys, time

DST = r"C:\提示词\工作区\同步-数学选必1复合修复-0903\子步8\tmp\原件全同副本"

ITEMS = [
    ("衔接1", r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何·衔接件（29题）.docx",
     "5d502ff51b5818c0b1ed2942e77627021574185bc064fa997ecaed7d3b550ee4"),
    ("清单1", r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何·知识清单（完成）.docx",
     "8f786bdefc427eb340e4d721c1bd8776e9ef9bc7b6ded556c5f256275d586f36"),
    ("讲练1上", r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（上）·讲练件（61题）.docx",
     "f286cd898026f8579aff26b1b946003f6df70532b3159be2047b13ca1029c355"),
    ("讲练1下", r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第1章 空间向量与立体几何（下）·讲练件（79题）.docx",
     "007be2041df05d8738b275c487f5d484ab3d7b47844ca6c0569fbcf7d48874cc"),
    ("衔接2", r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何·衔接件（13题）.docx",
     "704c0f80fdef53b2ae8c072600d085d498544d1dd719ef5180c05c057e72ee07"),
    ("清单2", r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何·知识清单（完成）.docx",
     "b521cc684dc16a687cc5f99124ebf3b5537cdeae9ddcb1c5db820e9accbf990e"),
    ("讲练2a", r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.1—2.3.3）·讲练件（92题）.docx",
     "d53bcb98b5f204175f43ae0e7be48b366650c5cbed5bcc17061a5e4ef18358ad"),
    ("讲练2b", r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.3.4—2.5.2）·讲练件（90题）.docx",
     "d2c92b22f11182268bf12ef08dddfd1b2c27ee9012b86687aef92f69d23cff1c"),
    ("讲练2c", r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.6.1—2.7.2）·讲练件（68题）.docx",
     "303bc54eb69e3511d5d352f20865f3465b00f24b50df49a194e8771778601d06"),
    ("讲练2d", r"C:\提示词\高中数学\高中数学同步\人教B版选必1 第2章 平面解析几何（2.8）·讲练件（89题）.docx",
     "aa528becd29070798a11f1ae984b7687dd3c2840a6903cf55611ccdf3dddb96a"),
]

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    os.makedirs(DST, exist_ok=True)
    n_ok = 0
    print("短名\t件号\t处置\t期望sha256\t副本实际sha256\t结果")
    for idx, (name, src, exp) in enumerate(ITEMS, 1):
        dst = os.path.join(DST, os.path.basename(src))
        if os.path.isfile(dst):
            got = sha256(dst)
            action = "复用既有副本"
            if got != exp:
                action = "既有副本sha不符->重拷"
                os.remove(dst)
                got = None
        else:
            action = "新建拷贝"
            got = None
        if got is None:
            if not os.path.isfile(src):
                print("%s\t%d\t原件缺失:%s\t%s\t-\tFAIL" % (name, idx, src, exp))
                continue
            shutil.copyfile(src, dst)
            got = sha256(dst)
        ok = (got == exp)
        n_ok += ok
        print("%s\t%d\t%s\t%s\t%s\t%s" % (name, idx, action, exp, got, "OK" if ok else "MISMATCH"))
    print("SUMMARY %d/10 sha全同" % n_ok)
    sys.exit(0 if n_ok == 10 else 1)

if __name__ == "__main__":
    t0 = time.time()
    main()
    print("elapsed %.1fs" % (time.time() - t0))
