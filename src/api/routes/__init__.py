from src.api.routes.auth import router as auth_router
from src.api.routes.alerts import router as alerts_router
from src.api.routes.prices import router as prices_router
from src.api.routes.portfolio import router as portfolio_router
from src.api.routes.dashboard import router as dashboard_router
from src.api.routes.users import router as users_router
from src.api.routes.metrics import router as metrics_router

__all__ = [
    "auth_router",
    "alerts_router",
    "prices_router",
    "portfolio_router",
    "dashboard_router",
    "users_router",
    "metrics_router",
]
