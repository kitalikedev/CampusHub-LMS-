from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import get_current_user, require_roles
from src.modules.academics import service
from src.modules.academics.schemas import (GradeScaleOut, PrerequisitesUpdate, SemesterIn, SemesterOut,
                                           SemesterUpdate, SubjectIn, SubjectOut, SubjectUpdate)
from src.modules.users.models import Role, User

router = APIRouter(tags=["academics"])
admin_only = require_roles(Role.ADMIN)


@router.get("/semesters", response_model=List[SemesterOut])
def list_semesters(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return [service.semester_out(s) for s in service.list_semesters(db)]


@router.post("/semesters", response_model=SemesterOut, status_code=201)
def create_semester(data: SemesterIn, db: Session = Depends(get_db), _admin: User = Depends(admin_only)):
    return service.semester_out(service.create_semester(db, data))


@router.patch("/semesters/{semester_id}", response_model=SemesterOut)
def update_semester(semester_id: int, data: SemesterUpdate, db: Session = Depends(get_db),
                    _admin: User = Depends(admin_only)):
    return service.semester_out(service.update_semester(db, semester_id, data))


@router.get("/subjects", response_model=List[SubjectOut])
def list_subjects(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    graph = service.prerequisite_map(db)
    return [service.subject_out(db, s, graph) for s in service.list_subjects(db)]


@router.post("/subjects", response_model=SubjectOut, status_code=201)
def create_subject(data: SubjectIn, db: Session = Depends(get_db), _admin: User = Depends(admin_only)):
    return service.subject_out(db, service.create_subject(db, data))


@router.patch("/subjects/{subject_id}", response_model=SubjectOut)
def update_subject(subject_id: int, data: SubjectUpdate, db: Session = Depends(get_db),
                   _admin: User = Depends(admin_only)):
    return service.subject_out(db, service.update_subject(db, subject_id, data))


@router.put("/subjects/{subject_id}/prerequisites", response_model=SubjectOut)
def set_prerequisites(subject_id: int, data: PrerequisitesUpdate, db: Session = Depends(get_db),
                      _admin: User = Depends(admin_only)):
    return service.subject_out(db, service.set_prerequisites(db, subject_id, data.prerequisite_ids))


@router.get("/grade-scales", response_model=List[GradeScaleOut])
def list_grade_scales(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return service.list_grade_scales(db)
