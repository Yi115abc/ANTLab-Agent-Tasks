# -*- coding: utf-8 -*-
"""判分脚本 v1：检查 40 次主请求中 evaluation 基线的格式与引用合法性。
维度（依据 01_考核题目.md 第四步）：
- 技术成功（status=ok）与失败保留
- 模型回答是否为可解析 JSON，且含非空 answer
- citations 是否为列表、无重复、全部来自实际输入段落ID
- 记录耗时与 token 用量
输出：逐条核对表 + 汇总；问题行标记【问题】
"""
import json, glob, sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]          # 基础/
RUNS = BASE / 'runs'


def load_run(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def parse_answer(content):
    """模型可能返回纯JSON或带代码围栏，尽力解析；失败返回None。"""
    s = content.strip()
    if s.startswith('```'):
        lines = s.splitlines()
        if lines and lines[0].startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        s = '\n'.join(lines).strip()
    try:
        return json.loads(s)
    except Exception:
        return None


def main():
    files = sorted(glob.glob(str(RUNS / '*.json')))
    rows = []
    n_paid_eval = 0
    for f in files:
        r = load_run(f)
        if r.get('mode') != 'paid' or r.get('split') != 'evaluation':
            continue
        n_paid_eval += 1
        cid = r.get('case_id'); cond = r.get('condition')
        status = r.get('status')
        problems = []
        elapsed = r.get('elapsed_seconds')
        usage = r.get('usage') or {}
        tokens = usage.get('total_tokens')
        ans = '-'
        cit = '-'
        if status == 'ok':
            content = r['response']['choices'][0]['message']['content']
            obj = parse_answer(content)
            if obj is None:
                problems.append('回答非JSON或不可解析')
            else:
                ans = str(obj.get('answer', ''))
                cit = obj.get('citations')
                if not isinstance(ans, str) or not ans.strip():
                    problems.append('answer为空')
                if not isinstance(cit, list):
                    problems.append('citations非列表')
                    cit = str(cit)
                else:
                    if len(cit) != len(set(cit)):
                        problems.append('citations有重复')
                    allowed = set(r.get('original_passage_ids') or [])
                    bad = [c for c in cit if c not in allowed]
                    if bad:
                        problems.append('citations越界:' + ','.join(map(str, bad)))
                    cit = ','.join(map(str, cit)) if cit else '(空)'
        else:
            problems.append('状态非ok:' + str(status))
        rows.append((cid, cond, status, ans, cit, round(elapsed, 2) if elapsed is not None else '-',
                     tokens if tokens is not None else '-', '；'.join(problems) if problems else '通过'))

    print('=' * 70)
    print('判分脚本 v1 | evaluation paid 记录数:', n_paid_eval)
    print('=' * 70)
    print(f"{'题号':<5}{'条件':<5}{'状态':<9}{'answer':<18}{'citations':<26}{'耗时s':<8}{'tokens':<7}检查")
    print('-' * 70)
    for row in rows:
        print(f"{row[0]:<5}{row[1]:<5}{row[2]:<9}{str(row[3])[:18]:<18}{str(row[4])[:26]:<26}{row[5]:<8}{str(row[6]):<7}{row[7]}")
    print('-' * 70)
    n_ok = sum(1 for r in rows if r[2] == 'ok')
    n_pass = sum(1 for r in rows if r[7] == '通过')
    n_prob = sum(1 for r in rows if r[7] != '通过')
    total_tokens = sum(r[6] for r in rows if isinstance(r[6], int))
    print(f'汇总：技术成功 {n_ok}/{len(rows)}，全部检查通过 {n_pass}/{len(rows)}，有问题 {n_prob}')
    print(f'token 合计：{total_tokens}（基线32次）')
    if n_prob:
        print('提示：问题行需逐条人工核验；格式/引用错误保留在分母，另列技术成功结果。')


if __name__ == '__main__':
    main()
