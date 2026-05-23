from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.core.models import ZonePowerState, ActionResponse
from src.features.zones.service import ZoneService

router = APIRouter(prefix="/api/v1/airtouches", tags=["Zone Control"])


class ZonePowerRequest(BaseModel):
    """API request payload schema for changing Zone power state."""

    power: ZonePowerState


class ZoneTempRequest(BaseModel):
    """API request payload schema for changing Zone target temperature."""

    temperature: float = Field(..., description="Target temperature for the zone.")


class ZoneDamperRequest(BaseModel):
    """API request payload schema for changing Zone damper opening percentage."""

    damper_percentage: int = Field(
        ..., ge=0, le=100, description="Damper opening percentage (0-100)."
    )


@router.post(
    "/{host}/air-conditioner/{air_conditioner_id}/zones/{zone_id}/power",
    response_model=ActionResponse,
)
async def set_zone_power(
    host: str,
    air_conditioner_id: int,
    zone_id: int,
    request: ZonePowerRequest,
    service: ZoneService = Depends(),
) -> ActionResponse:
    """Sets the operational power state of a specific zone.

    Args:
        host: IP address or hostname of the AirTouch console.
        air_conditioner_id: ID of the parent Air Conditioner unit.
        zone_id: ID of the zone to control.
        request: Request body containing the desired ZonePowerState.
        service: The injected Zone service.

    Returns:
        ActionResponse: A status confirmation of the command execution.
    """
    return await service.set_zone_power(
        host, air_conditioner_id, zone_id, request.power
    )


@router.post(
    "/{host}/air-conditioner/{air_conditioner_id}/zones/{zone_id}/temp",
    response_model=ActionResponse,
)
async def set_zone_temp(
    host: str,
    air_conditioner_id: int,
    zone_id: int,
    request: ZoneTempRequest,
    service: ZoneService = Depends(),
) -> ActionResponse:
    """Sets the target temperature of a specific temperature-controlled zone.

    Args:
        host: IP address or hostname of the AirTouch console.
        air_conditioner_id: ID of the parent Air Conditioner unit.
        zone_id: ID of the zone to control.
        request: Request body containing the target temperature value.
        service: The injected Zone service.

    Returns:
        ActionResponse: A status confirmation of the command execution.
    """
    return await service.set_zone_temp(
        host, air_conditioner_id, zone_id, request.temperature
    )


@router.post(
    "/{host}/air-conditioner/{air_conditioner_id}/zones/{zone_id}/damper",
    response_model=ActionResponse,
)
async def set_zone_damper(
    host: str,
    air_conditioner_id: int,
    zone_id: int,
    request: ZoneDamperRequest,
    service: ZoneService = Depends(),
) -> ActionResponse:
    """Sets the damper opening percentage of a specific damper-controlled zone.

    Args:
        host: IP address or hostname of the AirTouch console.
        air_conditioner_id: ID of the parent Air Conditioner unit.
        zone_id: ID of the zone to control.
        request: Request body containing the damper opening percentage (0-100).
        service: The injected Zone service.

    Returns:
        ActionResponse: A status confirmation of the command execution.
    """
    return await service.set_zone_damper(
        host, air_conditioner_id, zone_id, request.damper_percentage
    )
