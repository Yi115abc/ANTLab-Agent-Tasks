"""Variant & boundary runner for the fixed engine.

Produces runs/variants.json with:
- V1 version switch (v2 -> repeat v2 -> v1): proves cache reuses only
  equivalent inputs and never bleeds across snapshots.
- V2 id remap (doc_id alpha -> docA, semantically equivalent corpus):
  proves the cache key honours doc_ids and retrieval works by content.
- V3 word-order permutation (semantically equivalent query): proves
  ranking is stable under equivalent wording.
- edge: self-constructed unresolved boundaries (unknown snapshot,
  unknown doc) that the minimal fix intentionally does not solve.

Run with:  python run_variants.py
"""
import json
from pathlib import Path

from my_engine import Engine

BASE = Path(__file__).parent
data = json.loads((BASE / 'data.json').read_text(encoding='utf-8'))
corpus = data['corpus']

out = {}

# --- V1: snapshot version switching -------------------------------------
eng1 = Engine()
cases_v1 = [
    ('V1a_alpha_v2', {'query': 'timeout request threshold', 'doc_ids': ['alpha'], 'snapshot': 'v2', 'k': 2},
     {'answer': '请求超时阈值为12秒。', 'citations': ['b02']}),
    ('V1b_alpha_v2_repeat', {'query': 'timeout request threshold', 'doc_ids': ['alpha'], 'snapshot': 'v2', 'k': 2},
     {'answer': '请求超时阈值为12秒。', 'citations': ['b02']}),
    ('V1c_alpha_v1_after_v2', {'query': 'timeout request threshold', 'doc_ids': ['alpha'], 'snapshot': 'v1', 'k': 2},
     {'answer': '请求超时阈值为30秒。', 'citations': ['b01']}),
]
out['V1_version_switch'] = [
    {'case': cid, 'output': eng1.evaluate(req, corpus, draft)} for cid, req, draft in cases_v1
]

# --- V2: id remap (semantically equivalent corpus) ----------------------
eng2 = Engine()
corpus2 = [{**b, 'doc_id': ('docA' if b['doc_id'] == 'alpha' else b['doc_id'])} for b in corpus]
cases_v2 = [
    ('V2a_docA_v1', {'query': 'timeout request threshold', 'doc_ids': ['docA'], 'snapshot': 'v1', 'k': 2},
     {'answer': '请求超时阈值为30秒。', 'citations': ['b01']}),
    ('V2b_docA_v2', {'query': 'timeout request threshold', 'doc_ids': ['docA'], 'snapshot': 'v2', 'k': 2},
     {'answer': '请求超时阈值为12秒。', 'citations': ['b02']}),
]
out['V2_id_remap'] = [
    {'case': cid, 'output': eng2.evaluate(req, corpus2, draft)} for cid, req, draft in cases_v2
]

# --- V3: word-order permutation (semantically equivalent query) ---------
eng3 = Engine()
cases_v3 = [
    ('V3a_permuted_order', {'query': 'threshold timeout request', 'doc_ids': ['alpha'], 'snapshot': 'v2', 'k': 2},
     {'answer': '请求超时阈值为12秒。', 'citations': ['b02']}),
]
out['V3_word_order'] = [
    {'case': cid, 'output': eng3.evaluate(req, corpus, draft)} for cid, req, draft in cases_v3
]

# --- Edge: self-constructed unresolved boundaries -----------------------
eng4 = Engine()
cases_edge = [
    ('E1_unknown_snapshot', {'query': 'timeout request threshold', 'doc_ids': ['alpha'], 'snapshot': 'v9', 'k': 2},
     {'answer': '未知快照。', 'citations': []}),
    ('E2_unknown_doc', {'query': 'metadata', 'doc_ids': ['missing'], 'snapshot': 'v1', 'k': 2},
     {'answer': '这个文档存在。', 'citations': ['b05']}),
]
out['edge_unresolved'] = [
    {'case': cid, 'output': eng4.evaluate(req, corpus, draft)} for cid, req, draft in cases_edge
]

(BASE / 'runs' / 'variants.json').write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print('written:', (BASE / 'runs' / 'variants.json'))
