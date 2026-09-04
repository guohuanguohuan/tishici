# -*- coding: utf-8 -*-
"""补推循环：fetch→比对→缺则 push→再 fetch 核销，直到 origin/main == main 或超帽。
日志落本目录 补推循环.log。"""
import subprocess, time, os, sys

PROXY = 'http://127.0.0.1:7897'
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '补推循环.log')
DEADLINE = time.time() + 3600

def log(m):
    line = time.strftime('%H:%M:%S') + ' ' + m
    print(line, flush=True)
    open(LOG, 'a', encoding='utf-8').write(line + '\n')

def git(*args, timeout=300):
    r = subprocess.run(['git', '-c', f'http.proxy={PROXY}', '-C', r'C:\提示词', *args],
                       capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout + r.stderr).strip()

def synced():
    rc, ahead = git('rev-list', '--count', 'origin/main..main')
    return rc == 0 and ahead.strip() == '0'

for i in range(1, 40):
    rc, out = git('fetch', 'origin', 'main', timeout=180)
    log(f'轮{i} fetch rc={rc} {out[-120:] if rc else "ok"}')
    if rc == 0:
        if synced():
            log('SUCCESS origin/main 已含本地全部提交')
            sys.exit(0)
        rc2, out2 = git('push', 'origin', 'main', timeout=900)
        log(f'轮{i} push rc={rc2} {out2[-200:]}')
        if rc2 == 0:
            rc3, _ = git('fetch', 'origin', 'main', timeout=180)
            if rc3 == 0 and synced():
                log('SUCCESS 推送并核销完成')
                sys.exit(0)
    time.sleep(90)
log('TIMEOUT 1小时未闭合')
sys.exit(1)
