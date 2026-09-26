-- Seed mínimo para desarrollo local.
-- No usar en producción.

INSERT INTO tenants (id, name, tax_id, status)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Demo SpA',
    '76000000-9',
    'active'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO users (id, email, name, password_hash, status)
VALUES (
    '00000000-0000-0000-0000-000000000101',
    'demo@example.com',
    'Usuario Demo',
    NULL,
    'active'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO memberships (tenant_id, user_id, role)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000101',
    'owner'
)
ON CONFLICT (tenant_id, user_id) DO NOTHING;

INSERT INTO accounting_accounts (tenant_id, code, name, account_type, is_active)
VALUES
    ('00000000-0000-0000-0000-000000000001', '1110101', 'Caja', 'asset', TRUE),
    ('00000000-0000-0000-0000-000000000001', '1110201', 'Bancos', 'asset', TRUE),
    ('00000000-0000-0000-0000-000000000001', '2110101', 'IVA por pagar', 'liability', TRUE),
    ('00000000-0000-0000-0000-000000000001', '3110101', 'Capital', 'equity', TRUE),
    ('00000000-0000-0000-0000-000000000001', '4110101', 'Ventas', 'income', TRUE),
    ('00000000-0000-0000-0000-000000000001', '5110101', 'Gastos operacionales', 'expense', TRUE)
ON CONFLICT (tenant_id, code) DO NOTHING;
