"""Fixed Engine for ANTLab challenge B (minimal fix).

Flaw being fixed (baseline R02): cache key only used request['query'],
so a request that changes snapshot/doc_ids/k hits the previous request's
cache entry and returns stale-scope results (spec rule 5: cache must not
pollute requests that change data/scope/response).

Minimal fix: cache key now includes the full request scope
(query, doc_ids, snapshot, k). Everything else intentionally unchanged
so R03/R04/R07 (registered symptoms) remain observable.

The original flawed engine stays untouched at challenge.py (baseline).
Run with:  python run_cases.py --engine my_engine:Engine --output runs/fixed.json
"""
import copy
import time
import uuid


class Engine:
    def __init__(self):
        self.cache = {}

    def evaluate(self, request, corpus, draft):
        started = time.perf_counter()
        key = (
            request['query'].strip().lower(),
            tuple(request.get('doc_ids', [])),
            request.get('snapshot'),
            request.get('k'),
        )
        hit = key in self.cache
        if hit:
            result = copy.deepcopy(self.cache[key])
        else:
            terms = set(key[0].split())
            ranked = sorted(corpus, key=lambda b: (-len(terms & set(b['tags'])), b['id']))
            selected = [b for b in ranked[:request['k']] if terms & set(b['tags'])]
            evidence = [b for b in selected if b['doc_id'] in request['doc_ids'] and b['snapshot'] == request['snapshot']]
            citations = draft['citations']
            valid = bool(citations) and set(citations).issubset({b['id'] for b in evidence})
            result = {'answer': draft['answer'], 'citations': citations, 'evidence': evidence,
                      'locator_status': 'valid' if valid else 'invalid',
                      'support_status': 'supported' if valid else 'not_checked',
                      'judgment_source': 'rule', 'status': 'ok'}
            self.cache[key] = copy.deepcopy(result)
        result.update(request_id=str(uuid.uuid4()), request=copy.deepcopy(request), cache_hit=hit,
                      elapsed_ms=(time.perf_counter()-started)*1000, run_kind='offline_replay')
        return result
