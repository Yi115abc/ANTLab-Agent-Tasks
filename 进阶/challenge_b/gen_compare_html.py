"""Generate compare.html: self-contained page showing before/after behavior."""
import json
import html as H
from pathlib import Path

BASE = Path(r'C:\Users\yihon\Desktop\AI Agent\ANTLab-Agent-Tasks-main\进阶\challenge_b')
RUNS = BASE / 'runs'

base = json.loads((RUNS / 'baseline.json').read_text(encoding='utf-8'))
fixed = json.loads((RUNS / 'fixed.json').read_text(encoding='utf-8'))
variants = json.loads((RUNS / 'variants.json').read_text(encoding='utf-8'))

def ev(rec):
    return ', '.join(e['id'] for e in rec['evidence']) or '—'

def req_str(rec):
    r = rec['request']
    return f"query=\"{r['query']}\" · doc_ids={r['doc_ids']} · snapshot={r['snapshot']} · k={r['k']}"

def badge(rec):
    parts = []
    parts.append(f"<span class='b {rec['locator_status']}'>{rec['locator_status']}</span>")
    parts.append(f"<span class='b {rec['support_status']}'>{rec['support_status']}</span>")
    parts.append(f"<span class='b hit'>{'cache_hit' if rec['cache_hit'] else 'no_cache'}</span>")
    return ' '.join(parts)

rows = []
for b, f in zip(base, fixed):
    bo, fo = b['output'], f['output']
    changed = (ev(bo) != ev(fo)) or (bo['cache_hit'] != fo['cache_hit'])
    rows.append(f"""
    <tr class="{'changed' if changed else ''}">
      <td>{b['case_id']}</td>
      <td class="l">{H.escape(req_str(bo))}</td>
      <td class="l">{H.escape(ev(bo))}<br>{H.escape(bo['answer'])}<br>{badge(bo)}</td>
      <td class="l">{H.escape(ev(fo))}<br>{H.escape(fo['answer'])}<br>{badge(fo)}</td>
      <td>{'<b>修复生效</b>' if changed else '不变'}</td>
    </tr>""")

def variant_rows(group, items):
    out = []
    for it in items:
        o = it['output']
        out.append(f"""
    <tr>
      <td>{H.escape(it['case'])}</td>
      <td class="l">{H.escape(req_str(o))}</td>
      <td class="l">{H.escape(ev(o))}<br>{H.escape(o['answer'])}<br>{badge(o)}</td>
    </tr>""")
    return '\n'.join(out)

v1 = variant_rows('V1', variants['V1_version_switch'])
v2 = variant_rows('V2', variants['V2_id_remap'])
v3 = variant_rows('V3', variants['V3_word_order'])
edge = variant_rows('Edge', variants['edge_unresolved'])

page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>ANTLab 进阶题B · 修复前后行为对比</title>
<style>
  body {{ font-family: "Microsoft YaHei", sans-serif; margin: 24px; color: #222; }}
  h1 {{ font-size: 20px; }}
  h2 {{ font-size: 16px; margin-top: 28px; border-left: 4px solid #4A90D9; padding-left: 8px; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
  th, td {{ border: 1px solid #bbb; padding: 6px 8px; font-size: 13px; vertical-align: top; }}
  th {{ background: #f2f2f2; }}
  td.l {{ text-align: left; }}
  tr.changed td {{ background: #fff8e1; }}
  .b {{ display: inline-block; padding: 1px 6px; border-radius: 3px; font-size: 11px; margin-right: 4px; }}
  .valid {{ background: #e8f5e9; color: #1b5e20; }}
  .invalid {{ background: #fce4ec; color: #b71c1c; }}
  .supported {{ background: #e3f2fd; color: #0d47a1; }}
  .not_checked {{ background: #eceff1; color: #455a64; }}
  .hit {{ background: #fff3e0; color: #e65100; }}
  .no_cache {{ background: #f5f5f5; color: #757575; }}
  .note {{ font-size: 12px; color: #666; }}
</style>
</head>
<body>
<h1>ANTLab 进阶题B · 系统失效诊断 — 修复前后行为对比</h1>
<p class="note">修复内容：缓存键由仅 query 扩展为 (query, doc_ids, snapshot, k)，消除跨快照缓存污染（spec 第 5 条）。
基线引擎 challenge.py 保留未动；本页数据来自 runs/baseline.json、runs/fixed.json、runs/variants.json。</p>

<h2>一、主用例：修复前后（R01–R07）</h2>
<table>
<tr><th>Case</th><th>请求</th><th>修复前（基线）</th><th>修复后</th><th>差异</th></tr>
{''.join(rows)}
</table>
<p class="note">R02 为修复目标：换 snapshot=v2 后不再命中 v1 缓存，正确返回 v2 的 12 秒与 b02。
R01/R03/R04/R05/R06/R07 均与基线一致：其中 R01/R05/R06 为原本正常的回归对照；R03/R04/R07 为登记症状（本次最小修复刻意不越权处理）。</p>

<h2>二、等价变体（验证修复按内容工作）</h2>
<h3>V1 · 资料版本切换</h3>
<table><tr><th>变体</th><th>请求</th><th>输出</th></tr>{v1}</table>
<p class="note">V1b 等价输入复用缓存（cache_hit=true 且结果仍正确）；V1c 证明 v2 缓存不会污染随后的 v1 请求。</p>
<h3>V2 · 标识重映射（doc_id alpha→docA）</h3>
<table><tr><th>变体</th><th>请求</th><th>输出</th></tr>{v2}</table>
<p class="note">标识重映射后检索仍按内容工作，且不同 doc_ids 互不串缓存。</p>
<h3>V3 · 等价词序（threshold timeout request）</h3>
<table><tr><th>变体</th><th>请求</th><th>输出</th></tr>{v3}</table>

<h2>三、自构造未解决边界</h2>
<table><tr><th>变体</th><th>请求</th><th>输出</th></tr>{edge}</table>
<p class="note">未知快照/未知文档目前仍返回 locator=invalid + status=ok，未实现 spec 第 1 条要求的 invalid_scope；登记为未解决边界。</p>

<p class="note">状态图例：<span class="b valid">valid</span><span class="b invalid">invalid</span><span class="b supported">supported</span><span class="b not_checked">not_checked</span><span class="b hit">cache_hit</span><span class="b no_cache">no_cache</span></p>
</body>
</html>"""

(BASE / 'compare.html').write_text(page, encoding='utf-8')
print('written:', BASE / 'compare.html')
