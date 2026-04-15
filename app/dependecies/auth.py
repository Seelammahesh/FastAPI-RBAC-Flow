from app.db.session import SessionLocal
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from app.core.config import Settings
from app.models.user import User 
from sqlalchemy.orm import Session
from fastapi import HTTPException, status



def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()


from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.models.user import User
from app.db.session import SessionLocal
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, Settings.SECRET_KEY, algorithms=[Settings.ALGORITHM])
        username = payload.get("sub")

        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(User).filter(User.username == username).first()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user   # ✅ return DB object

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    

        
    

def require_role(role : str):
    def role_checker(user : User =Depends(get_current_user)):
        if user.role.name  != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return role_checker










