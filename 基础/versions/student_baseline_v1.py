"""待候选人实现。避免读取dev_answers或题号/condition来构造答案。"""


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
    默认恒等映射仅用于联通，不算已完成改进。可自行扩展结构/调用，须披露与记录。"""
    return passages
