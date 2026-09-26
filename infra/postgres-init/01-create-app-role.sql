-- Solo desarrollo local.
-- En producción, gestionar credenciales mediante Secret Manager y permisos mínimos.

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_user') THEN
        CREATE ROLE app_user LOGIN PASSWORD 'app_password';
    END IF;
END
$$;

-- Permisos sobre la base de datos y esquema
GRANT CONNECT ON DATABASE nucleo TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;

-- Permisos sobre tablas y secuencias actuales
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Privilegios por defecto para tablas creadas en el futuro por 'nucleo' (ej. vía Alembic)
ALTER DEFAULT PRIVILEGES FOR ROLE nucleo IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;

ALTER DEFAULT PRIVILEGES FOR ROLE nucleo IN SCHEMA public
GRANT USAGE, SELECT ON SEQUENCES TO app_user;
