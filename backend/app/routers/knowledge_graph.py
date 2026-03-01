import json
import traceback
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import LearningRecord, WrongQuestion, LLMConfig, Subject
from ..llm_service import call_llm, build_knowledge_graph_prompt, get_llm_config_with_iflow

router = APIRouter()

SUBJECT_NAMES = {"math": "数学", "chinese": "语文", "english": "英语", "science": "科学"}


@router.get("/")
async def get_knowledge_graph(
    user_id: str = Query(...),
    subject_id: str = Query(None),
    db: Session = Depends(get_db),
):
    """获取用户的知识图谱（由AI根据学习数据生成）"""
    # 查询学习记录
    q = db.query(LearningRecord).filter(LearningRecord.user_id == user_id)
    if subject_id:
        q = q.filter(LearningRecord.subject_id == subject_id)
    records = q.order_by(LearningRecord.study_date.desc()).limit(50).all()

    # 查询错题
    wq = db.query(WrongQuestion).filter(WrongQuestion.user_id == user_id)
    if subject_id:
        wq = wq.filter(WrongQuestion.subject_id == subject_id)
    wrong_questions = wq.order_by(WrongQuestion.mistake_date.desc()).limit(30).all()

    if not records and not wrong_questions:
        return {
            "success": True,
            "has_data": False,
            "message": "还没有学习记录和错题数据，开始学习后就能生成知识图谱啦！",
            "graph": None,
        }

    # 准备数据
    records_data = [
        {"knowledge_point": r.knowledge_point, "mastery_level": r.mastery_level,
         "subject_id": r.subject_id, "notes": (r.notes or "")[:100]}
        for r in records if r.knowledge_point
    ]
    wrong_data = [
        {"knowledge_point": wq_item.knowledge_point, "question_content": wq_item.question_content[:100],
         "is_resolved": wq_item.is_resolved, "subject_id": wq_item.subject_id}
        for wq_item in wrong_questions if wq_item.knowledge_point
    ]

    # 无AI时构建基础图谱（使用全局配置，自动同步iFlow）
    llm_config = get_llm_config_with_iflow(db)

    subject_name = SUBJECT_NAMES.get(subject_id, "") if subject_id else ""

    if llm_config and llm_config.api_url and llm_config.api_key:
        # 用AI生成知识图谱
        prompt = build_knowledge_graph_prompt(records_data, wrong_data, subject_name)
        try:
            response = await call_llm(
                provider=llm_config.provider,
                api_url=llm_config.api_url,
                api_key=llm_config.api_key,
                model_name=llm_config.model_name,
                prompt=prompt,
                deep_thinking=llm_config.deep_thinking,
            )
            graph = _parse_graph_json(response)
            if graph:
                return {"success": True, "has_data": True, "graph": graph, "ai_generated": True}
        except Exception as e:
            print(f"[KNOWLEDGE GRAPH ERROR] {e}")
            traceback.print_exc()

    # 回退：基于数据自动生成简单图谱
    graph = _build_simple_graph(records_data, wrong_data)
    return {"success": True, "has_data": True, "graph": graph, "ai_generated": False}


def _parse_graph_json(response: str) -> dict | None:
    """解析AI返回的知识图谱JSON"""
    try:
        text = response.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            data = json.loads(text[start:end + 1])
            if "nodes" in data:
                return data
    except Exception:
        pass
    return None


def _build_simple_graph(records: list, wrong_questions: list) -> dict:
    """基于数据自动构建简单知识图谱（无AI回退方案）"""
    kp_map = {}  # knowledge_point -> {mastery, wrong_count, category}

    for r in records:
        kp = r.get("knowledge_point", "")
        if not kp:
            continue
        if kp not in kp_map:
            kp_map[kp] = {"mastery": r.get("mastery_level", 3), "wrong_count": 0,
                           "category": SUBJECT_NAMES.get(r.get("subject_id", ""), "其他")}
        else:
            kp_map[kp]["mastery"] = max(kp_map[kp]["mastery"], r.get("mastery_level", 3))

    for wq in wrong_questions:
        kp = wq.get("knowledge_point", "")
        if not kp:
            continue
        if kp not in kp_map:
            kp_map[kp] = {"mastery": 1, "wrong_count": 1,
                           "category": SUBJECT_NAMES.get(wq.get("subject_id", ""), "其他")}
        else:
            kp_map[kp]["wrong_count"] = kp_map[kp].get("wrong_count", 0) + 1

    nodes = []
    for i, (kp, info) in enumerate(kp_map.items()):
        importance = "high" if info["wrong_count"] > 0 or info["mastery"] <= 2 else (
            "medium" if info["mastery"] <= 3 else "low"
        )
        nodes.append({
            "id": f"kp_{i}",
            "name": kp,
            "category": info["category"],
            "mastery": info["mastery"],
            "importance": importance,
            "related_wrong_count": info["wrong_count"],
        })

    # 同类别节点建立关联
    links = []
    categories = {}
    for node in nodes:
        cat = node["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(node["id"])

    for cat, node_ids in categories.items():
        for j in range(len(node_ids) - 1):
            links.append({
                "source": node_ids[j],
                "target": node_ids[j + 1],
                "relation": "相关知识",
            })

    # 生成建议
    suggestions = []
    weak = [n for n in nodes if n["mastery"] <= 2]
    wrong = [n for n in nodes if n["related_wrong_count"] > 0]
    if weak:
        suggestions.append(f"建议重点复习：{'、'.join(n['name'] for n in weak[:5])}")
    if wrong:
        suggestions.append(f"以下知识点有错题需要巩固：{'、'.join(n['name'] for n in wrong[:5])}")
    if not suggestions:
        suggestions.append("学习情况良好，继续保持！")

    return {
        "summary": f"共记录了{len(nodes)}个知识点" + (f"，其中{len(weak)}个需要加强" if weak else ""),
        "nodes": nodes,
        "links": links,
        "suggestions": suggestions,
    }
