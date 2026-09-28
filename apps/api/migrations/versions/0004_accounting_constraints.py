"""add accounting safety constraints and functions

Revision ID: 0004_accounting_constraints
Revises: 0003_clp_integer
Create Date: 2026-09-27

"""
from alembic import op

revision = "0004_accounting_constraints"
down_revision = "0003_clp_integer"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        -- Constraint: status de journal_entries solo puede avanzar
        -- draft -> posted -> voided (no se puede "despublicar")
        CREATE OR REPLACE FUNCTION check_journal_status_transition()
        RETURNS TRIGGER AS $$
        BEGIN
            IF OLD.status = 'voided' THEN
                RAISE EXCEPTION 'Un asiento anulado no puede cambiar de estado.';
            END IF;
            IF OLD.status = 'posted' AND NEW.status = 'draft' THEN
                RAISE EXCEPTION 'Un asiento publicado no puede volver a borrador.';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS trg_journal_entry_status_transition ON journal_entries;
        CREATE TRIGGER trg_journal_entry_status_transition
            BEFORE UPDATE OF status ON journal_entries
            FOR EACH ROW
            EXECUTE FUNCTION check_journal_status_transition();

        -- Constraint: no permitir UPDATE/DELETE de journal_lines si el entry esta posted
        CREATE OR REPLACE FUNCTION prevent_posted_line_mutation()
        RETURNS TRIGGER AS $$
        DECLARE
            entry_status TEXT;
        BEGIN
            SELECT status INTO entry_status
            FROM journal_entries
            WHERE id = COALESCE(OLD.entry_id, NEW.entry_id);

            IF entry_status = 'posted' THEN
                RAISE EXCEPTION
                    'No se pueden modificar líneas de un asiento contable publicado (posted). Anule el asiento primero.';
            END IF;
            RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS trg_journal_lines_immutable_when_posted ON journal_lines;
        CREATE TRIGGER trg_journal_lines_immutable_when_posted
            BEFORE UPDATE OR DELETE ON journal_lines
            FOR EACH ROW
            EXECUTE FUNCTION prevent_posted_line_mutation();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_journal_lines_immutable_when_posted ON journal_lines;
        DROP FUNCTION IF EXISTS prevent_posted_line_mutation();
        DROP TRIGGER IF EXISTS trg_journal_entry_status_transition ON journal_entries;
        DROP FUNCTION IF EXISTS check_journal_status_transition();
        """
    )
