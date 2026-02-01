#!/bin/bash

# Script de despliegue completo para Fly.io

set -e  # Detener script en caso de error

echo "🚀 CRYPTO SENTINEL BOT - DEPLOYMENT"
echo "======================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que flyctl esté instalado
if ! command -v flyctl &> /dev/null; then
    echo -e "${YELLOW}⚠️  flyctl no encontrado. Instalando...${NC}"
    curl -L https://fly.io/install.sh | sh
    export FLYCTL_INSTALL="/home/$USER/.fly"
    export PATH="$FLYCTL_INSTALL/bin:$PATH"
fi

# Verificar autenticación
echo -e "${YELLOW}🔑 Verificando autenticación...${NC}"
if ! flyctl auth whoami &> /dev/null; then
    echo -e "${YELLOW}🔑 Autenticando en Fly.io...${NC}"
    flyctl auth login
fi

# Crear aplicación si no existe
APP_NAME="crypto-sentinel-bot"
if ! flyctl apps list | grep -q "$APP_NAME"; then
    echo -e "${YELLOW}📦 Creando aplicación en Fly.io...${NC}"
    flyctl apps create --name "$APP_NAME"
    echo -e "${GREEN}✅ Aplicación creada${NC}"
fi

# Configurar secrets desde .env
echo -e "${YELLOW}🔐 Configurando secrets...${NC}"
if [ -f .env ]; then
    # Extraer variables necesarias
    TELEGRAM_BOT_TOKEN=$(grep "^TELEGRAM_BOT_TOKEN=" .env | sed 's/^TELEGRAM_BOT_TOKEN=//')
    MONGODB_URI=$(grep "^MONGODB_URI=" .env | sed 's/^MONGODB_URI=//')
    
    if [ ! -z "$TELEGRAM_BOT_TOKEN" ]; then
        echo -e "${YELLOW}  Setting TELEGRAM_BOT_TOKEN...${NC}"
        flyctl secrets set TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" --app "$APP_NAME"
    fi
    
    if [ ! -z "$MONGODB_URI" ]; then
        echo -e "${YELLOW}  Setting MONGODB_URI...${NC}"
        flyctl secrets set MONGODB_URI="$MONGODB_URI" --app "$APP_NAME"
    fi
else
    echo -e "${RED}❌ No se encontró archivo .env${NC}"
    exit 1
fi

# Desplegar aplicación
echo -e "${YELLOW}🚀 Desplegando aplicación...${NC}"
# Usamos --ha=false para evitar que intente crear 2 máquinas si estamos en el plan gratuito
flyctl deploy --remote-only --app "$APP_NAME" --ha=false

# Esperar a que la aplicación esté lista
echo -e "${YELLOW}⏳ Esperando a que la aplicación esté lista...${NC}"
sleep 10

# Verificar estado
echo -e "${YELLOW}🔍 Verificando estado...${NC}"
if flyctl status --app "$APP_NAME" | grep -q "✓"; then
    echo -e "${GREEN}✅ Despliegue exitoso!${NC}"
else
    echo -e "${RED}❌ Error en el despliegue${NC}"
    flyctl logs --app "$APP_NAME"
    exit 1
fi

# Obtener URL de la aplicación
APP_URL=$(flyctl info --app "$APP_NAME" | grep "Hostname" | awk '{print $2}')
echo -e "${GREEN}🌐 Aplicación desplegada en: https://${APP_URL}${NC}"

# Mostrar logs recientes
echo -e "${YELLOW}📋 Mostrando logs recientes...${NC}"
flyctl logs --app "$APP_NAME" --lines 10

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}🚀 DESPLIEGUE COMPLETADO EXITOSAMENTE${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Comandos útiles:"
echo "  flyctl logs --app $APP_NAME      # Ver logs"
echo "  flyctl status --app $APP_NAME    # Ver estado"
echo "  flyctl open --app $APP_NAME      # Abrir en navegador"
echo ""
