# 🛠️ Guía de Configuración e Instalación

Esta guía detalla cómo poner en marcha el Crypto Sentinel Bot en diferentes entornos.

## Requisitos Previos

- Docker y Docker Compose (Recomendado).
- Alternativamente: Python 3.11+, MongoDB y Redis.

## Variables de Entorno

El bot utiliza un archivo `.env` para su configuración. Crea uno en la raíz:

```bash
# Telegram
TELEGRAM_BOT_TOKEN=tu_token_aqui

# MongoDB (Docker)
MONGODB_URI=mongodb://crypto_mongodb:27017
MONGODB_DB_NAME=crypto_bot

# Configuración de Alertas
ALERT_CHECK_INTERVAL=60  # Segundos entre chequeos
COINGECKO_API_URL=https://api.coingecko.com/api/v3
```

## Instalación con Docker (Recomendado)

Docker gestiona automáticamente todas las dependencias y servicios.

```bash
# Construir e iniciar contenedores
docker-compose up --build -d

# Ver logs del bot
docker logs crypto_bot -f
```

## Despliegue en Fly.io

El proyecto está configurado para Fly.io. Asegúrate de tener instalado `flyctl`.

1. **Configurar la App**:
   ```bash
   fly launch
   ```
2. **Configurar Secretos**:
   ```bash
   fly secrets set TELEGRAM_BOT_TOKEN=tu_token
   ```
3. **Desplegar**:
   ```bash
   fly deploy
   ```

## Desarrollo Local (Sin Docker)

1. Crear entorno virtual: `python -m venv .venv`
2. Activar entorno: `.venv\Scripts\activate` (Windows) o `source .venv/bin/activate` (Linux/Mac)
3. Instalar dependencias: `pip install -r requirements.txt`
4. Iniciar: `python src/main.py`
