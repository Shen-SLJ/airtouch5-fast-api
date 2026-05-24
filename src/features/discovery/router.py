from fastapi import APIRouter, Depends
from src.core.gateway import IAirtouchGateway, get_gateway
from src.core.models import DiscoveryResponse
from src.features.discovery.service import DiscoveryService

router = APIRouter(prefix="/api/v1/airtouches", tags=["Discovery"])


def get_discovery_service(
    gateway: IAirtouchGateway = Depends(get_gateway),
) -> DiscoveryService:
    """Dependency provider function for DiscoveryService."""
    return DiscoveryService(gateway)


@router.get("", response_model=DiscoveryResponse)
async def get_airtouches(
    service: DiscoveryService = Depends(get_discovery_service),
) -> DiscoveryResponse:
    """Discovers all AirTouch consoles on the local network.

    Args:
        service: The injected discovery service.

    Returns:
        DiscoveryResponse: Model containing details of all discovered devices.
    """
    devices = await service.discover_devices()
    return DiscoveryResponse(airtouch_devices=devices)
