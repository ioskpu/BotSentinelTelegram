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
            self.notifications = self.db.notifications
            
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