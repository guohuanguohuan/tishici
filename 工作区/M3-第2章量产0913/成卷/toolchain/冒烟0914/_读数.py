# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
for f in ("dummy-true", "dummy-false"):
    log = open(f + ".log", encoding="utf-8", errors="replace").read()
    err = len(re.findall(r"^! ", log, re.M))
    ovb = len(re.findall(r"Overfull [\\]vbox", log))
    ovh = len(re.findall(r"Overfull [\\]hbox", log))
    un = len(re.findall(r"Underfull", log))
    mc = len(re.findall(r"Missing character", log))
    pg = re.search(r"Output written on .*?\((\d+) pages?", log)
    ak = len(re.findall(r"M3-ANSKEY", log))
    print("%s: error=%d Overfull(v/h)=%d/%d Underfull=%d Missing=%d pages=%s ANSKEY=%d"
          % (f, err, ovb, ovh, un, mc, pg.group(1) if pg else "?", ak))
for p in ("探针-速查表", "探针-平行框"):
    keep = []
    for i in (1, 2):
        log = open(p + ".log", encoding="utf-8", errors="replace").read()
        err = len(re.findall(r"^! ", log, re.M))
        for ln in log.splitlines():
            for tag in ("M3-EH-VALUE", "M3-TAB-HT", "M3-PAR-BEGINDOCEND", "M3-PAR-BODY"):
                if ln.startswith(tag):
                    keep.append("pass%d %s" % (i, ln[:64] + ("…" if len(ln) > 64 else "")))
        if err:
            keep.append("pass%d error=%d" % (i, err))
    print(p, "｜", " || ".join(keep[:4]))
