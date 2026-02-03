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
        "https://arterial-authigenic-aleshia.ngrok-free.dev",
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
    
    # Dashboard API integration (v1/dashboard/*)
    dashboard_api_prefix = "/api/v1/dashboard"
    app.include_router(auth_router, prefix=dashboard_api_prefix, tags=["dashboard-auth"])
    app.include_router(alerts_router, prefix=dashboard_api_prefix, tags=["dashboard-alerts"])
    app.include_router(prices_router, prefix=dashboard_api_prefix, tags=["dashboard-prices"])
    app.include_router(portfolio_router, prefix=dashboard_api_prefix, tags=["dashboard-portfolio"])
    app.include_router(dashboard_router, prefix=dashboard_api_prefix, tags=["dashboard-main"])
    app.include_router(users_router, prefix=dashboard_api_prefix, tags=["dashboard-users"])
    app.include_router(metrics_router, prefix=dashboard_api_prefix, tags=["dashboard-metrics"])
    
    # Static files for dashboard frontend
    from fastapi.staticfiles import StaticFiles
    import os
    
    # Path to frontend build files
    frontend_path = os.path.join(os.getcwd(), "dashboard/dist")
    
    if os.path.exists(frontend_path):
        app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
        logger.info(f"Mounted frontend from {frontend_path}")
    else:
        logger.warning(f"Frontend path {frontend_path} not found. Dashboard will not be served.")
    
    # WebSocket endpoint for dashboard
    @app.websocket("/ws/dashboard")
    async def dashboard_websocket(websocket: WebSocket):
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
