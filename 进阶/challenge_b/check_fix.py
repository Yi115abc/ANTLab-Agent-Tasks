"""Compare baseline vs fixed outputs and summarize variants/edge results."""
import json
from pathlib import Path

BASE = Path(r'C:\Users\yihon\Desktop\AI Agent\ANTLab-Agent-Tasks-main\进阶\challenge_b\runs')

base = json.loads((BASE / 'baseline.json').read_text(encoding='utf-8'))
fixed = json.loads((BASE / 'fixed.json').read_text(encoding='utf-8'))
variants = json.loads((BASE / 'variants.json').read_text(encoding='utf-8'))

def ev(rec):
    return [e['id'] for e in rec['evidence']]

print('=== fixed.json: baseline -> fixed ===')
for b, f in zip(base, fixed):
    bo, fo = b['output'], f['output']
    print(f"{b['case_id']}: baseline(hit={bo['cache_hit']}, loc={bo['locator_status']}, sup={bo['support_status']}, ev={ev(bo)})")
    print(f"           fixed   (hit={fo['cache_hit']}, loc={fo['locator_status']}, sup={fo['support_status']}, ev={ev(fo)})")

print()
for group, items in variants.items():
    print(f'=== {group} ===')
    for it in items:
        o = it['output']
        print(f"{it['case']}: hit={o['cache_hit']}, loc={o['locator_status']}, sup={o['support_status']}, ev={ev(o)}, answer={o['answer']}")
