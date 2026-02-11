from crud.base import CRUDBase
from domains.echurch.models.backup import BackupSnapshot
from domains.echurch.schemas.admin_tools import BackupCreateRequest


class CRUDBackupSnapshot(CRUDBase[BackupSnapshot, BackupCreateRequest, BackupCreateRequest]):
    pass


backup_snapshot_repo = CRUDBackupSnapshot(BackupSnapshot)

