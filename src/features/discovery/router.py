from fastapi import APIRouter, Depends
from src.core.gateway import AirtouchGateway, get_gateway
from src.core.models import DiscoveryResponse

router = APIRouter(prefix="/api/v1/airtouches", tags=["Discovery"])


@router.get("", response_model=DiscoveryResponse)
async def get_airtouches(
    gateway: AirtouchGateway = Depends(get_gateway),
) -> DiscoveryResponse:
    discovered_airtouches = await gateway.discover_devices()

    return DiscoveryResponse(
        airtouch_devices=[device for device in discovered_airtouches]
    )
