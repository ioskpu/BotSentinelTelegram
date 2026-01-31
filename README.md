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

## 📚 Comandos del Bot
- `/start` - Inicia el bot y registra tu usuario.
- `/price` - Consulta precios actuales.
- `/alert` - Configura una nueva alerta.
- `/myalerts` - Lista y gestiona tus alertas activas.
- `/help` - Guía detallada de uso.
