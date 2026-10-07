from f1_telemetry_bff.presentation.api.routes.head_to_head import (
    router as head_to_head_router,
)
from f1_telemetry_bff.presentation.api.routes.laps import router as laps_router
from f1_telemetry_bff.presentation.api.routes.sessions import (
    router as sessions_router,
)

__all__ = [
    "head_to_head_router",
    "laps_router",
    "sessions_router",
]
