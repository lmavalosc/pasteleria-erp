# 🍰 Maison du Délice — Monorepo de Pastelería & Repostería de Autor

Monorepo empresarial de alto rendimiento configurado con **Turborepo**, **pnpm / npm workspaces**, **Next.js 14**, **FastAPI**, **React Native (Expo)**, **OpenAPI Client tipado**, **Librería de Componentes UI** y **Tipos Compartidos**.

---

## 🏛️ Estructura del Monorepo

```text
mi-proyecto/ (PASTELERÍA)
├── apps/
│   ├── web/                     # Next.js 14 (App Router, catálogo gourmet, cotizador de autor)
│   ├── api/                     # FastAPI (Backend REST Python, routers modulares, multitenant)
│   └── mobile/                  # React Native + Expo (App móvil iOS & Android)
├── packages/
│   ├── shared-types/            # Tipos TypeScript generados y alineados con OpenAPI
│   ├── api-client/              # Cliente API compartido con fallback offline mock
│   └── ui/                      # Componentes UI compartidos y tokens de marca (Gourmet theme)
├── openapi/
│   └── fase1.yaml               # Contrato formal de API Fase 1 (OpenAPI 3.0.3)
├── docs/
│   ├── adr/
│   │   └── 0001-multitenancy.md # Registro de decisión arquitectónica sobre multitenancy
│   └── dod/
│       └── fase1.md             # Criterios de aceptación (Definition of Done) Fase 1
├── package.json                 # Workspaces raíz y scripts de orquestación Turborepo
├── pnpm-workspace.yaml          # Configuración de workspaces para pnpm
├── turbo.json                   # Pipeline de compilación y caché de Turborepo 2.x
├── tsconfig.base.json           # Configuración base de TypeScript y path mapping
├── .gitignore                   # Exclusiones de Git
└── .env.example                 # Variables de entorno de referencia para web, api y mobile
```

---

## 📦 Aplicaciones y Paquetes

| Módulo | Tipo | Descripción | Tecnologías Principales |
| :--- | :--- | :--- | :--- |
| `apps/web` | Web App | Tienda web de alta pastelería, catálogo, pedidos y carrito | Next.js 14, React 18, CSS Vanilla moderno |
| `apps/api` | Backend API | API REST modular, catálogo, pedidos y multitenant | Python 3.10+, FastAPI, Pydantic v2, Uvicorn |
| `apps/mobile` | Mobile App | Aplicación móvil para clientes con seguimiento de pedidos | React Native 0.74, Expo SDK 51, TypeScript |
| `packages/shared-types` | Package | Modelos y contratos de TypeScript comunes | TypeScript puro |
| `packages/api-client` | Package | Cliente HTTP tipado generado desde el contrato OpenAPI | OpenAPI 3.0, openapi-typescript, Fetch API |
| `packages/ui` | Package | Sistema de diseño (oro, rosa, cacao), Button, Badge, Card... | React 18+, CSS-in-JS Tokens |

---

## 🚀 Comandos Rápidos de Ejecución

### 1. Instalación de Dependencias
Puedes usar **npm** o **pnpm**:
```bash
# Con npm
npm install

# Con pnpm
pnpm install
```

### 2. Desarrollo con Turborepo
Para levantar todo en paralelo:
```bash
npm run dev
# o con pnpm
pnpm dev
```

Para levantar entornos individuales:
- **Solo Frontend Web (Next.js 14):**
  ```bash
  npm run dev:web       # http://localhost:3000
  ```
- **Solo Backend API (FastAPI):**
  ```bash
  npm run dev:api       # http://localhost:4000/docs
  ```
- **Solo App Móvil (Expo React Native):**
  ```bash
  npm run dev:mobile
  ```

### 3. Compilación y Calidad de Código
```bash
# Compilar todos los paquetes y apps
npm run build

# Verificación estática de tipos en todo el monorepo
npm run type-check

# Linter unificado
npm run lint
```

### 4. Regenerar Cliente OpenAPI
Para regenerar los tipos a partir de `openapi/fase1.yaml`:
```bash
npm run generate:api
```

---

## 📚 Documentación de Arquitectura

- [ADR 0001: Estrategia de Arquitectura Multi-Tenant](file:///docs/adr/0001-multitenancy.md)
- [DoD: Criterios de Aceptación Fase 1](file:///docs/dod/fase1.md)
- [Especificación OpenAPI Fase 1](file:///openapi/fase1.yaml)
- [Documentación del Backend FastAPI](file:///apps/api/README.md)
