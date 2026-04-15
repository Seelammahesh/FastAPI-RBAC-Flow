from app.models.role import Role
from app.models.permissions import Permission


def assign_permission_to_role(db,role_name: str,permission_name:str):
    role=db.query(Role).filter(Role.name == role_name).first()
    permission=db.query(Permission).filter(Permission.name == permission_name).first()

    if not role and not permission:
        raise ValueError("Role or Permission not found")
    
    role.permissions.append(permission)
    db.commit()
    return role 