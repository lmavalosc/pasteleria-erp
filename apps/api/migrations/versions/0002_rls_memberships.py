"""add RLS policy to memberships table and force RLS on all tenant tables

Revision ID: 0002_rls_memberships
Revises: 0001_fase1_initial
Create Date: 2026-09-27 00:00:00.000000

"""
from alembic import op

revision = "0002_rls_memberships"
down_revision = "0001_fase1_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        -- Habilitar RLS en memberships
        ALTER TABLE memberships ENABLE ROW LEVEL SECURITY;

        -- Politica: cada tenant solo ve sus propios memberships
        CREATE POLICY tenant_isolation_memberships
            ON memberships
            USING (tenant_id = NULLIF(CURRENT_SETTING('app.tenant_id', TRUE), '')::UUID)
            WITH CHECK (tenant_id = NULLIF(CURRENT_SETTING('app.tenant_id', TRUE), '')::UUID);

        -- Forzar RLS en memberships y en todas las entidades multitenant
        -- para garantizar aislamiento estricto incluso con table owner
        ALTER TABLE memberships FORCE ROW LEVEL SECURITY;
        ALTER TABLE accounting_accounts FORCE ROW LEVEL SECURITY;
        ALTER TABLE journal_entries FORCE ROW LEVEL SECURITY;
        ALTER TABLE journal_lines FORCE ROW LEVEL SECURITY;
        ALTER TABLE documents FORCE ROW LEVEL SECURITY;
        ALTER TABLE expenses FORCE ROW LEVEL SECURITY;
        ALTER TABLE dte_invoices FORCE ROW LEVEL SECURITY;
        ALTER TABLE dte_invoice_items FORCE ROW LEVEL SECURITY;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP POLICY IF EXISTS tenant_isolation_memberships ON memberships;
        ALTER TABLE memberships DISABLE ROW LEVEL SECURITY;
        ALTER TABLE memberships NO FORCE ROW LEVEL SECURITY;
        ALTER TABLE accounting_accounts NO FORCE ROW LEVEL SECURITY;
        ALTER TABLE journal_entries NO FORCE ROW LEVEL SECURITY;
        ALTER TABLE journal_lines NO FORCE ROW LEVEL SECURITY;
        ALTER TABLE documents NO FORCE ROW LEVEL SECURITY;
        ALTER TABLE expenses NO FORCE ROW LEVEL SECURITY;
        ALTER TABLE dte_invoices NO FORCE ROW LEVEL SECURITY;
        ALTER TABLE dte_invoice_items NO FORCE ROW LEVEL SECURITY;
        """
    )
