
# **PROMPT 15: SCRIPT DE DESPLIEGUE FLY.IO**

**Archivo: deploy/fly_deploy.sh**
```bash
#!/bin/bash

# Script de despliegue para Fly.io

echo "🚀 Preparando despliegue en Fly.io..."

# Verificar que flyctl esté instalado
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl no encontrado. Instalando..."
    curl -L https://fly.io/install.sh | sh
    export FLYCTL_INSTALL="/home/$USER/.fly"
    export PATH="$FLYCTL_INSTALL/bin:$PATH"
fi

# Verificar que estamos autenticados
if ! flyctl auth whoami &> /dev/null; then
    echo "🔑 Autenticando en Fly.io..."
    flyctl auth login
fi

# Crear aplicación si no existe
if ! flyctl apps list | grep -q "crypto-sentinel-bot"; then
    echo "📦 Creando aplicación en Fly.io..."
    flyctl apps create crypto-sentinel-bot
fi

# Configurar secrets desde .env
echo "🔐 Configurando secrets..."
if [ -f .env ]; then
    # Extraer variables necesarias
    TELEGRAM_BOT_TOKEN=$(grep TELEGRAM_BOT_TOKEN .env | cut -d '=' -f2)
    MONGODB_URI=$(grep MONGODB_URI .env | cut -d '=' -f2)
    
    # Configurar secrets en Fly.io
    flyctl secrets set TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
    if [ ! -z "$MONGODB_URI" ] && [ "$MONGODB_URI" != "mongodb://localhost:27017" ]; then
        flyctl secrets set MONGODB_URI=$MONGODB_URI
    fi
else
    echo "⚠️  No se encontró .env, usando secrets existentes"
fi

# Desplegar
echo "🚀 Desplegando aplicación..."
flyctl deploy --remote-only

echo "✅ Despliegue completado!"
echo "🌐 URL: https://crypto-sentinel-bot.fly.dev"