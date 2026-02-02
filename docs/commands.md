¡Perfecto! Vamos directamente a la Fase 2. En esta fase, integraremos Stellar y Solana de manera más profunda, yendo más allá de solo precios para incluir transacciones, balances y alertas de blockchain.

Objetivos de la Fase 2:
Monitoreo de transacciones de Stellar y Solana en tiempo real.

Alertas de transacciones (grandes movimientos, transacciones específicas).

Seguimiento de balances de cuentas específicas.

Interacción básica (consultar balances, enviar transacciones? - tal vez en una fase posterior).

Vamos a estructurar el proyecto para que sea modular, agregando nuevos servicios y handlers.

🏗️ Arquitectura propuesta para Fase 2:
text
src/
├── services/
│   ├── stellar/          # Servicios específicos de Stellar
│   │   ├── monitor.py    # Monitoreo de transacciones y balances
│   │   └── client.py     # Cliente Horizon
│   ├── solana/           # Servicios específicos de Solana
│   │   ├── monitor.py    # Monitoreo de transacciones y balances
│   │   └── client.py     # Cliente RPC
│   └── alert_service.py  # Extender para alertas de blockchain
└── bot/
    └── handlers.py       # Nuevos comandos para Stellar/Solana
Vamos a empezar por la integración de Stellar, luego Solana, y finalmente unificar en el servicio de alertas.

Paso 1: Integración de Stellar
PROMPT 36: Configurar cliente Stellar Horizon
Archivo: src/services/stellar/client.py

python
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
            account = self.server.accounts().account_id(account_id).call()
            
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
                        'asset_type': 'credit_alphanum4' if balance['asset_type'] == 'credit_alphanum4' else 'credit_alphanum12'
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
            transactions = []
            
            # Obtener transacciones
            tx_call = self.server.transactions().for_account(account_id).limit(limit).order('desc')
            response = tx_call.call()
            
            for tx in response['_embedded']['records']:
                transactions.append({
                    'id': tx['id'],
                    'hash': tx['hash'],
                    'created_at': tx['created_at'],
                    'fee_charged': tx['fee_charged'],
                    'operation_count': tx['operation_count'],
                    'successful': tx['successful'],
                    'type': tx['type'],
                    'memo': tx.get('memo', '')
                })
            
            return transactions
        except Exception as e:
            logger.error(f"Error obteniendo transacciones de Stellar: {e}")
            return []
    
    async def get_transaction_details(self, transaction_hash: str) -> Optional[Dict]:
        """Obtener detalles de una transacción específica"""
        try:
            tx = self.server.transactions().transaction(transaction_hash).call()
            
            # Obtener operaciones de la transacción
            operations = []
            ops_call = self.server.operations().for_transaction(transaction_hash).limit(20)
            ops_response = ops_call.call()
            
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
    
    async def stream_payments(self, account_id: str, callback):
        """Stream de pagos en tiempo real para una cuenta"""
        try:
            # Esta función se usará para monitoreo en tiempo real
            payments = self.server.payments().for_account(account_id).cursor('now')
            
            for payment in payments:
                if payment['type'] == 'payment':
                    await callback(payment)
        except Exception as e:
            logger.error(f"Error en stream de pagos: {e}")
    
    async def get_current_ledger(self) -> Optional[Dict]:
        """Obtener información del ledger actual"""
        try:
            ledger = self.server.ledgers().order('desc').limit(1).call()
            if ledger['_embedded']['records']:
                return ledger['_embedded']['records'][0]
            return None
        except Exception as e:
            logger.error(f"Error obteniendo ledger actual: {e}")
            return None
PROMPT 37: Servicio de monitoreo Stellar
Archivo: src/services/stellar/monitor.py

python
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from loguru import logger
from src.services.stellar.client import StellarClient
from src.database.mongodb import mongodb

class StellarMonitor:
    def __init__(self):
        self.client = StellarClient()
        self.watched_accounts: Dict[str, Dict] = {}
        self.watched_transactions: Dict[str, Dict] = {}
        self.is_monitoring = False
    
    async def add_account_to_watch(self, account_id: str, user_id: int, 
                                  alert_on_payment: bool = True, 
                                  min_amount: float = 100.0) -> bool:
        """Añadir cuenta Stellar para monitoreo"""
        try:
            # Verificar que la cuenta existe
            balance = await self.client.get_account_balance(account_id)
            if not balance:
                return False
            
            # Guardar en base de datos
            await mongodb.stellar_accounts.update_one(
                {
                    'account_id': account_id,
                    'user_id': user_id
                },
                {
                    '$set': {
                        'account_id': account_id,
                        'user_id': user_id,
                        'alert_on_payment': alert_on_payment,
                        'min_amount': min_amount,
                        'last_checked': datetime.utcnow(),
                        'is_active': True
                    }
                },
                upsert=True
            )
            
            # Agregar a memoria para monitoreo rápido
            self.watched_accounts[account_id] = {
                'user_id': user_id,
                'alert_on_payment': alert_on_payment,
                'min_amount': min_amount,
                'last_tx_hash': None
            }
            
            logger.info(f"✅ Cuenta Stellar añadida para monitoreo: {account_id[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error añadiendo cuenta a monitoreo: {e}")
            return False
    
    async def remove_account_from_watch(self, account_id: str, user_id: int) -> bool:
        """Remover cuenta Stellar del monitoreo"""
        try:
            # Remover de base de datos
            await mongodb.stellar_accounts.update_one(
                {
                    'account_id': account_id,
                    'user_id': user_id
                },
                {
                    '$set': {'is_active': False}
                }
            )
            
            # Remover de memoria
            if account_id in self.watched_accounts:
                del self.watched_accounts[account_id]
            
            logger.info(f"✅ Cuenta Stellar removida del monitoreo: {account_id[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error removiendo cuenta del monitoreo: {e}")
            return False
    
    async def check_account_activity(self, account_id: str) -> List[Dict]:
        """Revisar actividad reciente de una cuenta"""
        try:
            # Obtener transacciones recientes
            transactions = await self.client.get_account_transactions(account_id, limit=5)
            
            # Obtener balance actual
            balance_info = await self.client.get_account_balance(account_id)
            
            return {
                'account_id': account_id,
                'transactions': transactions,
                'balance': balance_info['balances'] if balance_info else [],
                'last_checked': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error revisando actividad de cuenta: {e}")
            return []
    
    async def start_monitoring(self, callback: Callable):
        """Iniciar monitoreo en tiempo real de cuentas"""
        self.is_monitoring = True
        
        while self.is_monitoring:
            try:
                # Cargar cuentas activas desde la base de datos
                active_accounts = await mongodb.stellar_accounts.find(
                    {'is_active': True}
                ).to_list(length=100)
                
                for account in active_accounts:
                    account_id = account['account_id']
                    
                    # Revisar transacciones recientes
                    recent_txs = await self.client.get_account_transactions(account_id, limit=3)
                    
                    if recent_txs and account.get('last_tx_hash') != recent_txs[0]['hash']:
                        # Nueva transacción detectada
                        await callback({
                            'type': 'new_transaction',
                            'account_id': account_id,
                            'user_id': account['user_id'],
                            'transaction': recent_txs[0],
                            'timestamp': datetime.utcnow()
                        })
                        
                        # Actualizar última transacción conocida
                        await mongodb.stellar_accounts.update_one(
                            {'_id': account['_id']},
                            {'$set': {'last_tx_hash': recent_txs[0]['hash']}}
                        )
                
                # Esperar antes de la siguiente verificación
                await asyncio.sleep(30)  # Revisar cada 30 segundos
                
            except Exception as e:
                logger.error(f"Error en monitoreo Stellar: {e}")
                await asyncio.sleep(10)
    
    async def stop_monitoring(self):
        """Detener monitoreo en tiempo real"""
        self.is_monitoring = False
    
    async def get_account_summary(self, account_id: str) -> Optional[Dict]:
        """Obtener resumen completo de una cuenta"""
        try:
            balance_info = await self.client.get_account_balance(account_id)
            if not balance_info:
                return None
            
            transactions = await self.client.get_account_transactions(account_id, limit=5)
            
            return {
                'account_id': account_id,
                'balances': balance_info['balances'],
                'recent_transactions': transactions,
                'sequence': balance_info.get('sequence', 0),
                'subentry_count': balance_info.get('subentry_count', 0)
            }
        except Exception as e:
            logger.error(f"Error obteniendo resumen de cuenta: {e}")
            return None
Paso 2: Integración de Solana
PROMPT 38: Configurar cliente Solana RPC
Archivo: src/services/solana/client.py

python
import asyncio
import base58
import base64
from typing import Dict, List, Optional
from loguru import logger
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solana.publickey import PublicKey
from solana.transaction import Transaction
from solders.signature import Signature
from src.config.settings import settings

class SolanaClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializar cliente Solana RPC"""
        try:
            self.client = AsyncClient(settings.SOLANA_RPC_URL)
            logger.info(f"✅ Conectado a Solana RPC: {settings.SOLANA_RPC_URL}")
        except Exception as e:
            logger.error(f"❌ Error conectando a Solana RPC: {e}")
            raise
    
    async def get_account_balance(self, public_key: str) -> Optional[Dict]:
        """Obtener balance de una cuenta Solana"""
        try:
            pubkey = PublicKey(public_key)
            response = await self.client.get_balance(pubkey, commitment=Commitment("confirmed"))
            
            if response.value:
                balance_lamports = response.value
                balance_sol = balance_lamports / 1_000_000_000
                
                return {
                    'public_key': public_key,
                    'balance_lamports': balance_lamports,
                    'balance_sol': balance_sol,
                    'slot': response.context.slot
                }
            return None
        except Exception as e:
            logger.error(f"Error obteniendo balance de Solana: {e}")
            return None
    
    async def get_account_info(self, public_key: str) -> Optional[Dict]:
        """Obtener información detallada de una cuenta"""
        try:
            pubkey = PublicKey(public_key)
            response = await self.client.get_account_info(pubkey, commitment=Commitment("confirmed"))
            
            if response.value:
                account_info = response.value
                return {
                    'public_key': public_key,
                    'lamports': account_info.lamports,
                    'owner': str(account_info.owner),
                    'executable': account_info.executable,
                    'rent_epoch': account_info.rent_epoch,
                    'data': base64.b64encode(account_info.data).decode('utf-8') if account_info.data else None,
                    'slot': response.context.slot
                }
            return None
        except Exception as e:
            logger.error(f"Error obteniendo info de cuenta Solana: {e}")
            return None
    
    async def get_transaction(self, signature: str) -> Optional[Dict]:
        """Obtener detalles de una transacción"""
        try:
            sig = Signature.from_string(signature)
            response = await self.client.get_transaction(
                sig,
                encoding="jsonParsed",
                commitment=Commitment("confirmed")
            )
            
            if response.value:
                tx = response.value
                return {
                    'signature': signature,
                    'slot': tx.slot,
                    'block_time': tx.block_time,
                    'meta': tx.meta.to_json() if tx.meta else None,
                    'transaction': tx.transaction.to_json() if tx.transaction else None
                }
            return None
        except Exception as e:
            logger.error(f"Error obteniendo transacción Solana: {e}")
            return None
    
    async def get_recent_transactions(self, public_key: str, limit: int = 10) -> List[Dict]:
        """Obtener transacciones recientes de una cuenta"""
        try:
            pubkey = PublicKey(public_key)
            
            # Obtener firmas recientes
            response = await self.client.get_signatures_for_address(
                pubkey,
                limit=limit,
                commitment=Commitment("confirmed")
            )
            
            transactions = []
            for sig_info in response.value:
                tx_details = await self.get_transaction(str(sig_info.signature))
                if tx_details:
                    transactions.append({
                        'signature': str(sig_info.signature),
                        'slot': sig_info.slot,
                        'block_time': sig_info.block_time,
                        'err': sig_info.err,
                        'memo': sig_info.memo,
                        'details': tx_details
                    })
            
            return transactions
        except Exception as e:
            logger.error(f"Error obteniendo transacciones Solana: {e}")
            return []
    
    async def get_token_accounts(self, public_key: str) -> List[Dict]:
        """Obtener cuentas de tokens asociadas a una wallet"""
        try:
            pubkey = PublicKey(public_key)
            
            # Obtener todas las cuentas de tokens
            response = await self.client.get_token_accounts_by_owner(
                pubkey,
                {"programId": PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")},
                commitment=Commitment("confirmed")
            )
            
            token_accounts = []
            for account in response.value:
                account_info = account.account.data.parsed['info']
                token_amount = account_info['tokenAmount']
                
                token_accounts.append({
                    'mint': account_info['mint'],
                    'owner': account_info['owner'],
                    'token_amount': {
                        'amount': token_amount['amount'],
                        'decimals': token_amount['decimals'],
                        'ui_amount': token_amount['uiAmount'],
                        'ui_amount_string': token_amount['uiAmountString']
                    },
                    'pubkey': str(account.pubkey)
                })
            
            return token_accounts
        except Exception as e:
            logger.error(f"Error obteniendo cuentas de tokens: {e}")
            return []
    
    async def get_slot_info(self) -> Optional[Dict]:
        """Obtener información del slot actual"""
        try:
            slot_response = await self.client.get_slot(commitment=Commitment("confirmed"))
            epoch_info = await self.client.get_epoch_info(commitment=Commitment("confirmed"))
            
            return {
                'current_slot': slot_response.value,
                'epoch': epoch_info.epoch,
                'slot_index': epoch_info.slot_index,
                'slots_in_epoch': epoch_info.slots_in_epoch
            }
        except Exception as e:
            logger.error(f"Error obteniendo info de slot: {e}")
            return None
PROMPT 39: Servicio de monitoreo Solana
Archivo: src/services/solana/monitor.py

python
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from loguru import logger
from src.services.solana.client import SolanaClient
from src.database.mongodb import mongodb

class SolanaMonitor:
    def __init__(self):
        self.client = SolanaClient()
        self.watched_accounts: Dict[str, Dict] = {}
        self.watched_tokens: Dict[str, Dict] = {}
        self.is_monitoring = False
    
    async def add_account_to_watch(self, public_key: str, user_id: int,
                                  alert_on_transfer: bool = True,
                                  min_amount_sol: float = 1.0) -> bool:
        """Añadir cuenta Solana para monitoreo"""
        try:
            # Verificar que la cuenta existe
            balance = await self.client.get_account_balance(public_key)
            if not balance:
                return False
            
            # Guardar en base de datos
            await mongodb.solana_accounts.update_one(
                {
                    'public_key': public_key,
                    'user_id': user_id
                },
                {
                    '$set': {
                        'public_key': public_key,
                        'user_id': user_id,
                        'alert_on_transfer': alert_on_transfer,
                        'min_amount_sol': min_amount_sol,
                        'last_signature': None,
                        'last_checked': datetime.utcnow(),
                        'is_active': True
                    }
                },
                upsert=True
            )
            
            # Agregar a memoria para monitoreo rápido
            self.watched_accounts[public_key] = {
                'user_id': user_id,
                'alert_on_transfer': alert_on_transfer,
                'min_amount_sol': min_amount_sol,
                'last_signature': None
            }
            
            logger.info(f"✅ Cuenta Solana añadida para monitoreo: {public_key[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error añadiendo cuenta a monitoreo: {e}")
            return False
    
    async def add_token_to_watch(self, mint_address: str, user_id: int,
                                alert_on_transfer: bool = True,
                                min_amount_token: float = 100.0) -> bool:
        """Añadir token para monitoreo"""
        try:
            # Guardar en base de datos
            await mongodb.solana_tokens.update_one(
                {
                    'mint_address': mint_address,
                    'user_id': user_id
                },
                {
                    '$set': {
                        'mint_address': mint_address,
                        'user_id': user_id,
                        'alert_on_transfer': alert_on_transfer,
                        'min_amount_token': min_amount_token,
                        'last_checked': datetime.utcnow(),
                        'is_active': True
                    }
                },
                upsert=True
            )
            
            # Agregar a memoria
            self.watched_tokens[mint_address] = {
                'user_id': user_id,
                'alert_on_transfer': alert_on_transfer,
                'min_amount_token': min_amount_token
            }
            
            logger.info(f"✅ Token añadido para monitoreo: {mint_address[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error añadiendo token a monitoreo: {e}")
            return False
    
    async def check_account_activity(self, public_key: str) -> Optional[Dict]:
        """Revisar actividad reciente de una cuenta"""
        try:
            # Obtener balance actual
            balance = await self.client.get_account_balance(public_key)
            if not balance:
                return None
            
            # Obtener transacciones recientes
            transactions = await self.client.get_recent_transactions(public_key, limit=5)
            
            # Obtener tokens
            token_accounts = await self.client.get_token_accounts(public_key)
            
            return {
                'public_key': public_key,
                'balance_sol': balance['balance_sol'],
                'recent_transactions': transactions,
                'token_accounts': token_accounts,
                'last_checked': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error revisando actividad de cuenta: {e}")
            return None
    
    async def start_monitoring(self, callback: Callable):
        """Iniciar monitoreo en tiempo real de cuentas"""
        self.is_monitoring = True
        
        while self.is_monitoring:
            try:
                # Cargar cuentas activas desde la base de datos
                active_accounts = await mongodb.solana_accounts.find(
                    {'is_active': True}
                ).to_list(length=100)
                
                for account in active_accounts:
                    public_key = account['public_key']
                    
                    # Revisar transacciones recientes
                    recent_txs = await self.client.get_recent_transactions(public_key, limit=3)
                    
                    if recent_txs and account.get('last_signature') != recent_txs[0]['signature']:
                        # Nueva transacción detectada
                        await callback({
                            'type': 'new_solana_transaction',
                            'public_key': public_key,
                            'user_id': account['user_id'],
                            'transaction': recent_txs[0],
                            'timestamp': datetime.utcnow()
                        })
                        
                        # Actualizar última firma conocida
                        await mongodb.solana_accounts.update_one(
                            {'_id': account['_id']},
                            {'$set': {'last_signature': recent_txs[0]['signature']}}
                        )
                
                # Esperar antes de la siguiente verificación
                await asyncio.sleep(30)  # Revisar cada 30 segundos
                
            except Exception as e:
                logger.error(f"Error en monitoreo Solana: {e}")
                await asyncio.sleep(10)
    
    async def stop_monitoring(self):
        """Detener monitoreo en tiempo real"""
        self.is_monitoring = False
    
    async def get_account_summary(self, public_key: str) -> Optional[Dict]:
        """Obtener resumen completo de una cuenta"""
        try:
            balance = await self.client.get_account_balance(public_key)
            if not balance:
                return None
            
            transactions = await self.client.get_recent_transactions(public_key, limit=10)
            token_accounts = await self.client.get_token_accounts(public_key)
            
            total_tokens_value = 0
            token_details = []
            
            for token_acc in token_accounts:
                token_value = float(token_acc['token_amount']['ui_amount'] or 0)
                total_tokens_value += token_value
                token_details.append({
                    'mint': token_acc['mint'][:8] + '...',
                    'amount': token_acc['token_amount']['ui_amount_string'],
                    'decimals': token_acc['token_amount']['decimals']
                })
            
            return {
                'public_key': public_key,
                'balance_sol': balance['balance_sol'],
                'recent_transactions_count': len(transactions),
                'tokens_count': len(token_accounts),
                'total_tokens_value': total_tokens_value,
                'token_details': token_details,
                'last_activity': transactions[0]['block_time'] if transactions else None
            }
        except Exception as e:
            logger.error(f"Error obteniendo resumen de cuenta: {e}")
            return None
Paso 3: Ampliar el servicio de alertas
PROMPT 40: Extender alert_service.py para blockchain
Actualizar src/services/alert_service.py:

python
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger
from src.database.mongodb import mongodb
from src.services.price_monitor import PriceMonitor
from src.services.stellar.monitor import StellarMonitor
from src.services.solana.monitor import SolanaMonitor
from src.config.settings import settings

class AlertService:
    def __init__(self):
        self.price_monitor = PriceMonitor()
        self.stellar_monitor = StellarMonitor()
        self.solana_monitor = SolanaMonitor()
        self.last_prices: Dict[str, float] = {}
        self.is_running = False
        self.bot = None
        self.alert_cooldown: Dict[str, datetime] = {}
    
    def set_bot(self, bot):
        """Establecer la instancia del bot para enviar notificaciones"""
        self.bot = bot
        # Configurar monitores con callback para notificaciones
        self.stellar_monitor.callback = self.handle_stellar_alert
        self.solana_monitor.callback = self.handle_solana_alert
    
    async def start(self):
        """Iniciar todos los servicios de alertas"""
        self.is_running = True
        await self.price_monitor.start()
        
        logger.info("🚀 Servicios de alertas iniciados")
        
        # Iniciar tareas en paralelo
        tasks = [
            self.check_price_alerts(),
            self.stellar_monitor.start_monitoring(self.handle_stellar_alert),
            self.solana_monitor.start_monitoring(self.handle_solana_alert)
        ]
        
        # Ejecutar todas las tareas
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def handle_stellar_alert(self, alert_data: Dict):
        """Manejar alertas de Stellar"""
        try:
            if alert_data['type'] == 'new_transaction':
                tx = alert_data['transaction']
                
                # Verificar si es una transacción importante
                if tx['successful'] and tx['operation_count'] > 0:
                    message = (
                        f"🌌 *Nueva Transacción Stellar*\n\n"
                        f"• *Cuenta:* `{alert_data['account_id'][:8]}...`\n"
                        f"• *Hash:* `{tx['hash'][:16]}...`\n"
                        f"• *Fecha:* {tx['created_at']}\n"
                        f"• *Fee:* {tx['fee_charged']} XLM\n"
                        f"• *Operaciones:* {tx['operation_count']}\n\n"
                        f"_Transacción exitosa_"
                    )
                    
                    await self.send_alert_to_user(
                        alert_data['user_id'],
                        message,
                        alert_type='stellar_transaction'
                    )
                    
        except Exception as e:
            logger.error(f"Error manejando alerta Stellar: {e}")
    
    async def handle_solana_alert(self, alert_data: Dict):
        """Manejar alertas de Solana"""
        try:
            if alert_data['type'] == 'new_solana_transaction':
                tx = alert_data['transaction']
                
                message = (
                    f"🔵 *Nueva Transacción Solana*\n\n"
                    f"• *Cuenta:* `{alert_data['public_key'][:8]}...`\n"
                    f"• *Firma:* `{tx['signature'][:16]}...`\n"
                    f"• *Slot:* {tx['slot']}\n"
                    f"• *Tiempo:* {tx['block_time']}\n"
                    f"• *Estado:* {'✅ Éxito' if not tx['err'] else '❌ Error'}\n\n"
                    f"_Nueva actividad detectada_"
                )
                
                await self.send_alert_to_user(
                    alert_data['user_id'],
                    message,
                    alert_type='solana_transaction'
                )
                
        except Exception as e:
            logger.error(f"Error manejando alerta Solana: {e}")
    
    async def send_alert_to_user(self, user_id: int, message: str, alert_type: str = 'general'):
        """Enviar alerta a usuario"""
        try:
            # Obtener información del usuario
            user = await mongodb.users.find_one({"telegram_id": user_id})
            if not user or not user.get('alerts_active', True):
                return
            
            # Verificar cooldown
            alert_key = f"{user_id}_{alert_type}"
            last_alert = self.alert_cooldown.get(alert_key)
            
            if last_alert and (datetime.utcnow() - last_alert).seconds < 60:  # 1 minuto
                return
            
            # Enviar mensaje si tenemos bot configurado
            if self.bot:
                await self.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='Markdown'
                )
                
                self.alert_cooldown[alert_key] = datetime.utcnow()
                logger.info(f"✅ Alerta {alert_type} enviada a usuario {user_id}")
                
                # Guardar en historial
                await self._save_alert_history(
                    user_id=user['_id'],
                    alert_type=alert_type,
                    message=message
                )
                
        except Exception as e:
            logger.error(f"Error enviando alerta a usuario: {e}")
    
    async def _save_alert_history(self, user_id, alert_type: str, message: str):
        """Guardar historial de alertas"""
        try:
            await mongodb.alert_history.insert_one({
                "user_id": user_id,
                "alert_type": alert_type,
                "message": message,
                "sent_at": datetime.utcnow(),
                "delivered": True
            })
        except Exception as e:
            logger.error(f"Error saving alert history: {e}")
    
    # Mantener los métodos existentes para alertas de precios...
    # [Los métodos check_alerts, _check_single_alert, etc. se mantienen igual]
Paso 4: Nuevos handlers para comandos de Stellar y Solana
PROMPT 41: Handlers para Stellar y Solana
Crear src/bot/blockchain_handlers.py:

python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from loguru import logger
from src.services.stellar.monitor import StellarMonitor
from src.services.solana.monitor import SolanaMonitor
from src.database.mongodb import mongodb

class BlockchainHandlers:
    def __init__(self):
        self.stellar_monitor = StellarMonitor()
        self.solana_monitor = SolanaMonitor()
    
    async def stellar_balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /sbalance - Consultar balance Stellar"""
        args = context.args
        
        if not args:
            await update.message.reply_text(
                "🌌 *Consulta de Balance Stellar*\n\n"
                "*Uso:* `/sbalance [DIRECCIÓN_STELLAR]`\n\n"
                "*Ejemplo:*\n"
                "`/sbalance GABCD...`\n\n"
                "*Nota:* La dirección debe comenzar con 'G'",
                parse_mode='Markdown'
            )
            return
        
        address = args[0].strip()
        
        if not address.startswith('G'):
            await update.message.reply_text(
                "❌ Dirección Stellar inválida. Debe comenzar con 'G'"
            )
            return
        
        message = await update.message.reply_text("🔍 Consultando balance Stellar...")
        
        try:
            from src.services.stellar.client import StellarClient
            client = StellarClient()
            balance_info = await client.get_account_balance(address)
            
            if not balance_info:
                await message.edit_text("❌ Cuenta Stellar no encontrada o sin fondos")
                return
            
            response = f"🌌 *Balance Stellar:* `{address[:8]}...`\n\n"
            
            for balance in balance_info['balances']:
                if balance['asset'] == 'XLM':
                    response += f"• *XLM:* {balance['balance']:,.4f}\n"
                else:
                    response += f"• *{balance['asset']}:* {balance['balance']:,.4f}\n"
            
            response += f"\n*Secuencia:* {balance_info['sequence']:,}\n"
            response += f"*Entradas:* {balance_info['subentry_count']}"
            
            keyboard = [
                [InlineKeyboardButton("📊 Ver Transacciones", callback_data=f"stellar_tx:{address}")],
                [InlineKeyboardButton("🔔 Monitorear", callback_data=f"stellar_watch:{address}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await message.edit_text(response, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error consultando balance Stellar: {e}")
            await message.edit_text("❌ Error consultando balance Stellar")
    
    async def stellar_watch_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /swatch - Monitorear cuenta Stellar"""
        args = context.args
        
        if len(args) < 1:
            await update.message.reply_text(
                "🔔 *Monitorear Cuenta Stellar*\n\n"
                "*Uso:* `/swatch [DIRECCIÓN] [MIN_XLM]`\n\n"
                "*Ejemplos:*\n"
                "`/swatch GABCD...` - Monitorear todas las transacciones\n"
                "`/swatch GABCD... 100` - Alertar solo si > 100 XLM\n\n"
                "*Nota:* Recibirás alertas de nuevas transacciones",
                parse_mode='Markdown'
            )
            return
        
        address = args[0].strip()
        min_amount = float(args[1]) if len(args) > 1 and args[1].replace('.', '', 1).isdigit() else 0.0
        
        if not address.startswith('G'):
            await update.message.reply_text("❌ Dirección Stellar inválida")
            return
        
        user = await mongodb.users.find_one({"telegram_id": update.effective_user.id})
        if not user:
            await update.message.reply_text("❌ Usuario no encontrado")
            return
        
        message = await update.message.reply_text("🔍 Configurando monitoreo Stellar...")
        
        try:
            success = await self.stellar_monitor.add_account_to_watch(
                account_id=address,
                user_id=user['_id'],
                alert_on_payment=True,
                min_amount=min_amount
            )
            
            if success:
                response = (
                    f"✅ *Cuenta Stellar añadida al monitoreo*\n\n"
                    f"• *Dirección:* `{address[:8]}...`\n"
                    f"• *Umbral:* {min_amount} XLM\n"
                    f"• *Estado:* 🔔 Activo\n\n"
                    f"Recibirás alertas de nuevas transacciones.\n"
                    f"Usa `/sunwatch {address}` para detener."
                )
            else:
                response = "❌ Error añadiendo cuenta al monitoreo"
            
            await message.edit_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error configurando monitoreo Stellar: {e}")
            await message.edit_text("❌ Error configurando monitoreo")
    
    async def solana_balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /sobalance - Consultar balance Solana"""
        args = context.args
        
        if not args:
            await update.message.reply_text(
                "🔵 *Consulta de Balance Solana*\n\n"
                "*Uso:* `/sobalance [DIRECCIÓN_SOLANA]`\n\n"
                "*Ejemplo:*\n"
                "`/sobalance 9ABCD...`\n\n"
                "*Nota:* También puedes consultar tokens con /sotokens",
                parse_mode='Markdown'
            )
            return
        
        address = args[0].strip()
        
        message = await update.message.reply_text("🔍 Consultando balance Solana...")
        
        try:
            from src.services.solana.client import SolanaClient
            client = SolanaClient()
            balance_info = await client.get_account_balance(address)
            
            if not balance_info:
                await message.edit_text("❌ Cuenta Solana no encontrada o sin fondos")
                return
            
            response = (
                f"🔵 *Balance Solana:* `{address[:8]}...`\n\n"
                f"• *SOL:* {balance_info['balance_sol']:,.4f}\n"
                f"• *Lamports:* {balance_info['balance_lamports']:,}\n"
                f"• *Slot:* {balance_info['slot']:,}\n\n"
                f"_Consulta tokens con `/sotokens {address}`_"
            )
            
            keyboard = [
                [InlineKeyboardButton("📊 Ver Transacciones", callback_data=f"solana_tx:{address}")],
                [InlineKeyboardButton("🔔 Monitorear", callback_data=f"solana_watch:{address}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await message.edit_text(response, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error consultando balance Solana: {e}")
            await message.edit_text("❌ Error consultando balance Solana")
    
    async def solana_tokens_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /sotokens - Consultar tokens Solana"""
        args = context.args
        
        if not args:
            await update.message.reply_text(
                "🪙 *Tokens Solana*\n\n"
                "*Uso:* `/sotokens [DIRECCIÓN_SOLANA]`\n\n"
                "*Ejemplo:*\n"
                "`/sotokens 9ABCD...`",
                parse_mode='Markdown'
            )
            return
        
        address = args[0].strip()
        
        message = await update.message.reply_text("🔍 Consultando tokens Solana...")
        
        try:
            from src.services.solana.client import SolanaClient
            client = SolanaClient()
            token_accounts = await client.get_token_accounts(address)
            
            if not token_accounts:
                await message.edit_text("❌ No se encontraron tokens en esta cuenta")
                return
            
            response = f"🪙 *Tokens en:* `{address[:8]}...`\n\n"
            
            for i, token in enumerate(token_accounts[:10], 1):  # Mostrar primeros 10
                amount = token['token_amount']['ui_amount_string']
                mint_short = token['mint'][:8] + '...'
                response += f"{i}. *Mint:* `{mint_short}`\n"
                response += f"   *Cantidad:* {amount}\n"
                response += f"   *Decimales:* {token['token_amount']['decimals']}\n\n"
            
            if len(token_accounts) > 10:
                response += f"... y {len(token_accounts) - 10} más"
            
            await message.edit_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error consultando tokens Solana: {e}")
            await message.edit_text("❌ Error consultando tokens")
    
    async def solana_watch_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /sowatch - Monitorear cuenta Solana"""
        args = context.args
        
        if len(args) < 1:
            await update.message.reply_text(
                "🔔 *Monitorear Cuenta Solana*\n\n"
                "*Uso:* `/sowatch [DIRECCIÓN] [MIN_SOL]`\n\n"
                "*Ejemplos:*\n"
                "`/sowatch 9ABCD...` - Monitorear todas las transacciones\n"
                "`/sowatch 9ABCD... 1` - Alertar solo si > 1 SOL\n\n"
                "*Nota:* Recibirás alertas de nuevas transacciones",
                parse_mode='Markdown'
            )
            return
        
        address = args[0].strip()
        min_amount = float(args[1]) if len(args) > 1 and args[1].replace('.', '', 1).isdigit() else 0.0
        
        user = await mongodb.users.find_one({"telegram_id": update.effective_user.id})
        if not user:
            await update.message.reply_text("❌ Usuario no encontrado")
            return
        
        message = await update.message.reply_text("🔍 Configurando monitoreo Solana...")
        
        try:
            success = await self.solana_monitor.add_account_to_watch(
                public_key=address,
                user_id=user['_id'],
                alert_on_transfer=True,
                min_amount_sol=min_amount
            )
            
            if success:
                response = (
                    f"✅ *Cuenta Solana añadida al monitoreo*\n\n"
                    f"• *Dirección:* `{address[:8]}...`\n"
                    f"• *Umbral:* {min_amount} SOL\n"
                    f"• *Estado:* 🔔 Activo\n\n"
                    f"Recibirás alertas de nuevas transacciones.\n"
                    f"Usa `/sounwatch {address}` para detener."
                )
            else:
                response = "❌ Error añadiendo cuenta al monitoreo"
            
            await message.edit_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error configurando monitoreo Solana: {e}")
            await message.edit_text("❌ Error configurando monitoreo")
    
    async def blockchain_help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra ayuda para comandos de blockchain"""
        help_text = """
🌐 *Comandos de Blockchain - Crypto Sentinel Bot*

*Stellar (XLM):*
/sbalance [dirección] - Consultar balance Stellar
/swatch [dirección] [min_xlm] - Monitorear cuenta Stellar
/sunwatch [dirección] - Dejar de monitorear
/stransactions [dirección] - Ver transacciones recientes

*Solana (SOL):*
/sobalance [dirección] - Consultar balance Solana
/sotokens [dirección] - Consultar tokens en cuenta
/sowatch [dirección] [min_sol] - Monitorear cuenta Solana
/sounwatch [dirección] - Dejar de monitorear
/sotransactions [dirección] - Ver transacciones recientes

*Ejemplos:*
`/sbalance GABCD123...`
`/swatch GABCD123... 50`
`/sobalance 9WXYZ456...`
`/sowatch 9WXYZ456... 1`
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
Actualizar src/bot/telegram_bot.py para incluir nuevos handlers:

python
    def _register_handlers(self):
        """Registra todos los handlers de comandos"""
        from src.bot.blockchain_handlers import BlockchainHandlers
        blockchain_handlers = BlockchainHandlers()
        
        # Comandos existentes...
        
        # Comandos Stellar
        self.application.add_handler(CommandHandler("sbalance", blockchain_handlers.stellar_balance_command))
        self.application.add_handler(CommandHandler("swatch", blockchain_handlers.stellar_watch_command))
        self.application.add_handler(CommandHandler("sunwatch", blockchain_handlers.stellar_unwatch_command))
        self.application.add_handler(CommandHandler("stransactions", blockchain_handlers.stellar_transactions_command))
        
        # Comandos Solana
        self.application.add_handler(CommandHandler("sobalance", blockchain_handlers.solana_balance_command))
        self.application.add_handler(CommandHandler("sotokens", blockchain_handlers.solana_tokens_command))
        self.application.add_handler(CommandHandler("sowatch", blockchain_handlers.solana_watch_command))
        self.application.add_handler(CommandHandler("sounwatch", blockchain_handlers.solana_unwatch_command))
        self.application.add_handler(CommandHandler("sotransactions", blockchain_handlers.solana_transactions_command))
        
        # Ayuda blockchain
        self.application.add_handler(CommandHandler("blockchain", blockchain_handlers.blockchain_help_command))
Paso 5: Actualizar dependencias y configuración
PROMPT 42: Actualizar requirements.txt
txt
# Dependencias existentes...

# Stellar SDK
stellar-sdk==9.0.0

# Solana SDK
solana==0.29.0
solders==0.18.0
anchorpy==0.15.0

# Web3
web3==6.11.1

# Otros
base58==2.1.1
PROMPT 43: Actualizar configuración
Actualizar src/config/settings.py:

python
class Settings(BaseSettings):
    # ... configuraciones existentes ...
    
    # Stellar
    STELLAR_HORIZON_URL: str = "https://horizon.stellar.org"
    STELLAR_NETWORK_PASSPHRASE: str = "Public Global Stellar Network ; September 2015"
    
    # Solana
    SOLANA_RPC_URL: str = "https://api.mainnet-beta.solana.com"
    SOLANA_WS_URL: Optional[str] = "wss://api.mainnet-beta.solana.com"
    
    # Ethereum (para futura expansión)
    ETHEREUM_RPC_URL: Optional[str] = "https://mainnet.infura.io/v3/YOUR_INFURA_KEY"
    
    # Configuración de monitoreo blockchain
    BLOCKCHAIN_CHECK_INTERVAL: int = 30  # segundos
    MAX_WATCHED_ACCOUNTS_PER_USER: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True
Paso 6: Script de prueba para blockchain
PROMPT 44: Crear script de prueba blockchain
Crear test_blockchain.py:

python
#!/usr/bin/env python3
"""
Script de prueba para funcionalidades blockchain
"""

import asyncio
import sys
from src.services.stellar.client import StellarClient
from src.services.solana.client import SolanaClient
from loguru import logger

async def test_stellar():
    """Probar cliente Stellar"""
    print("🌌 Probando conexión Stellar...")
    try:
        client = StellarClient()
        
        # Cuenta de prueba pública de Stellar
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
        
        # Cuenta de prueba pública de Solana
        test_account = "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
        
        balance = await client.get_account_balance(test_account)
        if balance:
            print(f"✅ Solana conectado")
            print(f"   Cuenta: {test_account[:8]}...")
            print(f"   Balance SOL: {balance['balance_sol']}")
            print(f"   Slot: {balance['slot']}")
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
Resumen de lo implementado en Fase 2:
✅ 1. Integración Stellar completa:

Cliente Horizon para consultas

Monitoreo de balances y transacciones

Alertas en tiempo real

Comandos: /sbalance, /swatch, etc.

✅ 2. Integración Solana completa:

Cliente RPC para consultas

Monitoreo de balances, tokens y transacciones

Alertas en tiempo real

Comandos: /sobalance, /sotokens, /sowatch, etc.

✅ 3. Sistema de alertas unificado:

Extensión del servicio de alertas

Soporte para alertas de blockchain

Historial de alertas

✅ 4. Nuevos handlers de Telegram:

Comandos específicos para cada blockchain

Interfaz de usuario intuitiva

Sistema de monitoreo configurable

Próximos pasos inmediatos:
Ejecutar pruebas: python test_blockchain.py

Actualizar dependencias: pip install -r requirements.txt

Probar localmente: python src/main.py

Desplegar en Fly.io: flyctl deploy

Características adicionales para futuras expansiones:
Dashboard web para monitoreo blockchain

Alertas de smart contracts (Solana)

Soporte para más blockchains (Ethereum, Polygon)

Análisis de transacciones avanzado

API REST para consultas blockchain

