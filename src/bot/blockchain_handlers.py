from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from src.services.stellar.client import StellarClient
from src.services.solana.client import SolanaClient
from src.database.mongodb import mongodb
from datetime import datetime

class BlockchainHandlers:
    def __init__(self, alert_service=None):
        self.stellar_client = StellarClient()
        self.solana_client = SolanaClient()
        self.alert_service = alert_service

    async def stellar_balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /sbalance - Consultar balance Stellar"""
        args = context.args
        if not args:
            await update.message.reply_text(
                "🌌 *Consulta de Balance Stellar*\n\n"
                "*Uso:* `/sbalance [DIRECCIÓN_STELLAR]`\n\n"
                "*Ejemplo:*\n"
                "`/sbalance GABCD...`",
                parse_mode='Markdown'
            )
            return
        
        address = args[0].strip()
        message = await update.message.reply_text("🔍 Consultando balance Stellar...")
        
        try:
            balance_info = await self.stellar_client.get_account_balance(address)
            if not balance_info:
                await message.edit_text("❌ Cuenta Stellar no encontrada o sin fondos")
                return
            
            response = f"🌌 *Balance Stellar:* `{address[:8]}...`\n\n"
            for bal in balance_info['balances']:
                asset = bal['asset']
                response += f"• *{asset}:* {bal['balance']:,.4f}\n"
            
            keyboard = [
                [InlineKeyboardButton("📜 Ver Transacciones", callback_data=f"stellar_tx:{address}")],
                [InlineKeyboardButton("🔔 Monitorear", callback_data=f"stellar_watch:{address}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await message.edit_text(response, parse_mode='Markdown', reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error consultando balance Stellar: {e}")
            await message.edit_text("❌ Error consultando balance Stellar")

    async def solana_balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /sobalance - Consultar balance Solana"""
        args = context.args
        if not args:
            await update.message.reply_text(
                "🔵 *Consulta de Balance Solana*\n\n"
                "*Uso:* `/sobalance [DIRECCIÓN_SOLANA]`\n\n"
                "*Ejemplo:*\n"
                "`/sobalance 9ABCD...`",
                parse_mode='Markdown'
            )
            return
        
        address = args[0].strip()
        message = await update.message.reply_text("🔍 Consultando balance Solana...")
        
        try:
            balance_info = await self.solana_client.get_account_balance(address)
            if not balance_info:
                await message.edit_text("❌ Cuenta Solana no encontrada o sin fondos")
                return
            
            response = (
                f"🔵 *Balance Solana:* `{address[:8]}...`\n\n"
                f"• *SOL:* {balance_info['balance_sol']:,.4f}\n"
                f"• *Lamports:* {balance_info['balance_lamports']:,}\n\n"
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
            token_accounts = await self.solana_client.get_token_accounts(address)
            if not token_accounts:
                await message.edit_text("❌ No se encontraron tokens en esta cuenta")
                return
            
            response = f"🪙 *Tokens en:* `{address[:8]}...`\n\n"
            for i, token in enumerate(token_accounts[:10], 1):
                amount = token['token_amount'].get('uiAmountString', '0')
                mint_short = token['mint'][:8] + '...' if token['mint'] != "Desconocido (requiere parsing de data)" else "???"
                response += f"{i}. *Mint:* `{mint_short}`\n"
                response += f"   *Cantidad:* {amount}\n\n"
            
            if len(token_accounts) > 10:
                response += f"... y {len(token_accounts) - 10} más"
            
            await message.edit_text(response, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error consultando tokens Solana: {e}")
            await message.edit_text("❌ Error consultando tokens")

    async def stellar_watch_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /swatch - Monitorear cuenta Stellar"""
        args = context.args
        if not args:
            await update.message.reply_text("📝 Uso: `/swatch [DIRECCIÓN]`", parse_mode='Markdown')
            return
        
        address = args[0].strip()
        chat_id = update.effective_chat.id
        
        try:
            await mongodb.watched_accounts.update_one(
                {"address": address, "network": "STELLAR"},
                {
                    "$set": {
                        "address": address,
                        "network": "STELLAR",
                        "chat_id": chat_id,
                        "added_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            if self.alert_service:
                await self.alert_service.stellar_monitor.add_account(address, chat_id)
                await update.message.reply_text(f"✅ Monitoreando cuenta Stellar: `{address[:8]}...`", parse_mode='Markdown')
            else:
                await update.message.reply_text("✅ Cuenta guardada. El monitoreo se activará pronto.")
        except Exception as e:
            logger.error(f"Error en swatch: {e}")
            await update.message.reply_text("❌ Error configurando monitoreo")

    async def solana_watch_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /sowatch - Monitorear cuenta Solana"""
        args = context.args
        if not args:
            await update.message.reply_text("📝 Uso: `/sowatch [DIRECCIÓN]`", parse_mode='Markdown')
            return
        
        address = args[0].strip()
        chat_id = update.effective_chat.id
        
        try:
            await mongodb.watched_accounts.update_one(
                {"address": address, "network": "SOLANA"},
                {
                    "$set": {
                        "address": address,
                        "network": "SOLANA",
                        "chat_id": chat_id,
                        "added_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            if self.alert_service:
                await self.alert_service.solana_monitor.add_account(address, chat_id)
                await update.message.reply_text(f"✅ Monitoreando cuenta Solana: `{address[:8]}...`", parse_mode='Markdown')
            else:
                await update.message.reply_text("✅ Cuenta guardada. El monitoreo se activará pronto.")
        except Exception as e:
            logger.error(f"Error en sowatch: {e}")
            await update.message.reply_text("❌ Error configurando monitoreo")

    async def stellar_unwatch_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /sunwatch - Detener monitoreo Stellar"""
        args = context.args
        if not args:
            await update.message.reply_text("📝 Uso: `/sunwatch [DIRECCIÓN]`", parse_mode='Markdown')
            return
        
        address = args[0].strip()
        try:
            result = await mongodb.watched_accounts.delete_one({"address": address, "network": "STELLAR"})
            if result.deleted_count > 0:
                if self.alert_service:
                    await self.alert_service.stellar_monitor.remove_account(address)
                await update.message.reply_text(f"🛑 Monitoreo detenido para: `{address[:8]}...`", parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Esa cuenta no está siendo monitoreada.")
        except Exception as e:
            logger.error(f"Error en sunwatch: {e}")
            await update.message.reply_text("❌ Error al detener monitoreo")

    async def solana_unwatch_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /sounwatch - Detener monitoreo Solana"""
        args = context.args
        if not args:
            await update.message.reply_text("📝 Uso: `/sounwatch [DIRECCIÓN]`", parse_mode='Markdown')
            return
        
        address = args[0].strip()
        try:
            result = await mongodb.watched_accounts.delete_one({"address": address, "network": "SOLANA"})
            if result.deleted_count > 0:
                if self.alert_service:
                    await self.alert_service.solana_monitor.remove_account(address)
                await update.message.reply_text(f"🛑 Monitoreo detenido para: `{address[:8]}...`", parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Esa cuenta no está siendo monitoreada.")
        except Exception as e:
            logger.error(f"Error en sounwatch: {e}")
            await update.message.reply_text("❌ Error al detener monitoreo")

    async def blockchain_help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra ayuda para comandos de blockchain"""
        help_text = """
🌐 *Comandos de Blockchain*

*Stellar (XLM):*
/sbalance [dirección] - Consultar balance
/swatch [dirección] - Monitorear cuenta
/sunwatch [dirección] - Detener monitoreo
/stransactions [dirección] - Ver transacciones

*Solana (SOL):*
/sobalance [dirección] - Consultar balance
/sotokens [dirección] - Consultar tokens
/sowatch [dirección] - Monitorear cuenta
/sounwatch [dirección] - Detener monitoreo
/sotransactions [dirección] - Ver transacciones

*Ejemplos:*
`/sbalance GABCD...`
`/sobalance 9ABCD...`
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def stellar_transactions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /stransactions"""
        args = context.args
        if not args:
            await update.message.reply_text("📝 Uso: `/stransactions [DIRECCIÓN]`")
            return
        address = args[0].strip()
        try:
            txs = await self.stellar_client.get_account_transactions(address, limit=5)
            if txs:
                msg = f"📜 *Últimas transacciones XLM*\n`{address[:10]}...`\n\n"
                for tx in txs:
                    status = "✅" if tx['successful'] else "❌"
                    msg += f"{status} `{tx['hash'][:8]}...`\n"
                    msg += f"📅 {tx['created_at']}\n\n"
                await update.message.reply_text(msg, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ No se encontraron transacciones.")
        except Exception as e:
            logger.error(f"Error: {e}")
            await update.message.reply_text("❌ Error al consultar transacciones.")

    async def solana_transactions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /sotransactions"""
        args = context.args
        if not args:
            await update.message.reply_text("📝 Uso: `/sotransactions [DIRECCIÓN]`")
            return
        address = args[0].strip()
        try:
            txs = await self.solana_client.get_recent_transactions(address, limit=5)
            if txs:
                msg = f"📜 *Últimas transacciones SOL*\n`{address[:10]}...`\n\n"
                for tx in txs:
                    status = "❌" if tx['err'] else "✅"
                    msg += f"{status} `{tx['signature'][:8]}...`\n"
                await update.message.reply_text(msg, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ No se encontraron transacciones.")
        except Exception as e:
            logger.error(f"Error: {e}")
            await update.message.reply_text("❌ Error al consultar transacciones.")
