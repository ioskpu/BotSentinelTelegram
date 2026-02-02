import asyncio
import base64
from typing import Dict, List, Optional
from loguru import logger
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solders.pubkey import Pubkey
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
            pubkey = Pubkey.from_string(public_key)
            response = await self.client.get_balance(pubkey, commitment=Commitment("confirmed"))
            
            if response.value is not None:
                balance_lamports = response.value
                balance_sol = balance_lamports / 1_000_000_000
                
                return {
                    'public_key': public_key,
                    'balance_lamports': balance_lamports,
                    'balance_sol': balance_sol
                }
            return None
        except Exception as e:
            logger.error(f"Error obteniendo balance de Solana: {e}")
            return None
    
    async def get_account_info(self, public_key: str) -> Optional[Dict]:
        """Obtener información detallada de una cuenta"""
        try:
            pubkey = Pubkey.from_string(public_key)
            response = await self.client.get_account_info(pubkey, commitment=Commitment("confirmed"))
            
            if response.value:
                account_info = response.value
                return {
                    'public_key': public_key,
                    'lamports': account_info.lamports,
                    'owner': str(account_info.owner),
                    'executable': account_info.executable,
                    'rent_epoch': account_info.rent_epoch
                }
            return None
        except Exception as e:
            logger.error(f"Error obteniendo info de cuenta Solana: {e}")
            return None
    
    async def get_recent_transactions(self, public_key: str, limit: int = 5) -> List[Dict]:
        """Obtener transacciones recientes de una cuenta"""
        try:
            pubkey = Pubkey.from_string(public_key)
            
            response = await self.client.get_signatures_for_address(
                pubkey,
                limit=limit,
                commitment=Commitment("confirmed")
            )
            
            transactions = []
            if response.value:
                for sig_info in response.value:
                    transactions.append({
                        'signature': str(sig_info.signature),
                        'slot': sig_info.slot,
                        'block_time': sig_info.block_time,
                        'err': sig_info.err,
                        'memo': sig_info.memo
                    })
            
            return transactions
        except Exception as e:
            logger.error(f"Error obteniendo transacciones Solana: {e}")
            return []

    async def get_token_accounts(self, public_key: str) -> List[Dict]:
        """Obtener cuentas de tokens (SPL) de una dirección"""
        try:
            from solders.pubkey import Pubkey
            from solana.rpc.types import TokenAccountOpts
            
            pubkey = Pubkey.from_string(public_key)
            # Usar el ID del programa Token de Solana
            TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
            
            opts = TokenAccountOpts(program_id=TOKEN_PROGRAM_ID)
            response = await self.client.get_token_accounts_by_owner(pubkey, opts)
            
            tokens = []
            if response.value:
                for account in response.value:
                    # El mint está en los primeros 32 bytes de los datos de la cuenta
                    # data = account.account.data
                    # Pero es más fácil pedir el balance y ver si viene con más info
                    
                    token_info = {
                        'pubkey': str(account.pubkey),
                        'mint': "Cargando...",
                        'token_amount': {
                            'uiAmountString': "0",
                            'decimals': 0
                        }
                    }
                    
                    # Obtener balance y mint del account info
                    balance_resp = await self.client.get_token_account_balance(account.pubkey)
                    if balance_resp.value:
                        token_info['token_amount'] = balance_resp.value.to_json()
                    
                    # Intentar obtener el mint de los datos de la cuenta (32 bytes iniciales)
                    try:
                        data = account.account.data
                        if isinstance(data, bytes):
                            mint_pubkey = Pubkey.from_bytes(data[:32])
                            token_info['mint'] = str(mint_pubkey)
                    except:
                        pass
                        
                    tokens.append(token_info)
                        
            return tokens
        except Exception as e:
            logger.error(f"Error obteniendo tokens Solana: {e}")
            return []
