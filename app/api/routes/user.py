#app/api/routes/user.py
from fastapi import APIRouter, Depends
from app.schemas.user  import OTPVerify, UserCreate,UserLogin,UserOut
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
from app.models.otp import OTP

from app.models.permissions import LogoutRequest
from app.services.otp_service import create_otp, verify_user_otp
from app.core.security import hash_password
from app.core.security import verify_password



router =APIRouter()

@router.post("/register")
def register(user:UserCreate, db : Session =Depends(get_db)):
    return create_user(db,user.username,user.password,user.role)




@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.username, user.password)

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate OTP
    otp = create_otp(db, db_user.id, "login")
    print(f"Generated OTP for user {db_user.username}: {otp}")

    return {"message": "OTP sent to your registered method"}


@router.post("/verify-login")
def verify_login(data: OTPVerify, db: Session = Depends(get_db)):
    # Find user by username
    db_user = db.query(User).filter(User.username == data.username).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username")

    # Verify OTP
    if not verify_user_otp(db, db_user.id, data.otp, "login"):
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")

    # Create tokens
    access_token = create_access_token({
        "sub": db_user.username,
        "role": db_user.role.name
    })

    refresh_token = create_refresh_token({
        "sub": db_user.username,
        "role": db_user.role.name
    })

    db_token = RefreshToken(
        token=refresh_token,
        user_id=db_user.id
    )
    db.add(db_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

    
@router.post("/resend-login-otp")
def resend_login_otp(username: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(404, "User not found")

    otp=create_otp(db, user.id, "resent  opt for login")
    print(f"New otp sent to the user{username} : {otp}")

    return {
        "message":"resend Otp sent successfully",
        "Your otp is":otp
    }



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


@router.post("/forgot-password")
def forgot_password(username: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.username == username).first()

    if user:
        otp = create_otp(db, user.id, "reset_password")
        print(f"OTP for password reset for user {user.username}: {otp}")

    return {"message": "If user exists, OTP has been sent"}



@router.post("/reset-password")
def reset_password(
    username: str,
    otp: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    #Step 1: Fetch user
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid username or OTP"
        )

    # Step 2: Verify OTP (with purpose)
    is_valid_otp = verify_user_otp(
        db,
        user.id,
        otp,
        "reset_password"
    )

    if not is_valid_otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid username or OTP"
        )

    # 🛡️ Step 3: Password validation
    if username.lower() in new_password.lower():
        raise HTTPException(
            status_code=400,
            detail="Password should not contain username"
        )

    if len(new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long"
        )

    #Step 4: Prevent reuse of old password
    if verify_password(new_password, user.password):
        raise HTTPException(
            status_code=400,
            detail="New password must be different from the old password"
        )

    # 🔄 Step 5: Update password
    user.password = hash_password(new_password)

    # (Optional but recommended) invalidate all OTPs for this user
    # db.query(OTP).filter(OTP.user_id == user.id).update({"is_used": 1})

    db.commit()

    return {
        "message": "Password reset successful",
        "status": "success"
    }