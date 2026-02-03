from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from src.api import health
from src.api.routes import (
    auth_router,
    alerts_router,
    prices_router,
    portfolio_router,
    dashboard_router,
    users_router,
    metrics_router,
)
from src.api.websocket import websocket_endpoint, manager
from loguru import logger


def create_app():
    """Create FastAPI application"""
    app = FastAPI(
        title="Crypto Sentinel Bot API",
        description="API for Crypto Sentinel Telegram Bot",
        version="1.0.0"
    )
    
    # CORS middleware - configured for development and production
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    # Add production URLs from environment if available
    import os
    if os.getenv("DASHBOARD_URL"):
        allowed_origins.append(os.getenv("DASHBOARD_URL"))
    if os.getenv("CORS_ORIGINS"):
        allowed_origins.extend(os.getenv("CORS_ORIGINS", "").split(","))
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    )
    
    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
    app.include_router(alerts_router, prefix="/api/v1", tags=["alerts"])
    app.include_router(prices_router, prefix="/api/v1", tags=["prices"])
    app.include_router(portfolio_router, prefix="/api/v1", tags=["portfolio"])
    app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])
    app.include_router(users_router, prefix="/api/v1", tags=["users"])
    app.include_router(metrics_router, prefix="/api/v1", tags=["metrics"])
    
    # WebSocket endpoint
    @app.websocket("/ws")
    async def websocket_route(websocket: WebSocket):
        await websocket_endpoint(websocket)
    
    # WebSocket status endpoint
    @app.get("/api/v1/ws/status")
    async def websocket_status():
        return {
            "active_connections": manager.get_connection_count(),
            "authenticated_users": len(manager.active_connections),
        }
    
    # Fly.io health check redirect
    @app.get("/health")
    async def health_check_fly():
        return await health.health_check()
    
    @app.get("/")
    async def root():
        return {
            "message": "Crypto Sentinel Bot API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/api/v1/health",
            "websocket": "/ws",
        }
    
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting API server...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
