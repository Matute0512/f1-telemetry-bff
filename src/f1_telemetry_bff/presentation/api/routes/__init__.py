from f1_telemetry_bff.presentation.api.routes.laps import router as laps_router
from f1_telemetry_bff.presentation.api.routes.sessions import (
    router as sessions_router,
)

__all__ = [
    "laps_router",
    "sessions_router",
]
