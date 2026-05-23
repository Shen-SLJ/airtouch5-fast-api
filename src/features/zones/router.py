from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.core.gateway import AirtouchGateway, get_gateway
from src.core.models import ZonePowerState, ActionResponse

router = APIRouter(prefix="/api/v1/airtouches", tags=["Zone Control"])


class ZonePowerRequest(BaseModel):
    power: ZonePowerState


class ZoneTempRequest(BaseModel):
    temperature: float = Field(..., description="Target temperature for the zone.")


class ZoneDamperRequest(BaseModel):
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
