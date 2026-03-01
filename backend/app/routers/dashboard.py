from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import User, Subject, LearningRecord, WrongQuestion
from ..schemas import DashboardData, SubjectProgress, LearningRecordOut, UserOut

router = APIRouter()


@router.get("/", response_model=DashboardData)
def get_dashboard(user_id: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "用户不存在")

    subjects = db.query(Subject).all()
    all_records = db.query(LearningRecord).filter(LearningRecord.user_id == user_id).all()
    all_wrong = db.query(WrongQuestion).filter(WrongQuestion.user_id == user_id).all()

    # 总体统计
    study_days = len(set(r.study_date for r in all_records))
    total_minutes = sum(r.duration_minutes for r in all_records)
    total_wrong = len(all_wrong)
    resolved_wrong = sum(1 for w in all_wrong if w.is_resolved)

    # 各科进度
    subject_progress = []
    for s in subjects:
        s_records = [r for r in all_records if r.subject_id == s.id]
        s_wrong = [w for w in all_wrong if w.subject_id == s.id]
        avg_mastery = sum(r.mastery_level for r in s_records) / len(s_records) if s_records else 0
        weak = [r.knowledge_point for r in s_records if r.mastery_level <= 2]

        subject_progress.append(SubjectProgress(
            subject_id=s.id,
            subject_name=s.name,
            icon=s.icon,
            total_records=len(s_records),
            avg_mastery=round(avg_mastery, 1),
            weak_points=list(set(weak))[:5],
            wrong_count=len(s_wrong),
            resolved_count=sum(1 for w in s_wrong if w.is_resolved),
        ))

    # 最近记录
    recent = sorted(all_records, key=lambda r: r.study_date, reverse=True)[:10]

    # 全局薄弱点
    weak_all = list(set(r.knowledge_point for r in all_records if r.mastery_level <= 2))

    return DashboardData(
        user=user,
        total_study_days=study_days,
        total_study_minutes=total_minutes,
        total_wrong_questions=total_wrong,
        resolved_wrong_questions=resolved_wrong,
        subject_progress=subject_progress,
        recent_records=recent,
        weak_knowledge_points=weak_all[:10],
    )
