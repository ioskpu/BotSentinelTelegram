import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
from loguru import logger
from src.database.mongodb import mongodb
from src.services.price_monitor import PriceMonitor
from src.config.settings import settings

class AlertService:
    def __init__(self, bot=None):
        self.price_monitor = PriceMonitor()
        self.last_prices: Dict[str, float] = {}
        self.is_running = False
        self.bot = bot
    
    def set_bot(self, bot):
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
            current_prices = await self.price_monitor.get_multiple_prices(coin_ids)
            
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
    
    async def _check_single_alert(self, alert: Dict, current_price: float, last_price: float = None):
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
            
            elif alert['alert_type'] == 'percent_change' and last_price:
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
                
        except Exception as e:
            logger.error(f"Error checking single alert: {e}")
    
    async def _trigger_alert(self, alert: Dict, message: str):
        """Dispara una alerta y notifica al usuario"""
        try:
            # Obtener información del usuario
            user = await mongodb.users.find_one({"_id": alert['user_id']})
            if not user or not user.get('alerts_active', True):
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
            
            # Enviar la notificación real a Telegram
            if self.bot:
                await self._send_telegram_notification(user['telegram_id'], message)
            else:
                logger.warning(f"⚠️ Alerta disparada para {user['telegram_id']} pero el bot no está configurado")
            
            logger.info(f"⚠️ Alerta disparada para usuario {user['telegram_id']}: {message}")
            
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
    
    async def _send_telegram_notification(self, chat_id: int, message: str):
        """Envía una notificación por Telegram"""
        if self.bot:
            await self.bot.send_message(chat_id=chat_id, text=message)