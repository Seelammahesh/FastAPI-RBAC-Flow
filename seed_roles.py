from app.db.session import SessionLocal
from app.models.role import Role
from app.models.permissions import Permission
print(Permission.__mapper__.relationships)

def seed_roles_permissions():
    db = SessionLocal()

    try:
        # ✅ Define permissions
        permissions_list = ["read", "write", "delete"]

        # ✅ Define roles with permissions mapping
        role_permissions_map = {
            "admin": ["read", "write", "delete"],
            "manager": ["read", "write"],
            "user": ["read"]
        }

        # -----------------------------
        # 1. Create Permissions
        # -----------------------------
        existing_permissions = {
            p.name: p for p in db.query(Permission).all()
        }

        for perm_name in permissions_list:
            if perm_name not in existing_permissions:
                perm = Permission(name=perm_name)
                db.add(perm)
                db.flush()  # get ID without commit
                existing_permissions[perm_name] = perm

        # -----------------------------
        # 2. Create Roles
        # -----------------------------
        existing_roles = {
            r.name: r for r in db.query(Role).all()
        }

        for role_name in role_permissions_map.keys():
            if role_name not in existing_roles:
                role = Role(name=role_name)
                db.add(role)
                db.flush()
                existing_roles[role_name] = role

        # -----------------------------
        # 3. Assign Permissions to Roles
        # -----------------------------
        for role_name, perms in role_permissions_map.items():
            role = existing_roles[role_name]

            existing_perm_names = {p.name for p in role.permissions}

            for perm_name in perms:
                if perm_name not in existing_perm_names:
                    role.permissions.append(existing_permissions[perm_name])

        db.commit()
        print("✅ Roles & Permissions seeded successfully")

    except Exception as e:
        db.rollback()
        print("❌ Error:", str(e))

    finally:
        db.close()


if __name__ == "__main__":
    seed_roles_permissions()