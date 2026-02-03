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

```
dashboard/
├── src/
│   ├── components/
│   │   ├── alerts/          # AlertCard, AlertList, CreateAlertForm
│   │   ├── charts/          # PriceChart, AlertsChart (Recharts)
│   │   ├── dashboard/       # StatsCard, RecentActivity
│   │   └── layout/          # Layout, Header, Sidebar
│   ├── config/
│   │   ├── api.ts           # Axios config con interceptors JWT
│   │   └── websocket.ts     # Socket.io client config
│   ├── context/
│   │   ├── ThemeContext.tsx # Tema claro/oscuro
│   │   └── WebSocketContext.tsx # Conexión real-time
│   ├── hooks/
│   │   ├── useAlerts.ts
│   │   ├── useAuth.ts
│   │   └── usePrices.ts
│   ├── pages/
│   │   ├── Dashboard.tsx    # Página principal
│   │   ├── Alerts.tsx       # CRUD de alertas
│   │   ├── Portfolio.tsx    # Holdings del usuario
│   │   ├── Transactions.tsx # Historial de transacciones
│   │   ├── Settings.tsx     # Configuración
│   │   ├── Login.tsx        # Login con Telegram
│   │   ├── Register.tsx     # Registro
│   │   └── About.tsx        # Landing page pública
│   ├── services/
│   │   ├── auth.service.ts
│   │   ├── alerts.service.ts
│   │   ├── metrics.service.ts
│   │   └── websocket.service.ts
│   ├── store/
│   │   ├── authStore.ts     # Zustand - estado auth
│   │   └── alertStore.ts    # Zustand - estado alertas
│   ├── types/
│   │   └── index.ts         # Tipos TypeScript
│   ├── App.tsx              # Router principal
│   └── main.tsx             # Entry point con providers
├── package.json
├── vite.config.ts           # Alias @ + proxy API/WS
├── tailwind.config.js       # Tema crypto (oscuro)
├── Dockerfile               # Multi-stage build
└── nginx.conf               # Proxy para producción
```

**Dependencias principales:**
- React 18, React Router DOM 6
- TanStack React Query
- Zustand (estado)
- Recharts (gráficos)
- Socket.io-client
- Axios

**Tema de colores:**
```javascript
crypto: {
  bg: '#0f0f23',
  accent: '#00d9ff',      // Cyan
  gain: '#00ff88',        // Verde
  loss: '#ff4757',        // Rojo
  purple: '#8b5cf6',
  blue: '#3b82f6',
}
```

### 2. Backend API Extendido (`/src/api/`)

```
src/api/
├── middleware/
│   └── auth.py              # JWT + validación hash Telegram
├── routes/
│   ├── auth.py              # POST /telegram, /refresh, /logout, GET /me
│   ├── alerts.py            # CRUD alertas + stats
│   ├── prices.py            # Precios actuales + históricos
│   ├── portfolio.py         # CRUD portfolio + P&L
│   ├── dashboard.py         # Stats generales + actividad
│   ├── users.py             # Perfil + stats usuario
│   └── metrics.py           # Datos para gráficos
├── schemas/
│   ├── auth.py              # TelegramAuthData, TokenResponse
│   ├── alerts.py            # AlertCreate, AlertUpdate, AlertResponse
│   ├── portfolio.py         # PortfolioPosition, PortfolioResponse
│   └── prices.py            # PriceResponse, PriceHistory
├── websocket.py             # ConnectionManager + endpoint /ws
└── main.py                  # FastAPI app con todos los routers
```

**Endpoints principales:**
| Ruta | Método | Descripción |
|------|--------|-------------|
| `/api/v1/auth/telegram` | POST | Login con Telegram Widget |
| `/api/v1/auth/me` | GET | Usuario actual |
| `/api/v1/alerts` | GET/POST | Listar/crear alertas |
| `/api/v1/alerts/{id}` | PUT/DELETE | Editar/eliminar alerta |
| `/api/v1/prices/current` | GET | Precios actuales |
| `/api/v1/portfolio` | GET/POST | Portfolio del usuario |
| `/api/v1/dashboard/stats` | GET | Estadísticas dashboard |
| `/api/v1/metrics/market/overview` | GET | Resumen del mercado |
| `/ws` | WebSocket | Actualizaciones real-time |

### 3. Modelos de Base de Datos (`/src/database/`)

**Nuevas colecciones MongoDB:**
- `web_users` - Usuarios registrados desde web
- `sessions` - Sesiones activas JWT
- `activity_logs` - Log de actividad
- `portfolio` - Posiciones del usuario
- `portfolio_history` - Histórico de valor

### 4. Infraestructura

**Docker Compose** (`docker-compose.yml`):
```yaml
services:
  mongodb:    # Puerto 27017
  redis:      # Puerto 6379
  api:        # Puerto 8080 - FastAPI
  bot:        # Telegram bot
  dashboard:  # Puerto 3000 - React (Nginx)
```

**Scripts de desarrollo** (`/scripts/`):
- `dev.ps1` / `dev.sh` - Iniciar desarrollo local
- `build.ps1` / `build.sh` - Build de producción
- `deploy.ps1` / `deploy.sh` - Deploy multi-plataforma

**Configuración Fly.io:**
- `fly.toml` - Bot + API (existente)
- `deploy/fly.dashboard.toml` - Dashboard frontend

### 5. Dependencias Añadidas

**requirements.txt:**
```
PyJWT==2.8.0
websockets==12.0
python-socketio==5.11.0
async-timeout==4.0.3
```

---

## 📊 Estado Actual

| Componente | Estado | Notas |
|------------|--------|-------|
| Estructura frontend | ✅ Completo | Falta `npm install` |
| Componentes React | ✅ Completo | Layout, páginas, charts |
| Servicios API (frontend) | ✅ Completo | auth, alerts, metrics, ws |
| Contextos React | ✅ Completo | Theme, WebSocket |
| Backend routes | ✅ Completo | 7 routers implementados |
| Schemas Pydantic | ✅ Completo | Validación completa |
| JWT Auth | ✅ Completo | Compatible Telegram |
| WebSocket server | ✅ Completo | ConnectionManager |
| Docker config | ✅ Completo | Dev + Prod |
| Tests | ❌ Pendiente | No se han creado tests |
| Deploy real | ❌ Pendiente | Solo configuración |

---

## 🚀 Próximos Pasos Sugeridos

### Fase 1: Validación
1. Instalar dependencias frontend: `cd dashboard && npm install`
2. Probar compilación TypeScript: `npm run build`
3. Verificar imports Python: `python -c "from src.api.main import app"`
4. Levantar con Docker: `docker-compose up -d`

### Fase 2: Integración
1. Conectar frontend con backend real
2. Probar flujo de autenticación Telegram
3. Verificar WebSocket connections
4. Probar CRUD de alertas desde UI

### Fase 3: Testing
1. Tests unitarios para servicios backend
2. Tests de integración API
3. Tests E2E con Playwright/Cypress

### Fase 4: Deploy
1. Configurar variables de entorno producción
2. Deploy dashboard a Fly.io o Vercel
3. Configurar dominio y SSL

---

## 📁 Archivos Clave para Referencia

| Archivo | Propósito |
|---------|-----------|
| `dashboard/src/App.tsx` | Router y rutas protegidas |
| `dashboard/src/main.tsx` | Entry point con providers |
| `dashboard/src/store/authStore.ts` | Estado de autenticación |
| `dashboard/src/services/auth.service.ts` | Llamadas API auth |
| `src/api/main.py` | FastAPI app principal |
| `src/api/middleware/auth.py` | JWT + Telegram validation |
| `src/api/routes/auth.py` | Endpoints de auth |
| `src/api/websocket.py` | WebSocket manager |
| `docker-compose.yml` | Servicios Docker |

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
