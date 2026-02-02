import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Callable
from loguru import logger
from src.services.stellar.client import StellarClient
from src.database.mongodb import mongodb

class StellarMonitor:
    def __init__(self):
        self.client = StellarClient()
        self.watched_accounts: Dict[str, Dict] = {}
        self.is_monitoring = False
    
    async def add_account(self, address: str, chat_id: int) -> bool:
        """Añadir cuenta Stellar para monitoreo"""
        try:
            # Verificar que la cuenta existe
            balance = await self.client.get_account_balance(address)
            if not balance:
                return False
            
            # Agregar a memoria si no está
            if address not in self.watched_accounts:
                # Obtener última transacción para empezar a monitorear desde ahí
                recent_txs = await self.client.get_account_transactions(address, limit=1)
                last_tx_hash = recent_txs[0]['hash'] if recent_txs else None
                
                self.watched_accounts[address] = {
                    'chat_id': chat_id,
                    'last_tx_hash': last_tx_hash,
                    'added_at': datetime.utcnow()
                }
                logger.info(f"✅ Cuenta Stellar añadida para monitoreo: {address[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error añadiendo cuenta a monitoreo: {e}")
            return False
    
    async def remove_account(self, address: str) -> bool:
        """Remover cuenta Stellar del monitoreo"""
        try:
            if address in self.watched_accounts:
                del self.watched_accounts[address]
            
            logger.info(f"✅ Cuenta Stellar removida del monitoreo: {address[:8]}...")
            return True
        except Exception as e:
            logger.error(f"Error removiendo cuenta del monitoreo: {e}")
            return False

    async def start_monitoring(self, callback: Callable):
        """Iniciar monitoreo en tiempo real de cuentas"""
        self.is_monitoring = True
        logger.info("🚀 Iniciando monitoreo de Stellar...")
        
        while self.is_monitoring:
            try:
                # Monitorear cuentas en memoria
                for address, info in list(self.watched_accounts.items()):
                    # Revisar transacciones recientes
                    recent_txs = await self.client.get_account_transactions(address, limit=5)
                    
                    if not recent_txs:
                        continue
                        
                    # Filtrar nuevas transacciones
                    new_txs = []
                    for tx in recent_txs:
                        if tx['hash'] == info['last_tx_hash']:
                            break
                        new_txs.append(tx)
                    
                    if new_txs:
                        # Actualizar el último hash visto
                        self.watched_accounts[address]['last_tx_hash'] = new_txs[0]['hash']
                        
                        # Notificar vía callback (de más antigua a más nueva)
                        for tx in reversed(new_txs):
                            await callback(
                                network="STELLAR",
                                address=address,
                                chat_id=info['chat_id'],
                                tx_data=tx
                            )
                
                await asyncio.sleep(60) # Revisar cada minuto
                
            except Exception as e:
                logger.error(f"Error en monitoreo Stellar: {e}")
                await asyncio.sleep(30)

    async def stop_monitoring(self):
        self.is_monitoring = False
