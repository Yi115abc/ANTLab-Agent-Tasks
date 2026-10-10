# -*- coding: utf-8 -*-
"""改进对比：给定改进 run_id 列表，自动配同题 R0 基线，并排答案/引用/耗时。
用法：python compare_improved.py <improved_run_id> [<improved_run_id> ...]
"""
import json, glob, re, sys
from pathlib import Path

RUNS = Path(__file__).resolve().parents[2] / 'runs'


def load_all():
    out = []
    for f in glob.glob(str(RUNS / '*.json')):
        r = json.loads(Path(f).read_text(encoding='utf-8'))
        if r.get('mode') == 'paid' and r.get('split') == 'evaluation':
            out.append(r)
    return out


def ans_of(r):
    if r.get('response') is None:
        return '(无响应)'
    content = r['response']['choices'][0]['message']['content']
    m = re.search(r'"answer"\s*:\s*"([^"]*)"', content)
    c = re.search(r'"citations"\s*:\s*\[([^\]]*)\]', content)
    return (m.group(1) if m else '?'), (c.group(1) if c else '')


records = load_all()
imps = []
for arg in sys.argv[1:]:
    r = next((x for x in records if x['run_id'] == arg), None)
    if r is None:
        print('找不到记录:', arg)
        continue
    imps.append(r)

print('=' * 100)
print('改进对比（v2：R0 baseline vs improved）')
print('=' * 100)
print(f"{'题号':<5}{'基线answer':<14}{'基线citations':<32}{'改进answer':<14}{'改进citations':<32}耗时")
print('-' * 100)
for imp in imps:
    cid = imp['case_id']
    base = next((x for x in records if x['case_id'] == cid and x['condition'] == 'R0' and x['variant'] == 'baseline'), None)
    a2, c2 = ans_of(imp)
    e2 = round(imp.get('elapsed_seconds') or 0, 2)
    if base is None:
        print(f"{cid:<5}{'-':<14}{'-':<32}{str(a2)[:13]:<14}{c2[:31]:<32}{e2}s")
        continue
    a1, c1 = ans_of(base)
    e1 = round(base.get('elapsed_seconds') or 0, 2)
    print(f"{cid:<5}{str(a1)[:13]:<14}{c1[:31]:<32}{str(a2)[:13]:<14}{c2[:31]:<32}{e1}s->{e2}s")
print('-' * 100)
