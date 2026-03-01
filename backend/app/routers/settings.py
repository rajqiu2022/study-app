from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import LLMConfig, User
from ..schemas import LLMConfigCreate, LLMConfigOut
from ..llm_service import sync_iflow_to_db

router = APIRouter()

GLOBAL_USER_ID = "__global__"


@router.get("/llm", response_model=LLMConfigOut | None)
def get_llm_config(user_id: str = Query(""), db: Session = Depends(get_db)):
    """获取全局大模型配置（所有用户通用，自动同步iFlow）"""
    sync_iflow_to_db(db)
    config = db.query(LLMConfig).filter(LLMConfig.user_id == GLOBAL_USER_ID).first()
    return config


@router.post("/llm", response_model=LLMConfigOut)
def save_llm_config(data: LLMConfigCreate, user_id: str = Query(...), db: Session = Depends(get_db)):
    """保存全局大模型配置（仅管理员可操作）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_admin:
        raise HTTPException(403, "仅管理员可修改大模型设置")

    config = db.query(LLMConfig).filter(LLMConfig.user_id == GLOBAL_USER_ID).first()
    if config:
        config.provider = data.provider
        config.api_url = data.api_url
        config.api_key = data.api_key
        config.model_name = data.model_name
        config.enabled = data.enabled
        config.deep_thinking = data.deep_thinking
    else:
        config = LLMConfig(
            user_id=GLOBAL_USER_ID,
            provider=data.provider,
            api_url=data.api_url,
            api_key=data.api_key,
            model_name=data.model_name,
            enabled=data.enabled,
            deep_thinking=data.deep_thinking,
        )
        db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.post("/llm/test")
async def test_llm_connection(data: LLMConfigCreate):
    """测试大模型连接是否正常"""
    from ..llm_service import call_llm
    try:
        result = await call_llm(
            provider=data.provider,
            api_url=data.api_url,
            api_key=data.api_key,
            model_name=data.model_name,
            prompt="请用一句话回答：1+1等于几？",
        )
        return {"success": True, "reply": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
