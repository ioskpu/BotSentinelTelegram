# Crypto Sentinel Bot - Dashboard Web Development Context

> Documento de contexto para continuidad del desarrollo con IA

**Fecha de creación:** Febrero 2026  
**Último commit:** `4e181e3` - "feat: Add web dashboard structure"  
**Repositorio:** https://github.com/ioskpu/BotSentinelTelegram

---

## 📋 Resumen del Proyecto Original

**Crypto Sentinel Bot** es un bot de Telegram para monitoreo de criptomonedas que incluye:

- Alertas de precio (por encima/debajo de umbral)
- Monitoreo de ballenas (transacciones grandes)
- Seguimiento de múltiples blockchains (Ethereum, Solana, Stellar)
- Notificaciones en tiempo real vía Telegram

### Stack Tecnológico Base
- **Backend:** Python + FastAPI
- **Bot:** python-telegram-bot
- **Base de datos:** MongoDB Atlas
- **Cache:** Redis
- **Deploy:** Fly.io

---

## 🎯 Trabajo Solicitado

El usuario solicitó crear un **dashboard web** para el Crypto Sentinel Bot con los siguientes requisitos:

1. **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS
2. **Backend:** Extender el FastAPI existente con nuevas rutas
3. **Comunicación:** WebSocket para actualizaciones en tiempo real
4. **Autenticación:** JWT tokens compatibles con Telegram
5. **Infraestructura:** Docker Compose + scripts de despliegue

---

## ✅ Trabajo Completado

### 1. Estructura Frontend (`/dashboard/`)
- **Limpieza y Calidad:** Se resolvieron errores de linter en `portfolio.service.ts`, `transaction.service.ts`, y `metrics.service.ts`.
- **Tipado:** Se añadieron interfaces faltantes (`PortfolioSummary`, `CreatePositionRequest`) y se alinearon los tipos frontend con los esquemas Pydantic del backend (snake_case).
- **Optimización:** Limpieza de imports no utilizados en `Skeleton.tsx` y `useAuth.ts`.
- **Configuración:** Corrección de `vite.config.ts` para soporte de Node.js types, `__dirname` y compatibilidad con Vitest.

### 2. Backend API Extendido (`/src/api/`)
- **Hosting Estático:** Se configuró FastAPI para servir los archivos estáticos del frontend construido desde `/dashboard/dist`.
- **Middleware:** Mejoras en la validación de tokens y manejo de errores.

### 3. Testing e Integración
- **Backend (Pytest):** Implementación de tests para endpoints de dashboard y autenticación JWT en `tests/api/test_dashboard_api.py`.
- **Frontend (Vitest):** Configuración de Vitest + Testing Library y creación de tests para componentes críticos como `MetricsCards.test.tsx`.
- **CI/CD:** Creación de workflow de GitHub Actions (`.github/workflows/main.yml`) para ejecutar tests automáticos, build del frontend y preparación para despliegue.

### 4. Despliegue y Producción
- **Docker:** Actualización del `Dockerfile` raíz a un build multi-etapa que construye el frontend con Node y sirve todo desde la imagen final de Python con FastAPI.
- **Analytics:** Integración de script de Google Analytics en `index.html`.
- **Performance:** Implementación de **Code Splitting** con `React.lazy()` y `Suspense` en el router principal (`App.tsx`) para reducir el tamaño del bundle inicial.

---

## 📊 Estado Actual

| Componente | Estado | Notas |
|------------|--------|-------|
| Estructura frontend | ✅ Completo | Limpio y optimizado |
| Componentes React | ✅ Completo | Con Lazy Loading implementado |
| Servicios API (frontend) | ✅ Completo | Sincronizado con backend |
| Contextos React | ✅ Completo | Theme, WebSocket |
| Backend routes | ✅ Completo | Integrado con hosting estático |
| Schemas Pydantic | ✅ Completo | Validación completa |
| JWT Auth | ✅ Completo | Testeado con Pytest |
| WebSocket server | ✅ Completo | ConnectionManager |
| Docker config | ✅ Completo | Multi-stage build (Prod ready) |
| Tests | ✅ En progreso | Pytest (Backend) y Vitest (Frontend) |
| Deploy real | 🔄 Configurado | GitHub Actions listo |

---

## 🚀 Próximos Pasos Sugeridos

### Fase 1: Estabilización de Tests
1. Expandir cobertura de tests en frontend para todos los componentes de `/pages`.
2. Implementar tests E2E con Playwright for flujos críticos (Login -> Dashboard -> Crear Alerta).
3. Añadir tests de integración para WebSockets.

### Fase 2: Optimización y UX
1. Configurar PWA (Progressive Web App) con `manifest.json` y Service Workers.
2. Implementar Sentry para monitoreo de errores en frontend y backend.
3. Optimización de imágenes y assets.

### Fase 3: Despliegue Final
1. Ejecutar despliegue inicial en Fly.io usando el nuevo Dockerfile multi-etapa.
2. Configurar dominios personalizados y certificados SSL.
3. Verificar validación de origen en WebSockets para producción.

---

## 📁 Archivos Clave para Referencia

| Archivo | Propósito |
|---------|-----------|
| `dashboard/src/App.tsx` | Router con Code Splitting (Lazy) |
| `dashboard/src/components/dashboard/__tests__/MetricsCards.test.tsx` | Ejemplo de test Vitest |
| `tests/api/test_dashboard_api.py` | Tests de integración API |
| `Dockerfile` | Multi-stage build (Frontend + Backend) |
| `.github/workflows/main.yml` | Pipeline de CI/CD |
| `vite.config.ts` | Configuración Vite + Vitest |

---

## ⚠️ Consideraciones Importantes

1. **CORS:** Configurado para `localhost:3000` y `localhost:5173`. Para producción, añadir URL real en `DASHBOARD_URL` env var.

2. **JWT Secret:** Debe configurarse `JWT_SECRET` en `.env` antes de usar autenticación.

3. **Telegram Bot Token:** Necesario para validar hash de autenticación.

4. **MongoDB:** El proyecto usa MongoDB Atlas. Las colecciones web se crean automáticamente.

5. **WebSocket:** El frontend usa Socket.io-client pero el backend usa websockets nativo de FastAPI. Puede requerir ajuste de compatibilidad.

---

## 💬 Comandos Útiles

```bash
# Desarrollo frontend
cd dashboard && npm install && npm run dev

# Desarrollo backend
python -m uvicorn src.api.main:app --reload --port 8000

# Docker completo
docker-compose up -d

# Ver logs
docker-compose logs -f api dashboard

# Build producción
npm run build:frontend
docker-compose -f deploy/docker-compose.prod.yml build
```

---

*Documento generado para continuidad de desarrollo con asistentes IA.*
