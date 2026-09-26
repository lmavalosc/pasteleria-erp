import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.accounting import AccountingAccount, JournalEntry, JournalLine


class AccountingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_account(self, account: AccountingAccount) -> AccountingAccount:
        self.db.add(account)
        self.db.flush()
        return account

    def get_account_by_code(self, code: str) -> AccountingAccount | None:
        return (
            self.db.query(AccountingAccount)
            .filter(AccountingAccount.code == code)
            .first()
        )

    def get_account_by_id(self, account_id: uuid.UUID) -> AccountingAccount | None:
        return (
            self.db.query(AccountingAccount)
            .filter(AccountingAccount.id == account_id)
            .first()
        )

    def list_accounts(self) -> list[AccountingAccount]:
        return (
            self.db.query(AccountingAccount)
            .order_by(AccountingAccount.code.asc())
            .all()
        )

    def list_accounts_paginated(self, offset: int, limit: int) -> tuple[list[AccountingAccount], int]:
        total = self.db.query(func.count(AccountingAccount.id)).scalar() or 0
        items = (
            self.db.query(AccountingAccount)
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
        total = self.db.query(func.count(JournalEntry.id)).scalar() or 0
        items = (
            self.db.query(JournalEntry)
            .order_by(JournalEntry.entry_date.desc(), JournalEntry.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total
