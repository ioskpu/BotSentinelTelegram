# 📂 Estructura del Proyecto

Esta es la jerarquía de archivos del Crypto Sentinel Bot y una breve descripción de la responsabilidad de cada componente.

## Jerarquía de Archivos

```text
crypto-sentinel-bot/
├── deploy/                 # Scripts de despliegue
│   └── fly_deploy.sh       # Automatización para Fly.io
├── docs/                   # Documentación detallada
├── src/                    # Código fuente principal
│   ├── api/                # Servidor FastAPI (Health Checks)
│   │   ├── health.py       # Lógica de verificación de salud
│   │   └── main.py         # Configuración del servidor web
│   ├── bot/                # Interfaz de Telegram
│   │   ├── handlers.py     # Comandos (/start, /price, etc.)
│   │   └── telegram_bot.py # Inicialización y polling
│   ├── config/             # Configuraciones y Secretos
│   │   └── settings.py     # Modelos de Pydantic para .env
│   ├── database/           # Persistencia de Datos
│   │   ├── models.py       # Esquemas de MongoDB
│   │   └── mongodb.py      # Cliente asíncrono (Motor)
│   ├── services/           # Lógica de Negocio
│   │   ├── alert_service.py # Motor de reglas de alertas
│   │   └── price_monitor.py # Cliente para CoinGecko
│   ├── utils/              # Utilidades transversales
│   │   ├── helpers.py      # Funciones auxiliares
│   │   └── logger.py       # Configuración de Loguru
│   └── main.py             # Punto de entrada de la aplicación
├── .env                    # Variables de entorno (No subir a Git)
├── Dockerfile              # Definición del contenedor
├── fly.toml                # Configuración de Fly.io
├── requirements.txt        # Dependencias de Python
└── README.md               # Guía general
```

## Descripción de Módulos

### `src/main.py`
El corazón de la aplicación. Orquesta el arranque de todos los servicios asíncronos en paralelo utilizando `asyncio`.

### `src/api/`
Módulo encargado de la comunicación externa no relacionada con Telegram. Su función principal actual es responder a los *health checks* de Fly.io para asegurar que el bot no sea reiniciado por "falta de respuesta".

### `src/bot/`
Contiene toda la interacción con el usuario. Los `handlers.py` separan la lógica de los comandos para mantener el código limpio.

### `src/services/`
Aquí reside la inteligencia del bot. 
- El `PriceMonitor` centraliza las llamadas a APIs externas para evitar duplicidad.
- El `AlertService` corre continuamente comparando el mercado con las preferencias de los usuarios.

### `src/database/`
Gestiona la conexión con MongoDB. Utiliza el patrón Singleton para asegurar que solo haya una conexión activa compartida por todos los servicios.
