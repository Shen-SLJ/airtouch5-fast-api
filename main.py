from contextlib import asynccontextmanager, AsyncExitStack
from typing import AsyncContextManager, Callable, Sequence
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.features.discovery.router import router as discovery_router
from src.features.ac.router import router as ac_router
from src.features.zones.router import router as zones_router
from src.core.system.router import router as system_router
from src.core.gateway.pyairtouch import pyairtouch_lifespan
from src.core.models import AirtouchConnectionError, AirtouchControlError

LifespanCallable = Callable[[FastAPI], AsyncContextManager[None]]


@asynccontextmanager
async def global_lifespan(
    app: FastAPI,
    lifespans: Sequence[LifespanCallable] = (pyairtouch_lifespan,),
):
    """Composes multiple registered modular lifespan managers into a single global lifespan.

    Ensures that startup routines are executed in sequence, and shutdown resource cleanups
    are safely managed in reverse order.
    """
    async with AsyncExitStack() as stack:
        for lifespan_fn in lifespans:
            await stack.enter_async_context(lifespan_fn(app))
        yield


app = FastAPI(
    title="AirTouch 5 FastAPI Service",
    description="A vertically sliced FastAPI service for controlling AirTouch 5 AC units and Zones.",
    version="1.0.0",
    lifespan=global_lifespan,
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


@app.exception_handler(AirtouchControlError)
async def airtouch_control_error_handler(
    _request, exception: AirtouchControlError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": exception.message},
    )


app.include_router(system_router)
app.include_router(discovery_router)
app.include_router(ac_router)
app.include_router(zones_router)