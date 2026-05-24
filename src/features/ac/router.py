from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.core.models import (
    AirtouchStatus,
    AirtouchCapabilities,
    AcPowerControl,
    AcMode,
    AcFanSpeed,
    ActionResponse,
    AirtouchPowerResponse,
)
from src.features.ac.service import AcService

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
    host: str, service: AcService = Depends()
) -> AirtouchPowerResponse:
    """Starts all Air Conditioner units on a given host console.

    Args:
        host: IP address or hostname of the AirTouch console.
        service: The injected AC service.

    Returns:
        AirtouchPowerResponse: Operational status showing which AC units were successfully turned on.
    """
    status_info, action_results = await service.start_airtouch(host)
    return AirtouchPowerResponse(
        model=status_info.model,
        host=status_info.host,
        port=status_info.port,
        connected=status_info.connected,
        air_conditioners=action_results,
    )


@router.post("/{host}/stop", response_model=AirtouchPowerResponse)
async def stop_airtouch(
    host: str, service: AcService = Depends()
) -> AirtouchPowerResponse:
    """Stops all Air Conditioner units on a given host console.

    Args:
        host: IP address or hostname of the AirTouch console.
        service: The injected AC service.

    Returns:
        AirtouchPowerResponse: Operational status showing which AC units were successfully turned off.
    """
    status_info, action_results = await service.stop_airtouch(host)
    return AirtouchPowerResponse(
        model=status_info.model,
        host=status_info.host,
        port=status_info.port,
        connected=status_info.connected,
        air_conditioners=action_results,
    )


@router.get("/{host}/status", response_model=AirtouchStatus)
async def get_airtouch_status(
    host: str, service: AcService = Depends()
) -> AirtouchStatus:
    """Retrieves the comprehensive status of all Air Conditioners and Zones on a host console.

    Args:
        host: IP address or hostname of the AirTouch console.
        service: The injected AC service.

    Returns:
        AirtouchStatus: Detailed runtime status model.
    """
    return await service.get_status(host)


@router.get("/{host}/capabilities", response_model=AirtouchCapabilities)
async def get_airtouch_capabilities(
    host: str, service: AcService = Depends()
) -> AirtouchCapabilities:
    """Retrieves supported hardware capabilities of a host console.

    Args:
        host: IP address or hostname of the AirTouch console.
        service: The injected AC service.

    Returns:
        AirtouchCapabilities: Detailed hardware capabilities model.
    """
    return await service.get_capabilities(host)


@router.post(
    "/{host}/air-conditioner/{air_conditioner_id}/power",
    response_model=ActionResponse,
)
async def set_ac_power(
    host: str,
    air_conditioner_id: int,
    request: AcPowerRequest,
    service: AcService = Depends(),
) -> ActionResponse:
    """Sets the power state of a specific AC unit.

    Args:
        host: IP address or hostname of the AirTouch console.
        air_conditioner_id: ID of the Air Conditioner unit to control.
        request: Request body containing the desired AcPowerControl state.
        service: The injected AC service.

    Returns:
        ActionResponse: A status confirmation of the command execution.
    """
    await service.set_ac_power(host, air_conditioner_id, request.power)
    return ActionResponse(
        status="success",
        message=f"AC {air_conditioner_id} power state set to {request.power}",
    )


@router.post(
    "/{host}/air-conditioner/{air_conditioner_id}/mode",
    response_model=ActionResponse,
)
async def set_ac_mode(
    host: str,
    air_conditioner_id: int,
    request: AcModeRequest,
    service: AcService = Depends(),
) -> ActionResponse:
    """Sets the operational mode of a specific AC unit.

    Args:
        host: IP address or hostname of the AirTouch console.
        air_conditioner_id: ID of the Air Conditioner unit to control.
        request: Request body containing the desired AcMode.
        service: The injected AC service.

    Returns:
        ActionResponse: A status confirmation of the command execution.
    """
    await service.set_ac_mode(host, air_conditioner_id, request.mode)
    return ActionResponse(
        status="success",
        message=f"AC {air_conditioner_id} mode set to {request.mode}",
    )


@router.post(
    "/{host}/air-conditioner/{air_conditioner_id}/fan-speed",
    response_model=ActionResponse,
)
async def set_ac_fan_speed(
    host: str,
    air_conditioner_id: int,
    request: AcFanSpeedRequest,
    service: AcService = Depends(),
) -> ActionResponse:
    """Sets the fan speed of a specific AC unit.

    Args:
        host: IP address or hostname of the AirTouch console.
        air_conditioner_id: ID of the Air Conditioner unit to control.
        request: Request body containing the desired AcFanSpeed.
        service: The injected AC service.

    Returns:
        ActionResponse: A status confirmation of the command execution.
    """
    await service.set_ac_fan_speed(host, air_conditioner_id, request.fan_speed)
    return ActionResponse(
        status="success",
        message=f"AC {air_conditioner_id} fan speed set to {request.fan_speed}",
    )


@router.post(
    "/{host}/air-conditioner/{air_conditioner_id}/temp",
    response_model=ActionResponse,
)
async def set_ac_temp(
    host: str,
    air_conditioner_id: int,
    request: AcTempRequest,
    service: AcService = Depends(),
) -> ActionResponse:
    """Sets the target temperature of a specific Air Conditioner unit.

    Args:
        host: IP address or hostname of the AirTouch console.
        air_conditioner_id: ID of the Air Conditioner unit to control.
        request: Request body containing the target temperature.
        service: The injected AC service.

    Returns:
        ActionResponse: A status confirmation of the command execution.
    """
    await service.set_ac_temp(host, air_conditioner_id, request.temperature)
    return ActionResponse(
        status="success",
        message=f"AC {air_conditioner_id} temperature set to {request.temperature}",
    )
