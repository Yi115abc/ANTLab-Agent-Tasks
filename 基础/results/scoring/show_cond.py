# -*- coding: utf-8 -*-
"""查看指定条件（如 K）的基线段落与答案。"""
import json, glob, re, sys
from pathlib import Path

RUNS = Path(r'C:\Users\yihon\Desktop\AI Agent\ANTLab-Agent-Tasks-main\基础\runs')
recs = [json.loads(Path(f).read_text(encoding='utf-8')) for f in glob.glob(str(RUNS / '*.json'))]

cond = sys.argv[1] if len(sys.argv) > 1 else 'K'
for cid in sys.argv[2:]:
    for r in recs:
        if r.get('mode') == 'paid' and r.get('case_id') == cid and r.get('condition') == cond and r.get('variant') == 'baseline':
            lines = [ln for ln in r['messages'][1]['content'].split('\n') if ln.startswith('[')]
            print('====', cid, cond, '====')
            for ln in lines:
                t = ln[ln.index(']') + 1:].replace('\n', ' ')
                print('   ', t[:72])
            content = r['response']['choices'][0]['message']['content']
            m = re.search(r'"answer"\s*:\s*"([^"]*)"', content)
            print('>>> 答案:', m.group(1) if m else '?')
