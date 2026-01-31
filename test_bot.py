#!/usr/bin/env python3
"""
Script de prueba rápida para verificar el funcionamiento del bot
"""

import asyncio
import sys
import os
from datetime import datetime
from src.database.mongodb import mongodb
from src.services.price_monitor import PriceMonitor
from loguru import logger

async def test_database():
    """Probar conexión a MongoDB"""
    print("🧪 Probando conexión a MongoDB...")
    try:
        if await mongodb.ping():
            print("✅ MongoDB conectado correctamente")
            return True
        else:
            print("❌ MongoDB no responde")
            return False
    except Exception as e:
        print(f"❌ Error de MongoDB: {e}")
        return False

async def test_price_monitor():
    """Probar el monitor de precios"""
    print("🧪 Probando monitor de precios...")
    monitor = PriceMonitor()
    await monitor.start()
    
    try:
        prices = await monitor.get_multiple_prices(['solana', 'stellar'])
        
        for coin, price in prices.items():
            if price:
                print(f"✅ {coin.capitalize()}: ${price:,.4f}")
            else:
                print(f"⚠️  No se pudo obtener precio para {coin}")
        
        await monitor.stop()
        return True
    except Exception as e:
        print(f"❌ Error en monitor de precios: {e}")
        return False

async def test_basic_operations():
    """Probar operaciones básicas de la base de datos"""
    print("🧪 Probando operaciones de base de datos...")
    
    try:
        # Crear usuario de prueba
        test_user = {
            "telegram_id": 123456789,
            "username": "test_user",
            "first_name": "Test",
            "last_name": "User",
            "created_at": datetime.utcnow()
        }
        
        # Insertar usuario
        result = await mongodb.users.insert_one(test_user)
        print(f"✅ Usuario insertado: {result.inserted_id}")
        
        # Crear alerta de prueba
        test_alert = {
            "user_id": result.inserted_id,
            "coin_id": "solana",
            "coin_symbol": "SOL",
            "alert_type": "price_above",
            "threshold": 100.0,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        alert_result = await mongodb.alerts.insert_one(test_alert)
        print(f"✅ Alerta insertada: {alert_result.inserted_id}")
        
        # Contar documentos
        user_count = await mongodb.users.count_documents({})
        alert_count = await mongodb.alerts.count_documents({})
        print(f"📊 Estadísticas: {user_count} usuarios, {alert_count} alertas")
        
        # Limpiar datos de prueba
        await mongodb.users.delete_one({"_id": result.inserted_id})
        await mongodb.alerts.delete_one({"_id": alert_result.inserted_id})
        print("🧹 Datos de prueba eliminados")
        
        return True
    except Exception as e:
        print(f"❌ Error en operaciones de base de datos: {e}")
        return False

async def main():
    """Ejecutar todas las pruebas"""
    print("🔍 INICIANDO PRUEBAS DEL BOT")
    print("=" * 40)
    
    tests = [
        ("Base de datos", test_database),
        ("Monitor de precios", test_price_monitor),
        ("Operaciones básicas", test_basic_operations)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("📊 RESUMEN DE PRUEBAS:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Resultado: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("\n✨ ¡Todas las pruebas pasaron! El bot está listo.")
        return 0
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los errores.")
        return 1

if __name__ == "__main__":
    # Configurar logging simple para pruebas
    logger.remove()
    
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Pruebas interrumpidas por el usuario")
        sys.exit(1)
