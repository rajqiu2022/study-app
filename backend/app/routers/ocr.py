import os
import uuid
import re
import base64
import traceback
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import date

from ..database import get_db
from ..models import WrongQuestion, LearningRecord, Subject, LLMConfig
from ..llm_service import get_llm_config_with_iflow

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def ai_ocr(image_path: str, llm_config) -> str:
    """使用 AI 大模型的视觉能力识别图片内容"""
    import httpx

    # 读取图片并转为 base64
    with open(image_path, "rb") as f:
        img_data = f.read()
    ext = os.path.splitext(image_path)[1].lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
                ".gif": "image/gif", ".webp": "image/webp", ".bmp": "image/bmp"}
    mime = mime_map.get(ext, "image/jpeg")
    b64 = base64.b64encode(img_data).decode("utf-8")

    # 构建 API 请求
    url = llm_config.api_url.rstrip("/")
    if not url.endswith("/chat/completions"):
        if url.endswith("/v1") or url.endswith("/v4"):
            url += "/chat/completions"
        else:
            url += "/v1/chat/completions"

    headers = {"Content-Type": "application/json"}
    if llm_config.api_key:
        headers["Authorization"] = f"Bearer {llm_config.api_key}"

    # 选择视觉模型：自动映射到支持图片输入的模型
    model = llm_config.model_name
    # 智谱GLM视觉模型映射
    if "glm-4" in model and "v" not in model:
        model = "glm-4v-flash"
    # 通义千问视觉模型映射
    elif "qwen" in model.lower() and "vl" not in model.lower():
        model = "qwen3-vl-plus"
    # DeepSeek 不支持视觉，回退到 qwen3-vl-plus
    elif "deepseek" in model.lower():
        model = "qwen3-vl-plus"
    # Kimi 视觉模型映射
    elif "kimi" in model.lower() and "vision" not in model.lower():
        model = "kimi-k2"  # kimi-k2 支持多模态

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"},
                    },
                    {
                        "type": "text",
                        "text": "请仔细识别这张图片中的所有文字内容，包括题目、选项、公式、手写文字等。"
                              "请按原始格式完整输出识别到的文字内容，不要做任何总结或分析。"
                              "如果有数学公式请用文字描述。如果图片中没有文字，请描述图片的主要内容。",
                    },
                ],
            }
        ],
        "max_tokens": 2048,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def ai_analyze_image(image_path: str, llm_config, user_note: str = "", action: str = "wrong_question") -> dict:
    """使用 AI 分析图片内容，提取知识点和结构化信息"""
    import httpx

    with open(image_path, "rb") as f:
        img_data = f.read()
    ext = os.path.splitext(image_path)[1].lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
                ".gif": "image/gif", ".webp": "image/webp", ".bmp": "image/bmp"}
    mime = mime_map.get(ext, "image/jpeg")
    b64 = base64.b64encode(img_data).decode("utf-8")

    url = llm_config.api_url.rstrip("/")
    if not url.endswith("/chat/completions"):
        if url.endswith("/v1") or url.endswith("/v4"):
            url += "/chat/completions"
        else:
            url += "/v1/chat/completions"

    headers = {"Content-Type": "application/json"}
    if llm_config.api_key:
        headers["Authorization"] = f"Bearer {llm_config.api_key}"

    model = llm_config.model_name
    if "glm-4" in model and "v" not in model:
        model = "glm-4v-flash"
    elif "qwen" in model.lower() and "vl" not in model.lower():
        model = "qwen3-vl-plus"
    elif "deepseek" in model.lower():
        model = "qwen3-vl-plus"
    elif "kimi" in model.lower() and "vision" not in model.lower():
        model = "kimi-k2"

    note_text = f"\n用户补充说明：{user_note}" if user_note else ""
    if action == "wrong_question":
        analysis_prompt = f"""请分析这张图片中的题目内容。{note_text}

请按以下JSON格式返回，不要返回其他内容：
```json
{{
  "ocr_text": "图片中完整的文字内容",
  "subject": "学科（数学/语文/英语/科学）",
  "knowledge_point": "涉及的核心知识点（如：分数加减法、古诗默写等）",
  "question": "题目内容的整理版本",
  "correct_answer": "正确答案（如果能判断的话）",
  "error_analysis": "错误原因分析和建议"
}}
```"""
    else:
        analysis_prompt = f"""请分析这张图片中的学习内容。{note_text}

请按以下JSON格式返回，不要返回其他内容：
```json
{{
  "ocr_text": "图片中完整的文字内容",
  "subject": "学科（数学/语文/英语/科学）",
  "knowledge_point": "涉及的核心知识点",
  "summary": "知识点的简要总结",
  "key_concepts": ["关键概念1", "关键概念2"],
  "mastery_suggestion": "建议掌握程度（1-5，1=需重点学习，5=已熟练）"
}}
```"""

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    {"type": "text", "text": analysis_prompt},
                ],
            }
        ],
        "max_tokens": 2048,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]

    # 解析 JSON
    import json
    try:
        text = content.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end + 1])
    except Exception:
        pass
    return {"ocr_text": content, "knowledge_point": "", "subject": ""}


def try_ocr(image_path: str) -> str:
    """尝试用 pytesseract 做 OCR 作为备用方案"""
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang="chi_sim+eng")
        return text.strip()
    except Exception:
        pass
    return ""


@router.post("/upload")
async def upload_image(file: UploadFile = File(...), user_id: str = Form("")):
    """上传图片，使用AI识别内容，备用pytesseract"""
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    file_id = str(uuid.uuid4())[:8]
    filename = f"{file_id}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    ocr_text = ""
    ai_used = False

    # 优先用 AI 视觉模型识别（使用全局配置，自动同步iFlow）
    from ..database import SessionLocal
    db = SessionLocal()
    try:
        llm_config = get_llm_config_with_iflow(db)
        if llm_config and llm_config.api_url and llm_config.api_key:
            try:
                ocr_text = await ai_ocr(filepath, llm_config)
                ai_used = True
            except Exception as e:
                print(f"[AI OCR ERROR] {e}")
                traceback.print_exc()
    finally:
        db.close()

    # 备用: pytesseract
    if not ocr_text:
        ocr_text = try_ocr(filepath)

    return {
        "file_id": file_id,
        "filename": filename,
        "url": f"/api/ocr/image/{filename}",
        "ocr_text": ocr_text,
        "ai_used": ai_used,
    }


@router.get("/image/{filename}")
async def get_image(filename: str):
    """获取上传的图片"""
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(404, "图片不存在")
    return FileResponse(filepath)


SUBJECT_MAP = {"数学": "math", "语文": "chinese", "英语": "english", "科学": "science"}


@router.post("/recognize-and-save")
async def recognize_and_save(
    user_id: str = Form(...),
    action: str = Form(...),
    subject_id: str = Form("math"),
    content: str = Form(""),
    image_filename: str = Form(""),
    ocr_text: str = Form(""),
    db: Session = Depends(get_db),
):
    """使用AI深度分析图片，提取知识点并保存"""
    image_url = f"/api/ocr/image/{image_filename}" if image_filename else ""
    filepath = os.path.join(UPLOAD_DIR, image_filename) if image_filename else ""

    # 尝试用 AI 深度分析图片（使用全局配置，自动同步iFlow）
    ai_analysis = None
    llm_config = get_llm_config_with_iflow(db)

    if llm_config and llm_config.api_url and llm_config.api_key and filepath and os.path.exists(filepath):
        try:
            ai_analysis = await ai_analyze_image(filepath, llm_config, content, action)
        except Exception as e:
            print(f"[AI ANALYZE ERROR] {e}")
            traceback.print_exc()

    if ai_analysis:
        final_ocr = ai_analysis.get("ocr_text", ocr_text) or ocr_text
        knowledge_point = ai_analysis.get("knowledge_point", "")
        # 自动识别学科
        ai_subject = ai_analysis.get("subject", "")
        if ai_subject and ai_subject in SUBJECT_MAP:
            subject_id = SUBJECT_MAP[ai_subject]

        if action == "wrong_question":
            question_content = ai_analysis.get("question", final_ocr) or final_ocr or "（图片题目）"
            correct_answer = ai_analysis.get("correct_answer", "")
            error_analysis = ai_analysis.get("error_analysis", "")

            wq = WrongQuestion(
                user_id=user_id,
                subject_id=subject_id,
                knowledge_point=knowledge_point,
                question_content=question_content,
                correct_answer=correct_answer,
                my_answer=f"[图片] {image_url}" if image_url else "",
                analysis=error_analysis,
                mistake_date=date.today(),
                image_url=image_url,
            )
            db.add(wq)
            db.commit()

            msg = f"已智能记录到错题本！"
            if knowledge_point:
                msg += f"\n📌 知识点：{knowledge_point}"
            if correct_answer:
                msg += f"\n✅ 正确答案：{correct_answer}"
            if error_analysis:
                msg += f"\n💡 分析：{error_analysis}"

            return {
                "success": True, "action": "wrong_question",
                "message": msg, "ocr_text": final_ocr,
                "ai_analysis": ai_analysis,
            }
        else:
            summary = ai_analysis.get("summary", "")
            key_concepts = ai_analysis.get("key_concepts", [])
            mastery = 2
            try:
                mastery = int(ai_analysis.get("mastery_suggestion", 2))
                mastery = max(1, min(5, mastery))
            except (ValueError, TypeError):
                mastery = 2

            notes_parts = []
            if final_ocr:
                notes_parts.append(final_ocr)
            if summary:
                notes_parts.append(f"AI总结：{summary}")
            if key_concepts:
                notes_parts.append(f"关键概念：{'、'.join(key_concepts)}")
            if image_url:
                notes_parts.append(image_url)

            record = LearningRecord(
                user_id=user_id,
                subject_id=subject_id,
                knowledge_point=knowledge_point or (final_ocr[:50] if final_ocr else "图片知识点"),
                study_date=date.today(),
                mastery_level=mastery,
                notes="\n".join(notes_parts),
                image_url=image_url,
            )
            db.add(record)
            db.commit()

            msg = f"已智能记录为学习知识！"
            if knowledge_point:
                msg += f"\n📌 知识点：{knowledge_point}"
            if summary:
                msg += f"\n📝 总结：{summary}"
            if key_concepts:
                msg += f"\n🔑 关键概念：{'、'.join(key_concepts)}"

            return {
                "success": True, "action": "learning_record",
                "message": msg, "ocr_text": final_ocr,
                "ai_analysis": ai_analysis,
            }
    else:
        # 回退：无AI时的原始逻辑
        full_content = ""
        if ocr_text:
            full_content = ocr_text
        if content:
            full_content = f"{content}\n---\n{full_content}" if full_content else content
        if not full_content:
            full_content = "（图片题目）"

        knowledge_point = ""
        if content:
            stop_words = ["这道题", "这题", "做错了", "不会", "记录", "帮我", "一下", "错题", "知识点"]
            kp = content
            for w in stop_words:
                kp = kp.replace(w, " ")
            parts = [p.strip() for p in kp.split() if len(p.strip()) >= 2]
            knowledge_point = parts[0] if parts else ""

        if action == "wrong_question":
            wq = WrongQuestion(
                user_id=user_id, subject_id=subject_id,
                knowledge_point=knowledge_point,
                question_content=full_content,
                my_answer=f"[图片] {image_url}" if image_url else "",
                mistake_date=date.today(),
                image_url=image_url,
            )
            db.add(wq)
            db.commit()
            return {
                "success": True, "action": "wrong_question",
                "message": f"已记录到错题本！{f'知识点：{knowledge_point}' if knowledge_point else ''}",
                "ocr_text": ocr_text,
            }
        elif action == "learning_record":
            record = LearningRecord(
                user_id=user_id, subject_id=subject_id,
                knowledge_point=knowledge_point or full_content[:50],
                study_date=date.today(), mastery_level=2,
                notes=f"{full_content}\n{image_url}" if image_url else full_content,
                image_url=image_url,
            )
            db.add(record)
            db.commit()
            return {
                "success": True, "action": "learning_record",
                "message": f"已记录为重点知识！{f'知识点：{knowledge_point}' if knowledge_point else ''}",
                "ocr_text": ocr_text,
            }
        else:
            raise HTTPException(400, "action 必须是 wrong_question 或 learning_record")
