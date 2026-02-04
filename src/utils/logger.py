import sys
import json
from loguru import logger
from datetime import datetime
from typing import Dict, Any

class JSONFormatter:
    def __init__(self):
        self.pid = None
    
    def format(self, record: Dict[str, Any]) -> str:
        """Formatear log como JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record["level"].name,
            "message": record["message"],
            "module": record["name"],
            "function": record["function"],
            "line": record["line"],
            "process": record["process"].id,
            "thread": record["thread"].id,
        }
        
        # Agregar excepciones si existen
        if record["exception"]:
            log_entry["exception"] = {
                "type": record["exception"].type.__name__,
                "value": str(record["exception"].value),
                "traceback": record["exception"].traceback.format()
            }
        
        return json.dumps(log_entry) + "\n"

def setup_logging(level: str = "INFO", json_format: bool = False):
    """Configurar logging con Loguru"""
    
    # Remover handler por defecto
    logger.remove()
    
    if json_format:
        # Formato JSON para producción usando serialize=True de Loguru
        logger.add(
            sys.stdout,
            serialize=True,
            level=level
        )
    else:
        # Formato legible para desarrollo
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=level
        )
    
    # Archivo de log para errores
    logger.add(
        "logs/error_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="00:00",
        retention="30 days"
    )
    
    # Archivo de log para debug (solo en desarrollo)
    if level == "DEBUG":
        logger.add(
            "logs/debug_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="00:00",
            retention="7 days"
        )
    
    return logger

# Logger global (por defecto configuración básica)
log = setup_logging()
