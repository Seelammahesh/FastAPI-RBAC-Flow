from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Table, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import  Base

class User(Base):
    __tablename__ = "users"

    id =Column(Integer,primary_key=True,index=True)
    username=Column(String,index=True)
    password=Column(String,nullable=False)

    role_id=Column(Integer,ForeignKey("roles.id"))
    role=relationship("Role")

    


    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.name }')>"
