import json
import os
import uuid
import traceback
import base64
import re
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..models import Notebook, User, Subject
from ..schemas import NotebookOut, NotebookUpdate
from ..llm_service import get_llm_config_with_iflow

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
AUDIO_DIR = os.path.join(UPLOAD_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

SUBJECT_MAP = {"数学": "math", "语文": "chinese", "英语": "english", "科学": "science"}
SUBJECT_NAMES = {"math": "数学", "chinese": "语文", "english": "英语", "science": "科学"}


async def ai_classify_note(content: str, image_paths: list, llm_config, grade: str = "三年级") -> dict:
    """用AI分析笔记内容，自动归类"""
    # 构建分析文本
    text_to_analyze = content or ""

    # 如果有图片，用视觉模型分析第一张
    image_content = None
    if image_paths:
        first_img = image_paths[0]
        if os.path.exists(first_img):
            with open(first_img, "rb") as f:
                img_data = f.read()
            ext = os.path.splitext(first_img)[1].lower()
            mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
                        ".gif": "image/gif", ".webp": "image/webp"}
            mime = mime_map.get(ext, "image/jpeg")
            b64 = base64.b64encode(img_data).decode("utf-8")
            image_content = {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}

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
    if image_content:
        if "glm-4" in model and "v" not in model:
            model = "glm-4v-flash"
        elif "qwen" in model.lower() and "vl" not in model.lower():
            model = "qwen3-vl-plus"
        elif "deepseek" in model.lower():
            model = "qwen3-vl-plus"
        elif "kimi" in model.lower() and "vision" not in model.lower():
            model = "kimi-k2"

    prompt = f"""请分析以下学生笔记内容，该学生是{grade}学生。

笔记内容：
{text_to_analyze or '（请根据图片内容分析）'}

请按以下JSON格式返回分析结果，不要返回其他内容：
```json
{{
  "title": "为这条笔记生成一个简洁的标题（10字以内）",
  "subject": "判断所属学科（数学/语文/英语/科学/综合）",
  "knowledge_points": ["知识点1", "知识点2"],
  "summary": "内容摘要（50字以内）",
  "category": "笔记类型（课堂笔记/复习总结/错题整理/公式定理/读书笔记/实验记录/词汇积累/作文素材/其他）",
  "tags": ["标签1", "标签2", "标签3"]
}}
```"""

    user_content = []
    if image_content:
        user_content.append(image_content)
    user_content.append({"type": "text", "text": prompt})

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": user_content if image_content else prompt}],
        "max_tokens": 1024,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        result_text = data["choices"][0]["message"]["content"]

    # 解析 JSON
    try:
        text = result_text.strip()
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
    return {}


@router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """上传语音文件"""
    ext = os.path.splitext(file.filename or "audio.webm")[1] or ".webm"
    file_id = str(uuid.uuid4())[:8]
    filename = f"{file_id}{ext}"
    filepath = os.path.join(AUDIO_DIR, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    return {"filename": filename, "url": f"/api/notebooks/audio/{filename}"}


@router.get("/audio/{filename}")
async def get_audio(filename: str):
    """获取语音文件"""
    filepath = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(404, "音频文件不存在")
    return FileResponse(filepath)


@router.post("/upload-image")
async def upload_note_image(file: UploadFile = File(...)):
    """上传笔记图片"""
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    file_id = str(uuid.uuid4())[:8]
    filename = f"note_{file_id}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    return {"filename": filename, "url": f"/api/ocr/image/{filename}"}


@router.post("/", response_model=NotebookOut)
async def create_notebook(
    user_id: str = Form(...),
    content: str = Form(""),
    audio_text: str = Form(""),
    image_filenames: str = Form(""),  # JSON array string
    db: Session = Depends(get_db),
):
    """创建笔记，AI自动分析归类"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "用户不存在")

    grade = user.grade or "三年级"

    # 处理图片
    img_filenames = []
    if image_filenames:
        try:
            img_filenames = json.loads(image_filenames)
        except Exception:
            if image_filenames.strip():
                img_filenames = [image_filenames.strip()]

    image_urls = [f"/api/ocr/image/{fn}" for fn in img_filenames if fn]
    image_paths = [os.path.join(UPLOAD_DIR, fn) for fn in img_filenames if fn]

    # 合并所有文字内容
    full_text = ""
    if content:
        full_text += content
    if audio_text:
        full_text += ("\n" if full_text else "") + audio_text

    # AI 归类
    ai_result = {}
    llm_config = get_llm_config_with_iflow(db)
    if llm_config and llm_config.api_url and llm_config.api_key and (full_text or image_paths):
        try:
            ai_result = await ai_classify_note(full_text, image_paths, llm_config, grade)
        except Exception as e:
            print(f"[NOTEBOOK AI ERROR] {e}")
            traceback.print_exc()

    # 解析AI结果
    title = ai_result.get("title", "")
    if not title:
        title = (full_text[:20] + "..." if len(full_text) > 20 else full_text) if full_text else "图片笔记"

    subject_name = ai_result.get("subject", "")
    subject_id = SUBJECT_MAP.get(subject_name, "")
    knowledge_points = ai_result.get("knowledge_points", [])
    summary = ai_result.get("summary", "")
    category = ai_result.get("category", "课堂笔记")
    tags = ai_result.get("tags", [])

    notebook = Notebook(
        user_id=user_id,
        subject_id=subject_id if subject_id else None,
        title=title,
        content=content,
        image_urls=json.dumps(image_urls, ensure_ascii=False),
        audio_url="",
        audio_text=audio_text,
        ai_summary=summary,
        ai_knowledge_points=json.dumps(knowledge_points, ensure_ascii=False),
        ai_category=category,
        grade=grade,
        semester="",
        tags=json.dumps(tags, ensure_ascii=False),
        is_starred=False,
    )
    db.add(notebook)
    db.commit()
    db.refresh(notebook)
    return notebook


@router.get("/")
async def list_notebooks(
    user_id: str = Query(...),
    subject_id: str = Query(None),
    category: str = Query(None),
    is_starred: bool = Query(None),
    keyword: str = Query(None),
    db: Session = Depends(get_db),
):
    """查询笔记列表"""
    q = db.query(Notebook).filter(Notebook.user_id == user_id)
    if subject_id:
        q = q.filter(Notebook.subject_id == subject_id)
    if category:
        q = q.filter(Notebook.ai_category == category)
    if is_starred is not None:
        q = q.filter(Notebook.is_starred == is_starred)
    if keyword:
        kw = f"%{keyword}%"
        q = q.filter(
            (Notebook.title.like(kw)) |
            (Notebook.content.like(kw)) |
            (Notebook.audio_text.like(kw)) |
            (Notebook.ai_summary.like(kw)) |
            (Notebook.ai_knowledge_points.like(kw))
        )
    notebooks = q.order_by(Notebook.created_at.desc()).all()

    results = []
    for nb in notebooks:
        results.append({
            "id": nb.id,
            "user_id": nb.user_id,
            "subject_id": nb.subject_id or "",
            "title": nb.title,
            "content": nb.content,
            "image_urls": nb.image_urls,
            "audio_url": nb.audio_url,
            "audio_text": nb.audio_text,
            "ai_summary": nb.ai_summary,
            "ai_knowledge_points": nb.ai_knowledge_points,
            "ai_category": nb.ai_category,
            "grade": nb.grade,
            "semester": nb.semester,
            "tags": nb.tags,
            "is_starred": nb.is_starred,
            "created_at": nb.created_at.isoformat() if nb.created_at else "",
            "updated_at": nb.updated_at.isoformat() if nb.updated_at else "",
        })
    return results


@router.get("/{notebook_id}", response_model=NotebookOut)
async def get_notebook(notebook_id: str, db: Session = Depends(get_db)):
    """获取笔记详情"""
    nb = db.query(Notebook).filter(Notebook.id == notebook_id).first()
    if not nb:
        raise HTTPException(404, "笔记不存在")
    return nb


@router.put("/{notebook_id}", response_model=NotebookOut)
async def update_notebook(notebook_id: str, data: NotebookUpdate, db: Session = Depends(get_db)):
    """更新笔记"""
    nb = db.query(Notebook).filter(Notebook.id == notebook_id).first()
    if not nb:
        raise HTTPException(404, "笔记不存在")

    if data.title is not None:
        nb.title = data.title
    if data.content is not None:
        nb.content = data.content
    if data.is_starred is not None:
        nb.is_starred = data.is_starred
    if data.tags is not None:
        nb.tags = json.dumps(data.tags, ensure_ascii=False)

    db.commit()
    db.refresh(nb)
    return nb


@router.delete("/{notebook_id}")
async def delete_notebook(notebook_id: str, db: Session = Depends(get_db)):
    """删除笔记"""
    nb = db.query(Notebook).filter(Notebook.id == notebook_id).first()
    if not nb:
        raise HTTPException(404, "笔记不存在")
    db.delete(nb)
    db.commit()
    return {"success": True}
