import os
import re
import sys

PATTERNS = [
    (r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", "Llave privada criptográfica"),
    (r"AIza[0-9A-Za-z\\-_]{35}", "API Key de Google"),
    (r"ghp_[0-9a-zA-Z]{36}", "GitHub Personal Access Token"),
    (r"xox[baprs]-[0-9a-zA-Z]{10,48}", "Token de Slack"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"(?i)caf[\s_:=]+[a-z0-9+/=]{40,}", "Contenido o XML CAF"),
    (r"(?i)sii[\s_:=]+password[\s_:=]+[^\s]{6,}", "Clave de SII en texto plano")
]

EXCLUDED_DIRS = {"node_modules", ".venv", ".git", ".next", ".turbo", "dist", "build", ".expo"}

def scan():
    findings = []
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for f in files:
            if f.endswith((".png", ".jpg", ".jpeg", ".webp", ".ico", ".pdf", ".zip", ".bin")):
                continue
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                    content = handle.read()
                    for pattern, desc in PATTERNS:
                        if re.search(pattern, content):
                            findings.append((path, desc))
            except Exception:
                pass

    if findings:
        print("[ALERTA DE SEGURIDAD] Se encontraron posibles secretos en el repositorio:")
        for path, desc in findings:
            print(f" - {desc}: {os.path.relpath(path, root_dir)}")
        sys.exit(1)
    else:
        print("[SEGURO] Auditoria de secretos superada con exito. Cero secretos encontrados.")

if __name__ == "__main__":
    scan()
