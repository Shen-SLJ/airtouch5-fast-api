from fastapi import APIRouter, Depends
from src.core.models import DiscoveryResponse
from src.features.discovery.service import DiscoveryService

router = APIRouter(prefix="/api/v1/airtouches", tags=["Discovery"])


@router.get("", response_model=DiscoveryResponse)
async def get_airtouches(
    service: DiscoveryService = Depends(),
) -> DiscoveryResponse:
    """Discovers all AirTouch consoles on the local network.

    Args:
        service: The injected discovery service.

    Returns:
        DiscoveryResponse: Model containing details of all discovered devices.
    """
    return await service.discover_devices()
