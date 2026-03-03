from fastapi import APIRouter, Query
from typing import Optional
from ..curriculum_data import CURRICULUM, ALL_GRADES, get_curriculum, get_unit_topics, get_semester_all_topics

router = APIRouter()


@router.get("/grades")
def list_grades():
    """获取所有年级列表"""
    return ALL_GRADES


@router.get("/")
def get_curriculum_data(
    grade: str = Query(..., description="年级"),
    subject_id: str = Query(..., description="学科ID"),
    semester: Optional[str] = Query(None, description="学期：上册/下册"),
):
    """获取指定年级学科的课本大纲"""
    data = get_curriculum(grade, subject_id, semester)
    return data


@router.get("/topics")
def get_topics(
    grade: str = Query(..., description="年级"),
    subject_id: str = Query(..., description="学科ID"),
    semester: str = Query(..., description="学期：上册/下册"),
    unit: Optional[str] = Query(None, description="单元名称"),
):
    """获取指定单元或整个学期的知识点"""
    if unit:
        topics = get_unit_topics(grade, subject_id, semester, unit)
    else:
        topics = get_semester_all_topics(grade, subject_id, semester)
    return topics
