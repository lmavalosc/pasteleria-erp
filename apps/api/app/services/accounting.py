import uuid
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import DomainError, DomainException
from app.models.entities import AccountingAccount, JournalEntry, JournalLine
from app.repositories.accounting import AccountingRepository
from app.schemas.accounting import (
    AccountCreate,
    AccountingAccountCreate,
    AccountingAccountPage,
    AccountingAccountRead,
    AccountingAccountUpdate,
    JournalEntryCreate,
    JournalEntryPage,
    JournalEntryRead,
    JournalLineRead,
)
from app.services.common import build_page_meta, paginate


def list_accounts(
    db: Session,
    tenant_id: UUID,
    page: int = 1,
    page_size: int = 20,
) -> AccountingAccountPage:
    stmt = (
        select(AccountingAccount)
        .where(AccountingAccount.tenant_id == tenant_id)
        .order_by(AccountingAccount.code.asc())
    )
    items, total = paginate(db, stmt, page, page_size)
    meta = build_page_meta(total=total, page=page, page_size=page_size)
    return AccountingAccountPage(
        items=[AccountingAccountRead.model_validate(acc) for acc in items],
        **meta.model_dump(),
    )


def create_account(
    db: Session,
    tenant_id: UUID,
    payload: AccountingAccountCreate,
) -> AccountingAccountRead:
    exists = db.scalar(
        select(AccountingAccount.id).where(
            AccountingAccount.tenant_id == tenant_id,
            AccountingAccount.code == payload.code,
        )
    )
    if exists:
        raise DomainError(
            status_code=409,
            title="Cuenta duplicada",
            detail=f"Ya existe una cuenta con el código {payload.code}.",
            code="ACCOUNT_DUPLICATE",
        )

    if payload.parent_id:
        parent_exists = db.scalar(
            select(AccountingAccount.id).where(
                AccountingAccount.tenant_id == tenant_id,
                AccountingAccount.id == payload.parent_id,
            )
        )
        if not parent_exists:
            raise DomainError(
                status_code=400,
                title="Cuenta padre no existe",
                detail="La cuenta superior referenciada no existe.",
                code="PARENT_ACCOUNT_NOT_FOUND",
            )

    account = AccountingAccount(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        code=payload.code,
        name=payload.name,
        account_type=payload.account_type,
        parent_id=payload.parent_id,
        is_active=True,
    )
    db.add(account)
    db.flush()
    db.refresh(account)
    return AccountingAccountRead.model_validate(account)


def get_account(
    db: Session,
    tenant_id: UUID,
    account_id: UUID,
) -> AccountingAccountRead:
    account = db.scalar(
        select(AccountingAccount).where(
            AccountingAccount.tenant_id == tenant_id,
            AccountingAccount.id == account_id,
        )
    )
    if not account:
        raise DomainError(
            status_code=404,
            title="Cuenta no encontrada",
            detail=f"La cuenta contable con ID {account_id} no existe.",
            code="ACCOUNT_NOT_FOUND",
        )
    return AccountingAccountRead.model_validate(account)


def update_account(
    db: Session,
    tenant_id: UUID,
    account_id: UUID,
    payload: AccountingAccountUpdate,
) -> AccountingAccountRead:
    account = db.scalar(
        select(AccountingAccount).where(
            AccountingAccount.tenant_id == tenant_id,
            AccountingAccount.id == account_id,
        )
    )
    if not account:
        raise DomainError(
            status_code=404,
            title="Cuenta no encontrada",
            detail=f"La cuenta contable con ID {account_id} no existe.",
            code="ACCOUNT_NOT_FOUND",
        )

    if payload.code is not None and payload.code != account.code:
        code_exists = db.scalar(
            select(AccountingAccount.id).where(
                AccountingAccount.tenant_id == tenant_id,
                AccountingAccount.code == payload.code,
                AccountingAccount.id != account_id,
            )
        )
        if code_exists:
            raise DomainError(
                status_code=409,
                title="Código de cuenta duplicado",
                detail=f"El código {payload.code} ya está en uso por otra cuenta.",
                code="ACCOUNT_CODE_DUPLICATE",
            )
        account.code = payload.code

    if payload.name is not None:
        account.name = payload.name
    if payload.account_type is not None:
        account.account_type = payload.account_type
    if payload.is_active is not None:
        account.is_active = payload.is_active

    db.flush()
    db.refresh(account)
    return AccountingAccountRead.model_validate(account)


def list_journal_entries(
    db: Session,
    tenant_id: UUID,
    page: int = 1,
    page_size: int = 20,
) -> JournalEntryPage:
    stmt = (
        select(JournalEntry)
        .options(selectinload(JournalEntry.lines))
        .where(JournalEntry.tenant_id == tenant_id)
        .order_by(JournalEntry.entry_date.desc(), JournalEntry.created_at.desc())
    )
    items, total = paginate(db, stmt, page, page_size)
    meta = build_page_meta(total=total, page=page, page_size=page_size)
    return JournalEntryPage(
        items=[_to_journal_entry_read(item) for item in items],
        **meta.model_dump(),
    )


def create_journal_entry(
    db: Session,
    tenant_id: UUID,
    payload: JournalEntryCreate,
) -> JournalEntryRead:
    account_ids = {line.account_id for line in payload.lines}
    existing_count = db.scalar(
        select(func.count(AccountingAccount.id)).where(
            AccountingAccount.tenant_id == tenant_id,
            AccountingAccount.id.in_(account_ids),
        )
    ) or 0

    if existing_count != len(account_ids):
        raise DomainError(
            status_code=400,
            title="Cuenta inexistente",
            detail="Una o más cuentas contables referenciadas no existen para este tenant.",
            code="ACCOUNT_NOT_FOUND",
        )

    total_debit = sum(Decimal(str(line.debit)) for line in payload.lines)
    total_credit = sum(Decimal(str(line.credit)) for line in payload.lines)

    entry_id = uuid.uuid4()
    entry = JournalEntry(
        id=entry_id,
        tenant_id=tenant_id,
        entry_date=payload.entry_date,
        description=payload.description,
        status="draft",
        total_debit=total_debit,
        total_credit=total_credit,
    )

    for line in payload.lines:
        entry.lines.append(
            JournalLine(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                entry_id=entry_id,
                account_id=line.account_id,
                debit=Decimal(str(line.debit)),
                credit=Decimal(str(line.credit)),
                memo=line.memo,
            )
        )

    db.add(entry)
    db.flush()
    db.refresh(entry)
    return _to_journal_entry_read(entry)


def get_journal_entry(
    db: Session,
    tenant_id: UUID,
    entry_id: UUID,
) -> JournalEntryRead:
    entry = db.scalar(
        select(JournalEntry)
        .options(selectinload(JournalEntry.lines))
        .where(
            JournalEntry.tenant_id == tenant_id,
            JournalEntry.id == entry_id,
        )
    )
    if not entry:
        raise DomainError(
            status_code=404,
            title="Asiento contable no encontrado",
            detail=f"El asiento con ID {entry_id} no existe.",
            code="JOURNAL_ENTRY_NOT_FOUND",
        )
    return _to_journal_entry_read(entry)


def post_journal_entry(
    db: Session,
    tenant_id: UUID,
    entry_id: UUID,
) -> JournalEntryRead:
    entry = db.scalar(
        select(JournalEntry)
        .options(selectinload(JournalEntry.lines))
        .where(
            JournalEntry.tenant_id == tenant_id,
            JournalEntry.id == entry_id,
        )
    )
    if not entry:
        raise DomainError(
            status_code=404,
            title="Asiento contable no encontrado",
            detail=f"El asiento con ID {entry_id} no existe.",
            code="JOURNAL_ENTRY_NOT_FOUND",
        )
    if entry.status == "posted":
        return _to_journal_entry_read(entry)
    if entry.status == "voided":
        raise DomainError(
            status_code=409,
            title="Asiento anulado",
            detail="Un asiento anulado no puede ser publicado.",
            code="JOURNAL_ENTRY_VOIDED",
        )

    entry.status = "posted"
    entry.posted_at = datetime.now(timezone.utc)
    db.flush()
    db.refresh(entry)
    return _to_journal_entry_read(entry)


def _to_journal_entry_read(entry: JournalEntry) -> JournalEntryRead:
    return JournalEntryRead(
        id=entry.id,
        tenant_id=entry.tenant_id,
        entry_date=entry.entry_date,
        description=entry.description,
        status=entry.status,
        total_debit=f"{entry.total_debit:.2f}",
        total_credit=f"{entry.total_credit:.2f}",
        posted_at=entry.posted_at,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
        lines=[
            JournalLineRead(
                id=line.id,
                tenant_id=line.tenant_id,
                entry_id=line.entry_id,
                account_id=line.account_id,
                debit=f"{line.debit:.2f}",
                credit=f"{line.credit:.2f}",
                memo=line.memo,
                created_at=line.created_at,
            )
            for line in entry.lines
        ],
    )


# =========================================================================
# Clase AccountingService para retrocompatibilidad con clases existentes
# =========================================================================
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
        for line in data.lines:
            if not self.repo.get_account_by_id(line.account_id):
                raise DomainException(
                    "Cuenta inexistente",
                    f"La cuenta con ID {line.account_id} no existe en el plan de cuentas.",
                    400,
                )

        total_debit = sum(Decimal(str(line.debit)) for line in data.lines)
        total_credit = sum(Decimal(str(line.credit)) for line in data.lines)

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
                    debit=Decimal(str(line.debit)),
                    credit=Decimal(str(line.credit)),
                    memo=line.memo,
                )
            )

        return self.repo.create_journal_entry(entry)
