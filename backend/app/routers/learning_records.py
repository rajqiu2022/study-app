from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database import get_db
from ..models import LearningRecord
from ..schemas import LearningRecordCreate, LearningRecordUpdate, LearningRecordOut

router = APIRouter()


@router.get("/", response_model=List[LearningRecordOut])
def list_records(
    user_id: str = Query(...),
    subject_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(LearningRecord).filter(LearningRecord.user_id == user_id)
    if subject_id:
        q = q.filter(LearningRecord.subject_id == subject_id)
    return q.order_by(LearningRecord.study_date.desc()).all()


@router.post("/", response_model=LearningRecordOut)
def create_record(data: LearningRecordCreate, db: Session = Depends(get_db)):
    record = LearningRecord(
        user_id=data.user_id,
        subject_id=data.subject_id,
        knowledge_point=data.knowledge_point,
        study_date=data.study_date or date.today(),
        duration_minutes=data.duration_minutes,
        mastery_level=data.mastery_level,
        is_important=data.is_important,
        notes=data.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/{record_id}", response_model=LearningRecordOut)
def update_record(record_id: str, data: LearningRecordUpdate, db: Session = Depends(get_db)):
    record = db.query(LearningRecord).filter(LearningRecord.id == record_id).first()
    if not record:
        raise HTTPException(404, "记录不存在")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}")
def delete_record(record_id: str, db: Session = Depends(get_db)):
    record = db.query(LearningRecord).filter(LearningRecord.id == record_id).first()
    if not record:
        raise HTTPException(404, "记录不存在")
    db.delete(record)
    db.commit()
    return {"message": "已删除"}
