from pydantic_settings import BaseSettings, SettingsConfigDict
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
    SOLANA_WS_URL: Optional[str] = "wss://api.mainnet-beta.solana.com"
    STELLAR_HORIZON_URL: str = "https://horizon.stellar.org"
    STELLAR_NETWORK_PASSPHRASE: str = "Public Global Stellar Network ; September 2015"
    ETHEREUM_RPC_URL: Optional[str] = None
    
    # Configuración de monitoreo blockchain
    BLOCKCHAIN_CHECK_INTERVAL: int = 60  # segundos
    MAX_WATCHED_ACCOUNTS_PER_USER: int = 10
    
    # Configuración de alertas
    ALERT_CHECK_INTERVAL: int = 60  # segundos
    PRICE_CHECK_INTERVAL: int = 300  # segundos
    
    # Redis (para cache y workers)
    REDIS_URL: Optional[str] = "redis://localhost:6379"
    
    # Modo debug e entorno
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

settings = Settings()