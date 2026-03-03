from sqlalchemy import Column, String, Integer, Text, Date, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, date
import uuid

from .database import Base


def gen_id():
    return str(uuid.uuid4())[:8]


class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=gen_id)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    name = Column(String(50), nullable=False)
    grade = Column(String(10), nullable=False, default="三年级")
    avatar = Column(String(200), default="")
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    learning_records = relationship("LearningRecord", back_populates="user", cascade="all, delete-orphan")
    wrong_questions = relationship("WrongQuestion", back_populates="user", cascade="all, delete-orphan")
    practice_sessions = relationship("PracticeSession", back_populates="user", cascade="all, delete-orphan")
    notebooks = relationship("Notebook", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"
    id = Column(String(36), primary_key=True, default=gen_id)
    name = Column(String(50), nullable=False, unique=True)
    icon = Column(String(10), default="📚")

    knowledge_points = relationship("KnowledgePoint", back_populates="subject", cascade="all, delete-orphan")


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"
    id = Column(String(36), primary_key=True, default=gen_id)
    subject_id = Column(String(36), ForeignKey("subjects.id"), nullable=False)
    chapter = Column(String(100), default="")
    title = Column(String(200), nullable=False)
    difficulty = Column(Integer, default=1)  # 1-5

    subject = relationship("Subject", back_populates="knowledge_points")


class LearningRecord(Base):
    __tablename__ = "learning_records"
    id = Column(String(36), primary_key=True, default=gen_id)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id"), nullable=False)
    knowledge_point = Column(Text, nullable=False)
    study_date = Column(Date, default=date.today)
    duration_minutes = Column(Integer, default=0)
    mastery_level = Column(Integer, default=3)  # 1=未掌握 2=需加强 3=一般 4=熟练 5=精通
    is_important = Column(Boolean, default=False)
    notes = Column(Text, default="")
    image_url = Column(String(500), default="")  # 学习内容原图URL

    user = relationship("User", back_populates="learning_records")
    subject = relationship("Subject")


class WrongQuestion(Base):
    __tablename__ = "wrong_questions"
    id = Column(String(36), primary_key=True, default=gen_id)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id"), nullable=False)
    knowledge_point = Column(Text, default="")
    question_content = Column(Text, nullable=False)
    my_answer = Column(Text, default="")
    correct_answer = Column(Text, default="")
    error_type = Column(String(50), default="概念不清")  # 计算错误/概念不清/粗心大意/方法错误
    analysis = Column(Text, default="")
    difficulty = Column(Integer, default=2)  # 1=简单 2=中等 3=困难
    mistake_date = Column(Date, default=date.today)
    review_count = Column(Integer, default=0)
    last_reviewed = Column(Date, nullable=True)
    is_resolved = Column(Boolean, default=False)
    image_url = Column(String(500), default="")  # 题目原图URL

    user = relationship("User", back_populates="wrong_questions")
    subject = relationship("Subject")


class LLMConfig(Base):
    __tablename__ = "llm_configs"
    id = Column(String(36), primary_key=True, default=gen_id)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    provider = Column(String(20), default="openai")  # openai / ollama
    api_url = Column(String(500), default="")  # 接口地址
    api_key = Column(String(500), default="")  # API Key（ollama不需要）
    model_name = Column(String(100), default="")  # 模型名称
    enabled = Column(Boolean, default=False)  # 是否启用大模型出题
    deep_thinking = Column(Boolean, default=False)  # 是否启用深度思考
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User")


class Notebook(Base):
    __tablename__ = "notebooks"
    id = Column(String(36), primary_key=True, default=gen_id)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id"), nullable=True)
    title = Column(String(200), default="")
    content = Column(Text, default="")
    image_urls = Column(Text, default="")
    audio_url = Column(String(500), default="")
    audio_text = Column(Text, default="")
    ai_summary = Column(Text, default="")
    ai_knowledge_points = Column(Text, default="")
    ai_category = Column(String(100), default="")
    grade = Column(String(10), default="")
    semester = Column(String(10), default="")
    tags = Column(Text, default="")
    is_starred = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", overlaps="notebooks")
    subject = relationship("Subject")


class PracticeSession(Base):
    __tablename__ = "practice_sessions"
    id = Column(String(36), primary_key=True, default=gen_id)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id"), nullable=False)
    knowledge_point = Column(Text, default="")
    question_type = Column(String(20), default="混合")  # 选择题/填空题/应用题/混合/AI出题
    practice_mode = Column(String(20), default="custom")  # wrong_review/important_review/custom
    total_questions = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    status = Column(String(20), default="generating")  # generating/practicing/completed/abandoned
    questions_json = Column(Text, default="[]")  # JSON存储题目和答案
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="practice_sessions")
    subject = relationship("Subject")
