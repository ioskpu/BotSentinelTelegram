from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from loguru import logger
from src.services.price_monitor import PriceMonitor
from src.database.mongodb import mongodb
from src.database.models import User, Alert
import re

class TelegramHandlers:
    def __init__(self):
        self.price_monitor = PriceMonitor()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /start"""
        user_data = update.effective_user
        
        # Guardar usuario en DB
        user = {
            "telegram_id": user_data.id,
            "username": user_data.username,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name
        }
        
        await mongodb.users.update_one(
            {"telegram_id": user_data.id},
            {"$set": user},
            upsert=True
        )
        
        welcome_text = """
🤖 *Bienvenido a Crypto Sentinel Bot* 🚀

*Comandos disponibles:*
/price - Ver precios de criptomonedas
/alert - Configurar una alerta de precio
/myalerts - Ver tus alertas activas
/help - Mostrar ayuda
        """
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /help"""
        help_text = """
📚 *Ayuda - Crypto Sentinel Bot*

*Comandos:*
/start - Iniciar el bot
/price [moneda] - Ver precio de una cripto (ej: /price SOL)
/alert - Configurar alerta de precio
/myalerts - Listar alertas activas
/deletealert [id] - Eliminar una alerta
/stats - Estadísticas del bot

*Ejemplos de alertas:*
- `SOL > 150` (alerta cuando SOL supere $150)
- `XLM < 0.12` (alerta cuando XLM baje de $0.12)
- `SOL 10%` (alerta cuando SOL suba/baje 10%)

*Monedas soportadas:* SOL, XLM, BTC, ETH
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def price_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /price"""
        args = context.args
        
        if not args:
            # Mostrar precios principales
            prices = await self.price_monitor.get_multiple_prices(['solana', 'stellar', 'bitcoin'])
            
            message = "💰 *Precios actuales:*\n\n"
            for coin, price in prices.items():
                if price:
                    coin_name = coin.capitalize()
                    message += f"• *{coin_name}:* ${price:,.4f}\n"
            
            keyboard = [
                [InlineKeyboardButton("🔄 Actualizar", callback_data="refresh_prices")],
                [InlineKeyboardButton("🔔 Nueva Alerta", callback_data="new_alert")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            # Buscar precio específico
            symbol = args[0].upper()
            coin_map = {
                'SOL': 'solana',
                'XLM': 'stellar',
                'BTC': 'bitcoin',
                'ETH': 'ethereum'
            }
            
            if symbol in coin_map:
                price = await self.price_monitor.get_price_by_symbol(symbol)
                if price:
                    await update.message.reply_text(
                        f"💎 *{symbol}:* ${price:,.4f} USD",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text(
                        f"❌ No se pudo obtener el precio de {symbol}",
                        parse_mode='Markdown'
                    )
            else:
                await update.message.reply_text(
                    "❌ Moneda no soportada. Usa: SOL, XLM, BTC, ETH",
                    parse_mode='Markdown'
                )
    
    async def alert_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /alert"""
        args = context.args
        
        if not args or len(args) < 2:
            await update.message.reply_text(
                "📝 *Uso:* /alert [MONEDA] [CONDICIÓN]\n\n"
                "*Ejemplos:*\n"
                "`/alert SOL > 150`\n"
                "`/alert XLM < 0.12`\n"
                "`/alert SOL 10%`\n\n"
                "*Monedas:* SOL, XLM, BTC, ETH",
                parse_mode='Markdown'
            )
            return
        
        try:
            # Parsear entrada
            symbol = args[0].upper()
            condition = args[1]
            threshold = float(args[2]) if len(args) > 2 else None
            
            # Validar símbolo
            coin_map = {
                'SOL': ('solana', 'SOL'),
                'XLM': ('stellar', 'XLM'),
                'BTC': ('bitcoin', 'BTC'),
                'ETH': ('ethereum', 'ETH')
            }
            
            if symbol not in coin_map:
                await update.message.reply_text("❌ Moneda no soportada")
                return
            
            coin_id, coin_symbol = coin_map[symbol]
            
            # Parsear condición
            alert_type = None
            parsed_threshold = None
            
            if '>' in condition:
                alert_type = 'price_above'
                parsed_threshold = float(condition.replace('>', ''))
            elif '<' in condition:
                alert_type = 'price_below'
                parsed_threshold = float(condition.replace('<', ''))
            elif '%' in condition:
                alert_type = 'percent_change'
                parsed_threshold = float(condition.replace('%', ''))
            elif threshold:
                # Formato: /alert SOL > 150
                if condition == '>':
                    alert_type = 'price_above'
                    parsed_threshold = threshold
                elif condition == '<':
                    alert_type = 'price_below'
                    parsed_threshold = threshold
            
            if not alert_type or parsed_threshold is None:
                await update.message.reply_text("❌ Formato de condición inválido")
                return
            
            # Obtener usuario
            user = await mongodb.users.find_one({"telegram_id": update.effective_user.id})
            if not user:
                await update.message.reply_text("❌ Usuario no encontrado")
                return
            
            # Crear alerta
            alert_data = Alert(
                user_id=user['_id'],
                coin_id=coin_id,
                coin_symbol=coin_symbol,
                alert_type=alert_type,
                threshold=parsed_threshold
            )
            
            result = await mongodb.alerts.insert_one(alert_data.dict(by_alias=True))
            
            await update.message.reply_text(
                f"✅ *Alerta creada exitosamente*\n\n"
                f"• *Moneda:* {coin_symbol}\n"
                f"• *Condición:* {alert_type.replace('_', ' ').title()}\n"
                f"• *Umbral:* {parsed_threshold}\n"
                f"• *ID:* `{result.inserted_id}`\n\n"
                f"Usa /myalerts para ver todas tus alertas.",
                parse_mode='Markdown'
            )
            
        except ValueError as e:
            await update.message.reply_text(f"❌ Error en los valores: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            await update.message.reply_text("❌ Error creando la alerta")
    
    async def myalerts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /myalerts"""
        user = await mongodb.users.find_one({"telegram_id": update.effective_user.id})
        if not user:
            await update.message.reply_text("❌ Usuario no encontrado")
            return
        
        alerts = await mongodb.alerts.find({
            "user_id": user['_id'],
            "is_active": True
        }).to_list(length=20)
        
        if not alerts:
            await update.message.reply_text("📭 No tienes alertas activas")
            return
        
        message = "🔔 *Tus Alertas Activas:*\n\n"
        for alert in alerts:
            condition_map = {
                'price_above': '>',
                'price_below': '<',
                'percent_change': '%'
            }
            condition = condition_map.get(alert['alert_type'], alert['alert_type'])
            
            message += (
                f"• *{alert['coin_symbol']}* {condition} {alert['threshold']}\n"
                f"  ID: `{alert['_id']}`\n\n"
            )
        
        message += "📝 Usa /deletealert [ID] para eliminar una alerta"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def deletealert_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /deletealert"""
        args = context.args
        
        if not args:
            await update.message.reply_text("📝 Uso: /deletealert [ID_DE_ALERTA]")
            return
        
        alert_id = args[0]
        
        try:
            from bson import ObjectId
            result = await mongodb.alerts.update_one(
                {"_id": ObjectId(alert_id)},
                {"$set": {"is_active": False}}
            )
            
            if result.modified_count > 0:
                await update.message.reply_text("✅ Alerta eliminada exitosamente")
            else:
                await update.message.reply_text("❌ Alerta no encontrada o ya inactiva")
        except Exception as e:
            await update.message.reply_text("❌ ID de alerta inválido")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /stats"""
        # Obtener estadísticas
        total_users = await mongodb.users.count_documents({})
        total_alerts = await mongodb.alerts.count_documents({})
        active_alerts = await mongodb.alerts.count_documents({"is_active": True})
        
        # Obtener precios actuales
        prices = await self.price_monitor.get_multiple_prices(['solana', 'stellar'])
        
        message = (
            f"📊 *Estadísticas del Bot*\n\n"
            f"• Usuarios totales: {total_users}\n"
            f"• Alertas totales: {total_alerts}\n"
            f"• Alertas activas: {active_alerts}\n\n"
            f"💰 *Precios actuales:*\n"
        )
        
        if prices.get('solana'):
            message += f"• SOL: ${prices['solana']:,.4f}\n"
        if prices.get('stellar'):
            message += f"• XLM: ${prices['stellar']:,.4f}\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def callback_query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja las llamadas de callback (botones)"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "refresh_prices":
            prices = await self.price_monitor.get_multiple_prices(['solana', 'stellar', 'bitcoin'])
            
            message = "💰 *Precios actualizados:*\n\n"
            for coin, price in prices.items():
                if price:
                    coin_name = coin.capitalize()
                    message += f"• *{coin_name}:* ${price:,.4f}\n"
            
            await query.edit_message_text(text=message, parse_mode='Markdown')
            
        elif query.data == "new_alert":
            await query.edit_message_text(
                text="📝 *Crear Nueva Alerta*\n\n"
                     "Envía el comando:\n"
                     "`/alert [MONEDA] [CONDICIÓN]`\n\n"
                     "*Ejemplo:* `/alert SOL > 150`",
                parse_mode='Markdown'
            )

    async def check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /check - Verifica alertas manualmente"""
        user = await mongodb.users.find_one({"telegram_id": update.effective_user.id})
        if not user:
            await update.message.reply_text("❌ Usuario no encontrado")
            return
        
        message = await update.message.reply_text("🔍 Verificando tus alertas...")
        
        # Obtener servicio de alertas del bot (inyectado o desde price_monitor)
        alert_service = getattr(self, 'alert_service', None)
        if not alert_service and hasattr(self.price_monitor, 'alert_service'):
            alert_service = self.price_monitor.alert_service
        
        if alert_service:
            triggered = await alert_service.check_user_alerts(update.effective_user.id, force_check=True)
            
            if triggered:
                await message.edit_text(
                    f"✅ Se activaron {len(triggered)} alertas. Revisa tus mensajes privados."
                )
            else:
                await message.edit_text("📭 No se activaron alertas en este momento.")
        else:
            await message.edit_text("⚠️ Servicio de alertas no disponible temporalmente.")
    
    async def test_alert_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /testalert - Envía una alerta de prueba"""
        try:
            # Crear alerta de prueba
            test_message = (
                "🚨 *ALERTA DE PRUEBA*\n\n"
                "• *Moneda:* SOL\n"
                "• *Precio actual:* $150.25\n"
                "• *Condición:* > $150.00\n\n"
                "✅ Este es un mensaje de prueba para verificar "
                "que las notificaciones funcionan correctamente."
            )
            
            await update.message.reply_text(test_message, parse_mode='Markdown')
            
            logger.info(f"Usuario {update.effective_user.id} solicitó prueba de alerta")
            
        except Exception as e:
            await update.message.reply_text("❌ Error en la prueba de alerta")
            logger.error(f"Error en test_alert: {e}")