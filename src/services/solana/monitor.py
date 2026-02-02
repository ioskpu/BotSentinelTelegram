import asyncio
from typing import Dict, List, Optional, Callable
from loguru import logger
from datetime import datetime
from src.services.solana.client import SolanaClient

class SolanaMonitor:
    """Monitor de transacciones para la red Solana"""
    
    def __init__(self):
        self.client = SolanaClient()
        self.watched_accounts: Dict[str, Dict] = {}
        self.is_monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        
    async def add_account(self, public_key: str, chat_id: int):
        """Añadir una cuenta a la lista de monitoreo"""
        if public_key not in self.watched_accounts:
            # Obtener la última transacción para empezar a monitorear desde ahí
            last_txs = await self.client.get_recent_transactions(public_key, limit=1)
            last_signature = last_txs[0]['signature'] if last_txs else None
            
            self.watched_accounts[public_key] = {
                'chat_id': chat_id,
                'last_signature': last_signature,
                'added_at': datetime.now()
            }
            logger.info(f"👀 Monitoreando cuenta Solana: {public_key} para chat {chat_id}")
            return True
        return False
        
    async def remove_account(self, public_key: str):
        """Eliminar una cuenta del monitoreo"""
        if public_key in self.watched_accounts:
            del self.watched_accounts[public_key]
            logger.info(f"🚫 Dejando de monitorear cuenta Solana: {public_key}")
            return True
        return False

    async def start_monitoring(self, callback: Callable):
        """Iniciar el bucle de monitoreo"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        logger.info("🚀 Iniciando monitor de Solana...")
        
        while self.is_monitoring:
            try:
                for public_key, info in list(self.watched_accounts.items()):
                    # Obtener transacciones recientes
                    txs = await self.client.get_recent_transactions(public_key, limit=5)
                    
                    if not txs:
                        continue
                        
                    # Filtrar transacciones nuevas (posteriores a la última guardada)
                    new_txs = []
                    for tx in txs:
                        if tx['signature'] == info['last_signature']:
                            break
                        new_txs.append(tx)
                    
                    if new_txs:
                        # Actualizar la última firma vista
                        self.watched_accounts[public_key]['last_signature'] = new_txs[0]['signature']
                        
                        # Notificar vía callback
                        for tx in reversed(new_txs): # Procesar de la más antigua a la más nueva
                            await callback(
                                network="SOLANA",
                                address=public_key,
                                chat_id=info['chat_id'],
                                tx_data=tx
                            )
                
                # Esperar antes de la siguiente ronda (Solana es rápido, pero no queremos saturar el RPC)
                await asyncio.sleep(60) 
                
            except Exception as e:
                logger.error(f"Error en el bucle de monitoreo de Solana: {e}")
                await asyncio.sleep(30) # Esperar un poco antes de reintentar si hay error

    def stop_monitoring(self):
        """Detener el monitoreo"""
        self.is_monitoring = False
        logger.info("🛑 Monitor de Solana detenido.")
