from crud.base import CRUDBase
from domains.echurch.models.department import Department
from domains.echurch.schemas.department import DepartmentCreate, DepartmentUpdate


class CRUDDepartment(CRUDBase[Department, DepartmentCreate, DepartmentUpdate]):
    pass


department_repo = CRUDDepartment(Department)

