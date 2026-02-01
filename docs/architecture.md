# 🏗️ Arquitectura del Sistema

Crypto Sentinel Bot utiliza una arquitectura modular asíncrona diseñada para alta disponibilidad y facilidad de monitoreo.

## Componentes Principales

### 1. Núcleo de la Aplicación (`src/main.py`)
El orquestador principal que gestiona:
- Inicialización de la base de datos y creación de índices.
- Ciclo de vida del Bot de Telegram.
- Ejecución en segundo plano del `AlertService`.
- Lanzamiento del servidor web FastAPI.

### 2. Capa de API y Monitoreo (`src/api/`)
Implementado con **FastAPI**, proporciona:
- **Health Checks**: Endpoints para que Fly.io verifique que la app está viva.
- **Monitoreo Externo**: `/api/v1/health` verifica la conectividad con MongoDB y APIs externas.
- **Escalabilidad**: Base para un futuro Dashboard administrativo.

### 3. Bot de Telegram (`src/bot/`)
- **Polling Mode**: Recibe comandos en tiempo real.
- **Handlers**: Lógica para `/start`, `/price`, `/alert`, etc.
- **Middleware**: Sistema de logs para cada interacción del usuario.

### 4. Servicios de Monitoreo (`src/services/`)
- **`PriceMonitor`**: Consulta precios a CoinGecko de forma asíncrona.
- **`AlertService`**: Motor de reglas que verifica alertas cada 60s (configurable). Incluye un **cooldown de 5 minutos** por alerta para evitar spam.

### 5. Capa de Datos (`src/database/`)
- **MongoDB (Motor)**: Acceso asíncrono a la base de datos.
- **Modelos Pydantic**: Validación estricta de datos antes de persistir.

---

## Flujo de Datos y Salud (Health)

1. **Arranque**: `main.py` levanta el servidor FastAPI en el puerto 8080.
2. **Health Check**: Fly.io consulta `GET /health` cada 10-30 segundos.
3. **Respuesta**: El servidor verifica la conexión a MongoDB y responde `200 OK` si todo está correcto.
4. **Ciclo de Alertas**: El `AlertService` corre en un bucle infinito, consultando precios y enviando notificaciones vía `TelegramBot`.

---

## Infraestructura (Cloud)

- **Fly.io**: Orquestador de contenedores.
- **MongoDB Atlas**: Base de datos como servicio (DBaaS).
- **Loguru**: Centralización de logs en formato JSON para producción.
