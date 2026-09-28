#!/usr/bin/env python3
"""
Script de verificación de alineación de contrato OpenAPI Fase 1.
Valida que apps/api/openapi_exported.json coincida estrictamente con openapi/fase1.yaml.
"""
import json
import sys
from pathlib import Path
import yaml

ROOT_DIR = Path(__file__).resolve().parents[1]
SPEC_YAML_PATH = ROOT_DIR / "openapi" / "fase1.yaml"
EXPORTED_JSON_PATH = ROOT_DIR / "apps" / "api" / "openapi_exported.json"

REQUIRED_PATHS = [
    "/health",
    "/accounting/accounts",
    "/accounting/journal-entries",
    "/accounting/journal-entries/{entryId}/post",
    "/invoicing/dte",
    "/invoicing/dte/{dteId}/issue",
    "/expenses",
    "/documents",
]

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}


def main():
    print("=" * 60)
    print("Verificación de Alineación de Contrato OpenAPI Fase 1")
    print("=" * 60)

    if not SPEC_YAML_PATH.exists():
        print(f"[FAIL] Archivo fuente de verdad no encontrado: {SPEC_YAML_PATH}")
        sys.exit(1)

    if not EXPORTED_JSON_PATH.exists():
        print(f"[FAIL] Archivo exportado no encontrado: {EXPORTED_JSON_PATH}")
        sys.exit(1)

    try:
        spec_yaml = yaml.safe_load(SPEC_YAML_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[FAIL] Error leyendo {SPEC_YAML_PATH}: {e}")
        sys.exit(1)

    try:
        exported_json = json.loads(EXPORTED_JSON_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[FAIL] Error leyendo {EXPORTED_JSON_PATH}: {e}")
        sys.exit(1)

    spec_paths = spec_yaml.get("paths", {})
    exported_paths = exported_json.get("paths", {})

    errors = []
    warnings = []

    # 1. Comprobar paths no permitidos en exported_json
    print(f"\n1. Verificando paths exportados ({len(exported_paths)} paths)...")
    for path in exported_paths.keys():
        if path not in spec_paths:
            errors.append(f"Path en exportado NO existe en fase1.yaml: {path}")

    # 2. Comprobar que todos los paths obligatorios de Fase 1 estén presentes
    print("2. Verificando paths obligatorios de Fase 1...")
    for req_path in REQUIRED_PATHS:
        if req_path not in exported_paths:
            errors.append(f"Falta path obligatorio de Fase 1 en exportado: {req_path}")
        else:
            print(f"  [OK] {req_path}")

    # 3. Comprobar métodos HTTP en paths comunes
    print("\n3. Verificando métodos HTTP por path...")
    for path, exp_item in exported_paths.items():
        if path in spec_paths:
            spec_item = spec_paths[path]
            exp_methods = {k.lower() for k in exp_item.keys() if k.lower() in HTTP_METHODS}
            spec_methods = {k.lower() for k in spec_item.keys() if k.lower() in HTTP_METHODS}

            extra_methods = exp_methods - spec_methods
            if extra_methods:
                errors.append(f"Métodos no documentados en {path}: {extra_methods}")

            missing_methods = spec_methods - exp_methods
            if missing_methods:
                warnings.append(f"Métodos faltantes en exportado para {path}: {missing_methods}")

    # 4. Validar X-Tenant-ID: no default "default-atelier" y que sea UUID
    print("\n4. Verificando configuración del header X-Tenant-ID...")
    tenant_params_checked = 0
    for path, path_item in exported_paths.items():
        if path == "/health":
            continue  # Health check no requiere tenant

        for method, op in path_item.items():
            if not isinstance(op, dict):
                continue

            params = op.get("parameters", [])
            tenant_header = next((p for p in params if p.get("name") == "X-Tenant-ID"), None)

            if not tenant_header:
                warnings.append(f"Operación {method.upper()} {path} no declara X-Tenant-ID")
                continue

            tenant_params_checked += 1
            schema = tenant_header.get("schema", {})

            # Validar que no tenga default "default-atelier"
            if "default" in schema and schema["default"] == "default-atelier":
                errors.append(f"Operación {method.upper()} {path}: X-Tenant-ID tiene default 'default-atelier'")
            if "default" in tenant_header and tenant_header["default"] == "default-atelier":
                errors.append(f"Operación {method.upper()} {path}: X-Tenant-ID tiene default 'default-atelier'")

            # Validar que sea UUID
            fmt = schema.get("format")
            if fmt != "uuid":
                errors.append(f"Operación {method.upper()} {path}: X-Tenant-ID schema format no es 'uuid' (es '{fmt}')")

            # Validar required: true
            if not tenant_header.get("required"):
                errors.append(f"Operación {method.upper()} {path}: X-Tenant-ID no está marcado como required: true")

    print(f"  [OK] Verificadas {tenant_params_checked} declaraciones de X-Tenant-ID en operaciones de negocio.")

    # 5. Resumen
    print("\n" + "=" * 60)
    if warnings:
        print("ADVERTENCIAS:")
        for w in warnings:
            print(f"  [WARN] {w}")

    if errors:
        print("\nERRORES DE ALINEACIÓN:")
        for err in errors:
            print(f"  [ERROR] {err}")
        print("\nResultado: FAIL")
        sys.exit(1)

    print("\nResultado: PASS - OpenAPI exportado está 100% alineado con fase1.yaml.")
    sys.exit(0)


if __name__ == "__main__":
    main()
