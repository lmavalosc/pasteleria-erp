import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.accounting import AccountingAccount, JournalEntry, JournalLine


class AccountingRepository:
    def __init__(self, db: Session, tenant_id: uuid.UUID | None = None):
        self.db = db
        self.tenant_id = tenant_id

    def create_account(self, account: AccountingAccount) -> AccountingAccount:
        self.db.add(account)
        self.db.flush()
        return account

    def get_account_by_code(self, code: str) -> AccountingAccount | None:
        q = self.db.query(AccountingAccount).filter(AccountingAccount.code == code)
        if self.tenant_id:
            q = q.filter(AccountingAccount.tenant_id == self.tenant_id)
        return q.first()

    def get_account_by_id(self, account_id: uuid.UUID) -> AccountingAccount | None:
        q = self.db.query(AccountingAccount).filter(AccountingAccount.id == account_id)
        if self.tenant_id:
            q = q.filter(AccountingAccount.tenant_id == self.tenant_id)
        return q.first()

    def list_accounts(self) -> list[AccountingAccount]:
        q = self.db.query(AccountingAccount)
        if self.tenant_id:
            q = q.filter(AccountingAccount.tenant_id == self.tenant_id)
        return q.order_by(AccountingAccount.code.asc()).all()

    def list_accounts_paginated(self, offset: int, limit: int) -> tuple[list[AccountingAccount], int]:
        count_q = self.db.query(func.count(AccountingAccount.id))
        items_q = self.db.query(AccountingAccount)
        if self.tenant_id:
            count_q = count_q.filter(AccountingAccount.tenant_id == self.tenant_id)
            items_q = items_q.filter(AccountingAccount.tenant_id == self.tenant_id)
        total = count_q.scalar() or 0
        items = (
            items_q
            .order_by(AccountingAccount.code.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def create_journal_entry(self, entry: JournalEntry) -> JournalEntry:
        self.db.add(entry)
        self.db.flush()
        return entry

    def list_journal_entries_paginated(
        self, offset: int, limit: int
    ) -> tuple[list[JournalEntry], int]:
        count_q = self.db.query(func.count(JournalEntry.id))
        items_q = self.db.query(JournalEntry)
        if self.tenant_id:
            count_q = count_q.filter(JournalEntry.tenant_id == self.tenant_id)
            items_q = items_q.filter(JournalEntry.tenant_id == self.tenant_id)
        total = count_q.scalar() or 0
        items = (
            items_q
            .order_by(JournalEntry.entry_date.desc(), JournalEntry.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total
