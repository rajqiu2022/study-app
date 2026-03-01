from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Subject, KnowledgePoint
from ..schemas import SubjectOut, KnowledgePointOut

router = APIRouter()


@router.get("/", response_model=List[SubjectOut])
def list_subjects(db: Session = Depends(get_db)):
    return db.query(Subject).all()


@router.get("/{subject_id}/knowledge-points", response_model=List[KnowledgePointOut])
def list_knowledge_points(subject_id: str, db: Session = Depends(get_db)):
    return db.query(KnowledgePoint).filter(KnowledgePoint.subject_id == subject_id).all()
