#!/usr/bin/env python3
"""
Script de mantenimiento para Crypto Sentinel Bot
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Asegurar que el directorio raíz esté en el PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.mongodb import mongodb
from src.services.price_monitor import PriceMonitor
from loguru import logger

async def cleanup_old_data():
    """Limpiar datos antiguos de la base de datos"""
    try:
        # Eliminar historial de precios mayor a 30 días
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        result = await mongodb.price_history.delete_many({
            "timestamp": {"$lt": cutoff_date}
        })
        logger.info(f"🧹 Eliminados {result.deleted_count} registros antiguos de price_history")
        
        # Eliminar notificaciones antiguas
        result = await mongodb.notifications.delete_many({
            "sent_at": {"$lt": cutoff_date}
        })
        logger.info(f"🧹 Eliminados {result.deleted_count} notificaciones antiguas")
        
        # Desactivar alertas muy antiguas sin disparar
        old_alerts_cutoff = datetime.utcnow() - timedelta(days=90)
        result = await mongodb.alerts.update_many({
            "is_active": True,
            "created_at": {"$lt": old_alerts_cutoff},
            "triggered_at": None
        }, {
            "$set": {"is_active": False, "deactivated_reason": "auto_cleanup"}
        })
        logger.info(f"🧹 Desactivadas {result.modified_count} alertas antiguas")
        
        return True
    except Exception as e:
        logger.error(f"Error en cleanup: {e}")
        return False

async def update_price_history():
    """Actualizar historial de precios"""
    try:
        monitor = PriceMonitor()
        await monitor.start()
        
        coins = ['solana', 'stellar', 'bitcoin', 'ethereum']
        prices = await monitor.get_multiple_prices(coins)
        
        for coin_id, price in prices.items():
            if price:
                await mongodb.price_history.insert_one({
                    "coin_id": coin_id,
                    "price": price,
                    "timestamp": datetime.utcnow()
                })
        
        await monitor.stop()
        logger.info(f"📈 Historial de precios actualizado para {len(prices)} monedas")
        return True
    except Exception as e:
        logger.error(f"Error actualizando historial de precios: {e}")
        return False

async def main():
    """Ejecución principal del mantenimiento"""
    logger.info("🛠️ Iniciando tareas de mantenimiento...")
    
    # Conectar a MongoDB si no está conectado
    if not await mongodb.ping():
        logger.error("❌ No se pudo conectar a MongoDB para el mantenimiento")
        return

    # Ejecutar tareas
    await cleanup_old_data()
    await update_price_history()
    
    logger.info("✅ Mantenimiento completado")

if __name__ == "__main__":
    asyncio.run(main())
