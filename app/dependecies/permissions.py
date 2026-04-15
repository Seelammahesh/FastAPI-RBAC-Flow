from fastapi import Depends ,HTTPException,status
from app.dependecies.auth import get_current_user
from app.models.user import User



def require_permission(permission_name : str):
    def permission_checker(user : User = Depends(get_current_user)):
        user_permissions=[permission.name for permission in user.role.permissions]

        if permission_name  not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )
        return user
    return permission_checker