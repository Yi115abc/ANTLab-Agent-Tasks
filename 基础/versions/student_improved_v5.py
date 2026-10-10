"""待候选人实现。避免读取dev_answers或题号/condition来构造答案。"""

import re


def prepare_messages(question, passages):
    """返回 [{"role":"system|user", "content":"..."}, ...]。
    passages仅含id/source/text，不包含答案或条件标记。
    必须请求JSON对象: {"answer": "简短答案", "citations": ["P..."]}。
    prompt需由本人设计、核查、解释。"""
    # ——第一版正式实现：全篇阅读 + 跨段整合 + 证据不足规则——
    lines = []
    for p in passages:
        lines.append("[" + p["id"] + "] " + p["text"])
    user_content = (
        "问题：" + question + "\n\n资料：\n" + "\n\n".join(lines)
        + "\n\n要求：\n"
        + "1. 先通读全部资料，找出与问题直接相关的段落，允许跨段落组合信息后计算；\n"
        + "2. 答案必须能从资料推出，资料不足以推出答案时answer返回“证据不足”，citations留空；\n"
        + "3. 引用中的段落ID必须来自上面资料，不得自创；\n"
        + "4. 只输出JSON：{\"answer\": \"简短答案\", \"citations\": [\"段落ID\"]}"
    )
    return [
        {"role": "system", "content": "你是文档核验助手。只依据所给资料作答，引用必须使用资料中的段落ID；资料不足以推出答案时返回“证据不足”；绝不编造事实。"},
        {"role": "user", "content": user_content},
    ]


def improve(question, passages):
    """返回重新组织/选择的原段落列表，不能修改id/source/text或使用答案标签。
    改进v5（双段聚焦·记录优先）：保留排序后前2段——记录段与规则/口径段，
    且记录段排第1、规则/口径段排第2，让模型先读证据数字、再读判定规则。
    该组织方式同时缓解计算聚焦（T06类）与顺序干扰（T01/T07类）。
    不调用模型，仅重排与选择原段落。"""
    ents = set()
    pats = [
        r'([\u4e00-\u9fff]{2,3}项目R\d版本)',
        r'(20\d\d-\d{2})',
        r'([A-Z]{2}\d+)',
        r'(完整支持率|技术失败率|支持率|release_snapshot|selected_snapshot|快照|核验率|配置|流程甲|流程乙|流程丙)',
    ]
    for pat in pats:
        for m in re.finditer(pat, question):
            g = m.group(1)
            if g:
                ents.add(g)

    def score(p):
        text = p['text']
        s = sum(1 for e in ents if e in text)
        first = text.split('：')[0][:40]
        if '的记录' in first:
            s += 6          # 记录段（证据数字）最高优先
        elif '复核补页' in first or '规则' in first or '口径' in first:
            s += 5          # 规则/口径段次之
        elif '批次' in first:
            s += 1
        return s

    ordered = sorted(passages, key=score, reverse=True)
    return ordered[:2]
