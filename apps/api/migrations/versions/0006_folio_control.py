"""create folio_ranges table for pessimistic locking

Revision ID: 0006_folio_control
Revises: 0005_double_entry_trigger
Create Date: 2026-09-27

"""
from alembic import op

revision = "0006_folio_control"
down_revision = "0005_double_entry_trigger"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE folio_ranges (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            dte_type TEXT NOT NULL,
            range_start INTEGER NOT NULL CHECK (range_start > 0),
            range_end INTEGER NOT NULL CHECK (range_end >= range_start),
            next_folio INTEGER NOT NULL CHECK (next_folio >= range_start),
            caf_xml TEXT,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (tenant_id, dte_type, range_start)
        );

        CREATE INDEX idx_folio_ranges_active
            ON folio_ranges(tenant_id, dte_type, is_active)
            WHERE is_active = TRUE;

        -- Row-Level Security
        ALTER TABLE folio_ranges ENABLE ROW LEVEL SECURITY;
        CREATE POLICY tenant_isolation_folio_ranges
            ON folio_ranges
            USING (tenant_id = NULLIF(CURRENT_SETTING('app.tenant_id', TRUE), '')::UUID)
            WITH CHECK (tenant_id = NULLIF(CURRENT_SETTING('app.tenant_id', TRUE), '')::UUID);

        ALTER TABLE folio_ranges FORCE ROW LEVEL SECURITY;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP POLICY IF EXISTS tenant_isolation_folio_ranges ON folio_ranges;
        DROP TABLE IF EXISTS folio_ranges;
        """
    )
