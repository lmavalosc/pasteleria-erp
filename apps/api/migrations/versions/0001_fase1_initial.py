"""fase1 initial schema

Revision ID: 0001_fase1_initial
Revises: 
Create Date: 2026-09-26 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_fase1_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE EXTENSION IF NOT EXISTS pgcrypto;

        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        --------------------------------------------------
        -- TENANTS
        --------------------------------------------------
        CREATE TABLE tenants (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            tax_id TEXT,
            status TEXT NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'suspended', 'deleted')),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE INDEX idx_tenants_status ON tenants(status);

        --------------------------------------------------
        -- USERS
        --------------------------------------------------
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email TEXT NOT NULL UNIQUE,
            name TEXT,
            password_hash TEXT,
            status TEXT NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'invited', 'disabled', 'deleted')),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT users_email_lowercase CHECK (email = LOWER(email))
        );

        --------------------------------------------------
        -- MEMBERSHIPS
        --------------------------------------------------
        CREATE TABLE memberships (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role TEXT NOT NULL DEFAULT 'member'
                CHECK (role IN ('owner', 'admin', 'accountant', 'approver', 'member', 'viewer')),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (tenant_id, user_id)
        );

        CREATE INDEX idx_memberships_tenant ON memberships(tenant_id);
        CREATE INDEX idx_memberships_user ON memberships(user_id);

        --------------------------------------------------
        -- ACCOUNTING ACCOUNTS
        --------------------------------------------------
        CREATE TABLE accounting_accounts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            parent_id UUID REFERENCES accounting_accounts(id) ON DELETE SET NULL,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            account_type TEXT NOT NULL
                CHECK (account_type IN ('asset', 'liability', 'equity', 'income', 'expense')),
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT accounting_accounts_code_format
                CHECK (code ~ '^[0-9.]{1,25}$'),
            UNIQUE (tenant_id, code)
        );

        CREATE INDEX idx_accounting_accounts_tenant ON accounting_accounts(tenant_id);
        CREATE INDEX idx_accounting_accounts_type ON accounting_accounts(tenant_id, account_type);
        CREATE INDEX idx_accounting_accounts_active ON accounting_accounts(tenant_id, is_active);
        CREATE INDEX idx_accounting_accounts_parent ON accounting_accounts(parent_id);

        --------------------------------------------------
        -- JOURNAL ENTRIES
        --------------------------------------------------
        CREATE TABLE journal_entries (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            entry_date DATE NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft'
                CHECK (status IN ('draft', 'posted', 'voided')),
            total_debit NUMERIC(18, 2) NOT NULL DEFAULT 0,
            total_credit NUMERIC(18, 2) NOT NULL DEFAULT 0,
            posted_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT journal_entries_total_debit_non_negative CHECK (total_debit >= 0),
            CONSTRAINT journal_entries_total_credit_non_negative CHECK (total_credit >= 0),
            CONSTRAINT journal_entries_balance CHECK (total_debit = total_credit)
        );

        CREATE INDEX idx_journal_entries_tenant_date ON journal_entries(tenant_id, entry_date);
        CREATE INDEX idx_journal_entries_tenant_status ON journal_entries(tenant_id, status);

        --------------------------------------------------
        -- JOURNAL LINES
        --------------------------------------------------
        CREATE TABLE journal_lines (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            entry_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
            account_id UUID NOT NULL REFERENCES accounting_accounts(id) ON DELETE RESTRICT,
            debit NUMERIC(18, 2) NOT NULL DEFAULT 0,
            credit NUMERIC(18, 2) NOT NULL DEFAULT 0,
            memo TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT journal_lines_debit_non_negative CHECK (debit >= 0),
            CONSTRAINT journal_lines_credit_non_negative CHECK (credit >= 0),
            CONSTRAINT journal_lines_not_both_zero CHECK (NOT (debit = 0 AND credit = 0)),
            CONSTRAINT journal_lines_not_both_positive CHECK (NOT (debit > 0 AND credit > 0))
        );

        CREATE INDEX idx_journal_lines_tenant ON journal_lines(tenant_id);
        CREATE INDEX idx_journal_lines_entry ON journal_lines(entry_id);
        CREATE INDEX idx_journal_lines_account ON journal_lines(account_id);

        --------------------------------------------------
        -- DOCUMENTS
        --------------------------------------------------
        CREATE TABLE documents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            filename TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            size_bytes BIGINT NOT NULL DEFAULT 0,
            checksum_sha256 TEXT,
            storage_provider TEXT NOT NULL DEFAULT 'local'
                CHECK (storage_provider IN ('local', 's3', 'gcs', 'azure')),
            storage_uri TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT documents_size_non_negative CHECK (size_bytes >= 0),
            CONSTRAINT documents_checksum_format
                CHECK (checksum_sha256 IS NULL OR checksum_sha256 ~ '^[a-fA-F0-9]{64}$')
        );

        CREATE INDEX idx_documents_tenant ON documents(tenant_id);
        CREATE INDEX idx_documents_created_at ON documents(tenant_id, created_at DESC);

        --------------------------------------------------
        -- EXPENSES
        --------------------------------------------------
        CREATE TABLE expenses (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            expense_date DATE NOT NULL,
            amount NUMERIC(18, 2) NOT NULL,
            currency TEXT NOT NULL DEFAULT 'CLP'
                CHECK (currency IN ('CLP', 'USD')),
            status TEXT NOT NULL DEFAULT 'draft'
                CHECK (status IN ('draft', 'submitted', 'approved', 'paid', 'rejected')),
            document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
            description TEXT,
            merchant TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT expenses_amount_non_negative CHECK (amount >= 0)
        );

        CREATE INDEX idx_expenses_tenant_date ON expenses(tenant_id, expense_date);
        CREATE INDEX idx_expenses_tenant_status ON expenses(tenant_id, status);
        CREATE INDEX idx_expenses_document ON expenses(document_id);

        --------------------------------------------------
        -- DTE INVOICES
        --------------------------------------------------
        CREATE TABLE dte_invoices (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            dte_type TEXT NOT NULL
                CHECK (dte_type IN (
                    '33', '34', '39', '41', '43', '45', '46',
                    '52', '56', '61', '110', '111', '112'
                )),
            folio INTEGER NOT NULL,
            issue_date DATE NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft'
                CHECK (status IN ('draft', 'issued', 'accepted', 'rejected', 'annulled')),
            currency TEXT NOT NULL DEFAULT 'CLP'
                CHECK (currency IN ('CLP', 'USD')),
            recipient_rut TEXT,
            recipient_name TEXT,
            subtotal NUMERIC(18, 2),
            tax_amount NUMERIC(18, 2),
            total NUMERIC(18, 2) NOT NULL,
            sii_receipt_uri TEXT,
            sii_track_id TEXT,
            emitted_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT dte_invoices_folio_positive CHECK (folio > 0),
            CONSTRAINT dte_invoices_total_non_negative CHECK (total >= 0),
            UNIQUE (tenant_id, dte_type, folio)
        );

        CREATE INDEX idx_dte_invoices_tenant_date ON dte_invoices(tenant_id, issue_date);
        CREATE INDEX idx_dte_invoices_tenant_status ON dte_invoices(tenant_id, status);
        CREATE INDEX idx_dte_invoices_tenant_type ON dte_invoices(tenant_id, dte_type);

        --------------------------------------------------
        -- DTE INVOICE ITEMS
        --------------------------------------------------
        CREATE TABLE dte_invoice_items (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            dte_invoice_id UUID NOT NULL REFERENCES dte_invoices(id) ON DELETE CASCADE,
            line_number INTEGER NOT NULL,
            description TEXT NOT NULL,
            quantity NUMERIC(18, 3) NOT NULL DEFAULT 1,
            unit_price NUMERIC(18, 2) NOT NULL,
            discount NUMERIC(18, 2) NOT NULL DEFAULT 0,
            tax_rate NUMERIC(5, 2) NOT NULL DEFAULT 19.00,
            tax_amount NUMERIC(18, 2) NOT NULL DEFAULT 0,
            line_total NUMERIC(18, 2) NOT NULL,
            account_id UUID REFERENCES accounting_accounts(id) ON DELETE SET NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT dte_invoice_items_line_number_positive CHECK (line_number > 0),
            CONSTRAINT dte_invoice_items_quantity_non_negative CHECK (quantity >= 0),
            CONSTRAINT dte_invoice_items_unit_price_non_negative CHECK (unit_price >= 0),
            CONSTRAINT dte_invoice_items_discount_non_negative CHECK (discount >= 0),
            CONSTRAINT dte_invoice_items_tax_amount_non_negative CHECK (tax_amount >= 0),
            CONSTRAINT dte_invoice_items_line_total_non_negative CHECK (line_total >= 0),
            UNIQUE (dte_invoice_id, line_number)
        );

        CREATE INDEX idx_dte_invoice_items_tenant ON dte_invoice_items(tenant_id);
        CREATE INDEX idx_dte_invoice_items_invoice ON dte_invoice_items(dte_invoice_id);
        CREATE INDEX idx_dte_invoice_items_account ON dte_invoice_items(account_id);

        --------------------------------------------------
        -- TRIGGERS updated_at
        --------------------------------------------------
        CREATE TRIGGER trg_tenants_updated_at
            BEFORE UPDATE ON tenants
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();

        CREATE TRIGGER trg_users_updated_at
            BEFORE UPDATE ON users
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();

        CREATE TRIGGER trg_accounting_accounts_updated_at
            BEFORE UPDATE ON accounting_accounts
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();

        CREATE TRIGGER trg_journal_entries_updated_at
            BEFORE UPDATE ON journal_entries
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();

        CREATE TRIGGER trg_expenses_updated_at
            BEFORE UPDATE ON expenses
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();

        CREATE TRIGGER trg_dte_invoices_updated_at
            BEFORE UPDATE ON dte_invoices
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();

        --------------------------------------------------
        -- ROW LEVEL SECURITY (RLS)
        --------------------------------------------------
        ALTER TABLE accounting_accounts ENABLE ROW LEVEL SECURITY;
        ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
        ALTER TABLE journal_lines ENABLE ROW LEVEL SECURITY;
        ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
        ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
        ALTER TABLE dte_invoices ENABLE ROW LEVEL SECURITY;
        ALTER TABLE dte_invoice_items ENABLE ROW LEVEL SECURITY;

        CREATE POLICY tenant_isolation_accounting_accounts
            ON accounting_accounts
            USING (tenant_id = NULLIF(CURRENT_SETTING('app.tenant_id', TRUE), '')::UUID)
            WITH CHECK (tenant_id = NULLIF(CURRENT_SETTING('app.tenant_id', TRUE), '')::UUID);

        CREATE POLICY tenant_isolation_journal_entries
            ON journal_entries
            USING (tenant_id = NULLIF(CURRENT_SETTING('app.tenant_id', TRUE), '')::UUID)
            WITH CHECK (tenant_id = NULLIF(CURRENT_SETTING('app.tenant_id', TRUE), '')::UUID);

        CREATE POLICY tenant_isolation_journal_lines
            ON journal_lines
            USING (tenant_id = NULLIF(CURRENT_SETTING('app.tenant_id', TRUE), '')::UUID)
            WITH CHECK (tenant_id = NULLIF(CURRENT_SETTING('app.tenant_id', TRUE), '')::UUID);

        CREATE POLICY tenant_isolation_documents
            ON documents
            USING (tenant_id = NULLIF(CURRENT_SETTING('app.tenant_id', TRUE), '')::UUID)
            WITH CHECK (tenant_id = NULLIF(CURRENT_SETTING('app.tenant_id', TRUE), '')::UUID);

        CREATE POLICY tenant_isolation_expenses
            ON expenses
            USING (tenant_id = NULLIF(CURRENT_SETTING('app.tenant_id', TRUE), '')::UUID)
            WITH CHECK (tenant_id = NULLIF(CURRENT_SETTING('app.tenant_id', TRUE), '')::UUID);

        CREATE POLICY tenant_isolation_dte_invoices
            ON dte_invoices
            USING (tenant_id = NULLIF(CURRENT_SETTING('app.tenant_id', TRUE), '')::UUID)
            WITH CHECK (tenant_id = NULLIF(CURRENT_SETTING('app.tenant_id', TRUE), '')::UUID);

        CREATE POLICY tenant_isolation_dte_invoice_items
            ON dte_invoice_items
            USING (tenant_id = NULLIF(CURRENT_SETTING('app.tenant_id', TRUE), '')::UUID)
            WITH CHECK (tenant_id = NULLIF(CURRENT_SETTING('app.tenant_id', TRUE), '')::UUID);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS dte_invoice_items;
        DROP TABLE IF EXISTS dte_invoices;
        DROP TABLE IF EXISTS expenses;
        DROP TABLE IF EXISTS documents;
        DROP TABLE IF EXISTS journal_lines;
        DROP TABLE IF EXISTS journal_entries;
        DROP TABLE IF EXISTS accounting_accounts;
        DROP TABLE IF EXISTS memberships;
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS tenants;

        DROP FUNCTION IF EXISTS set_updated_at();
        """
    )
