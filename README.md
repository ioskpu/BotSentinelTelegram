# 🤖 Crypto Sentinel Bot

Crypto Sentinel es un asistente inteligente diseñado para el monitoreo y gestión de activos criptográficos, optimizado para ofrecer datos en tiempo real y notificaciones automatizadas a través de Telegram.

---

## 📍 Estado del Proyecto: Fase 3 (Integración Web3 en Progreso) 🚀

El proyecto ha entrado en su **Fase 3**, integrando capacidades avanzadas de Web3 y monitoreo on-chain.

### ¿Qué ofrece el Bot?
- **Monitoreo On-Chain (Web3):**
  - **Stellar (XLM):** Consulta de balances, historial de transacciones y monitoreo en tiempo real de cuentas.
  - **Solana (SOL):** Soporte para SOL y tokens SPL, tracking de firmas y alertas de actividad.
- **Monitoreo Expandido (28+ Monedas):** Seguimiento en tiempo real de Layer 1 (SOL, AVAX, MATIC), Memes (PEPE, SHIB), DeFi (UNI, LINK) y Stables (USDT, USDC).
- **Gestión de Portafolio:** Seguimiento de inversiones con cálculo automático de ganancias/pérdidas (P&L) en tiempo real (`/portfolio`).
- **Análisis Inteligente (IA & TA):**
  - Predicciones basadas en RSI y Medias Móviles (`/predict`).
  - Identificación automática de niveles de Soporte y Resistencia.
  - Visualización de tendencias globales con datos de CoinGecko (`/trending`).
- **Sistema de Alertas Avanzado:**
  - Alertas de precio y variaciones porcentuales.
  - Monitoreo automático de transacciones blockchain para cuentas seguidas.
- **Gráficos en Tiempo Real:** Generación de gráficos de evolución de precio directamente en Telegram (`/chart`).
- **Infraestructura de Producción:**
  - **Fly.io**: Despliegue en la nube optimizado para Python 3.11+.
  - **MongoDB Atlas**: Base de datos NoSQL para persistencia de usuarios, alertas, portafolios y cuentas monitoreadas.
  - **FastAPI**: Endpoints de salud y monitoreo de API.

---

## 🤖 Comandos Principales

### Mercado y Análisis
| Comando | Descripción |
|---------|-------------|
| `/price [moneda]` | Precio actual y variaciones (ej: `/price SOL`) |
| `/predict [moneda]` | Análisis técnico y predicción de movimiento |
| `/chart [moneda]` | Gráfico de precio de los últimos 7 días |
| `/trending` | Top 7 monedas en tendencia mundial |
| `/portfolio` | Resumen de inversión y P&L total |

### Web3 (Stellar & Solana)
| Comando | Descripción |
|---------|-------------|
| `/sbalance [dir]` | Balances en Stellar (XLM/Assets) |
| `/swatch [dir]` | Iniciar monitoreo on-chain de cuenta Stellar |
| `/sobalance [dir]` | Balance de SOL en Solana |
| `/sotokens [dir]` | Lista tokens SPL en Solana |
| `/blockchain` | Ayuda completa de comandos Web3 |

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

- [📖 Guía de Usuario (Manual)](docs/user_guide.md): Instrucciones completas para el usuario final del bot en Telegram.
- [🛠️ Guía de Instalación y Setup](docs/setup.md): Paso a paso para MongoDB Atlas y Fly.io.
- [📂 Estructura del Proyecto](docs/project_structure.md): Descripción de cada archivo y carpeta.
- [🏗️ Arquitectura](docs/architecture.md): Diagrama de flujo y componentes.

---

## 🛠️ Próximamente (Fase 3: Avanzado)
- **Alertas de Ballenas (Whale Tracking)**: Notificaciones automáticas de grandes movimientos.
- **Dashboard Web**: Panel administrativo para usuarios avanzados.
- **Social Listening**: Análisis de sentimiento en Twitter/X.
- **Soporte Multi-red**: Ethereum y redes Layer 2.
