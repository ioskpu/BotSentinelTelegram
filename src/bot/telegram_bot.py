import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.error import TelegramError
from loguru import logger
from src.config.settings import settings
from src.bot.handlers import TelegramHandlers

class CryptoTelegramBot:
    def __init__(self):
        self.application = None
        self.handlers = TelegramHandlers()
    
    async def initialize(self):
        """Inicializa el bot de Telegram"""
        try:
            if not self.application:
                self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
                # Registrar handlers
                self._register_handlers()
            
            # Inicializar la aplicación (capa de red de PTB)
            await self.application.initialize()
            logger.info("✅ Bot de Telegram inicializado")
            return True
        except Exception as e:
            logger.error(f"❌ Error inicializando bot: {e}")
            return False
    
    def _register_handlers(self):
        """Registra todos los handlers de comandos"""
        # Comandos
        self.application.add_handler(CommandHandler("start", self.handlers.start))
        self.application.add_handler(CommandHandler("help", self.handlers.help_command))
        self.application.add_handler(CommandHandler("price", self.handlers.price_command))
        self.application.add_handler(CommandHandler("alert", self.handlers.alert_command))
        self.application.add_handler(CommandHandler("myalerts", self.handlers.myalerts_command))
        self.application.add_handler(CommandHandler("deletealert", self.handlers.deletealert_command))
        self.application.add_handler(CommandHandler("stats", self.handlers.stats_command))
        
        # Callback queries (botones)
        self.application.add_handler(CallbackQueryHandler(self.handlers.callback_query_handler))
        
        # Mensajes no reconocidos
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.help_command)
        )
    
    async def start_polling(self):
        """Inicia el bot en modo polling"""
        try:
            # Ya inicializado en self.initialize(), ahora solo arrancamos
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("🤖 Bot iniciado en modo polling")
            
            # Mantener vivo el loop sin bloquear otras tareas
            while True:
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error en polling: {e}")
            raise
        finally:
            await self.stop()
    
    async def stop(self):
        """Detiene el bot"""
        try:
            if self.application:
                if self.application.updater and self.application.updater.running:
                    await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            logger.info("Bot detenido")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")

    async def send_message(self, chat_id: int, text: str, parse_mode: str = 'Markdown'):
        """Envía un mensaje a un usuario específico"""
        try:
            if self.application and self.application.bot:
                await self.application.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode=parse_mode
                )
                return True
        except Exception as e:
            logger.error(f"Error enviando mensaje a {chat_id}: {e}")
        return False