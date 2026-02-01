import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger
from bson import ObjectId
from telegram import Bot
from telegram.error import TelegramError
from src.database.mongodb import mongodb
from src.services.price_monitor import PriceMonitor
from src.config.settings import settings

class AlertService:
    def __init__(self, bot: Optional[Bot] = None):
        self.price_monitor = PriceMonitor()
        self.last_prices: Dict[str, float] = {}
        self.is_running = False
        self.bot = bot
        self.alert_cooldown: Dict[str, datetime] = {}
    
    def set_bot(self, bot: Bot):
        """Asigna la instancia del bot para notificaciones"""
        self.bot = bot
    
    async def start(self):
        """Inicia el servicio de alertas"""
        self.is_running = True
        await self.price_monitor.start()
        
        logger.info("🚀 Servicio de alertas iniciado")
        
        # Bucle principal de verificación
        while self.is_running:
            try:
                await self.check_alerts()
                await asyncio.sleep(settings.ALERT_CHECK_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en servicio de alertas: {e}")
                await asyncio.sleep(10)
    
    async def stop(self):
        """Detiene el servicio de alertas"""
        self.is_running = False
        await self.price_monitor.stop()
        logger.info("Servicio de alertas detenido")
    
    async def check_alerts(self):
        """Verifica todas las alertas activas"""
        try:
            # Obtener todas las alertas activas
            alerts = await mongodb.alerts.find({"is_active": True}).to_list(length=None)
            if not alerts:
                return
            
            # Agrupar alertas por moneda
            alerts_by_coin: Dict[str, List] = {}
            for alert in alerts:
                coin_id = alert['coin_id']
                if coin_id not in alerts_by_coin:
                    alerts_by_coin[coin_id] = []
                alerts_by_coin[coin_id].append(alert)
            
            # Obtener precios actuales para las monedas necesarias
            coin_ids = list(alerts_by_coin.keys())
            # Siempre incluir monedas principales para el historial
            main_coins = ['bitcoin', 'ethereum', 'solana', 'stellar', 'cardano', 'polkadot', 'avalanche-2']
            all_coin_ids = list(set(coin_ids + main_coins))
            
            current_prices = await self.price_monitor.get_multiple_prices(all_coin_ids)
            
            # Guardar en historial de precios
            await self._save_price_history(current_prices)
            
            # Procesar cada alerta
            for coin_id, coin_alerts in alerts_by_coin.items():
                current_price = current_prices.get(coin_id)
                if not current_price:
                    continue
                
                last_price = self.last_prices.get(coin_id)
                self.last_prices[coin_id] = current_price
                
                for alert in coin_alerts:
                    await self._check_single_alert(alert, current_price, last_price)
                    
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    async def _check_single_alert(self, alert: Dict, current_price: float, last_price: float = None, force_check: bool = False):
        """Verifica una alerta individual"""
        try:
            triggered = False
            message = ""
            
            if alert['alert_type'] == 'price_above':
                if current_price > alert['threshold']:
                    triggered = True
                    message = f"🚀 *{alert['coin_symbol']}* ha superado ${alert['threshold']}!\nPrecio actual: ${current_price:,.4f}"
            
            elif alert['alert_type'] == 'price_below':
                if current_price < alert['threshold']:
                    triggered = True
                    message = f"📉 *{alert['coin_symbol']}* ha caído por debajo de ${alert['threshold']}!\nPrecio actual: ${current_price:,.4f}"
            
            elif alert['alert_type'] == 'percent_change' and (last_price or force_check):
                # Si es force_check y no hay last_price, usamos el precio de cuando se creó la alerta si estuviera disponible, 
                # pero por ahora mantenemos la lógica de comparación si hay last_price.
                if last_price:
                    change_percent = ((current_price - last_price) / last_price) * 100
                    if abs(change_percent) >= alert['threshold']:
                        triggered = True
                        direction = "subido" if change_percent > 0 else "bajado"
                        message = (
                            f"📊 *{alert['coin_symbol']}* ha {direction} {abs(change_percent):.2f}%!\n"
                            f"De ${last_price:,.4f} a ${current_price:,.4f}"
                        )
            
            if triggered:
                await self._trigger_alert(alert, message)
                return True
            
            return False
                
        except Exception as e:
            logger.error(f"Error checking single alert: {e}")
            return False
    
    async def _trigger_alert(self, alert: Dict, message: str):
        """Dispara una alerta y notifica al usuario"""
        try:
            # Obtener información del usuario
            user = await mongodb.users.find_one({"_id": alert['user_id']})
            if not user or not user.get('alerts_active', True):
                return
            
            # Verificar cooldown (evitar spam)
            alert_key = f"{alert['_id']}_{alert['alert_type']}"
            last_trigger = self.alert_cooldown.get(alert_key)
            
            if last_trigger and (datetime.utcnow() - last_trigger).seconds < 300:  # 5 minutos
                return
            
            # Marcar alerta como disparada
            await mongodb.alerts.update_one(
                {"_id": alert['_id']},
                {
                    "$set": {
                        "triggered_at": datetime.utcnow(),
                        "is_active": False
                    }
                }
            )
            
            # Enviar notificación si tenemos bot configurado
            if self.bot:
                try:
                    await self.bot.send_message(
                        chat_id=user['telegram_id'],
                        text=f"🚨 *ALERTA ACTIVADA*\n\n{message}\n\n_Esta alerta ha sido desactivada automáticamente._",
                        parse_mode='Markdown'
                    )
                    self.alert_cooldown[alert_key] = datetime.utcnow()
                    logger.info(f"✅ Notificación enviada a usuario {user['telegram_id']}")
                    
                    # Guardar en historial de notificaciones
                    await self._save_notification_history(
                        user_id=user['_id'],
                        alert_id=alert['_id'],
                        message=message
                    )
                    
                except TelegramError as e:
                    logger.error(f"Error enviando mensaje a Telegram: {e}")
                    # Si el usuario bloqueó el bot, desactivar alertas
                    if "bot was blocked" in str(e).lower():
                        await mongodb.users.update_one(
                            {"_id": user['_id']},
                            {"$set": {"alerts_active": False}}
                        )
            else:
                logger.warning(f"⚠️ Alerta disparada pero bot no configurado: {message}")
                
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
    
    async def _save_notification_history(self, user_id: ObjectId, alert_id: ObjectId, message: str):
        """Guardar historial de notificaciones"""
        try:
            await mongodb.notifications.insert_one({
                "user_id": user_id,
                "alert_id": alert_id,
                "message": message,
                "sent_at": datetime.utcnow(),
                "delivered": True
            })
        except Exception as e:
            logger.error(f"Error saving notification history: {e}")

    async def _save_price_history(self, prices: Dict[str, float]):
        """Guarda los precios actuales en la colección price_history"""
        try:
            if not prices:
                return
                
            timestamp = datetime.utcnow()
            history_entries = [
                {
                    "coin_id": coin_id,
                    "price": price,
                    "timestamp": timestamp
                }
                for coin_id, price in prices.items() if price is not None
            ]
            
            if history_entries:
                await mongodb.price_history.insert_many(history_entries)
                # logger.debug(f"Guardadas {len(history_entries)} entradas en historial de precios")
        except Exception as e:
            logger.error(f"Error saving price history: {e}")

    async def check_user_alerts(self, user_id: int, force_check: bool = False):
        """Verifica alertas de un usuario específico (para comandos)"""
        try:
            user = await mongodb.users.find_one({"telegram_id": user_id})
            if not user:
                return []
            
            alerts = await mongodb.alerts.find({
                "user_id": user['_id'],
                "is_active": True
            }).to_list(length=None)
            
            triggered_alerts = []
            current_prices = {}
            
            for alert in alerts:
                if alert['coin_id'] not in current_prices:
                    price = await self.price_monitor._get_price_by_id(alert['coin_id'])
                    current_prices[alert['coin_id']] = price
                
                if current_prices[alert['coin_id']]:
                    triggered = await self._check_single_alert(alert, current_prices[alert['coin_id']], force_check=force_check)
                    if triggered:
                        triggered_alerts.append(alert)
            
            return triggered_alerts
        except Exception as e:
            logger.error(f"Error checking user alerts: {e}")
            return []