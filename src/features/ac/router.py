from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.core.gateway import AirtouchGateway, get_gateway
from src.core.models import (
    AirtouchStatus,
    AirtouchCapabilities,
    AcPowerControl,
    AcMode,
    AcFanSpeed,
    ActionResponse,
    AirtouchPowerResponse,
)

router = APIRouter(prefix="/api/v1/airtouches", tags=["AC Control"])


class AcPowerRequest(BaseModel):
    power: AcPowerControl


class AcModeRequest(BaseModel):
    mode: AcMode


class AcFanSpeedRequest(BaseModel):
    fan_speed: AcFanSpeed


class AcTempRequest(BaseModel):
    temperature: float = Field(..., description="Target temperature value.")


@router.post("/{host}/start", response_model=AirtouchPowerResponse)
async def start_airtouch(
    host: str, gateway: AirtouchGateway = Depends(get_gateway)
) -> AirtouchPowerResponse:
    action_results = await gateway.set_all_ac_power(host, AcPowerControl.TURN_ON)
    status_info = await gateway.get_status(host)

    return AirtouchPowerResponse(
        model=status_info.model,
        host=status_info.host,
        port=status_info.port,
        connected=status_info.connected,
        air_conditioners=action_results,
    )


@router.post("/{host}/stop", response_model=AirtouchPowerResponse)
async def stop_airtouch(
    host: str, gateway: AirtouchGateway = Depends(get_gateway)
) -> AirtouchPowerResponse:
    action_results = await gateway.set_all_ac_power(host, AcPowerControl.TURN_OFF)
    status_info = await gateway.get_status(host)

    return AirtouchPowerResponse(
        model=status_info.model,
        host=status_info.host,
        port=status_info.port,
        connected=status_info.connected,
        air_conditioners=action_results,
    )


@router.get("/{host}/status", response_model=AirtouchStatus)
async def get_airtouch_status(
    host: str, gateway: AirtouchGateway = Depends(get_gateway)
) -> AirtouchStatus:
    status_info = await gateway.get_status(host)

    return status_info


@router.get("/{host}/capabilities", response_model=AirtouchCapabilities)
async def get_airtouch_capabilities(
    host: str, gateway: AirtouchGateway = Depends(get_gateway)
) -> AirtouchCapabilities:
    capabilities = await gateway.get_capabilities(host)

    return capabilities


@router.post(
    "/{host}/air-conditioner/{air_conditioner_id}/power", response_model=ActionResponse
)
async def set_ac_power(
    host: str,
    air_conditioner_id: int,
    request: AcPowerRequest,
    gateway: AirtouchGateway = Depends(get_gateway),
) -> ActionResponse:
    is_successful = await gateway.set_ac_power(host, air_conditioner_id, request.power)
    if not is_successful:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to set AC {air_conditioner_id} power state to {request.power}. AC might not exist, or control is unsupported.",
        )

    return ActionResponse(
        status="success",
        message=f"AC {air_conditioner_id} power state set to {request.power}",
    )


@router.post(
    "/{host}/air-conditioner/{air_conditioner_id}/mode", response_model=ActionResponse
)
async def set_ac_mode(
    host: str,
    air_conditioner_id: int,
    request: AcModeRequest,
    gateway: AirtouchGateway = Depends(get_gateway),
) -> ActionResponse:
    is_successful = await gateway.set_ac_mode(host, air_conditioner_id, request.mode)
    if not is_successful:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to set AC {air_conditioner_id} mode to {request.mode}. AC might not exist, or mode is unsupported.",
        )

    return ActionResponse(
        status="success", message=f"AC {air_conditioner_id} mode set to {request.mode}"
    )


@router.post(
    "/{host}/air-conditioner/{air_conditioner_id}/fan-speed",
    response_model=ActionResponse,
)
async def set_ac_fan_speed(
    host: str,
    air_conditioner_id: int,
    request: AcFanSpeedRequest,
    gateway: AirtouchGateway = Depends(get_gateway),
) -> ActionResponse:
    is_successful = await gateway.set_ac_fan_speed(
        host, air_conditioner_id, request.fan_speed
    )
    if not is_successful:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to set AC {air_conditioner_id} fan speed to {request.fan_speed}. AC might not exist, or speed is unsupported.",
        )

    return ActionResponse(
        status="success",
        message=f"AC {air_conditioner_id} fan speed set to {request.fan_speed}",
    )


@router.post(
    "/{host}/air-conditioner/{air_conditioner_id}/temp", response_model=ActionResponse
)
async def set_ac_temp(
    host: str,
    air_conditioner_id: int,
    request: AcTempRequest,
    gateway: AirtouchGateway = Depends(get_gateway),
) -> ActionResponse:
    is_successful = await gateway.set_ac_temp(
        host, air_conditioner_id, request.temperature
    )
    if not is_successful:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to set AC {air_conditioner_id} temperature to {request.temperature}. Target value out of range or AC does not exist.",
        )

    return ActionResponse(
        status="success",
        message=f"AC {air_conditioner_id} temperature set to {request.temperature}",
    )
