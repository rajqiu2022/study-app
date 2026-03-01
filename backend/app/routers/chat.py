import json
import re
import traceback
import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from ..database import get_db
from ..models import LearningRecord, WrongQuestion, Subject, LLMConfig
from ..schemas import ChatMessage, ChatResponse
from ..llm_service import call_llm, get_llm_config_with_iflow

router = APIRouter()

SUBJECT_NAMES = {"math": "数学", "chinese": "语文", "english": "英语", "science": "科学"}


async def web_search(query: str, max_results: int = 5) -> str:
    """使用 DuckDuckGo 进行联网搜索，返回摘要文本"""
    try:
        # DuckDuckGo HTML 搜索（轻量级，不需要 API key）
        search_url = "https://html.duckduckgo.com/html/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.post(search_url, data={"q": query}, headers=headers)
            resp.raise_for_status()
            html = resp.text

        # 简单解析搜索结果
        results = []
        # 提取结果片段
        snippets = re.findall(r'class="result__snippet">(.*?)</a>', html, re.DOTALL)
        titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)

        for i, (title, snippet) in enumerate(zip(titles, snippets)):
            if i >= max_results:
                break
            # 清理 HTML 标签
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            clean_snippet = re.sub(r'<[^>]+>', '', snippet).strip()
            if clean_title and clean_snippet:
                results.append(f"{i+1}. {clean_title}\n   {clean_snippet}")

        if results:
            return "\n\n".join(results)

        # 备用方案：DuckDuckGo Instant Answer API
        api_url = "https://api.duckduckgo.com/"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(api_url, params={"q": query, "format": "json", "no_html": 1})
            data = resp.json()

        parts = []
        if data.get("AbstractText"):
            parts.append(f"概述：{data['AbstractText']}")
        if data.get("RelatedTopics"):
            for topic in data["RelatedTopics"][:max_results]:
                if isinstance(topic, dict) and topic.get("Text"):
                    parts.append(f"- {topic['Text']}")

        return "\n".join(parts) if parts else ""

    except Exception as e:
        print(f"[WEB SEARCH ERROR] {e}")
        traceback.print_exc()
        return ""


def _build_chat_system_prompt(user_grade: str = "三年级", has_search: bool = False) -> str:
    """构建聊天系统提示词"""
    base = f"""你是一个友善、专业的小学学业辅导助手，正在和一名{user_grade}的小学生对话。

你的职责：
1. 友善地回答学习相关的问题，用通俗易懂的语言讲解知识
2. 鼓励和引导学生学习，语气亲切，适当使用emoji
3. 如果学生告诉你学了什么内容，帮助他总结和巩固
4. 如果学生说做错了题，帮助分析错误原因并讲解
5. 如果学生想做练习，引导他去「智能练习」页面
6. 可以回答语文、数学、英语、科学等小学科目的问题

注意事项：
- 回答要简洁明了，适合小学生理解
- 不要回答与学习无关的不当内容
- 如果涉及到具体题目讲解，要分步骤解释
- 回复不要太长，控制在200字以内"""

    if has_search:
        base += """

联网搜索已开启。你会收到来自网络搜索的参考资料，请：
- 结合搜索结果回答问题，使内容更准确、更丰富
- 用适合小学生的语言重新组织搜索到的信息
- 如果搜索结果与问题无关，就忽略它，用自己的知识回答
- 不要直接照搬搜索结果，要用自己的话总结"""

    return base


def _build_chat_prompt(message: str, records_context: str, wrong_context: str, search_results: str = "") -> str:
    """构建用户消息 prompt，带上学习数据上下文"""
    parts = []
    if search_results:
        parts.append(f"[联网搜索结果]\n{search_results}")
    if records_context:
        parts.append(f"[该学生近期学习记录]\n{records_context}")
    if wrong_context:
        parts.append(f"[该学生近期错题]\n{wrong_context}")

    if parts:
        context = "\n\n".join(parts)
        return f"{context}\n\n[学生说] {message}"
    return message


async def ai_chat(message: str, user_id: str, db: Session, llm_config, enable_search: bool = False) -> str | None:
    """使用大模型进行智能对话"""
    try:
        # 获取用户年级
        from ..models import User
        user = db.query(User).filter(User.id == user_id).first()
        grade = user.grade if user else "三年级"

        # 获取近期学习记录作为上下文（最近10条）
        records = (
            db.query(LearningRecord)
            .filter(LearningRecord.user_id == user_id)
            .order_by(LearningRecord.study_date.desc())
            .limit(10)
            .all()
        )
        records_context = ""
        if records:
            mastery_text = {1: "未掌握", 2: "需加强", 3: "一般", 4: "熟练", 5: "精通"}
            lines = [f"- {r.knowledge_point}（{mastery_text.get(r.mastery_level, '一般')}）" for r in records if r.knowledge_point]
            if lines:
                records_context = "\n".join(lines[:8])

        # 获取近期错题作为上下文（最近5条未解决的）
        wrong_qs = (
            db.query(WrongQuestion)
            .filter(WrongQuestion.user_id == user_id, WrongQuestion.is_resolved == False)
            .order_by(WrongQuestion.mistake_date.desc())
            .limit(5)
            .all()
        )
        wrong_context = ""
        if wrong_qs:
            lines = [f"- {wq.knowledge_point}: {wq.question_content[:60]}" for wq in wrong_qs if wq.knowledge_point]
            if lines:
                wrong_context = "\n".join(lines)

        # 联网搜索
        search_results = ""
        if enable_search:
            search_results = await web_search(message)

        system_prompt = _build_chat_system_prompt(grade, has_search=bool(search_results))
        user_prompt = _build_chat_prompt(message, records_context, wrong_context, search_results)

        # 调用大模型
        response = await _call_llm_chat(
            llm_config=llm_config,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
        return response
    except Exception as e:
        print(f"[AI CHAT ERROR] {e}")
        traceback.print_exc()
        return None


async def _call_llm_chat(llm_config, system_prompt: str, user_prompt: str) -> str:
    """调用大模型进行对话（自定义 system prompt）"""
    provider = llm_config.provider
    api_url = llm_config.api_url.rstrip("/")
    api_key = llm_config.api_key
    model_name = llm_config.model_name

    if provider == "ollama":
        if not api_url.endswith("/api/generate") and not api_url.endswith("/api/chat"):
            api_url += "/api/chat"
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(api_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "") or data.get("response", "")
    else:
        # OpenAI 兼容接口
        if not api_url.endswith("/chat/completions"):
            if api_url.endswith("/completions"):
                pass
            elif api_url.endswith("/v1") or api_url.endswith("/v4"):
                api_url += "/chat/completions"
            else:
                api_url += "/v1/chat/completions"

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 1024,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(api_url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]


def parse_intent(message: str, subjects: list):
    """简单的意图识别（不依赖AI API）"""
    msg = message.lower()

    # 识别学科
    subject_id = None
    subject_name = ""
    for s in subjects:
        if s.name in message:
            subject_id = s.id
            subject_name = s.name
            break

    # 识别意图
    if any(kw in msg for kw in ["出题", "练习", "做题", "训练", "测试"]):
        num_match = re.search(r"(\d+)\s*道", message)
        count = int(num_match.group(1)) if num_match else 5
        return "practice", {
            "subject_id": subject_id or "math",
            "count": count,
            "knowledge_point": extract_knowledge(message),
        }

    elif any(kw in msg for kw in ["做错", "错题", "错了", "不会做"]):
        return "wrong_question", {
            "subject_id": subject_id or "math",
            "content": message,
            "knowledge_point": extract_knowledge(message),
        }

    elif any(kw in msg for kw in ["学了", "学习了", "复习了", "看了", "练了"]):
        mastery = 3
        if any(kw in msg for kw in ["不会", "不懂", "记不住", "不熟"]):
            mastery = 1
        elif any(kw in msg for kw in ["还行", "一般", "差不多"]):
            mastery = 3
        elif any(kw in msg for kw in ["会了", "掌握", "熟练", "没问题"]):
            mastery = 5
        return "learning_record", {
            "subject_id": subject_id or "math",
            "knowledge_point": extract_knowledge(message),
            "mastery_level": mastery,
        }

    elif any(kw in msg for kw in ["薄弱", "弱项", "哪里不好", "什么不会", "分析"]):
        return "analysis", {"subject_id": subject_id}

    else:
        return "chat", {"message": message}


def extract_knowledge(message: str) -> str:
    """从消息中提取知识点关键词"""
    stop_words = ["我", "今天", "学了", "学习了", "做错了", "帮我", "生成", "道", "题", "关于", "的", "了", "但是", "总是", "还是"]
    result = message
    for w in stop_words:
        result = result.replace(w, " ")
    parts = [p.strip() for p in result.split() if len(p.strip()) >= 2]
    return parts[0] if parts else ""


@router.post("/", response_model=ChatResponse)
async def chat(data: ChatMessage, db: Session = Depends(get_db)):
    subjects = db.query(Subject).all()
    intent, params = parse_intent(data.message, subjects)
    enable_search = data.web_search

    # 对于有明确系统操作的意图（记录学习、记录错题、出题、分析），先执行操作
    if intent == "learning_record":
        record = LearningRecord(
            user_id=data.user_id,
            subject_id=params["subject_id"],
            knowledge_point=params["knowledge_point"] or data.message,
            study_date=date.today(),
            mastery_level=params["mastery_level"],
        )
        db.add(record)
        db.commit()

        mastery_text = {1: "未掌握", 2: "需加强", 3: "一般", 4: "熟练", 5: "精通"}
        default_reply = f"已记录！学习内容：{params['knowledge_point'] or data.message}，掌握程度：{mastery_text.get(params['mastery_level'], '一般')}。继续加油哦！💪"

        llm_config = get_llm_config_with_iflow(db)
        if llm_config and llm_config.api_url and llm_config.api_key:
            ai_reply = await ai_chat(
                f"学生说：{data.message}\n\n系统已自动记录了这条学习内容。请你：1）确认已记录，2）对这个知识点给出简短的学习建议或鼓励",
                data.user_id, db, llm_config, enable_search,
            )
            if ai_reply:
                return ChatResponse(reply=f"✅ 已记录学习内容！\n\n{ai_reply}", action="created_learning_record")

        return ChatResponse(reply=default_reply, action="created_learning_record")

    elif intent == "wrong_question":
        wq = WrongQuestion(
            user_id=data.user_id,
            subject_id=params["subject_id"],
            knowledge_point=params.get("knowledge_point", ""),
            question_content=data.message,
            mistake_date=date.today(),
        )
        db.add(wq)
        db.commit()

        default_reply = f"已记录到错题本！知识点：{params.get('knowledge_point', '待分类')}。建议过几天复习一下哦！📝"

        llm_config = get_llm_config_with_iflow(db)
        if llm_config and llm_config.api_url and llm_config.api_key:
            ai_reply = await ai_chat(
                f"学生说做错了题目：{data.message}\n\n系统已自动添加到错题本。请你：1）确认已记录，2）简要分析可能的错误原因，3）给出改进建议",
                data.user_id, db, llm_config, enable_search,
            )
            if ai_reply:
                return ChatResponse(reply=f"📝 已添加到错题本！\n\n{ai_reply}", action="created_wrong_question")

        return ChatResponse(reply=default_reply, action="created_wrong_question")

    elif intent == "practice":
        count = params.get("count", 5)
        kp = params.get("knowledge_point", "")
        return ChatResponse(
            reply=f"好的！正在为你生成{count}道{kp}相关的练习题，请到「智能练习」页面查看！🎯",
            action="redirect_practice",
            data={"subject_id": params["subject_id"], "knowledge_point": kp, "count": count},
        )

    elif intent == "analysis":
        records = (
            db.query(LearningRecord)
            .filter(LearningRecord.user_id == data.user_id, LearningRecord.mastery_level <= 2)
            .all()
        )
        wrong_qs = (
            db.query(WrongQuestion)
            .filter(WrongQuestion.user_id == data.user_id, WrongQuestion.is_resolved == False)
            .all()
        )
        weak_points = list(set([r.knowledge_point for r in records]))
        wrong_points = list(set([w.knowledge_point for w in wrong_qs if w.knowledge_point]))

        llm_config = get_llm_config_with_iflow(db)
        if llm_config and llm_config.api_url and llm_config.api_key:
            analysis_msg = f"请分析这个学生的学习情况并给出建议。\n薄弱知识点：{', '.join(weak_points[:10]) if weak_points else '暂无'}\n未解决错题知识点：{', '.join(wrong_points[:10]) if wrong_points else '暂无'}"
            ai_reply = await ai_chat(analysis_msg, data.user_id, db, llm_config, enable_search)
            if ai_reply:
                return ChatResponse(reply=f"📊 学习分析报告：\n\n{ai_reply}", action="analysis")

        reply = "📊 学习分析报告：\n"
        if weak_points:
            reply += f"\n⚠️ 薄弱知识点({len(weak_points)}个)：\n" + "\n".join(f"  - {p}" for p in weak_points[:10])
        if wrong_points:
            reply += f"\n\n❌ 未解决错题相关({len(wrong_points)}个)：\n" + "\n".join(f"  - {p}" for p in wrong_points[:10])
        if not weak_points and not wrong_points:
            reply += "\n目前没有发现薄弱环节，继续保持！🌟"
        reply += "\n\n建议针对薄弱知识点多做练习哦！"
        return ChatResponse(reply=reply, action="analysis")

    else:
        # 通用对话：优先用 AI 回复
        llm_config = get_llm_config_with_iflow(db)
        if llm_config and llm_config.api_url and llm_config.api_key:
            ai_reply = await ai_chat(data.message, data.user_id, db, llm_config, enable_search)
            if ai_reply:
                return ChatResponse(reply=ai_reply)

        # 回退到规则回复
        return ChatResponse(
            reply="我是你的学习小助手！你可以告诉我：\n"
                  "📚 「我今天学了XXX」- 记录学习内容\n"
                  "❌ 「XX题做错了」- 添加错题\n"
                  "🎯 「帮我出5道XX题」- 生成练习\n"
                  "📊 「分析我的薄弱点」- 查看学习分析",
        )
