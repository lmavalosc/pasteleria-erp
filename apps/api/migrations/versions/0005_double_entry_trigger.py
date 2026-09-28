"""add deferred constraint trigger to enforce double-entry balance

Revision ID: 0005_double_entry_trigger
Revises: 0004_accounting_constraints
Create Date: 2026-09-27

"""
from alembic import op

revision = "0005_double_entry_trigger"
down_revision = "0004_accounting_constraints"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION sync_and_verify_journal_balance()
        RETURNS TRIGGER AS $$
        DECLARE
            target_entry_id UUID;
            new_debit NUMERIC(18,2);
            new_credit NUMERIC(18,2);
        BEGIN
            target_entry_id := COALESCE(NEW.entry_id, OLD.entry_id);

            SELECT
                COALESCE(SUM(debit), 0),
                COALESCE(SUM(credit), 0)
            INTO new_debit, new_credit
            FROM journal_lines
            WHERE entry_id = target_entry_id;

            UPDATE journal_entries
            SET total_debit = new_debit,
                total_credit = new_credit
            WHERE id = target_entry_id;

            IF new_debit != new_credit THEN
                RAISE EXCEPTION
                    'Asiento contable desbalanceado en base de datos: total_debit (%) != total_credit (%)',
                    new_debit, new_credit;
            END IF;

            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS trg_sync_journal_totals ON journal_lines;
        CREATE CONSTRAINT TRIGGER trg_sync_journal_totals
            AFTER INSERT OR UPDATE OR DELETE ON journal_lines
            DEFERRABLE INITIALLY DEFERRED
            FOR EACH ROW
            EXECUTE FUNCTION sync_and_verify_journal_balance();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_sync_journal_totals ON journal_lines;
        DROP FUNCTION IF EXISTS sync_and_verify_journal_balance();
        """
    )
