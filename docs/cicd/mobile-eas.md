# Estrategia de CI/CD para Mobile (Expo / React Native)

Este documento detalla la arquitectura de integración y entrega continua para la aplicación móvil (`apps/mobile`), basada en Expo React Native y EAS (Expo Application Services).

---

## 1. Justificación de Aislamiento del Pipeline Mobile

En un monorepo Turborepo, compilar binarios nativos para plataformas móviles introduce consideraciones críticas:

1. **Requisitos de Infraestructura Pesada:**
   - Compilar aplicaciones iOS (`.ipa`) requiere obligatoriamente runners con macOS, Xcode y certificados de aprovisionamiento de Apple Developer.
   - Compilar aplicaciones Android (`.aab` / `.apk`) requiere entornos con Android NDK/SDK, Gradle y JDK configurados.
2. **Tiempos y Costos de Ejecución:**
   - La compilación rutinaria de código web/API toma **1-3 minutos**.
   - Una compilación nativa completa toma entre **15 y 25 minutos**, consumiendo minutos de cómputo en GitHub Actions a costos significativamente superiores (especialmente las instancias macOS).
3. **Decisión Arquitectónica:**
   - **En cada PR o commit:** Solo se valida el código fuente móvil mediante **Linting**, **TypeScript Type-Check** (`npm run type-check`) y compatibilidad del contrato de API compartida (`@pasteleria/api-client`).
   - **La generación de binarios e instalación física (.apk, .aab, .ipa):** Se delega en la nube a **EAS Build** mediante disparadores selectivos (etiquetas Git semánticas).

---

## 2. Configuración de EAS Build (`eas.json`)

El archivo [`apps/mobile/eas.json`](../../apps/mobile/eas.json) define los perfiles de compilación desacoplados según el ciclo de vida del producto:

```json
{
  "$schema": "https://openapi.expo.dev/eas-json.schema.json",
  "cli": {
    "version": ">= 10.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "env": {
        "EXPO_PUBLIC_API_URL": "http://10.0.2.2:4000/v1",
        "EXPO_PUBLIC_TENANT_ID": "default-atelier"
      },
      "android": {
        "gradleCommand": ":app:assembleDebug"
      },
      "ios": {
        "simulator": true
      }
    },
    "preview": {
      "distribution": "internal",
      "env": {
        "EXPO_PUBLIC_API_URL": "https://api-staging.pasteleria-delice.com/v1",
        "EXPO_PUBLIC_TENANT_ID": "default-atelier"
      },
      "android": {
        "buildType": "apk"
      },
      "ios": {
        "simulator": false
      }
    },
    "production": {
      "env": {
        "EXPO_PUBLIC_API_URL": "https://api.pasteleria-delice.com/v1"
      },
      "android": {
        "buildType": "app-bundle"
      },
      "ios": {
        "enterpriseProvisioning": "adhoc"
      }
    }
  }
}
```

### Descripción de Perfiles:
- **`development`:** Genera clientes de desarrollo nativos con el SDK de depuración habilitado para correr en emuladores (Android Studio AVD y simulador iOS). Conecta al backend local (`10.0.2.2` para emulador Android).
- **`preview`:** Compila archivos ejecutables directos (`.apk` instalable en Android sin pasar por Play Store) y distribuciones Ad-Hoc internas para que los dueños de la pastelería y testeadores puedan probar la app en dispositivos reales.
- **`production`:** Genera paquetes optimizados para publicación oficial en tiendas: **Android App Bundle (`.aab`)** para Google Play Store y binario firmado para **Apple TestFlight / App Store**.

---

## 3. Disparo Mediante Etiquetas Git (Git Tags)

Para evitar compilaciones móviles accidentales o costosas en cada Pull Request, el pipeline de compilación nativa se dispara **únicamente** mediante etiquetas Git con el prefijo `mobile-v*`:

### Flujo de Lanzamiento:
1. Asegurar que los tests y type-checks pasan en `main`.
2. Crear y enviar una etiqueta Git:
   ```bash
   # Para versión Preview / Staging
   git tag mobile-v1.0.0-preview.1
   git push origin mobile-v1.0.0-preview.1

   # Para versión Release Production
   git tag mobile-v1.0.0
   git push origin mobile-v1.0.0
   ```
3. GitHub Actions detecta la etiqueta y ejecuta `eas build --profile <perfil> --non-interactive` autenticado mediante el token de servicio `EXPO_TOKEN` almacenado en los GitHub Secrets del repositorio.

---

## 4. Gestión de Certificados y Credenciales Móviles

Bajo ninguna circunstancia se versionan certificados ni almacenes de claves en el repositorio:
- Los archivos `*.keystore`, `*.jks`, `*.p8`, `*.p12` y `*.mobileprovision` están bloqueados por `.gitignore` y auditados por `scripts/check-secrets.py`.
- **EAS Credentials:** La gestión de firmas de producción (Keystore de Google Play y certificados de distribución de Apple) se almacena de forma segura y cifrada en el gestor de credenciales de EAS en la nube (`eas credentials`), permitiendo compilaciones automáticas y seguras sin manipulación manual de archivos sensibles.
