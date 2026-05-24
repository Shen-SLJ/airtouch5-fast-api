from contextlib import asynccontextmanager, AsyncExitStack
from typing import AsyncContextManager, Callable, Sequence
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.features.discovery.router import router as discovery_router
from src.features.ac.router import router as ac_router
from src.features.zones.router import router as zones_router
from src.core.system.router import router as system_router
from src.core.gateway.pyairtouch import pyairtouch_lifespan
from src.core.errors.exceptions import DomainError
from src.core.errors.exception_handlers import (
    domain_error_handler,
    request_validation_error_handler,
    global_exception_handler,
)

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

# Register business domain and validation exception handlers natively
app.add_exception_handler(DomainError, domain_error_handler)
app.add_exception_handler(RequestValidationError, request_validation_error_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(system_router)
app.include_router(discovery_router)
app.include_router(ac_router)
app.include_router(zones_router)