from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password,verify_password
from app.models.role import Role
from fastapi import HTTPException, status


def create_user(db: Session, username :str, password : str, role : str  ):
    db_role=db.query(Role).filter(Role.name == role).first()

    if  not db_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
    user=User(
        username=username,
        password=hash_password(password),
        role = db_role

    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db : Session,username : str,password : str):
    user=db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password,user.password):
        return None
    return user
