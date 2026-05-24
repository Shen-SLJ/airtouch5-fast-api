from fastapi import APIRouter, Depends

from src.core.gateway import IAirtouchGateway, get_gateway
from src.core.registry import DeviceRegistry, get_registry
from src.core.models import ActionResponse, ActionStatus
from src.features.zones.models import ZonePatchRequest
from src.features.zones.service import ZoneService

router = APIRouter(prefix="/api/v1/airtouches", tags=["Zone Control"])


def get_zone_service(
    gateway: IAirtouchGateway = Depends(get_gateway),
) -> ZoneService:
    """Dependency provider function for ZoneService."""
    return ZoneService(gateway)


@router.patch(
    "/{device_id}/air-conditioners/{air_conditioner_id}/zones/{zone_id}",
    response_model=ActionResponse,
)
async def patch_zone(
    device_id: str,
    air_conditioner_id: int,
    zone_id: int,
    request: ZonePatchRequest,
    service: ZoneService = Depends(get_zone_service),
    registry: DeviceRegistry = Depends(get_registry),
) -> ActionResponse:
    """Partially updates one or more properties of a specific zone.

    At least one field (power, temperature, or damper_percentage) must be provided.
    Fields not included in the request body are left unchanged.

    Args:
        device_id: The AirTouch device ID (from device discovery).
        air_conditioner_id: ID of the parent Air Conditioner unit.
        zone_id: ID of the zone to update.
        request: Sparse domain model containing the fields to update.
        service: The injected Zone service.
        registry: The injected device registry for resolving device_id to host IP.

    Returns:
        ActionResponse: A status confirmation listing the fields that were updated.
    """
    host = registry.resolve(device_id)
    applied = await service.update_zone(host, air_conditioner_id, zone_id, request)
    return ActionResponse(
        status=ActionStatus.SUCCESS,
        message=f"Zone {zone_id} updated: {', '.join(applied)}",
    )
