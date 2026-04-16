from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class OTP(Base):
    __tablename__ = "otps"

    id=Column(Integer, primary_key=True)
    user_id=Column(Integer, ForeignKey("users.id"))
    otp_hash=Column(String, nullable=False)
    purpose=Column(String, nullable=False)
    is_used=Column(Integer, default=0)
    expires_at=Column(DateTime, nullable=False)
    created_at=Column(DateTime, nullable=False)

