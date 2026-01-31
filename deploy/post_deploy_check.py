#!/usr/bin/env python3
"""
Script para verificar el estado después del despliegue
"""

import asyncio
import httpx
import sys
from loguru import logger

async def check_health(endpoint: str):
    """Verificar endpoint de health"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{endpoint}/health")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Health check: {data['status']}")
                for service, status in data.get('services', {}).items():
                    logger.info(f"   • {service}: {status}")
                return True
            else:
                logger.error(f"❌ Health check failed: {response.status_code}")
                return False
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return False

async def check_status(endpoint: str):
    """Verificar endpoint de status"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{endpoint}/status")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"📊 Status: {data['status']}")
                logger.info(f"   • Usuarios: {data.get('users', 0)}")
                logger.info(f"   • Alertas totales: {data.get('alerts', {}).get('total', 0)}")
                logger.info(f"   • Alertas activas: {data.get('alerts', {}).get('active', 0)}")
                return True
            else:
                logger.error(f"❌ Status check failed: {response.status_code}")
                return False
    except Exception as e:
        logger.error(f"❌ Status check error: {e}")
        return False

async def main():
    """Función principal"""
    if len(sys.argv) != 2:
        logger.error("Uso: python post_deploy_check.py <endpoint>")
        logger.error("Ejemplo: python post_deploy_check.py https://crypto-sentinel-bot.fly.dev")
        sys.exit(1)
    
    endpoint = sys.argv[1].rstrip('/')
    if not endpoint.startswith('http'):
        endpoint = f"https://{endpoint}"
    
    logger.info(f"🔍 Verificando despliegue en: {endpoint}")
    
    tasks = [
        check_health(endpoint),
        check_status(endpoint)
    ]
    
    results = await asyncio.gather(*tasks)
    
    if all(results):
        logger.success("✅ Todas las verificaciones pasaron!")
        return 0
    else:
        logger.error("❌ Algunas verificaciones fallaron")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
