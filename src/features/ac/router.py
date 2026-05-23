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
    """API request payload schema for changing Air Conditioner power status."""
    power: AcPowerControl


class AcModeRequest(BaseModel):
    """API request payload schema for changing Air Conditioner operational mode."""
    mode: AcMode


class AcFanSpeedRequest(BaseModel):
    """API request payload schema for changing Air Conditioner fan speed."""
    fan_speed: AcFanSpeed


class AcTempRequest(BaseModel):
    """API request payload schema for changing Air Conditioner target temperature."""
    temperature: float = Field(..., description="Target temperature value.")


@router.post("/{host}/start", response_model=AirtouchPowerResponse)
async def start_airtouch(
    host: str, gateway: AirtouchGateway = Depends(get_gateway)
) -> AirtouchPowerResponse:
    """Starts all Air Conditioner units on a given host console.

    Args:
        host: IP address or hostname of the AirTouch console.
        gateway: The injected hardware abstraction gateway.

    Returns:
        AirtouchPowerResponse: Operational status showing which AC units were successfully turned on.
    """
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
    """Stops all Air Conditioner units on a given host console.

    Args:
        host: IP address or hostname of the AirTouch console.
        gateway: The injected hardware abstraction gateway.

    Returns:
        AirtouchPowerResponse: Operational status showing which AC units were successfully turned off.
    """
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
    """Retrieves the comprehensive status of all Air Conditioners and Zones on a host console.

    Args:
        host: IP address or hostname of the AirTouch console.
        gateway: The injected hardware abstraction gateway.

    Returns:
        AirtouchStatus: Detailed runtime status model.
    """
    status_info = await gateway.get_status(host)

    return status_info


@router.get("/{host}/capabilities", response_model=AirtouchCapabilities)
async def get_airtouch_capabilities(
    host: str, gateway: AirtouchGateway = Depends(get_gateway)
) -> AirtouchCapabilities:
    """Retrieves supported hardware capabilities (target temp ranges, speeds, modes) of a host console.

    Args:
        host: IP address or hostname of the AirTouch console.
        gateway: The injected hardware abstraction gateway.

    Returns:
        AirtouchCapabilities: Detailed hardware capabilities model.
    """
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
    """Sets the power state (e.g. TURN_ON, TURN_OFF, TOGGLE, SLEEP, AWAY) of a specific AC unit.

    Args:
        host: IP address or hostname of the AirTouch console.
        air_conditioner_id: ID of the Air Conditioner unit to control.
        request: Request body containing the desired AcPowerControl state.
        gateway: The injected hardware abstraction gateway.

    Returns:
        ActionResponse: A status confirmation of the command execution.

    Raises:
        HTTPException: 400 Bad Request if the AC is invalid or command is unsupported.
    """
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
    """Sets the operational mode (e.g. COOL, HEAT, DRY, FAN, AUTO) of a specific AC unit.

    Args:
        host: IP address or hostname of the AirTouch console.
        air_conditioner_id: ID of the Air Conditioner unit to control.
        request: Request body containing the desired AcMode.
        gateway: The injected hardware abstraction gateway.

    Returns:
        ActionResponse: A status confirmation of the command execution.

    Raises:
        HTTPException: 400 Bad Request if the AC is invalid or mode is unsupported.
    """
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
    """Sets the fan speed (e.g. LOW, MEDIUM, HIGH, AUTO) of a specific AC unit.

    Args:
        host: IP address or hostname of the AirTouch console.
        air_conditioner_id: ID of the Air Conditioner unit to control.
        request: Request body containing the desired AcFanSpeed.
        gateway: The injected hardware abstraction gateway.

    Returns:
        ActionResponse: A status confirmation of the command execution.

    Raises:
        HTTPException: 400 Bad Request if the AC is invalid or fan speed is unsupported.
    """
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
    """Sets the target temperature of a specific Air Conditioner unit.

    Args:
        host: IP address or hostname of the AirTouch console.
        air_conditioner_id: ID of the Air Conditioner unit to control.
        request: Request body containing the target temperature.
        gateway: The injected hardware abstraction gateway.

    Returns:
        ActionResponse: A status confirmation of the command execution.

    Raises:
        HTTPException: 400 Bad Request if the AC is invalid or target temperature is out of bounds.
    """
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
