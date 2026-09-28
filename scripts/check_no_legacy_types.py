"""
Verifica que no existan tipos o artefactos manuales de pastelería en paquetes y aplicaciones activas.
Excluye: archive/, node_modules/, .venv/, openapi.ts generado, etc.
"""
import os
import sys
from pathlib import Path

FORBIDDEN_PATTERNS = [
    "PasteleriaApiClient",
    "mock-data",
    "MOCK_PRODUCTS",
    "MOCK_ORDERS",
    "export type Product",
    "export type Category",
    "export interface Order",
]

EXCLUDE_DIRS = {
    "archive",
    "node_modules",
    ".venv",
    ".git",
    ".turbo",
    ".next",
    "dist",
    "build",
    "__pycache__",
    ".expo",
}

EXCLUDE_FILES = {
    "openapi.ts",
    "openapi_exported.json",
    "fase1.yaml",
    "check_no_legacy_types.py",
}

def scan_file(file_path: Path) -> list[str]:
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return violations

    for pattern in FORBIDDEN_PATTERNS:
        if pattern in content:
            violations.append(pattern)
    return violations

def main() -> int:
    root = Path(__file__).resolve().parent.parent
    scan_targets = [root / "packages", root / "apps"]
    
    found_violations: dict[str, list[str]] = {}

    for target in scan_targets:
        if not target.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(target):
            # Prune excluded directories immediately
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith(".")]
            for f in filenames:
                if f in EXCLUDE_FILES:
                    continue
                ext = Path(f).suffix.lower()
                if ext not in {".ts", ".tsx", ".js", ".jsx", ".json", ".py"}:
                    continue
                file_p = Path(dirpath) / f
                violations = scan_file(file_p)
                if violations:
                    rel_path = str(file_p.relative_to(root))
                    found_violations[rel_path] = violations

    if found_violations:
        print("[FAIL] Se encontraron artefactos/tipos manuales de pastelería prohibidos:")
        for file_path, patterns in sorted(found_violations.items()):
            print(f"  - {file_path}: {', '.join(patterns)}")
        print("\nPor favor mueve estos elementos a archive/pastry-prototype/ o elimínalos.")
        return 1

    print("[PASS] No se encontraron tipos ni artefactos manuales de pastelería en paquetes activos.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
