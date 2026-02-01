# 🤖 Crypto Sentinel Bot

Crypto Sentinel es un asistente inteligente diseñado para el monitoreo y gestión de activos criptográficos, optimizado para ofrecer datos en tiempo real y notificaciones automatizadas a través de Telegram.

---

## 📍 Estado del Proyecto: Fase 2 (En Progreso)

Actualmente el proyecto se encuentra en su **Fase 2**, enfocada en la robustez del sistema, despliegue en producción y preparación para integraciones Web3.

### ¿Qué ofrece el Bot?
- **Monitoreo Multimoneda:** Seguimiento en tiempo real de precios para SOL, XLM, BTC y ETH mediante la API de CoinGecko.
- **Sistema de Alertas Inteligentes:**
  - `Precio Superior/Inferior`: Notificación inmediata al cruzar umbrales.
  - `Cooldown de 5 min`: Evita spam de notificaciones repetitivas.
- **Infraestructura de Producción:**
  - **Fly.io**: Despliegue en la nube con escalabilidad automática.
  - **MongoDB Atlas**: Persistencia en base de datos gestionada.
  - **FastAPI**: Servidor web integrado para monitoreo y salud (Health Checks).
- **Interfaz Telegram:** Comandos interactivos (`/start`, `/price`, `/alert`, `/myalerts`).

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

## 🛠️ Próximamente (Fase 2.5)
- Integración con Stellar Network para consultas de saldo.
- Dashboard Web para gestión de alertas.
- Alertas de volumen y movimientos de ballenas.
