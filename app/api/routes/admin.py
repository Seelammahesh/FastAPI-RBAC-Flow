from fastapi import Depends, HTTPException, status,APIRouter
from sqlalchemy.orm import Session
from app.services.role_service import assign_permission_to_role
from app.dependecies.auth import get_current_user,get_db,require_role

router = APIRouter()

@router.post("/assign_permission")

def assign_permission(role : str,permission : str, db : Session = Depends(get_db),user=Depends(require_role("admin"))):
    return assign_permission_to_role(db,role,permission)
    