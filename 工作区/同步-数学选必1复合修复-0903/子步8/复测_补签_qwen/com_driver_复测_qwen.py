# -*- coding: utf-8 -*-
"""COM driver（qwen复测·R3/R5）：配页两件一次会话；90s/开卷护栏、每件≤2次（第2次用我工作区SHA全同副本）；
挂→标环境阻断。WINWORD 前后差分，只清自建 PID，绝不动用户5实例。状态/副本全落我工作区，不写 tmp。"""
import sys, io, os, json, time, shutil, hashlib, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

HERE = os.path.dirname(os.path.abspath(__file__))
WORKER = os.path.join(HERE, 'com_worker_复测_qwen.py')
BASE = r'C:\提示词\高中数学\高中数学同步'
COPYDIR = os.path.join(HERE, '副本_qwen')
USER_PIDS = {28012, 26168, 5988, 13320, 10308}
GUARD = 90
FILES = {'册目录页': os.path.join(BASE, '人教B版选必1·册目录页.docx'),
         '使用说明': os.path.join(BASE, '人教B版选必1·使用说明.docx')}

def word_pids():
    out = subprocess.run(['powershell', '-NoProfile', '-Command',
                          "Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id"],
                         capture_output=True, text=True).stdout
    return {int(x) for x in out.split() if x.strip().isdigit()}

def sha(fp):
    h = hashlib.sha256()
    with open(fp, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

def read_status(path):
    evs = []
    if os.path.exists(path):
        for ln in open(path, encoding='utf-8'):
            ln = ln.strip()
            if ln:
                evs.append(json.loads(ln))
    return evs

def run_session(tag, files):
    status = os.path.join(HERE, 'com_status_复测_qwen_%s.jsonl' % tag)
    if os.path.exists(status):
        os.remove(status)
    before = word_pids()
    proc = subprocess.Popen([sys.executable, WORKER, status] + files,
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    pending = [os.path.basename(f) for f in files]
    result = {n: None for n in pending}
    wpid = None
    while True:
        evs = read_status(status)
        done = {e['file']: e for e in evs if e['ev'] == 'open_done'}
        starts = {e['file']: e for e in evs if e['ev'] == 'open_start'}
        wpid = next((e.get('pid') for e in evs if e['ev'] == 'word_started'), None)
        for n in pending:
            if n in done:
                result[n] = done[n]['pages']
        if any(e['ev'] == 'all_done' for e in evs) or proc.poll() is not None:
            time.sleep(0.3)
            for e in read_status(status):
                if e['ev'] == 'open_done':
                    result[e['file']] = e['pages']
                if e['ev'] == 'error':
                    print('  [%s] worker error: %s' % (tag, e['msg']))
            break
        cur = next(((n, starts[n]['ts']) for n in pending if n in starts and n not in done), None)
        if cur and time.time() - cur[1] > GUARD:
            if wpid and wpid not in USER_PIDS:
                subprocess.run(['taskkill', '/F', '/PID', str(wpid)], capture_output=True)
                print('  [%s] 已按 PID 清自建 Word %d' % (tag, wpid))
            elif wpid in USER_PIDS:
                print('  [%s] !! worker Word PID=%d 撞用户名单，拒杀' % (tag, wpid))
            proc.kill()
            print('  [%s] 开卷超90s挂死（%s）→ 本会话中止' % (tag, cur[0]))
            break
        time.sleep(1)
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()
    after = word_pids()
    leaked = {p for p in (after - before) if p not in USER_PIDS}
    for p in leaked:
        subprocess.run(['taskkill', '/F', '/PID', str(p)], capture_output=True)
    print('  [%s] WINWORD差分 before=%s after=%s 用户名单外残留=%s(已清)' % (tag, sorted(before), sorted(after), sorted(leaked)))
    return result, {'before': sorted(before), 'after': sorted(after), 'wpid': wpid}

out = {'页数': {}, '尝试': {}, '护栏阻断': {}, 'winword差分': {}}
r, diff = run_session('peiye', list(FILES.values()))
out['winword差分']['peiye'] = diff
inv = {os.path.basename(v): k for k, v in FILES.items()}
for name, path in FILES.items():
    pages = r[os.path.basename(path)]
    att = 1
    if pages is None:
        os.makedirs(COPYDIR, exist_ok=True)
        cp = os.path.join(COPYDIR, os.path.basename(path))
        shutil.copyfile(path, cp)
        assert sha(path) == sha(cp), '副本sha不等'
        r2, diff2 = run_session('peiye2', [cp])
        out['winword差分']['peiye2'] = diff2
        pages = r2.get(os.path.basename(cp))
        att = 2
    out['页数'][name] = pages
    out['尝试'][name] = att
    if pages is None:
        out['护栏阻断'][name] = '两次尝试均挂→环境阻断'

print(json.dumps(out, ensure_ascii=False, indent=1))
json.dump(out, open(os.path.join(HERE, 'com页数_复测_qwen.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
