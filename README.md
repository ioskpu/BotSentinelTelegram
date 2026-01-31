# 🤖 Crypto Sentinel Bot

Crypto Sentinel es un asistente inteligente diseñado para el monitoreo y gestión de activos criptográficos, optimizado para ofrecer datos en tiempo real y notificaciones automatizadas a través de Telegram.

---

## 📍 Estado del Proyecto: Fase 1 (Actual)

Actualmente el proyecto se encuentra en su **Fase 1**, enfocada en la infraestructura base y el monitoreo de mercado.

### ¿Qué ofrece la Fase 1?
- **Monitoreo Multimoneda:** Seguimiento en tiempo real de precios para Solana (SOL), Stellar (XLM), Bitcoin (BTC) y Ethereum (ETH) mediante la API de CoinGecko.
- **Sistema de Alertas Inteligentes:**
  - `Precio Superior`: Notificación cuando una moneda supera un umbral.
  - `Precio Inferior`: Notificación cuando cae por debajo de un valor.
  - `Variación Porcentual`: Alertas basadas en cambios bruscos de mercado.
- **Infraestructura Robusta:**
  - Totalmente contenedorizado con **Docker** y **Docker Compose**.
  - Base de datos asíncrona con **MongoDB** y **Motor**.
  - Gestión de logs avanzada con **Loguru**.
- **Interfaz Telegram:** Comandos interactivos (`/price`, `/alert`, `/myalerts`) para una gestión sencilla desde cualquier dispositivo.

---

## 🛠️ Próximamente: Fase 2 (En Desarrollo)

Estamos preparando la expansión del bot hacia un ecosistema financiero completo:

- **Integración con Stellar Network:**
  - Consultas de saldo en la red Stellar.
  - Ejecución de transacciones directamente desde el bot.
- **Dashboard Web Administrativo:**
  - Interfaz visual para gestionar alertas y ver estadísticas históricas.
  - Panel de control de usuario desarrollado en FastAPI/React.
- **Alertas de Volumen y Ballenas:** Detección de movimientos inusuales en el mercado.

---

## � Documentación Detallada

Para más información sobre el funcionamiento interno y la configuración, consulta nuestra documentación:

- [🏗️ Arquitectura del Sistema](docs/architecture.md): Detalles sobre componentes y flujo de datos.
- [📡 API y Comandos](docs/api.md): Guía completa de comandos y esquemas de datos.
- [🛠️ Guía de Instalación](docs/setup.md): Instrucciones paso a paso para diferentes entornos.

---

## �🚀 Instalación Rápida

### 1. Requisitos
- Docker y Docker Compose instalados.
- Un Token de Bot de Telegram (obtenido via [@BotFather](https://t.me/botfather)).

### 2. Configuración
Crea un archivo `.env` en la raíz del proyecto basado en `.env.example`:
```env
TELEGRAM_BOT_TOKEN=tu_token_aqui
MONGODB_URI=mongodb://crypto_mongodb:27017
MONGODB_DB_NAME=crypto_bot
```

### 3. Ejecución
```bash
docker-compose up --build
```

---

## 🚀 Despliegue en Fly.io

### Prerrequisitos
1. Cuenta en [Fly.io](https://fly.io)
2. Fly CLI instalado: `curl -L https://fly.io/install.sh | sh`
3. Token de Telegram Bot (@BotFather)

### Pasos de despliegue

```bash
# 1. Clonar y configurar
git clone <tu-repositorio>
cd crypto-sentinel-bot
cp .env.example .env

# 2. Editar .env con tus credenciales
nano .env

# 3. Ejecutar script de despliegue
chmod +x deploy/fly_deploy.sh
./deploy/fly_deploy.sh

# 4. Verificar despliegue
flyctl status --app crypto-sentinel-bot
flyctl logs --app crypto-sentinel-bot
```

### Variables de entorno requeridas
```bash
TELEGRAM_BOT_TOKEN=tu_token_de_telegram
MONGODB_URI=mongodb+srv://usuario:contraseña@cluster.mongodb.net/crypto_sentinel
```

### Base de datos en producción
Recomendamos usar:
- **MongoDB Atlas** (gratis hasta 512MB)
- O Railway para MongoDB gratis

### Monitoreo
- **Logs:** `flyctl logs --app crypto-sentinel-bot`
- **Health check:** `https://crypto-sentinel-bot.fly.dev/health`
- **Estado:** `https://crypto-sentinel-bot.fly.dev/status`

### Mantenimiento automático
El bot incluye tareas automáticas:
- Limpieza de datos antiguos (diario a las 2AM UTC)
- Actualización de historial de precios (cada hora)
- Generación de reportes diarios

---

## 📚 Comandos del Bot
- `/start` - Inicia el bot y registra tu usuario.
- `/price` - Consulta precios actuales.
- `/alert` - Configura una nueva alerta.
- `/myalerts` - Lista y gestiona tus alertas activas.
- `/help` - Guía detallada de uso.
