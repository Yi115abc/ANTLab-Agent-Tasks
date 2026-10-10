# -*- coding: utf-8 -*-
"""紧凑对比多个 run：问题/答案/引用 + 每段首部（人工核验引用是否支持结论）。"""
import json, re, sys
from pathlib import Path

RUNS = Path(__file__).resolve().parents[2] / 'runs'


def brief(text, n=110):
    text = text.replace('\n', ' ')
    return text[:n] + ('…' if len(text) > n else '')


for arg in sys.argv[1:]:
    p = RUNS / (arg + '.json')
    if not p.exists():
        print('找不到:', arg)
        continue
    r = json.loads(p.read_text(encoding='utf-8'))
    print('=' * 36, r['case_id'], r['condition'], r['mode'], '=' * 36)
    content = r['messages'][1]['content']
    print('问题:', content.split('\n')[0].replace('问题：', ''))
    for line in content.split('\n'):
        if line.startswith('['):
            print('  ', brief(line))
    resp = r['response']['choices'][0]['message']['content']
    m = re.search(r'"answer"\s*:\s*"([^"]*)"', resp)
    cits = re.findall(r'"citations"\s*:\s*\[([^\]]*)\]', resp)
    print('>>> 答案:', m.group(1) if m else '?', '| 引用:', cits)
