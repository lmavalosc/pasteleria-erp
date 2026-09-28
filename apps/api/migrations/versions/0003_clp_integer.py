"""convert CLP monetary columns to BIGINT for SII compliance

Revision ID: 0003_clp_integer
Revises: 0002_rls_memberships
Create Date: 2026-09-27

"""
from alembic import op

revision = "0003_clp_integer"
down_revision = "0002_rls_memberships"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        -- DTE Invoices: montos deben ser enteros para CLP
        ALTER TABLE dte_invoices
            ALTER COLUMN subtotal TYPE BIGINT USING ROUND(COALESCE(subtotal, 0))::BIGINT,
            ALTER COLUMN tax_amount TYPE BIGINT USING ROUND(COALESCE(tax_amount, 0))::BIGINT,
            ALTER COLUMN total TYPE BIGINT USING ROUND(total)::BIGINT;

        -- DTE Invoice Items: line_total y tax_amount enteros
        ALTER TABLE dte_invoice_items
            ALTER COLUMN tax_amount TYPE BIGINT USING ROUND(COALESCE(tax_amount, 0))::BIGINT,
            ALTER COLUMN line_total TYPE BIGINT USING ROUND(line_total)::BIGINT;

        -- Agregar CHECK constraint para IVA estándar: total = subtotal + tax_amount
        -- (solo cuando currency = 'CLP' y subtotal IS NOT NULL)
        ALTER TABLE dte_invoices
            ADD CONSTRAINT dte_invoices_clp_total_check
            CHECK (
                currency != 'CLP'
                OR subtotal IS NULL
                OR total = subtotal + tax_amount
            );

        -- Constraint para redondeo de IVA: ±1 peso de tolerancia
        -- IVA 19%: tax_amount BETWEEN floor(subtotal * 0.19) AND ceil(subtotal * 0.19)
        ALTER TABLE dte_invoices
            ADD CONSTRAINT dte_invoices_clp_iva_check
            CHECK (
                currency != 'CLP'
                OR subtotal IS NULL
                OR tax_amount IS NULL
                OR (
                    tax_amount >= FLOOR(subtotal * 0.19)
                    AND tax_amount <= CEIL(subtotal * 0.19)
                )
            );
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE dte_invoices DROP CONSTRAINT IF EXISTS dte_invoices_clp_iva_check;
        ALTER TABLE dte_invoices DROP CONSTRAINT IF EXISTS dte_invoices_clp_total_check;

        ALTER TABLE dte_invoice_items
            ALTER COLUMN tax_amount TYPE NUMERIC(18,2),
            ALTER COLUMN line_total TYPE NUMERIC(18,2);

        ALTER TABLE dte_invoices
            ALTER COLUMN subtotal TYPE NUMERIC(18,2),
            ALTER COLUMN tax_amount TYPE NUMERIC(18,2),
            ALTER COLUMN total TYPE NUMERIC(18,2);
        """
    )
