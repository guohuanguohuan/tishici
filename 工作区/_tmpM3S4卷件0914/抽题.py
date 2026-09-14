import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SRC = "源证"
need = {
 "2章件2":[27,30,37,41,48], "2章件5":[10,11], "2章件6":[4,7,8,11],
 "2章件7":[18], "2章件8":[19], "2章件11":[1], "2章件12":[1,35],
 "2章件13":[29,37], "2章件14":[6,19],
 "3章件5":[13], "3章件6":[5,12,21], "3章件11":[1,5,6], "3章件12":[8],
 "3章件14":[11,15,23,25], "3章件16":[9], "3章件17b":[22],
 "3章件18":[12,13], "3章件19":[4,6], "3章件21":[1,2,4],
}
qre = re.compile(r'^(\d{1,2})．')
out = []
for f, nums in need.items():
    lines = open(f"{SRC}/{f}.txt", encoding="utf-8").read().splitlines()
    cur, n = None, None
    blocks = {}
    for ln in lines:
        m = qre.match(ln)
        if m:
            if cur is not None: blocks.setdefault(n, []).extend(cur)
            n, cur = int(m.group(1)), [ln]
        elif cur is not None:
            cur.append(ln)
    if cur is not None: blocks.setdefault(n, []).extend(cur)
    for q in nums:
        body = blocks.get(q)
        out.append(f"\n{'='*20} {f}-#{q} {'='*20}\n" + ( "\n".join(body) if body else "!!未找到!!"))
open("抽取汇编.txt","w",encoding="utf-8").write("\n".join(out))
print("落盘 抽取汇编.txt，共", len(out), "块")
