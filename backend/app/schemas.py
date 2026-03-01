from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


# --- User ---
class UserRegister(BaseModel):
    username: str
    password: str
    name: str
    grade: Optional[str] = "三年级"

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    grade: Optional[str] = None

class UserCreate(BaseModel):
    name: str
    grade: str

class UserOut(BaseModel):
    id: str
    username: str
    name: str
    grade: str
    avatar: str
    is_admin: bool = False
    created_at: datetime
    class Config:
        from_attributes = True


# --- Subject ---
class SubjectOut(BaseModel):
    id: str
    name: str
    icon: str
    class Config:
        from_attributes = True


# --- KnowledgePoint ---
class KnowledgePointOut(BaseModel):
    id: str
    subject_id: str
    chapter: str
    title: str
    difficulty: int
    class Config:
        from_attributes = True


# --- LearningRecord ---
class LearningRecordCreate(BaseModel):
    user_id: str
    subject_id: str
    knowledge_point: str
    study_date: Optional[date] = None
    duration_minutes: Optional[int] = 0
    mastery_level: Optional[int] = 3
    is_important: Optional[bool] = False
    notes: Optional[str] = ""

class LearningRecordUpdate(BaseModel):
    knowledge_point: Optional[str] = None
    duration_minutes: Optional[int] = None
    mastery_level: Optional[int] = None
    is_important: Optional[bool] = None
    notes: Optional[str] = None

class LearningRecordOut(BaseModel):
    id: str
    user_id: str
    subject_id: str
    knowledge_point: str
    study_date: date
    duration_minutes: int
    mastery_level: int
    is_important: bool
    notes: str
    image_url: Optional[str] = ""
    class Config:
        from_attributes = True


# --- WrongQuestion ---
class WrongQuestionCreate(BaseModel):
    user_id: str
    subject_id: str
    knowledge_point: Optional[str] = ""
    question_content: str
    my_answer: Optional[str] = ""
    correct_answer: Optional[str] = ""
    error_type: Optional[str] = "概念不清"
    analysis: Optional[str] = ""
    difficulty: Optional[int] = 2
    mistake_date: Optional[date] = None

class WrongQuestionUpdate(BaseModel):
    question_content: Optional[str] = None
    my_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    error_type: Optional[str] = None
    analysis: Optional[str] = None
    difficulty: Optional[int] = None
    is_resolved: Optional[bool] = None
    review_count: Optional[int] = None

class WrongQuestionOut(BaseModel):
    id: str
    user_id: str
    subject_id: str
    knowledge_point: str
    question_content: str
    my_answer: str
    correct_answer: str
    error_type: str
    analysis: str
    difficulty: int
    mistake_date: date
    review_count: int
    last_reviewed: Optional[date]
    is_resolved: bool
    image_url: Optional[str] = ""
    class Config:
        from_attributes = True


# --- PracticeSession ---
class PracticeSessionCreate(BaseModel):
    user_id: str
    subject_id: str
    knowledge_point: Optional[str] = ""
    question_type: Optional[str] = "混合"
    total_questions: Optional[int] = 5

class PracticeSessionOut(BaseModel):
    id: str
    user_id: str
    subject_id: str
    knowledge_point: str
    question_type: str
    total_questions: int
    correct_count: int
    questions_json: str
    created_at: datetime
    class Config:
        from_attributes = True


# --- LLM Config ---
class LLMConfigCreate(BaseModel):
    provider: str = "openai"  # openai / ollama
    api_url: str = ""
    api_key: str = ""
    model_name: str = ""
    enabled: bool = False
    deep_thinking: bool = False

class LLMConfigOut(BaseModel):
    id: str
    user_id: str
    provider: str
    api_url: str
    api_key: str
    model_name: str
    enabled: bool
    deep_thinking: bool
    class Config:
        from_attributes = True


# --- AI Chat ---
class ChatMessage(BaseModel):
    user_id: str
    message: str
    web_search: bool = False

class ChatResponse(BaseModel):
    reply: str
    action: Optional[str] = None  # 系统执行的操作描述
    data: Optional[dict] = None


# --- Dashboard ---
class SubjectProgress(BaseModel):
    subject_id: str
    subject_name: str
    icon: str
    total_records: int
    avg_mastery: float
    weak_points: List[str]
    wrong_count: int
    resolved_count: int

class DashboardData(BaseModel):
    user: UserOut
    total_study_days: int
    total_study_minutes: int
    total_wrong_questions: int
    resolved_wrong_questions: int
    subject_progress: List[SubjectProgress]
    recent_records: List[LearningRecordOut]
    weak_knowledge_points: List[str]
