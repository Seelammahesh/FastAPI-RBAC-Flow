from app.models.otp import OTP
from datetime import datetime, timedelta
from app.core.otp import generate_otp, hash_otp,verify_otp

def create_otp(db,user_id : int ,purpose : str):
    otp= generate_otp()
    hashed_otp= hash_otp(str(otp))

    otp_entry=OTP(
        user_id=user_id,
        otp_hash=hashed_otp,
        purpose=purpose,
        expires_at=datetime.utcnow() + timedelta(minutes=5),
        created_at=datetime.utcnow()
    )
    db.add(otp_entry)
    db.commit()
    print(f"OTP for user {user_id} and purpose {purpose}: {otp}")
    return otp


def verify_user_otp(db, user_id : int ,otp:str,purpose : str):
    otp_entry=db.query(OTP).filter(
        OTP.user_id==user_id, 
        OTP.purpose==purpose,
        OTP.is_used==0
        ).order_by(OTP.created_at.desc()).first()
    if not otp_entry:
        return False
        
    if otp_entry.expires_at < datetime.utcnow():
        return False
    
    if not verify_otp(otp,otp_entry.otp_hash):
        return False
    
    otp_entry.is_used=1
    db.commit()

    return True





