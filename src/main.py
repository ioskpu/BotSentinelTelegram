import asyncio
import signal
import sys
import uvicorn
import os
from fastapi import FastAPI
from src.utils.logger import log as logger, setup_logging
from src.bot.telegram_bot import CryptoTelegramBot
from src.services.alert_service import AlertService
from src.database.mongodb import mongodb
import uvicorn
from src.api.main import app as web_app

class CryptoApp:
    def __init__(self):
        # Configurar logging según el entorno
        is_prod = os.getenv("ENVIRONMENT") == "production"
        setup_logging(level="INFO", json_format=is_prod)
        
        self.telegram_bot = CryptoTelegramBot()
        self.alert_service = AlertService()
        self.is_running = False
        self.web_server = None
        
    async def startup(self):
        """Inicializa la aplicación"""
        logger.info("🚀 Iniciando Crypto Sentinel Bot...")
        
        # Verificar conexión a MongoDB
        if not await mongodb.ping():
            logger.error("❌ No se pudo conectar a MongoDB")
            return False
        
        # Inicializar bot de Telegram
        if not await self.telegram_bot.initialize():
            logger.error("❌ Error inicializando bot de Telegram")
            return False
        
        # Configurar el bot en el servicio de alertas
        self.alert_service.set_bot(self.telegram_bot.get_bot())
        
        # Vincular el servicio de alertas a los handlers del bot para comandos como /check
        self.telegram_bot.handlers.alert_service = self.alert_service
        
        # Crear índices en MongoDB
        await self._create_database_indexes()
        
        logger.info("✅ Aplicación iniciada exitosamente")
        return True
    
    async def _create_database_indexes(self):
        """Crear índices necesarios en MongoDB"""
        try:
            # Índice para búsqueda rápida de usuarios por telegram_id
            await mongodb.users.create_index("telegram_id", unique=True)
            
            # Índice para búsqueda de alertas por usuario y estado
            await mongodb.alerts.create_index([("user_id", 1), ("is_active", 1)])
            
            # Índice para precio histórico por moneda y timestamp
            await mongodb.price_history.create_index([("coin_id", 1), ("timestamp", -1)])
            
            # Índice para portafolio por usuario
            await mongodb.portfolio.create_index("user_id")
            
            logger.info("📊 Índices de MongoDB creados")
        except Exception as e:
            logger.error(f"Error creando índices: {e}")
    
    async def start_web_server(self):
        """Inicia el servidor web en segundo plano"""
        config = uvicorn.Config(
            web_app,
            host="0.0.0.0",
            port=8080,
            log_level="info"
        )
        self.web_server = uvicorn.Server(config)
        
        # Ejecutar en segundo plano
        loop = asyncio.get_event_loop()
        await loop.create_task(self.web_server.serve())
    
    async def run(self):
        """Ejecuta la aplicación principal"""
        self.is_running = True
        
        # Configurar manejo de señales
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))
        
        # Iniciar servidor web en segundo plano
        web_task = asyncio.create_task(self.start_web_server())
        
        # Esperar un momento para que el servidor web inicie
        await asyncio.sleep(2)
        
        # Iniciar servicios del bot
        bot_task = asyncio.create_task(self.telegram_bot.start_polling())
        alert_task = asyncio.create_task(self.alert_service.start())
        
        try:
            # Esperar a que terminen las tareas
            await asyncio.gather(web_task, bot_task, alert_task)
        except asyncio.CancelledError:
            logger.info("Aplicación cancelada")
        except Exception as e:
            logger.error(f"Error en la aplicación: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Apaga la aplicación de manera controlada"""
        if not self.is_running:
            return
        
        logger.info("Apagando aplicación...")
        self.is_running = False
        
        # Detener servidor web
        if self.web_server:
            self.web_server.should_exit = True
        
        # Detener servicios
        await self.alert_service.stop()
        
        logger.info("Aplicación apagada exitosamente")
        sys.exit(0)

def main():
    """Función principal"""
    # Configurar logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Configurar logging a archivo
    logger.add(
        "logs/crypto_sentinel_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        level="DEBUG"
    )
    
    app = CryptoApp()
    
    try:
        # Iniciar aplicación
        loop = asyncio.get_event_loop()
        
        # Verificar startup
        if not loop.run_until_complete(app.startup()):
            logger.error("Fallo en el inicio de la aplicación")
            sys.exit(1)
        
        # Ejecutar aplicación
        loop.run_until_complete(app.run())
        
    except KeyboardInterrupt:
        logger.info("Aplicación interrumpida por el usuario")
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()