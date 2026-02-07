from typing import Annotated, List, Union
from fastapi import HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import text
from config.settings import settings
from domains.auth.models.users import User
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError 
from config.logger import log
from domains.auth.models.role_permissions import Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_current_user_db():
    from db.session import SessionLocal  # Lazy import to avoid circular import
    with SessionLocal() as db:
        yield db






def get_user_by_email(username: str, db: Session):
    return db.query(User).filter(User.email == username).first()

def get_user_by_id(id: str, db: Session):
    return db.query(User).filter(User.id == id).first()

def get_all_roles(db: Session):
    return db.query(User).all()

def get_current_user(request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_current_user_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(username=username, db=db)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="your account is not active"
        )
    return current_user

def check_if_is_system_admin(
        current_active_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_current_user_db)
):
    check_user_role = db.query(Role).filter(Role.id == current_active_user.role_id).first()

    if check_user_role.name == "System Administrator":
        return current_active_user
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                        detail="only system administrator can access this api route")





def require_permissions(required_permissions: Union[str, List[str]], require_all: bool = True):
    """
    Factory for checking multiple permissions (role-based and direct staff) using raw SQL.

    Args:
        required_permissions (Union[str, List[str]]): List or single string of required permission names.
        require_all (bool): If True, user needs all permissions. If False, needs at least one.
    """
    # Convert to set for efficient operations
    if isinstance(required_permissions, str):
        required_permissions_set = {required_permissions}
    else:
        required_permissions_set = set(required_permissions)

    def check_permissions(
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: Session = Depends(get_current_user_db),
        schema: str = "public"
    ) -> User:
        # Let's Handle System Admins (implicitly have all permissions) 
        if current_user.organization_id is None:
            log.debug(f"System Admin {current_user.email} granted access (bypassing specific permission check).")
            return current_user

        # Let's do Basic Checks for Organization Users ---
        permission_denied_exception = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have permission to : {', '.join(required_permissions_set)}",
        )

        if schema == "public": # Should not happen if organization_id exists
             log.error(f"Org user {current_user.email} resolved to public schema unexpectedly during permission check.")
             raise HTTPException(status_code=500, detail="Internal configuration error during permission check.")

        if not required_permissions_set: # If no permissions are required, allow access
            log.debug(f"No specific permissions required, granting access to {current_user.email}.")
            return current_user

        # Let's Fetch Effective Permissions 
        role_permissions: Set[str] = set()
        staff_permissions: Set[str] = set()

        # Let's Fetch permissions from Role
        if current_user.role_id:
            try:
                sql_role_perms = text(f"""
                    SELECT p.name
                    FROM "{schema}".organization_permissions p
                    JOIN "{schema}".organization_role_permissions rp ON p.id = rp.permission_id
                    WHERE rp.role_id = :role_id
                """)
                result = db.execute(sql_role_perms, {"role_id": current_user.role_id})
                role_permissions = {row[0] for row in result.fetchall()}
                log.debug(f"User {current_user.email} role permissions ({current_user.role_id}) in {schema}: {role_permissions}")
            except SQLAlchemyError as e:
                log.error(f"DB error fetching role permissions for user {current_user.email}, role {current_user.role_id} in {schema}: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="DB error checking role permissions.")
            except Exception as e: 
                 log.error(f"Unexpected error fetching role permissions for user {current_user.email} in {schema}: {e}", exc_info=True)
                 raise HTTPException(status_code=500, detail="Error checking role permissions.")

        # Fetch direct permissions from Staff
        staff_id = None
        try:
            # Find the staff record associated with the user
            staff_query = text(f'SELECT id FROM "{schema}".staffs WHERE user_id = :user_id')
            staff_result = db.execute(staff_query, {"user_id": current_user.id})
            staff_id = staff_result.scalar_one_or_none()

            if staff_id:
                log.debug(f"Found staff record {staff_id} for user {current_user.email} in schema {schema}")
                sql_staff_perms = text(f"""
                    SELECT p.name
                    FROM "{schema}".organization_permissions p
                    JOIN "{schema}".organization_staff_permissions sp ON p.id = sp.permission_id
                    WHERE sp.staff_id = :staff_id
                """)
                perm_result = db.execute(sql_staff_perms, {"staff_id": staff_id})
                staff_permissions = {row[0] for row in perm_result.fetchall()}
                log.debug(f"User {current_user.email} direct staff permissions ({staff_id}) in {schema}: {staff_permissions}")
            else:
                 log.debug(f"No staff record found for user {current_user.email} in schema {schema}")

        except SQLAlchemyError as e:
            log.error(f"DB error fetching staff permissions for user {current_user.email} (staff_id: {staff_id}) in {schema}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="DB error checking staff permissions.")
        except Exception as e: 
             log.error(f"Unexpected error fetching staff permissions for user {current_user.email} in {schema}: {e}", exc_info=True)
             raise HTTPException(status_code=500, detail="Error checking staff permissions.")

        # Let's Combine permissions
        effective_permissions = role_permissions.union(staff_permissions)
        log.debug(f"User {current_user.email} effective permissions in schema {schema}: {effective_permissions}")

        # Let's Check Permissions 
        has_permission = False
        if require_all:
            # Check if all required permissions are in the user's effective permissions
            if required_permissions_set.issubset(effective_permissions):
                has_permission = True
        else:
            # Check if at least one required permission is in the user's effective permissions
            if not required_permissions_set.isdisjoint(effective_permissions):
                has_permission = True

        if not has_permission:
            missing = required_permissions_set - effective_permissions
            
            log.debug(f"Permission Denied: User {current_user.email} in schema {schema}. Requires: {required_permissions_set}. Has: {effective_permissions}. Missing: {missing}")
            raise permission_denied_exception 

       
        log.debug(f"Permission Granted: User {current_user.email} in schema {schema} requiring {required_permissions_set}.")
        return current_user

    return check_permissions

    

