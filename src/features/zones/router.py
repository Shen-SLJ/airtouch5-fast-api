from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.core.gateway import AirtouchGateway, get_gateway
from src.core.models import ZonePowerState, ActionResponse

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
    gateway: AirtouchGateway = Depends(get_gateway),
) -> ActionResponse:
    """Sets the operational power state (e.g., ON, OFF, TURBO) of a specific zone.

    Args:
        host: IP address or hostname of the AirTouch console.
        air_conditioner_id: ID of the parent Air Conditioner unit.
        zone_id: ID of the zone to control.
        request: Request body containing the desired ZonePowerState.
        gateway: The injected hardware abstraction gateway.

    Returns:
        ActionResponse: A status confirmation of the command execution.

    Raises:
        HTTPException: 400 Bad Request if the zone/AC is invalid or state is unsupported.
    """
    is_successful = await gateway.set_zone_power(
        host, air_conditioner_id, zone_id, request.power
    )
    if not is_successful:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to set zone {zone_id} power state to {request.power}. Zone might not exist, or power state is unsupported.",
        )

    return ActionResponse(
        status="success", message=f"Zone {zone_id} power state set to {request.power}"
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
    gateway: AirtouchGateway = Depends(get_gateway),
) -> ActionResponse:
    """Sets the target temperature of a specific temperature-controlled zone.

    Args:
        host: IP address or hostname of the AirTouch console.
        air_conditioner_id: ID of the parent Air Conditioner unit.
        zone_id: ID of the zone to control.
        request: Request body containing the target temperature value.
        gateway: The injected hardware abstraction gateway.

    Returns:
        ActionResponse: A status confirmation of the command execution.

    Raises:
        HTTPException: 400 Bad Request if the zone/AC is invalid or not in temperature control mode.
    """
    is_successful = await gateway.set_zone_temp(
        host, air_conditioner_id, zone_id, request.temperature
    )
    if not is_successful:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to set zone {zone_id} temperature to {request.temperature}. Zone might not exist, or is not in TEMPERATURE control mode.",
        )

    return ActionResponse(
        status="success",
        message=f"Zone {zone_id} temperature set to {request.temperature}",
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
    gateway: AirtouchGateway = Depends(get_gateway),
) -> ActionResponse:
    """Sets the damper opening percentage of a specific damper-controlled zone.

    Args:
        host: IP address or hostname of the AirTouch console.
        air_conditioner_id: ID of the parent Air Conditioner unit.
        zone_id: ID of the zone to control.
        request: Request body containing the damper opening percentage (0-100).
        gateway: The injected hardware abstraction gateway.

    Returns:
        ActionResponse: A status confirmation of the command execution.

    Raises:
        HTTPException: 400 Bad Request if the zone/AC is invalid or percentage is out of range.
    """
    is_successful = await gateway.set_zone_damper(
        host, air_conditioner_id, zone_id, request.damper_percentage
    )
    if not is_successful:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to set zone {zone_id} damper percentage to {request.damper_percentage}. Zone might not exist, or percentage value out of range (0-100).",
        )

    return ActionResponse(
        status="success",
        message=f"Zone {zone_id} damper percentage set to {request.damper_percentage}",
    )
