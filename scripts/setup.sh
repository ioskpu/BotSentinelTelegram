
# **PROMPT 17: SCRIPT DE INICIALIZACIÓN**

**Crear script de setup: scripts/setup.sh**
```bash
#!/bin/bash

# Script de inicialización del proyecto

set -e

echo "🎉 Configurando Crypto Sentinel Bot..."

# Crear entorno virtual
echo "🐍 Creando entorno virtual..."
python -m venv venv --prompt="crypto-bot"

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tu token de Telegram"
fi

# Crear directorio de logs
mkdir -p logs

# Iniciar MongoDB si está disponible
if command -v docker &> /dev/null; then
    echo "🐳 Iniciando MongoDB con Docker..."
    docker-compose up -d mongodb
    echo "⏳ Esperando que MongoDB esté listo..."
    sleep 5
fi

echo "✅ Configuración completada!"
echo ""
echo "🚀 Para iniciar el bot:"
echo "1. Edita .env con tu token de Telegram"
echo "2. Ejecuta: python src/main.py"
echo "3. O usa: docker-compose up"
echo ""
echo "📚 Más info en docs/setup.md"