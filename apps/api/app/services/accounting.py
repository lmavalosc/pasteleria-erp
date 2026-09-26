import uuid
from app.core.errors import DomainException
from app.models.accounting import AccountingAccount, JournalEntry, JournalLine
from app.repositories.accounting import AccountingRepository
from app.schemas.accounting import AccountCreate, JournalEntryCreate


class AccountingService:
    def __init__(self, repo: AccountingRepository):
        self.repo = repo

    def create_account(self, tenant_id: uuid.UUID, data: AccountCreate) -> AccountingAccount:
        if self.repo.get_account_by_code(data.code):
            raise DomainException(
                "Cuenta duplicada",
                f"Ya existe una cuenta con el código {data.code}.",
                409,
            )

        if data.parent_id and not self.repo.get_account_by_id(data.parent_id):
            raise DomainException(
                "Cuenta padre no existe",
                "La cuenta superior referenciada no existe.",
                400,
            )

        account = AccountingAccount(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            parent_id=data.parent_id,
            code=data.code,
            name=data.name,
            account_type=data.account_type,
            is_active=True,
        )
        return self.repo.create_account(account)

    def create_journal_entry(self, tenant_id: uuid.UUID, data: JournalEntryCreate) -> JournalEntry:
        # Validar que todas las cuentas referenciadas existan
        for line in data.lines:
            if not self.repo.get_account_by_id(line.account_id):
                raise DomainException(
                    "Cuenta inexistente",
                    f"La cuenta con ID {line.account_id} no existe en el plan de cuentas.",
                    400,
                )

        total_debit = sum(line.debit for line in data.lines)
        total_credit = sum(line.credit for line in data.lines)

        entry_id = uuid.uuid4()
        entry = JournalEntry(
            id=entry_id,
            tenant_id=tenant_id,
            entry_date=data.entry_date,
            description=data.description,
            status="posted",
            total_debit=total_debit,
            total_credit=total_credit,
        )

        for line in data.lines:
            entry.lines.append(
                JournalLine(
                    id=uuid.uuid4(),
                    tenant_id=tenant_id,
                    entry_id=entry_id,
                    account_id=line.account_id,
                    debit=line.debit,
                    credit=line.credit,
                    memo=line.memo,
                )
            )

        return self.repo.create_journal_entry(entry)
