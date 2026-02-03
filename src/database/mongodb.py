import motor.motor_asyncio
from src.config.settings import settings
from loguru import logger

class MongoDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa la conexión a MongoDB"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
            self.db = self.client[settings.MONGODB_DB_NAME]
            
            # Colecciones
            self.users = self.db.users
            self.alerts = self.db.alerts
            self.price_history = self.db.price_history
            self.portfolio = self.db.portfolio
            self.portfolio_history = self.db.portfolio_history
            self.transactions = self.db.transactions
            self.notifications = self.db.notifications
            self.watched_accounts = self.db.watched_accounts
            self.cache = self.db.cache
            self.coins = self.db.coins
            
            # Web dashboard collections
            self.web_users = self.db.web_users
            self.sessions = self.db.sessions
            self.activity_logs = self.db.activity_logs
            
            logger.info("✅ MongoDB conectado exitosamente")
        except Exception as e:
            logger.error(f"❌ Error conectando a MongoDB: {e}")
            raise
    
    async def ping(self):
        """Verifica la conexión a MongoDB"""
        try:
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"MongoDB ping failed: {e}")
            return False

# Instancia global
mongodb = MongoDB()