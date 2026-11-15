from typing import List

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import get_current_user
from src.core.permissions import ensure_section_member
from src.modules.assignments import service
from src.modules.assignments.schemas import AssignmentIn, AssignmentOut, AssignmentUpdate
from src.modules.users.models import User

router = APIRouter(tags=["assignments"])


@router.get("/sections/{section_id}/assignments", response_model=List[AssignmentOut])
def list_assignments(section_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.list_for_section(db, user, section_id)


@router.post("/sections/{section_id}/assignments", response_model=AssignmentOut, status_code=201)
def create_assignment(section_id: int, data: AssignmentIn, db: Session = Depends(get_db),
                      user: User = Depends(get_current_user)):
    return service.create(db, user, section_id, data)


@router.get("/assignments/{assignment_id}", response_model=AssignmentOut)
def get_assignment(assignment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    assignment = service.get_assignment(db, assignment_id)
    ensure_section_member(db, service.section_of(db, assignment), user)
    return assignment


@router.patch("/assignments/{assignment_id}", response_model=AssignmentOut)
def update_assignment(assignment_id: int, data: AssignmentUpdate, db: Session = Depends(get_db),
                      user: User = Depends(get_current_user)):
    return service.update(db, user, assignment_id, data)


@router.delete("/assignments/{assignment_id}", status_code=204)
def delete_assignment(assignment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service.delete(db, user, assignment_id)
    return Response(status_code=204)
