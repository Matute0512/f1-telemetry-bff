from fastapi import FastAPI

app = FastAPI(
    title="F1 Telemetry BFF",
    version="0.1.0",
    description="Backend for Frontend for F1 telemetry head-to-head comparisons.",
)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
