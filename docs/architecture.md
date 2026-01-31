# 🏗️ Arquitectura del Sistema

Crypto Sentinel Bot está diseñado siguiendo un patrón modular y asíncrono para garantizar la escalabilidad y el rendimiento en tiempo real.

## Componentes Principales

### 1. Núcleo de la Aplicación (`src/main.py`)
El orquestador principal que gestiona el ciclo de vida de la aplicación, las señales del sistema (SIGINT, SIGTERM) y la ejecución paralela de servicios.

### 2. Bot de Telegram (`src/bot/`)
- **`telegram_bot.py`**: Gestiona la conexión con la API de Telegram, el polling y la inicialización de handlers.
- **`handlers.py`**: Contiene la lógica de negocio para cada comando recibido.
- **`models.py`**: Define las estructuras de datos utilizando Pydantic para validación.

### 3. Servicios de Monitoreo (`src/services/`)
- **`price_monitor.py`**: Cliente HTTP asíncrono (aiohttp) que consulta precios a CoinGecko con sistema de caché local.
- **`alert_service.py`**: Motor de reglas que verifica periódicamente los precios contra las alertas configuradas en la base de datos.

### 4. Capa de Datos (`src/database/`)
- **`mongodb.py`**: Singleton que gestiona la conexión con MongoDB mediante el driver asíncrono `motor`.

## Flujo de Datos

1. **Monitoreo**: El `AlertService` solicita precios al `PriceMonitor` cada X segundos.
2. **Evaluación**: Se comparan los precios actuales con las alertas activas en MongoDB.
3. **Notificación**: Si se cumple una condición, el `AlertService` utiliza la instancia del `TelegramBot` para enviar un mensaje al usuario.
4. **Interacción**: El usuario crea alertas vía Telegram, las cuales se validan y persisten inmediatamente en MongoDB.

## Tecnologías Utilizadas

- **Lenguaje**: Python 3.11+
- **Asincronía**: `asyncio` para concurrencia no bloqueante.
- **Framework Bot**: `python-telegram-bot` (v20+).
- **Base de Datos**: MongoDB (Motor).
- **Contenedores**: Docker & Docker Compose.
- **Logs**: Loguru para trazabilidad estructurada.
