from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import users, subjects, learning_records, wrong_questions, practice, chat, dashboard, ocr, settings, knowledge_graph, curriculum

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 数据库迁移：为已有表添加新字段
def _migrate_db():
    import sqlalchemy
    with engine.connect() as conn:
        # llm_configs 表添加 deep_thinking 字段
        try:
            conn.execute(sqlalchemy.text("ALTER TABLE llm_configs ADD COLUMN deep_thinking BOOLEAN DEFAULT 0"))
            conn.commit()
        except Exception:
            pass  # 字段已存在则忽略
        # users 表添加 is_admin 字段
        try:
            conn.execute(sqlalchemy.text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
            conn.commit()
        except Exception:
            pass
        # wrong_questions 表添加 image_url 字段
        try:
            conn.execute(sqlalchemy.text("ALTER TABLE wrong_questions ADD COLUMN image_url VARCHAR(500) DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        # learning_records 表添加 image_url 字段
        try:
            conn.execute(sqlalchemy.text("ALTER TABLE learning_records ADD COLUMN image_url VARCHAR(500) DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
        # practice_sessions 表添加 status 字段
        try:
            conn.execute(sqlalchemy.text("ALTER TABLE practice_sessions ADD COLUMN status VARCHAR(20) DEFAULT 'completed'"))
            conn.commit()
        except Exception:
            pass
        # practice_sessions 表添加 practice_mode 字段
        try:
            conn.execute(sqlalchemy.text("ALTER TABLE practice_sessions ADD COLUMN practice_mode VARCHAR(20) DEFAULT 'custom'"))
            conn.commit()
        except Exception:
            pass

_migrate_db()

app = FastAPI(title="学业辅导系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(subjects.router, prefix="/api/subjects", tags=["学科"])
app.include_router(learning_records.router, prefix="/api/records", tags=["学习记录"])
app.include_router(wrong_questions.router, prefix="/api/wrong-questions", tags=["错题本"])
app.include_router(practice.router, prefix="/api/practice", tags=["智能练习"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI对话"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["仪表盘"])
app.include_router(ocr.router, prefix="/api/ocr", tags=["图片识别"])
app.include_router(settings.router, prefix="/api/settings", tags=["系统设置"])
app.include_router(knowledge_graph.router, prefix="/api/knowledge-graph", tags=["知识图谱"])
app.include_router(curriculum.router, prefix="/api/curriculum", tags=["课本大纲"])
app.include_router(notebooks.router, prefix="/api/notebooks", tags=["笔记本"])


@app.on_event("startup")
async def startup():
    """初始化默认学科数据和管理员账号"""
    from .database import SessionLocal
    from .models import Subject, User, LLMConfig
    db = SessionLocal()
    try:
        if db.query(Subject).count() == 0:
            defaults = [
                Subject(id="math", name="数学", icon="🔢"),
                Subject(id="chinese", name="语文", icon="📖"),
                Subject(id="english", name="英语", icon="🔤"),
                Subject(id="science", name="科学", icon="🔬"),
            ]
            db.add_all(defaults)
            db.commit()

        # 自动创建管理员账号
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password="123321",
                name="管理员",
                grade="三年级",
                is_admin=True,
            )
            db.add(admin)
            db.commit()
        elif not admin.is_admin:
            admin.is_admin = True
            db.commit()

        # 迁移：将已有的用户级 LLM 配置合并为全局配置
        global_config = db.query(LLMConfig).filter(LLMConfig.user_id == "__global__").first()
        if not global_config:
            # 查找已有的任意启用的配置迁移过来，优先选有api_key的
            existing = (
                db.query(LLMConfig)
                .filter(LLMConfig.user_id != "__global__", LLMConfig.enabled == True, LLMConfig.api_key != "")
                .first()
            )
            if not existing:
                existing = db.query(LLMConfig).filter(LLMConfig.user_id != "__global__").first()
            if existing:
                existing.user_id = "__global__"
                db.commit()
        # 清理残留的用户级配置
        db.query(LLMConfig).filter(LLMConfig.user_id != "__global__").delete()
        db.commit()
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "学业辅导系统 API", "version": "1.0.0"}
