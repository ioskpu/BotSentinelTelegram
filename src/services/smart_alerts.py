import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from src.database.mongodb import mongodb
from loguru import logger

class SmartAlerts:
    def __init__(self, price_monitor):
        self.price_monitor = price_monitor

    async def detect_volume_spike(self, coin_id: str, threshold: float = 2.0) -> Optional[Dict]:
        """Detecta picos de volumen comparando el volumen actual con el promedio móvil"""
        try:
            # Obtener datos de volumen de CoinGecko (requiere endpoint extendido o history)
            # Por ahora simulamos con lógica de precio si no hay volumen en DB
            history = await mongodb.price_history.find({
                "coin_id": coin_id,
                "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=24)}
            }).sort("timestamp", 1).to_list(length=100)
            
            if len(history) < 10:
                return None
            
            # Nota: En una implementación real, usaríamos el campo 'volume' de la API
            # Aquí implementamos la estructura para el futuro
            return {
                "spike_detected": False,
                "ratio": 1.0,
                "message": "Datos de volumen insuficientes"
            }
        except Exception as e:
            logger.error(f"Error detectando pico de volumen: {e}")
            return None

    async def predict_price_movement(self, coin_id: str) -> Dict:
        """Predicción simple basada en medias móviles y RSI"""
        try:
            history = await mongodb.price_history.find({
                "coin_id": coin_id,
                "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=48)}
            }).sort("timestamp", 1).to_list(length=200)
            
            if len(history) < 14:
                return {"prediction": "neutral", "confidence": 0, "reason": "Datos insuficientes"}
            
            prices = [h['price'] for h in history]
            
            # RSI simple
            deltas = np.diff(prices)
            seed = deltas[:14]
            up = seed[seed >= 0].sum() / 14
            down = -seed[seed < 0].sum() / 14
            rs = up / down if down != 0 else 100
            rsi = 100. - 100. / (1. + rs)
            
            # Media móvil
            sma = np.mean(prices[-10:])
            current_price = prices[-1]
            
            prediction = "neutral"
            reason = "Mercado estable"
            confidence = 50
            
            if rsi < 30:
                prediction = "bullish"
                reason = "Sobrevendido (RSI bajo)"
                confidence = 70
            elif rsi > 70:
                prediction = "bearish"
                reason = "Sobrecomprado (RSI alto)"
                confidence = 70
            elif current_price > sma * 1.05:
                prediction = "bullish"
                reason = "Tendencia alcista (sobre SMA)"
                confidence = 60
                
            return {
                "prediction": prediction,
                "rsi": rsi,
                "current_price": current_price,
                "reason": reason,
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"Error prediciendo movimiento: {e}")
            return {"prediction": "error", "reason": str(e)}

    async def get_support_resistance(self, coin_id: str) -> Dict:
        """Calcula niveles de soporte y resistencia basados en el historial"""
        try:
            history = await mongodb.price_history.find({
                "coin_id": coin_id,
                "timestamp": {"$gte": datetime.utcnow() - timedelta(days=7)}
            }).sort("timestamp", 1).to_list(length=1000)
            
            if len(history) < 20:
                return {"support": None, "resistance": None}
            
            prices = [h['price'] for h in history]
            
            return {
                "support": min(prices),
                "resistance": max(prices),
                "current": prices[-1]
            }
        except Exception as e:
            logger.error(f"Error calculando soporte/resistencia: {e}")
            return {"support": None, "resistance": None}
