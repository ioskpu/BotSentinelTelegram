from datetime import datetime
from typing import List, Dict, Optional
from src.database.mongodb import mongodb
from src.database.models import PortfolioEntry, PyObjectId
from loguru import logger

class PortfolioService:
    def __init__(self):
        self._db = mongodb
    
    @property
    def portfolio_collection(self):
        """Acceso lazy a la colección de portafolio"""
        return self._db.portfolio
    
    async def add_entry(self, user_id: PyObjectId, coin_symbol: str, amount: float, 
                       buy_price: Optional[float] = None) -> PortfolioEntry:
        """Añade una entrada al portafolio"""
        entry = PortfolioEntry(
            user_id=user_id,
            coin_symbol=coin_symbol.upper(),
            amount=amount,
            buy_price=buy_price,
            buy_date=datetime.utcnow() if buy_price else None
        )
        
        result = await self.portfolio_collection.insert_one(entry.dict(by_alias=True))
        entry.id = result.inserted_id
        return entry
    
    async def get_user_portfolio(self, user_id: PyObjectId) -> List[PortfolioEntry]:
        """Obtiene el portafolio completo de un usuario"""
        entries = await self.portfolio_collection.find(
            {"user_id": user_id}
        ).to_list(length=100)
        
        return [PortfolioEntry(**entry) for entry in entries]
    
    async def remove_entry(self, entry_id: str) -> bool:
        """Elimina una entrada del portafolio"""
        try:
            from bson import ObjectId
            result = await self.portfolio_collection.delete_one({"_id": ObjectId(entry_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error removing portfolio entry: {e}")
            return False
    
    async def calculate_portfolio_value(self, user_id: PyObjectId, price_monitor) -> Dict:
        """Calcula el valor actual del portafolio"""
        entries = await self.get_user_portfolio(user_id)
        
        if not entries:
            return {"total_value": 0, "total_cost": 0, "total_profit": 0, "entries": []}
        
        # Agrupar por moneda
        portfolio_summary = {}
        for entry in entries:
            symbol = entry.coin_symbol
            if symbol not in portfolio_summary:
                portfolio_summary[symbol] = {
                    "total_amount": 0,
                    "total_cost": 0
                }
            
            portfolio_summary[symbol]["total_amount"] += entry.amount
            if entry.buy_price:
                portfolio_summary[symbol]["total_cost"] += entry.amount * entry.buy_price
        
        # Calcular valores actuales
        total_current_value = 0
        total_cost = 0
        detailed_entries = []
        
        for symbol, data in portfolio_summary.items():
            current_price = await price_monitor.get_price_by_symbol(symbol)
            if current_price:
                current_value = data["total_amount"] * current_price
                total_current_value += current_value
                
                if data["total_cost"] > 0:
                    avg_buy_price = data["total_cost"] / data["total_amount"]
                    total_cost += data["total_cost"]
                    profit_loss = current_value - data["total_cost"]
                    profit_loss_percent = (profit_loss / data["total_cost"]) * 100
                else:
                    avg_buy_price = None
                    profit_loss = None
                    profit_loss_percent = None
                
                detailed_entries.append({
                    "symbol": symbol,
                    "amount": data["total_amount"],
                    "avg_buy_price": avg_buy_price,
                    "current_price": current_price,
                    "current_value": current_value,
                    "profit_loss": profit_loss,
                    "profit_loss_percent": profit_loss_percent
                })
        
        # Ordenar por valor descendente
        detailed_entries.sort(key=lambda x: x["current_value"], reverse=True)
        
        return {
            "total_value": total_current_value,
            "total_cost": total_cost,
            "total_profit": total_current_value - total_cost if total_cost else 0,
            "entries": detailed_entries
        }
