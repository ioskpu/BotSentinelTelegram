from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from loguru import logger
from src.services.price_monitor import PriceMonitor
from src.services.portfolio_service import PortfolioService
from src.database.mongodb import mongodb
from src.database.models import User, Alert, PortfolioEntry
import re

class TelegramHandlers:
    def __init__(self):
        self.price_monitor = PriceMonitor()
        self.portfolio_service = PortfolioService()
    
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
/coins - Listar las 28+ monedas soportadas
/trending - Ver tendencias de CoinGecko
/predict [moneda] - Análisis IA y Soportes
/portfolio - Gestionar tu inversión
/help - Mostrar ayuda completa
        """
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /help"""
        help_text = """
📚 *Ayuda - Crypto Sentinel Bot*

*Comandos:*
/start - Iniciar el bot
/price [moneda] - Ver precio (ej: /price SOL)
/coins - Listar 28 monedas soportadas
/trending - Top 7 monedas en tendencia
/convert [cant] [de] [a] - Conversor (ej: /convert 1 BTC USD)
/alert [moneda] [condición] - Configurar alerta
/myalerts - Listar alertas activas
/predict [moneda] - Análisis Técnico (RSI, Soportes)
/chart [moneda] - Ver gráfico de precio
/portfolio - Ver valor de tu inversión
/padd [moneda] [cant] [precio] - Añadir compra
/pdel [id] - Eliminar del portafolio
/stats - Estadísticas del bot

*Ejemplos de alertas:*
- `SOL > 150` (alerta cuando supere $150)
- `SOL 10%` (alerta cuando cambie un 10%)
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def price_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /price"""
        args = context.args
        
        if not args:
            # Mostrar precios de las principales monedas
            default_coins = ['solana', 'stellar', 'bitcoin', 'ethereum', 'cardano']
            prices = await self.price_monitor.get_multiple_prices(default_coins)
            
            message = "💰 *Precios principales:*\n\n"
            for coin, price in prices.items():
                if price:
                    # Mapear ID a símbolo
                    coin_to_symbol = {
                        'solana': 'SOL',
                        'stellar': 'XLM',
                        'bitcoin': 'BTC',
                        'ethereum': 'ETH',
                        'cardano': 'ADA',
                        'polkadot': 'DOT',
                        'avalanche-2': 'AVAX',
                        'matic-network': 'MATIC',
                        'cosmos': 'ATOM',
                    }
                    symbol = coin_to_symbol.get(coin, coin.upper())
                    message += f"• *{symbol}:* ${price:,.4f}\n"
            
            keyboard = [
                [InlineKeyboardButton("🔄 Actualizar", callback_data="refresh_prices")],
                [InlineKeyboardButton("🔔 Nueva Alerta", callback_data="new_alert")],
                [InlineKeyboardButton("📈 Más monedas", callback_data="more_coins")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            # Buscar precio específico
            symbol = args[0].upper()
            price = await self.price_monitor.get_price_by_symbol(symbol)
            
            if price:
                await update.message.reply_text(
                    f"💎 *{symbol}:* ${price:,.4f} USD",
                    parse_mode='Markdown'
                )
            else:
                # Mostrar monedas disponibles
                available_coins = "SOL, XLM, BTC, ETH, ADA, DOT, AVAX, MATIC, ATOM, DOGE, SHIB, UNI, LINK"
                await update.message.reply_text(
                    f"❌ Moneda no encontrada\n\n"
                    f"*Monedas disponibles:*\n{available_coins}\n\n"
                    f"Ejemplo: `/price ADA`",
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
    
    async def list_coins_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /coins - Lista todas las monedas disponibles"""
        coins_list = """
📊 *Monedas disponibles:*

*Principales:*
• SOL - Solana
• XLM - Stellar
• BTC - Bitcoin
• ETH - Ethereum
• ADA - Cardano
• DOT - Polkadot

*Layer 1:*
• AVAX - Avalanche
• MATIC - Polygon
• ATOM - Cosmos
• ALGO - Algorand

*Meme Coins:*
• DOGE - Dogecoin
• SHIB - Shiba Inu
• PEPE - Pepe

*DeFi:*
• UNI - Uniswap
• LINK - Chainlink
• AAVE - Aave

*Stablecoins:*
• USDT - Tether
• USDC - USD Coin
• DAI - Dai

📝 *Uso:* `/price [SÍMBOLO]`
📝 *Ejemplo:* `/price AVAX`
"""
        await update.message.reply_text(coins_list, parse_mode='Markdown')

    async def convert_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /convert - Conversor de criptomonedas"""
        args = context.args
        
        if len(args) != 3:
            await update.message.reply_text(
                "🔄 *Conversor de Criptomonedas*\n\n"
                "*Uso:* `/convert [CANTIDAD] [DE] [A]`\n\n"
                "*Ejemplos:*\n"
                "`/convert 1 BTC USD`\n"
                "`/convert 100 SOL USDT`\n"
                "`/convert 0.5 ETH BTC`\n\n"
                "*Soportado:* USD, EUR, BTC, ETH, SOL, XLM, etc.",
                parse_mode='Markdown'
            )
            return
        
        try:
            amount = float(args[0])
            from_coin = args[1].upper()
            to_coin = args[2].upper()
            
            # Obtener precios
            if from_coin in ['USD', 'EUR']:
                from_price = 1
            else:
                from_price = await self.price_monitor.get_price_by_symbol(from_coin)
            
            if to_coin in ['USD', 'EUR']:
                to_price = 1
            else:
                to_price = await self.price_monitor.get_price_by_symbol(to_coin)
            
            if not from_price or not to_price:
                await update.message.reply_text("❌ No se pudo obtener los precios")
                return
            
            # Calcular conversión
            if from_coin in ['USD', 'EUR']:
                result = amount / to_price
            elif to_coin in ['USD', 'EUR']:
                result = amount * from_price
            else:
                result = (amount * from_price) / to_price
            
            # Formatear resultado
            if to_coin in ['USD', 'EUR']:
                result_text = f"${result:,.2f}" if to_coin == 'USD' else f"€{result:,.2f}"
            else:
                result_text = f"{result:.8f}"
            
            await update.message.reply_text(
                f"🔄 *Conversión:*\n\n"
                f"• {amount} {from_coin} = {result_text} {to_coin}\n\n"
                f"*Tasas:*\n"
                f"1 {from_coin} = {from_price:,.4f} USD\n"
                f"1 {to_coin} = {to_price:,.4f} USD",
                parse_mode='Markdown'
            )
            
        except ValueError:
            await update.message.reply_text("❌ Cantidad inválida")
        except Exception as e:
            logger.error(f"Error en conversión: {e}")
            await update.message.reply_text("❌ Error en la conversión")

    async def trending_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /trending - Monedas en tendencia"""
        try:
            trending = await self.price_monitor.get_trending_coins()
            
            if not trending:
                await update.message.reply_text("❌ No se pudieron obtener tendencias")
                return
            
            message = "🔥 *Monedas en Tendencia*\n\n"
            
            for i, coin in enumerate(trending[:7], 1):  # Top 7
                message += (
                    f"{i}. *{coin['symbol']}* - {coin['name']}\n"
                    f"   Rank: #{coin.get('market_cap_rank', 'N/A')}\n"
                    f"   Score: {coin.get('score', 0):.2f}\n\n"
                )
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error showing trending: {e}")
            await update.message.reply_text("❌ Error obteniendo tendencias")

    async def chart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /chart - Muestra gráfico de precios"""
        args = context.args
        
        if not args:
            await update.message.reply_text(
                "📈 *Uso:* `/chart [MONEDA] [días]`\n\n"
                "*Ejemplos:*\n"
                "`/chart SOL` - Gráfico de 7 días\n"
                "`/chart BTC 30` - Gráfico de 30 días\n\n"
                "*Monedas disponibles:* SOL, XLM, BTC, ETH, ADA, etc.",
                parse_mode='Markdown'
            )
            return
        
        coin_symbol = args[0].upper()
        days = int(args[1]) if len(args) > 1 and args[1].isdigit() else 7
        days = min(max(days, 1), 365)  # Limitar entre 1 y 365 días
        
        # Mapear símbolo a ID
        symbol_to_id = {
            'SOL': 'solana',
            'XLM': 'stellar',
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'AVAX': 'avalanche-2',
            'MATIC': 'matic-network',
            'ATOM': 'cosmos',
            'ALGO': 'algorand',
            'DOGE': 'dogecoin',
            'SHIB': 'shiba-inu',
            'PEPE': 'pepe',
            'UNI': 'uniswap',
            'LINK': 'chainlink',
            'AAVE': 'aave',
            'USDT': 'tether',
            'USDC': 'usd-coin',
            'DAI': 'dai',
            'XRP': 'ripple',
            'LTC': 'litecoin',
            'BNB': 'binancecoin',
        }
        
        coin_id = symbol_to_id.get(coin_symbol)
        if not coin_id:
            await update.message.reply_text(f"❌ Moneda {coin_symbol} no soportada")
            return
        
        # Generar gráfico
        from src.services.chart_generator import ChartGenerator
        chart_buffer = await ChartGenerator.generate_price_chart(coin_id, days)
        
        if chart_buffer:
            await update.message.reply_photo(
                photo=chart_buffer,
                caption=f"📈 *{coin_symbol} - Últimos {days} días*\n\n"
                       f"Usa `/price {coin_symbol}` para precio actual",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ No hay datos suficientes para {coin_symbol}. "
                "El sistema necesita recolectar datos históricos primero."
            )

    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /portfolio - Muestra el valor total del portafolio"""
        user = await mongodb.users.find_one({"telegram_id": update.effective_user.id})
        if not user:
            await update.message.reply_text("❌ Usuario no encontrado")
            return

        portfolio_data = await self.portfolio_service.calculate_portfolio_value(user['_id'], self.price_monitor)
        
        if not portfolio_data['entries']:
            await update.message.reply_text(
                "📭 *Tu portafolio está vacío*\n\n"
                "Usa `/padd [SÍMBOLO] [CANTIDAD] [PRECIO_COMPRA]` para añadir tu primera inversión.",
                parse_mode='Markdown'
            )
            return

        message = "📊 *Tu Portafolio:*\n\n"
        message += f"💰 *Valor Total:* ${portfolio_data['total_value']:,.2f} USD\n"
        
        if portfolio_data['total_cost'] > 0:
            profit = portfolio_data['total_profit']
            profit_percent = (profit / portfolio_data['total_cost']) * 100
            emoji = "🚀" if profit >= 0 else "📉"
            message += f"📈 *Ganancia/Pérdida:* {emoji} ${profit:,.2f} ({profit_percent:+.2f}%)\n"
        
        message += "\n*Detalle por moneda:*\n"
        for entry in portfolio_data['entries']:
            profit_emoji = "🟢" if (entry['profit_loss'] or 0) >= 0 else "🔴"
            message += (
                f"{profit_emoji} *{entry['symbol']}:* {entry['amount']:.4f} \n"
                f"   Valor: ${entry['current_value']:,.2f} | P: ${entry['current_price']:,.4f}\n"
            )
            if entry['profit_loss'] is not None:
                message += f"   G/P: ${entry['profit_loss']:,.2f} ({entry['profit_loss_percent']:+.2f}%)\n"
            message += "\n"

        message += "📝 Usa `/padd` para añadir y `/pdel [ID]` para eliminar."
        
        await update.message.reply_text(message, parse_mode='Markdown')

    async def portfolio_add_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /padd - Añade una moneda al portafolio"""
        args = context.args
        if len(args) < 2:
            await update.message.reply_text(
                "📝 *Uso:* `/padd [SÍMBOLO] [CANTIDAD] [PRECIO_OPCIONAL]`\n\n"
                "*Ejemplo:* `/padd SOL 10 150.5`",
                parse_mode='Markdown'
            )
            return

        try:
            symbol = args[0].upper()
            amount = float(args[1])
            buy_price = float(args[2]) if len(args) > 2 else None

            user = await mongodb.users.find_one({"telegram_id": update.effective_user.id})
            if not user:
                await update.message.reply_text("❌ Usuario no encontrado")
                return

            entry = await self.portfolio_service.add_entry(user['_id'], symbol, amount, buy_price)
            
            await update.message.reply_text(
                f"✅ *Inversión añadida*\n\n"
                f"• *Moneda:* {symbol}\n"
                f"• *Cantidad:* {amount}\n"
                f"• *Precio:* {f'${buy_price:,.2f}' if buy_price else 'N/A'}\n\n"
                f"Usa `/portfolio` para ver tu balance.",
                parse_mode='Markdown'
            )
        except ValueError:
            await update.message.reply_text("❌ Cantidad o precio inválidos")
        except Exception as e:
            logger.error(f"Error adding portfolio entry: {e}")
            await update.message.reply_text("❌ Error al añadir al portafolio")

    async def portfolio_del_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /pdel - Elimina una entrada del portafolio"""
        args = context.args
        if not args:
            await update.message.reply_text("📝 *Uso:* `/pdel [ID_ENTRADA]`", parse_mode='Markdown')
            return

        try:
            entry_id = args[0]
            success = await self.portfolio_service.remove_entry(entry_id)
            
            if success:
                await update.message.reply_text("✅ Entrada eliminada correctamente.")
            else:
                await update.message.reply_text("❌ No se encontró la entrada o hubo un error.")
        except Exception as e:
            logger.error(f"Error deleting portfolio entry: {e}")
            await update.message.reply_text("❌ ID de entrada inválido.")

    async def predict_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /predict - Predicción de movimiento de precio"""
        args = context.args
        if not args:
            await update.message.reply_text("📝 *Uso:* `/predict [SÍMBOLO]`", parse_mode='Markdown')
            return

        symbol = args[0].upper()
        # Mapear símbolo a ID
        symbol_to_id = {
            'SOL': 'solana', 'XLM': 'stellar', 'BTC': 'bitcoin', 'ETH': 'ethereum',
            'ADA': 'cardano', 'DOT': 'polkadot', 'AVAX': 'avalanche-2', 'MATIC': 'matic-network',
            'ATOM': 'cosmos', 'ALGO': 'algorand', 'DOGE': 'dogecoin', 'SHIB': 'shiba-inu',
            'PEPE': 'pepe', 'UNI': 'uniswap', 'LINK': 'chainlink', 'AAVE': 'aave',
            'USDT': 'tether', 'USDC': 'usd-coin', 'DAI': 'dai', 'XRP': 'ripple',
            'LTC': 'litecoin', 'BNB': 'binancecoin'
        }
        
        coin_id = symbol_to_id.get(symbol)
        if not coin_id:
            await update.message.reply_text(f"❌ Moneda {symbol} no soportada.")
            return

        from src.services.smart_alerts import SmartAlerts
        smart_alerts = SmartAlerts(self.price_monitor)
        
        message = await update.message.reply_text(f"🔍 Analizando {symbol}...")
        
        prediction = await smart_alerts.predict_price_movement(coin_id)
        levels = await smart_alerts.get_support_resistance(coin_id)
        
        emoji_map = {"bullish": "🚀 Alcista", "bearish": "📉 Bajista", "neutral": "⚖️ Neutral"}
        
        response = f"🤖 *Análisis Inteligente para {symbol}*\n\n"
        response += f"📈 *Predicción:* {emoji_map.get(prediction['prediction'], '❓ Desconocida')}\n"
        response += f"🎯 *Confianza:* {prediction['confidence']}%\n"
        response += f"📝 *Razón:* {prediction['reason']}\n\n"
        
        if levels['support'] and levels['resistance']:
            response += f"🛡️ *Soporte (7d):* ${levels['support']:,.4f}\n"
            response += f"🏔️ *Resistencia (7d):* ${levels['resistance']:,.4f}\n"
            response += f"💰 *Precio Actual:* ${levels['current']:,.4f}\n\n"
        
        response += "_Nota: Esto no es consejo financiero._"
        
        await message.edit_text(response, parse_mode='Markdown')

    async def callback_query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja las llamadas de callback (botones)"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "refresh_prices":
            default_coins = ['solana', 'stellar', 'bitcoin', 'ethereum', 'cardano']
            prices = await self.price_monitor.get_multiple_prices(default_coins)
            
            message = "💰 *Precios actualizados:*\n\n"
            for coin, price in prices.items():
                if price:
                    coin_to_symbol = {
                        'solana': 'SOL',
                        'stellar': 'XLM',
                        'bitcoin': 'BTC',
                        'ethereum': 'ETH',
                        'cardano': 'ADA'
                    }
                    symbol = coin_to_symbol.get(coin, coin.upper())
                    message += f"• *{symbol}:* ${price:,.4f}\n"
            
            keyboard = [
                [InlineKeyboardButton("🔄 Actualizar", callback_data="refresh_prices")],
                [InlineKeyboardButton("🔔 Nueva Alerta", callback_data="new_alert")],
                [InlineKeyboardButton("📈 Más monedas", callback_data="more_coins")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=message, parse_mode='Markdown', reply_markup=reply_markup)
            
        elif query.data == "more_coins":
            await self.list_coins_command(update, context)

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