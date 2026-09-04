import json, subprocess, urllib.parse, concurrent.futures

BASE = 'http://127.0.0.1:9097'
AUTH = 'Authorization: Bearer set-your-secret'
TEST_URL = 'http://www.gstatic.com/generate_204'

d = json.load(open(r'工作区/clash调节点-0902/proxies.json', encoding='utf-8'))['proxies']
grp = d['🚀节点选择']
cands = [n for n in grp['all'] if n not in ('DIRECT', 'REJECT', 'GLOBAL')
         and d.get(n, {}).get('type') not in ('Selector', 'URLTest', 'Fallback', 'Relay', 'Group', 'Pass')]
print('当前选择:', grp.get('now'), '| 待测候选:', len(cands))

def test(name):
    u = urllib.parse.quote(name, safe='')
    try:
        r = subprocess.run(['curl', '-s', '--max-time', '8', '-H', AUTH,
                            f'{BASE}/proxies/{u}/delay?timeout=6000&url={urllib.parse.quote(TEST_URL, safe="")}'],
                           capture_output=True, text=True, timeout=12)
        j = json.loads(r.stdout)
        return name, j.get('delay') if isinstance(j.get('delay'), int) else None
    except Exception:
        return name, None

results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for name, delay in ex.map(test, cands):
        results[name] = delay

ok = {k: v for k, v in results.items() if v is not None}
print('健康节点数:', len(ok), '/', len(cands))
for k, v in sorted(ok.items(), key=lambda x: x[1])[:12]:
    print(f'  {v:5d}ms  {k}')
json.dump(results, open(r'工作区/clash调节点-0902/全量测速.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
