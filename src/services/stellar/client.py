import asyncio
from typing import Dict, List, Optional
from loguru import logger
from stellar_sdk import Server, Network
from stellar_sdk.exceptions import NotFoundError
from src.config.settings import settings

class StellarClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializar cliente Stellar Horizon"""
        try:
            self.server = Server(settings.STELLAR_HORIZON_URL)
            # Verificar conexión
            logger.info(f"✅ Conectado a Stellar Horizon: {settings.STELLAR_HORIZON_URL}")
        except Exception as e:
            logger.error(f"❌ Error conectando a Stellar Horizon: {e}")
            raise
    
    async def get_account_balance(self, account_id: str) -> Optional[Dict]:
        """Obtener balance de una cuenta Stellar"""
        try:
            # Server.accounts().account_id().call() es síncrono en stellar-sdk
            # Lo ejecutamos en un thread para no bloquear el loop async
            account = await asyncio.to_thread(self.server.accounts().account_id(account_id).call)
            
            balances = []
            for balance in account['balances']:
                if balance['asset_type'] == 'native':
                    balances.append({
                        'asset': 'XLM',
                        'balance': float(balance['balance']),
                        'asset_type': 'native'
                    })
                else:
                    balances.append({
                        'asset': f"{balance['asset_code']}:{balance['asset_issuer']}",
                        'balance': float(balance['balance']),
                        'asset_type': balance['asset_type']
                    })
            
            return {
                'account_id': account_id,
                'balances': balances,
                'sequence': int(account['sequence']),
                'subentry_count': account['subentry_count']
            }
        except NotFoundError:
            logger.warning(f"Cuenta Stellar no encontrada: {account_id}")
            return None
        except Exception as e:
            logger.error(f"Error obteniendo balance de Stellar: {e}")
            return None
    
    async def get_account_transactions(self, account_id: str, limit: int = 10) -> List[Dict]:
        """Obtener últimas transacciones de una cuenta"""
        try:
            # Ejecutar llamada síncrona en thread
            def _get_txs():
                return self.server.transactions().for_account(account_id).limit(limit).order('desc').call()
            
            response = await asyncio.to_thread(_get_txs)
            
            transactions = []
            for tx in response['_embedded']['records']:
                transactions.append({
                    'id': tx['id'],
                    'hash': tx['hash'],
                    'created_at': tx['created_at'],
                    'fee_charged': tx['fee_charged'],
                    'operation_count': tx['operation_count'],
                    'successful': tx['successful'],
                    'type': tx.get('type', 'transaction'),
                    'memo': tx.get('memo', '')
                })
            
            return transactions
        except Exception as e:
            logger.error(f"Error obteniendo transacciones de Stellar: {e}")
            return []
    
    async def get_transaction_details(self, transaction_hash: str) -> Optional[Dict]:
        """Obtener detalles de una transacción específica"""
        try:
            tx = await asyncio.to_thread(self.server.transactions().transaction(transaction_hash).call)
            
            # Obtener operaciones de la transacción
            def _get_ops():
                return self.server.operations().for_transaction(transaction_hash).limit(20).call()
            
            ops_response = await asyncio.to_thread(_get_ops)
            
            operations = []
            for op in ops_response['_embedded']['records']:
                operations.append({
                    'id': op['id'],
                    'type': op['type'],
                    'source_account': op['source_account'],
                    'created_at': op['created_at']
                })
            
            return {
                'transaction': tx,
                'operations': operations
            }
        except Exception as e:
            logger.error(f"Error obteniendo detalles de transacción: {e}")
            return None
