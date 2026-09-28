#!/usr/bin/env python3
"""Genera el spec OpenAPI actualizado desde la app FastAPI."""
import json
import os
import sys
from pathlib import Path

# Agregar raíz de apps/api al sys.path
api_root = Path(__file__).resolve().parents[1]
if str(api_root) not in sys.path:
    sys.path.insert(0, str(api_root))

from app.main import app

spec = app.openapi()
out = Path(__file__).resolve().parents[2] / "openapi" / "fase1.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"OpenAPI spec generado en {out}")
