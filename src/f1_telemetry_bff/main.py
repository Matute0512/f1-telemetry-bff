from fastapi import FastAPI

from f1_telemetry_bff.presentation.api.routes import laps_router

app = FastAPI(
    title="F1 Telemetry BFF",
    version="0.1.0",
    description="Backend for Frontend for F1 telemetry head-to-head comparisons.",
)

app.include_router(laps_router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
