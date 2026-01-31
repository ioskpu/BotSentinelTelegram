from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "crypto_sentinel"
    
    # APIs
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3"
    SOLANA_RPC_URL: Optional[str] = "https://api.mainnet-beta.solana.com"
    STELLAR_HORIZON_URL: str = "https://horizon.stellar.org"
    
    # Configuración de alertas
    ALERT_CHECK_INTERVAL: int = 60  # segundos
    PRICE_CHECK_INTERVAL: int = 300  # segundos
    
    # Redis (para cache y workers)
    REDIS_URL: Optional[str] = "redis://localhost:6379"
    
    # Modo debug
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()