from fastapi import APIRouter
from fastapi.responses import JSONResponse
from src.database.mongodb import mongodb
import httpx
from loguru import logger
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """Endpoint de health check para Fly.io"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    try:
        # Verificar MongoDB
        mongo_ok = await mongodb.ping()
        health_status["services"]["mongodb"] = "healthy" if mongo_ok else "unhealthy"
        
        # Verificar CoinGecko API
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get("https://api.coingecko.com/api/v3/ping")
                health_status["services"]["coingecko"] = "healthy" if response.status_code == 200 else "unhealthy"
            except Exception:
                health_status["services"]["coingecko"] = "unreachable"
        
        # Determinar estado general
        all_healthy = all(status == "healthy" for status in health_status["services"].values())
        health_status["status"] = "healthy" if all_healthy else "degraded"
        
        status_code = 200 if all_healthy else 503
        
        return JSONResponse(content=health_status, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=503
        )

@router.get("/status")
async def status():
    """Endpoint de estado extendido"""
    try:
        # Obtener estadísticas
        total_users = await mongodb.users.count_documents({})
        total_alerts = await mongodb.alerts.count_documents({})
        active_alerts = await mongodb.alerts.count_documents({"is_active": True})
        
        return {
            "status": "operational",
            "users": total_users,
            "alerts": {
                "total": total_alerts,
                "active": active_alerts
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Status error: {e}")
        return {"status": "error", "message": str(e)}
