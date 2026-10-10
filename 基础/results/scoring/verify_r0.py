# -*- coding: utf-8 -*-
"""逐题核验：打印每题 R0 baseline 与 v2 improved 的问题、段落首句、答案与引用。"""
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


def head_of(r, n=95):
    lines = [ln for ln in r['messages'][1]['content'].split('\n') if ln.startswith('[')]
    out = []
    for ln in lines:
        t = ln[ln.index(']') + 1:].replace('\n', ' ')
        out.append(t[:n] + ('…' if len(t) > n else ''))
    return out


def ans_of(r):
    content = r['response']['choices'][0]['message']['content']
    m = re.search(r'"answer"\s*:\s*"([^"]*)"', content)
    c = re.search(r'"citations"\s*:\s*\[([^\]]*)\]', content)
    return (m.group(1) if m else '?'), (c.group(1) if c else '')


records = load_all()
for arg in sys.argv[1:]:
    imp = next(r for r in records if r['run_id'] == arg)
    cid = imp['case_id']
    base = next(r for r in records if r['case_id'] == cid and r['condition'] == 'R0' and r['variant'] == 'baseline')
    q = imp['messages'][1]['content'].split('\n')[0].replace('问题：', '')
    print('=' * 30, cid, 'R0', '=' * 30)
    print('问题:', q)
    print('--- 基线段落 ---')
    for h in head_of(base):
        print('   ', h)
    a1, c1 = ans_of(base)
    print('>>> 基线答案:', a1, '| 引用:', c1)
    print('--- 改进v2段落 ---')
    for h in head_of(imp):
        print('   ', h)
    a2, c2 = ans_of(imp)
    print('>>> 改进答案:', a2, '| 引用:', c2)
