from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.features.discovery.router import router as discovery_router
from src.features.ac.router import router as ac_router
from src.features.zones.router import router as zones_router
from src.core.gateway.pyairtouch import pyairtouch_lifespan
from src.core.models import AirtouchConnectionError


app = FastAPI(
    title="AirTouch 5 FastAPI Service",
    description="A vertically sliced FastAPI service for controlling AirTouch 5 AC units and Zones.",
    version="1.0.0",
    lifespan=pyairtouch_lifespan,
)


@app.exception_handler(AirtouchConnectionError)
async def airtouch_connection_error_handler(
    _request, exception: AirtouchConnectionError
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "detail": f"Could not connect to Airtouch console at {exception.host}"
        },
    )


@app.get("/health", tags=["Health"])
def get_health() -> dict:
    return {"status": "ok"}


app.include_router(discovery_router)
app.include_router(ac_router)
app.include_router(zones_router)