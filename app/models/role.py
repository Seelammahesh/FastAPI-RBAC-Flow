from sqlalchemy import Column, Integer, String,Table, ForeignKey
from app.db.base_class import Base
from sqlalchemy.orm import relationship

role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id',ForeignKey('roles.id')),
    Column('permission_id', ForeignKey('permissions.id'))

)



class Role(Base):
    
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    permissions=relationship("Permission",secondary=role_permissions, back_populates="roles")



