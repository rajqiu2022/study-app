"""
大模型调用服务，支持 OpenAI 兼容接口和 Ollama
支持 iFlow CLI 自动续期 API Key
"""
import json
import os
import re
import httpx

SUBJECT_NAMES = {"math": "数学", "chinese": "语文", "english": "英语", "science": "科学"}

# iFlow 配置文件路径
IFLOW_SETTINGS_PATH = os.path.expanduser("~/.iflow/settings.json")


def get_iflow_config() -> dict | None:
    """
    从 iFlow CLI 的 settings.json 读取最新配置（API Key 自动续期）。
    返回 {"api_key": ..., "base_url": ..., "model_name": ...} 或 None
    """
    try:
        if not os.path.exists(IFLOW_SETTINGS_PATH):
            return None
        with open(IFLOW_SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        api_key = data.get("apiKey") or data.get("api_key")
        base_url = data.get("baseUrl") or data.get("base_url")
        model_name = data.get("modelName") or data.get("model_name")
        if api_key and base_url:
            return {"api_key": api_key, "base_url": base_url, "model_name": model_name or ""}
        return None
    except Exception:
        return None


def sync_iflow_to_db(db) -> bool:
    """
    检查 iFlow 配置，如果有效则自动同步 API Key 和 Base URL 到数据库。
    注意：只同步 Key 和 URL，不覆盖用户手动设置的模型名。
    返回是否成功同步。
    """
    from .models import LLMConfig
    iflow = get_iflow_config()
    if not iflow:
        return False

    try:
        config = db.query(LLMConfig).filter(LLMConfig.user_id == "__global__").first()
        if config:
            # 仅当 Key 变化时才更新（iFlow 续期后 Key 会变）
            if config.api_key != iflow["api_key"]:
                config.api_key = iflow["api_key"]
                config.api_url = iflow["base_url"]
                # 不覆盖用户手动设置的模型名
                config.provider = "openai"
                config.enabled = True
                db.commit()
                print(f"[iFlow] API Key 已自动同步更新")
        else:
            # 全局配置不存在，自动创建（使用 iFlow 平台实际可用的模型）
            config = LLMConfig(
                user_id="__global__",
                provider="openai",
                api_url=iflow["base_url"],
                api_key=iflow["api_key"],
                model_name="qwen3-max",
                enabled=True,
            )
            db.add(config)
            db.commit()
            print(f"[iFlow] 已自动创建全局大模型配置")
        return True
    except Exception as e:
        print(f"[iFlow] 同步失败: {e}")
        return False


def get_llm_config_with_iflow(db):
    """
    获取全局 LLM 配置，优先从 iFlow 同步最新 Key。
    所有需要获取 LLM 配置的地方应使用此函数。
    """
    from .models import LLMConfig
    # 先尝试同步 iFlow 配置
    sync_iflow_to_db(db)
    # 返回数据库中的全局配置
    config = db.query(LLMConfig).filter(
        LLMConfig.user_id == "__global__", LLMConfig.enabled == True
    ).first()
    return config


async def call_llm(
    provider: str,
    api_url: str,
    api_key: str,
    model_name: str,
    prompt: str,
    timeout: float = 180.0,
    deep_thinking: bool = False,
) -> str:
    """
    调用大模型获取文本回复
    provider: "openai" 或 "ollama"
    deep_thinking: 是否启用深度思考模式
    """
    if provider == "ollama":
        return await _call_ollama(api_url, model_name, prompt, timeout)
    else:
        return await _call_openai_compatible(api_url, api_key, model_name, prompt, timeout, deep_thinking)


async def _call_openai_compatible(api_url: str, api_key: str, model_name: str, prompt: str, timeout: float, deep_thinking: bool = False) -> str:
    """调用 OpenAI 兼容接口（支持 OpenAI / DeepSeek / 通义千问 / Moonshot 等）"""
    # 规范化 URL：确保以 /chat/completions 结尾
    url = api_url.rstrip("/")
    if not url.endswith("/chat/completions"):
        if url.endswith("/completions"):
            pass  # 已经是 completions 结尾
        elif url.endswith("/v1") or url.endswith("/v4"):
            url += "/chat/completions"
        else:
            url += "/v1/chat/completions"

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    system_content = "你是一个小学学业辅导助手，专门为小学生出题和讲解知识。"
    if deep_thinking:
        system_content += "请深入思考每道题目，确保题目质量高、知识点准确、难度梯度合理，并仔细验证答案的正确性。"

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 4096,
    }

    # 深度思考模式：降低温度以获得更严谨的输出，增加 token 限制
    if deep_thinking:
        payload["temperature"] = 0.3
        payload["max_tokens"] = 8192

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def _call_ollama(api_url: str, model_name: str, prompt: str, timeout: float) -> str:
    """调用 Ollama 本地接口"""
    url = api_url.rstrip("/")
    if not url.endswith("/api/generate") and not url.endswith("/api/chat"):
        url += "/api/chat"

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "你是一个小学学业辅导助手，专门为小学生出题和讲解知识。"},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "") or data.get("response", "")


def build_practice_prompt(
    subject_id: str, knowledge_point: str, count: int, grade: str = "三年级",
    weak_points: list = None, wrong_questions: list = None,
) -> str:
    """构建出题 prompt，融合用户知识库数据"""
    subject_name = SUBJECT_NAMES.get(subject_id, "数学")
    kp_text = f"，知识点：{knowledge_point}" if knowledge_point else ""

    # 构建知识库上下文
    context_parts = []
    if weak_points:
        context_parts.append(f"该学生的薄弱知识点：{'、'.join(weak_points[:10])}")
    if wrong_questions:
        wq_list = []
        for wq in wrong_questions[:8]:
            wq_desc = f"  - {wq.get('knowledge_point', '未分类')}: {wq.get('question', '')[:60]}"
            if wq.get("correct_answer"):
                wq_desc += f"（正确答案：{wq['correct_answer']}）"
            wq_list.append(wq_desc)
        context_parts.append(f"该学生最近做错的题目：\n" + "\n".join(wq_list))

    context_text = ""
    if context_parts:
        context_text = f"""

以下是该学生的学习情况，请根据这些信息针对性出题，重点考查薄弱环节：
{chr(10).join(context_parts)}
"""

    return f"""请为{grade}小学生出{count}道{subject_name}题目{kp_text}。{context_text}
要求：
1. 题目难度适合小学{grade}学生
2. 题型可以混合（选择题、填空题、判断题等）
3. 每道题必须有明确的正确答案
4. 如果有薄弱知识点信息，请重点围绕这些知识点出题

请严格按照以下JSON格式返回，不要返回任何其他内容：
```json
[
  {{
    "question": "题目内容",
    "type": "选择题/填空题/判断题",
    "options": ["选项1", "选项2", "选项3", "选项4"],
    "answer": "正确答案"
  }}
]
```

注意：
- 选择题必须有 options 字段（4个选项），选项内容不要带A/B/C/D序号前缀
- 判断题的 options 设为 ["对", "错"]，answer 填写 "对" 或 "错"
- 填空题的 options 设为 null
- answer 字段填写正确答案的文本
- 只返回JSON数组，不要有其他文字"""


def build_knowledge_graph_prompt(records: list, wrong_questions: list, subject_name: str = "") -> str:
    """构建知识图谱生成 prompt"""
    context_parts = []

    if records:
        rec_list = []
        for r in records[:30]:
            mastery_text = {1: "未掌握", 2: "需加强", 3: "一般", 4: "熟练", 5: "精通"}
            rec_list.append(f"  - {r.get('knowledge_point', '')} (掌握度:{mastery_text.get(r.get('mastery_level', 3), '一般')})")
        context_parts.append("学习记录：\n" + "\n".join(rec_list))

    if wrong_questions:
        wq_list = []
        for wq in wrong_questions[:20]:
            resolved = "已解决" if wq.get("is_resolved") else "未解决"
            wq_list.append(f"  - [{resolved}] {wq.get('knowledge_point', '未分类')}: {wq.get('question_content', '')[:50]}")
        context_parts.append("错题记录：\n" + "\n".join(wq_list))

    subject_filter = f"（{subject_name}学科）" if subject_name else ""

    return f"""请根据以下学生的学习数据{subject_filter}，整理出一份知识图谱。

{chr(10).join(context_parts)}

请按以下JSON格式返回知识图谱，不要返回其他内容：
```json
{{
  "summary": "整体学习情况总结（2-3句话）",
  "nodes": [
    {{
      "id": "唯一标识",
      "name": "知识点名称",
      "category": "分类（如：计算、几何、阅读等）",
      "mastery": 1到5的掌握程度,
      "importance": "high/medium/low",
      "related_wrong_count": 相关错题数量
    }}
  ],
  "links": [
    {{
      "source": "源节点id",
      "target": "目标节点id",
      "relation": "关系描述（如：前置知识、相关知识、进阶知识）"
    }}
  ],
  "suggestions": [
    "学习建议1",
    "学习建议2",
    "学习建议3"
  ]
}}
```

要求：
- 合并相似的知识点，整理为结构化的知识节点
- 建立知识点之间的逻辑关系
- 标注每个知识点的掌握程度和重要性
- 给出针对性的学习建议
- 只返回JSON，不要有其他文字"""


def parse_llm_questions(llm_response: str, count: int) -> list | None:
    """
    解析大模型返回的题目JSON
    返回标准格式的题目列表，解析失败返回 None
    """
    try:
        # 尝试提取 JSON 部分
        text = llm_response.strip()

        # 去掉 markdown 代码块
        if "```json" in text:
            text = text.split("```json")[1]
            if "```" in text:
                text = text.split("```")[0]
        elif "```" in text:
            parts = text.split("```")
            if len(parts) >= 2:
                text = parts[1]

        # 找到 JSON 数组
        start = text.find("[")
        end = text.rfind("]")
        if start == -1 or end == -1:
            return None
        text = text[start:end + 1]

        raw_questions = json.loads(text)
        if not isinstance(raw_questions, list):
            return None

        questions = []
        for i, q in enumerate(raw_questions[:count]):
            options = q.get("options")
            if isinstance(options, list) and len(options) > 0:
                # 清理选项中的序号前缀，如 "A.xxx"、"A、xxx"、"A) xxx"
                options = [re.sub(r'^[A-Da-d][.、.\s)\]】]+\s*', '', str(opt)) for opt in options]
                q_type = "选择题"
            else:
                options = None
                q_type = q.get("type", "填空题")
                if "判断" in q_type:
                    q_type = "判断题"
                elif "填空" in q_type:
                    q_type = "填空题"
                else:
                    q_type = "填空题"

            questions.append({
                "index": i + 1,
                "question": q.get("question", ""),
                "type": q_type,
                "options": options,
                "answer": str(q.get("answer", "")),
                "user_answer": "",
                "is_correct": None,
            })

        return questions if questions else None

    except (json.JSONDecodeError, KeyError, TypeError, IndexError):
        return None
