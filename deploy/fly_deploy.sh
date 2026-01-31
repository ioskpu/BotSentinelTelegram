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
    flyctl apps create "$APP_NAME" --no-config
    echo -e "${GREEN}✅ Aplicación creada${NC}"
fi

# Configurar región
echo -e "${YELLOW}🌍 Configurando región (iad - Virginia, USA)...${NC}"
flyctl regions set iad --app "$APP_NAME" || true

# Configurar secrets desde .env
echo -e "${YELLOW}🔐 Configurando secrets...${NC}"
if [ -f .env ]; then
    # Leer variables de .env
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Ignorar comentarios y líneas vacías
        if [[ -n "$line" ]] && [[ ! "$line" =~ ^\s*# ]]; then
            key=$(echo "$line" | cut -d '=' -f1)
            value=$(echo "$line" | cut -d '=' -f2-)
            
            # Configurar solo las variables necesarias
            if [[ "$key" == "TELEGRAM_BOT_TOKEN" ]] || [[ "$key" == "MONGODB_URI" ]]; then
                echo -e "${YELLOW}  Setting $key...${NC}"
                flyctl secrets set "$key=$value" --app "$APP_NAME"
            fi
        fi
    done < .env
else
    echo -e "${RED}❌ No se encontró archivo .env${NC}"
    echo -e "${YELLOW}⚠️  Usando: flyctl secrets set TELEGRAM_BOT_TOKEN=tu_token${NC}"
    echo -e "${YELLOW}⚠️  Usando: flyctl secrets set MONGODB_URI=tu_mongodb_uri${NC}"
    exit 1
fi

# Desplegar aplicación
echo -e "${YELLOW}🚀 Desplegando aplicación...${NC}"
flyctl deploy --remote-only --app "$APP_NAME" --detach

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
