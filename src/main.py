import asyncio
import signal
import sys
from loguru import logger
from src.bot.telegram_bot import CryptoTelegramBot
from src.services.alert_service import AlertService
from src.database.mongodb import mongodb

class CryptoApp:
    def __init__(self):
        self.telegram_bot = CryptoTelegramBot()
        self.alert_service = AlertService()
        self.is_running = False
        
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
        
        # Vincular bot al servicio de alertas
        self.alert_service.set_bot(self.telegram_bot)
        
        logger.info("✅ Aplicación iniciada exitosamente")
        return True
    
    async def run(self):
        """Ejecuta la aplicación principal"""
        # Inicializar la aplicación primero
        if not await self.startup():
            logger.error("❌ Falló la inicialización de la aplicación")
            return

        self.is_running = True
        
        # Configurar manejo de señales
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))
        
        # Iniciar servicios en paralelo
        bot_task = asyncio.create_task(self.telegram_bot.start_polling())
        alert_task = asyncio.create_task(self.alert_service.start())
        
        try:
            # Esperar a que terminen las tareas
            await asyncio.gather(bot_task, alert_task)
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
    
    app = CryptoApp()
    
    try:
        # Iniciar aplicación
        asyncio.run(app.run())
    except KeyboardInterrupt:
        logger.info("Aplicación interrumpida por el usuario")
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()