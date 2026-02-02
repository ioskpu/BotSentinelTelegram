import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.error import TelegramError
from loguru import logger
from src.config.settings import settings
from src.bot.handlers import TelegramHandlers
from src.bot.blockchain_handlers import BlockchainHandlers

class CryptoTelegramBot:
    def __init__(self):
        self.application = None
        self.handlers = TelegramHandlers()
        self.blockchain_handlers = BlockchainHandlers()
    
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
        self.application.add_handler(CommandHandler("check", self.handlers.check_command))
        self.application.add_handler(CommandHandler("testalert", self.handlers.test_alert_command))
        self.application.add_handler(CommandHandler("coins", self.handlers.list_coins_command))
        self.application.add_handler(CommandHandler("convert", self.handlers.convert_command))
        self.application.add_handler(CommandHandler("trending", self.handlers.trending_command))
        self.application.add_handler(CommandHandler("chart", self.handlers.chart_command))
        self.application.add_handler(CommandHandler("portfolio", self.handlers.portfolio_command))
        self.application.add_handler(CommandHandler("padd", self.handlers.portfolio_add_command))
        self.application.add_handler(CommandHandler("pdel", self.handlers.portfolio_del_command))
        self.application.add_handler(CommandHandler("predict", self.handlers.predict_command))
        
        # Comandos Blockchain
        self.application.add_handler(CommandHandler("sbalance", self.blockchain_handlers.stellar_balance_command))
        self.application.add_handler(CommandHandler("swatch", self.blockchain_handlers.stellar_watch_command))
        self.application.add_handler(CommandHandler("sunwatch", self.blockchain_handlers.stellar_unwatch_command))
        self.application.add_handler(CommandHandler("stransactions", self.blockchain_handlers.stellar_transactions_command))
        self.application.add_handler(CommandHandler("sobalance", self.blockchain_handlers.solana_balance_command))
        self.application.add_handler(CommandHandler("sotokens", self.blockchain_handlers.solana_tokens_command))
        self.application.add_handler(CommandHandler("sowatch", self.blockchain_handlers.solana_watch_command))
        self.application.add_handler(CommandHandler("sounwatch", self.blockchain_handlers.solana_unwatch_command))
        self.application.add_handler(CommandHandler("sotransactions", self.blockchain_handlers.solana_transactions_command))
        self.application.add_handler(CommandHandler("blockchain", self.blockchain_handlers.blockchain_help_command))
        
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

    def get_bot(self):
        """Obtener la instancia del bot para usar en otros servicios"""
        if self.application and self.application.bot:
            return self.application.bot
        return None

    async def send_message_to_user(self, telegram_id: int, message: str, parse_mode: str = "Markdown"):
        """Enviar mensaje a un usuario específico"""
        try:
            bot = self.get_bot()
            if bot:
                await bot.send_message(
                    chat_id=telegram_id,
                    text=message,
                    parse_mode=parse_mode
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Error sending message to user {telegram_id}: {e}")
            return False