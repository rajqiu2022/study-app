from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database import get_db
from ..models import WrongQuestion
from ..schemas import WrongQuestionCreate, WrongQuestionUpdate, WrongQuestionOut

router = APIRouter()


@router.get("/", response_model=List[WrongQuestionOut])
def list_wrong_questions(
    user_id: str = Query(...),
    subject_id: Optional[str] = None,
    is_resolved: Optional[bool] = None,
    error_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(WrongQuestion).filter(WrongQuestion.user_id == user_id)
    if subject_id:
        q = q.filter(WrongQuestion.subject_id == subject_id)
    if is_resolved is not None:
        q = q.filter(WrongQuestion.is_resolved == is_resolved)
    if error_type:
        q = q.filter(WrongQuestion.error_type == error_type)
    return q.order_by(WrongQuestion.mistake_date.desc()).all()


@router.post("/", response_model=WrongQuestionOut)
def create_wrong_question(data: WrongQuestionCreate, db: Session = Depends(get_db)):
    wq = WrongQuestion(
        user_id=data.user_id,
        subject_id=data.subject_id,
        knowledge_point=data.knowledge_point,
        question_content=data.question_content,
        my_answer=data.my_answer,
        correct_answer=data.correct_answer,
        error_type=data.error_type,
        analysis=data.analysis,
        difficulty=data.difficulty,
        mistake_date=data.mistake_date or date.today(),
    )
    db.add(wq)
    db.commit()
    db.refresh(wq)
    return wq


@router.put("/{wq_id}", response_model=WrongQuestionOut)
def update_wrong_question(wq_id: str, data: WrongQuestionUpdate, db: Session = Depends(get_db)):
    wq = db.query(WrongQuestion).filter(WrongQuestion.id == wq_id).first()
    if not wq:
        raise HTTPException(404, "错题不存在")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(wq, field, value)
    db.commit()
    db.refresh(wq)
    return wq


@router.post("/{wq_id}/review", response_model=WrongQuestionOut)
def review_wrong_question(wq_id: str, db: Session = Depends(get_db)):
    wq = db.query(WrongQuestion).filter(WrongQuestion.id == wq_id).first()
    if not wq:
        raise HTTPException(404, "错题不存在")
    wq.review_count += 1
    wq.last_reviewed = date.today()
    db.commit()
    db.refresh(wq)
    return wq


@router.delete("/{wq_id}")
def delete_wrong_question(wq_id: str, db: Session = Depends(get_db)):
    wq = db.query(WrongQuestion).filter(WrongQuestion.id == wq_id).first()
    if not wq:
        raise HTTPException(404, "错题不存在")
    db.delete(wq)
    db.commit()
    return {"message": "已删除"}
