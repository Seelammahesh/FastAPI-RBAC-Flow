#app/models/tokens.py
from sqlalchemy import Column, Integer, String, ForeignKey,DateTime
from app.db.base_class import Base
from datetime import datetime

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id=Column(Integer, primary_key=True)
    token=Column(String, unique=True, nullable=False)
    user_id=Column(Integer,ForeignKey("users.id"))
    created_at=Column(DateTime,default=datetime.utcnow)
