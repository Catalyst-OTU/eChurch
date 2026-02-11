from crud.base import CRUDBase
from domains.echurch.models.finance import AuditLog, GivingTransaction
from domains.echurch.schemas.finance import GivingTransactionCreate, GivingTransactionUpdate


class CRUDGivingTransaction(CRUDBase[GivingTransaction, GivingTransactionCreate, GivingTransactionUpdate]):
    pass


class CRUDAuditLog(CRUDBase[AuditLog, dict, dict]):
    pass


giving_transaction_repo = CRUDGivingTransaction(GivingTransaction)
audit_log_repo = CRUDAuditLog(AuditLog)

