from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import health
from loguru import logger

def create_app():
    """Create FastAPI application"""
    app = FastAPI(
        title="Crypto Sentinel Bot API",
        description="API for Crypto Sentinel Telegram Bot",
        version="1.0.0"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    
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
            "health": "/api/v1/health"
        }
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting API server...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
