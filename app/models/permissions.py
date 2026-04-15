from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from pydantic import BaseModel


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    roles=relationship("Role", secondary="role_permissions", back_populates="permissions")


class LogoutRequest(BaseModel):
    refresh_token: str