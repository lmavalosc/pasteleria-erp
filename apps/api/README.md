# 🐍 Backend FastAPI — Pastelería Gourmet (Fase 1)

API REST construida con **FastAPI**, **Pydantic v2** y arquitectura multi-tenant según el ADR 0001.

---

## 🛠️ Tecnologías
- **Python 3.10+**
- **FastAPI**
- **Uvicorn**
- **Pydantic v2**

---

## 🚀 Puesta en marcha

### 1. Crear entorno virtual e instalar dependencias
```bash
python -m venv .venv

# En Windows:
.venv\Scripts\activate

# En macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Iniciar servidor de desarrollo
```bash
uvicorn main:app --reload --port 4000
```

O desde la raíz del monorepo mediante Turborepo:
```bash
npm run dev --filter=@pasteleria/api
```

---

## 📚 Documentación Interactiva

- **Swagger UI:** [http://localhost:4000/docs](http://localhost:4000/docs)
- **ReDoc:** [http://localhost:4000/redoc](http://localhost:4000/redoc)
- **OpenAPI JSON:** [http://localhost:4000/v1/openapi.json](http://localhost:4000/v1/openapi.json)
