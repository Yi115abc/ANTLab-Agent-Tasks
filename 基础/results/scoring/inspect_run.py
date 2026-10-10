# -*- coding: utf-8 -*-
"""人工核验辅助：打印指定 run 的问题、段落与模型答案（判断引用是否支持结论）。"""
import json, re, sys
from pathlib import Path

if len(sys.argv) < 2:
    print('用法: python inspect_run.py <run_id 或 文件名>')
    sys.exit(1)

arg = sys.argv[1]
p = Path(arg)
if not p.exists():
    p = Path(__file__).resolve().parents[2] / 'runs' / (arg + '.json')
if not p.exists():
    print('找不到文件:', arg)
    sys.exit(1)

r = json.loads(p.read_text(encoding='utf-8'))
print('=' * 40, r['case_id'], r['condition'], r['mode'], '=' * 40)
content = r['messages'][1]['content']
first = content.split('\n')[0]
print('问题:', first.replace('问题：', ''))
print('--- 输入段落 ---')
for line in content.split('\n'):
    if line.startswith('['):
        print(line)
print('--- 模型回答 ---')
if r.get('response') is None:
    print('（无模型回答：本记录为 dry/mock，未真实调用）')
    sys.exit(0)
resp = r['response']['choices'][0]['message']['content']
print(resp)
m = re.search(r'"answer"\s*:\s*"([^"]*)"', resp)
cits = re.findall(r'"citations"\s*:\s*\[([^\]]*)\]', resp)
print('>>> 答案:', m.group(1) if m else '?')
print('>>> 引用:', cits)
