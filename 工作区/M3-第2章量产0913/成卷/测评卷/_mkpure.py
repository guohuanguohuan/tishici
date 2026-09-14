s = open("main.tex", encoding="utf-8").read()
BS = chr(92)
a = BS + "usepackage{qp-m3}"
b = BS + "usepackage[pure]{qp-m3}"
assert s.count(a) == 1, s.count(a)
open("main-pure.tex", "w", encoding="utf-8", newline=chr(10)).write(s.replace(a, b))
print("pure ok")
