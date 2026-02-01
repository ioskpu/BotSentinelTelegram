# 🛠️ Guía de Configuración e Instalación

Esta guía detalla los pasos para configurar el entorno de producción (MongoDB Atlas + Fly.io) y el desarrollo local.

## 1. Configuración de Base de Datos (MongoDB Atlas)

Para producción, utilizamos MongoDB Atlas. Sigue estos pasos:

1. **Crear Cluster**: Crea un cluster gratuito (M0) en MongoDB Atlas.
2. **Network Access**: Agrega la IP `0.0.0.0/0` (permitir acceso desde cualquier lugar) para que Fly.io pueda conectarse.
3. **Database User**: Crea un usuario con permisos de `readWriteAnyDatabase`.
4. **Connection String**: Copia la URI de conexión. Debería verse así:
   `mongodb+srv://<usuario>:<password>@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority`

## 2. Configuración de Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
# Telegram (Obtenlo de @BotFather)
TELEGRAM_BOT_TOKEN=8090803712:AAERXJmZM9euXPVqIkm1WFx_TB3P2ZNOFVc

# MongoDB Atlas
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/crypto_bot
MONGODB_DB_NAME=crypto_bot

# Entorno
ENVIRONMENT=production
DEBUG=false
```

## 3. Despliegue en Fly.io

El despliegue está automatizado mediante el script `deploy/fly_deploy.sh`. Este script realiza las siguientes acciones:

1. **Crea la App**: Crea la aplicación en Fly.io si no existe.
2. **Configura Secretos**: Sincroniza las variables de tu `.env` con Fly.io de forma segura.
3. **Despliega**: Sube el código y lanza el contenedor.

### Pasos para desplegar:

```bash
# Asegúrate de estar logueado en Fly.io
flyctl auth login

# Ejecutar el despliegue
./deploy/fly_deploy.sh
```

### Verificación del Despliegue:
- **Logs**: `flyctl logs --app crypto-sentinel-bot`
- **Salud**: Abre `https://crypto-sentinel-bot.fly.dev/health` en tu navegador.

## 4. Desarrollo Local

Si deseas correr el bot localmente sin Docker:

1. **Entorno Virtual**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```
2. **Instalar Dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Ejecutar**:
   ```bash
   python src/main.py
   ```

> **Nota**: Para desarrollo local, puedes usar una instancia local de MongoDB cambiando la `MONGODB_URI` en tu `.env`.
