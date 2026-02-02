#!/usr/bin/env python3
"""
Script de prueba para funcionalidades blockchain
"""

import asyncio
import sys
import os

# Añadir el directorio raíz al path para poder importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.services.stellar.client import StellarClient
from src.services.solana.client import SolanaClient
from loguru import logger

async def test_stellar():
    """Probar cliente Stellar"""
    print("🌌 Probando conexión Stellar...")
    try:
        client = StellarClient()
        
        # Cuenta de prueba pública de Stellar (SDF)
        test_account = "GA5XIGA5C7QTPTWXQHY6MCJRMTRZDOSHR6EFIBNDQTCQHG262N4GGKTM"
        
        balance = await client.get_account_balance(test_account)
        if balance:
            print(f"✅ Stellar conectado")
            print(f"   Cuenta: {test_account[:8]}...")
            print(f"   Balances: {len(balance['balances'])}")
            for bal in balance['balances'][:3]:  # Mostrar primeros 3
                print(f"     • {bal['asset']}: {bal['balance']}")
            return True
        else:
            print("⚠️  No se pudo obtener balance de cuenta de prueba")
            return False
            
    except Exception as e:
        print(f"❌ Error en Stellar: {e}")
        return False

async def test_solana():
    """Probar cliente Solana"""
    print("🔵 Probando conexión Solana...")
    try:
        client = SolanaClient()
        
        # Cuenta de prueba pública de Solana (Solana Foundation)
        test_account = "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
        
        balance = await client.get_account_balance(test_account)
        if balance:
            print(f"✅ Solana conectado")
            print(f"   Cuenta: {test_account[:8]}...")
            print(f"   Balance SOL: {balance['balance_sol']}")
            return True
        else:
            print("⚠️  No se pudo obtener balance de cuenta de prueba")
            return False
            
    except Exception as e:
        print(f"❌ Error en Solana: {e}")
        return False

async def main():
    """Ejecutar todas las pruebas blockchain"""
    print("🔗 INICIANDO PRUEBAS BLOCKCHAIN")
    print("=" * 40)
    
    tests = [
        ("Stellar Network", test_stellar),
        ("Solana Network", test_solana)
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
    print("📊 RESUMEN DE PRUEBAS BLOCKCHAIN:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Resultado: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("\n✨ ¡Todas las pruebas blockchain pasaron!")
        return 0
    else:
        print("\n⚠️  Algunas pruebas blockchain fallaron")
        return 1

if __name__ == "__main__":
    logger.remove()
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
