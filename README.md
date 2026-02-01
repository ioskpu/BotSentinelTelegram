# 🤖 Crypto Sentinel Bot

Crypto Sentinel es un asistente inteligente diseñado para el monitoreo y gestión de activos criptográficos, optimizado para ofrecer datos en tiempo real y notificaciones automatizadas a través de Telegram.

---

## 📍 Estado del Proyecto: Fase 2 (Completada) ✅

El proyecto ha completado su **Fase 2**, consolidándose como una herramienta robusta de análisis y gestión de portafolio cripto en producción.

### ¿Qué ofrece el Bot?
- **Monitoreo Expandido (28+ Monedas):** Seguimiento en tiempo real de Layer 1 (SOL, AVAX, MATIC), Memes (PEPE, SHIB), DeFi (UNI, LINK) y Stables (USDT, USDC).
- **Gestión de Portafolio:** Seguimiento de inversiones con cálculo automático de ganancias/pérdidas (P&L) en tiempo real (`/portfolio`).
- **Análisis Inteligente (IA & TA):**
  - Predicciones basadas en RSI y Medias Móviles (`/predict`).
  - Identificación automática de niveles de Soporte y Resistencia.
  - Visualización de tendencias globales con datos de CoinGecko (`/trending`).
- **Sistema de Alertas Avanzado:**
  - Alertas de precio y variaciones porcentuales.
  - Almacenamiento de historial de precios para análisis visual.
- **Gráficos en Tiempo Real:** Generación de gráficos de evolución de precio directamente en Telegram (`/chart`).
- **Infraestructura de Producción:**
  - **Fly.io**: Despliegue en la nube con estrategias de "rolling update".
  - **MongoDB Atlas**: Base de datos NoSQL para persistencia de usuarios, alertas y portafolios.
  - **FastAPI**: Endpoints de salud y monitoreo de API.

---

## 🤖 Comandos Principales

| Comando | Descripción |
|---------|-------------|
| `/price [moneda]` | Precio actual y variaciones (ej: `/price SOL`) |
| `/coins` | Lista las 28+ monedas soportadas |
| `/trending` | Top 7 monedas en tendencia mundial |
| `/predict [moneda]` | Análisis técnico y predicción de movimiento |
| `/portfolio` | Resumen de inversión y P&L total |
| `/chart [moneda]` | Gráfico de precio de los últimos 7 días |
| `/alert [condicion]` | Configurar alertas inteligentes |
| `/convert [cant] [de] [a]` | Conversor de divisas y cripto |

---

## 🏗️ Arquitectura y Estructura

El sistema está diseñado de forma modular para facilitar su mantenimiento:

- `src/bot/`: Lógica del Bot de Telegram (handlers, comandos).
- `src/services/`: Motores de precios y alertas.
- `src/api/`: Servidor FastAPI para monitoreo y endpoints externos.
- `src/database/`: Capa de persistencia asíncrona con MongoDB (Motor).
- `src/config/`: Gestión de configuraciones y secretos con Pydantic.

Para más detalles, consulta [🏗️ Arquitectura del Sistema](docs/architecture.md).

---

## 🚀 Despliegue Rápido (MVP)

### 1. Requisitos
- Token de Telegram (@BotFather).
- Cuenta en MongoDB Atlas (URI de conexión).
- Fly CLI instalado para despliegue en la nube.

### 2. Configuración Local
Crea un archivo `.env` basado en el entorno de producción:
```env
TELEGRAM_BOT_TOKEN=tu_token_aqui
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/crypto_bot
MONGODB_DB_NAME=crypto_bot
ENVIRONMENT=production
```

### 3. Despliegue en Fly.io
El proyecto incluye un script automatizado para el despliegue:
```bash
# Otorgar permisos
chmod +x deploy/fly_deploy.sh

# Ejecutar despliegue
./deploy/fly_deploy.sh
```

---

## 📚 Documentación Detallada

- [🛠️ Guía de Instalación y Setup](docs/setup.md): Paso a paso para MongoDB Atlas y Fly.io.
- [📂 Estructura del Proyecto](docs/project_structure.md): Descripción de cada archivo y carpeta.
- [🏗️ Arquitectura](docs/architecture.md): Diagrama de flujo y componentes.

---

## 🛠️ Próximamente (Fase 3: Integración Web3)
- **Stellar Network**: Integración para consultas de saldo real y transferencias.
- **Notificaciones Push**: Alertas de movimientos de ballenas (Whale Alerts).
- **Dashboard Web**: Panel administrativo para usuarios avanzados.
- **Social Listening**: Análisis de sentimiento en Twitter/X para monedas meme.
