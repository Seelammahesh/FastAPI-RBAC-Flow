#app/api/routes/user.py
from fastapi import APIRouter, Depends
from app.schemas.user  import UserCreate,UserLogin,UserOut
from app.services.user_service import create_user,authenticate_user
from sqlalchemy.orm import Session
from app.core.security import create_access_token,create_refresh_token
from app.dependecies.auth import get_current_user,require_role,get_db
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import Settings
from jose import jwt
from app.models.tokens import RefreshToken
from app.models.user import User
from app.schemas.token import RefreshTokenRequest

from app.models.permissions import LogoutRequest
router =APIRouter()

@router.post("/register")
def register(user:UserCreate, db : Session =Depends(get_db)):
    return create_user(db,user.username,user.password,user.role)




@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = authenticate_user(db, form_data.username, form_data.password)

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({
        "sub": db_user.username,
        "role": db_user.role.name
    })

    refresh_token =create_refresh_token({
        "sub": db_user.username,
        "role": db_user.role.name
    })

    db_token=RefreshToken(
        token=refresh_token,
        user_id=db_user.id
    )
    db.add(db_token)
    db.commit()

    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer"}

    

@router.get("/me")
def read_current_user(current_user=Depends(get_current_user)):
    return ({
        "id":current_user.id,
        "username":current_user.username,
        "role":current_user.role
    })



@router.get("/admin-only")
def admin_data(user=Depends(require_role("admin"))):
    return {"message":"Welcom Admin, This is admin data"}


@router.post("/refresh")
def refresh_token(data : RefreshTokenRequest, db: Session = Depends(get_db)):

    #check if the refresh token is valid and exists in the database
    db_token=db.query(RefreshToken).filter(RefreshToken.token == data.refresh_token).first()

    if not db_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    #decode the token 

    try:
        payload=jwt.decode(
            data.refresh_token,
            Settings.SECRET_KEY,
            algorithms=[Settings.ALGORITHM]
        )
        username = payload.get("sub")
        print("Username from token:", username
              
              )
        role = payload.get("role")

        if not username :
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    #delete the old refresh token from the database
    db.delete(db_token)
    db.commit()

    #create new tokens
    new_access_token = create_access_token({
        "sub": username,
        "role": role
    })
    new_refresh_token = create_refresh_token({
        "sub": username,
        "role": role
    })

    #store the new refresh token in the database
    new_db_token=RefreshToken(
        token=new_refresh_token,
        user_id=db_token.user_id
    )

    db.add(new_db_token)
    db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }







@router.post("/logout")
def logout(data: LogoutRequest, db: Session = Depends(get_db)):
    print("LOGOUT HIT")

    token = db.query(RefreshToken).filter(
        RefreshToken.token == data.refresh_token
    ).first()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    db.delete(token)
    db.commit()

    return {"message": "Logged out successfully"}