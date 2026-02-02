import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Para usar sin display
from datetime import datetime, timedelta
import numpy as np
from src.database.mongodb import mongodb
from loguru import logger

class ChartGenerator:
    @staticmethod
    async def generate_price_chart(coin_id: str, days: int = 7, price_monitor=None) -> io.BytesIO:
        """Genera un gráfico de precios históricos"""
        try:
            # Obtener datos históricos de DB
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            history = await mongodb.price_history.find({
                "coin_id": coin_id,
                "timestamp": {"$gte": cutoff_date}
            }).sort("timestamp", 1).to_list(length=1000)
            
            # Si no hay datos en DB, intentar obtener de la API
            if (not history or len(history) < 10) and price_monitor:
                logger.info(f"Pocos datos en DB para gráfico de {coin_id}, consultando API...")
                history = await price_monitor.get_historical_data(coin_id, days=days)
            
            if not history or len(history) < 2:
                return None
            
            # Preparar datos
            timestamps = [h['timestamp'] for h in history]
            prices = [h['price'] for h in history]
            
            # Crear gráfico
            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, prices, 'b-', linewidth=2)
            plt.fill_between(timestamps, prices, alpha=0.3)
            
            # Configurar estilo
            plt.title(f'Precio de {coin_id.upper()} - Últimos {days} días', fontsize=14, fontweight='bold')
            plt.xlabel('Fecha')
            plt.ylabel('Precio (USD)')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Guardar en buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100)
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            return None
    
    @staticmethod
    def generate_price_change_chart(prices_24h: dict) -> io.BytesIO:
        """Genera gráfico de barras de cambios porcentuales"""
        try:
            # Filtrar monedas con datos
            valid_prices = {k: v for k, v in prices_24h.items() if v is not None}
            if not valid_prices:
                return None
            
            # Preparar datos
            coins = list(valid_prices.keys())
            changes = list(valid_prices.values())
            
            # Crear gráfico
            plt.figure(figsize=(12, 6))
            colors = ['green' if x >= 0 else 'red' for x in changes]
            plt.bar(coins, changes, color=colors)
            
            # Configurar estilo
            plt.title('Cambio porcentual 24h', fontsize=14, fontweight='bold')
            plt.ylabel('Cambio %')
            plt.xticks(rotation=45)
            plt.grid(True, axis='y', alpha=0.3)
            plt.tight_layout()
            
            # Guardar en buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100)
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating bar chart: {e}")
            return None
