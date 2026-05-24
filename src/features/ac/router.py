from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.core.gateway import IAirtouchGateway, get_gateway
from src.core.registry import DeviceRegistry, get_registry
from src.core.models import (
    AirtouchStatus,
    AirtouchCapabilities,
    AcPowerControl,
    ActionResponse,
    ActionStatus,
)
from src.features.ac.models import AcPatchRequest, AcField, AirtouchPowerResponse
from src.features.ac.service import AcService

router = APIRouter(prefix="/api/v1/airtouches", tags=["AC Control"])


class AcBulkPowerRequest(BaseModel):
    """Request body for a bulk power update across all AC units on a console."""

    power: AcPowerControl


def get_ac_service(gateway: IAirtouchGateway = Depends(get_gateway)) -> AcService:
    """Dependency provider function for AcService."""
    return AcService(gateway)


@router.get("/{device_id}", response_model=AirtouchStatus)
async def get_airtouch_status(
    device_id: str,
    service: AcService = Depends(get_ac_service),
    registry: DeviceRegistry = Depends(get_registry),
) -> AirtouchStatus:
    """Retrieves the comprehensive status of all Air Conditioners and Zones on a device console.

    Args:
        device_id: The AirTouch device ID (from device discovery).
        service: The injected AC service.
        registry: The injected device registry for resolving device_id to host IP.

    Returns:
        AirtouchStatus: Detailed runtime status model.
    """
    host = registry.resolve(device_id)
    return await service.get_status(host)


@router.get("/{device_id}/capabilities", response_model=AirtouchCapabilities)
async def get_airtouch_capabilities(
    device_id: str,
    service: AcService = Depends(get_ac_service),
    registry: DeviceRegistry = Depends(get_registry),
) -> AirtouchCapabilities:
    """Retrieves supported hardware capabilities of a device console.

    Args:
        device_id: The AirTouch device ID (from device discovery).
        service: The injected AC service.
        registry: The injected device registry for resolving device_id to host IP.

    Returns:
        AirtouchCapabilities: Detailed hardware capabilities model.
    """
    host = registry.resolve(device_id)
    return await service.get_capabilities(host)


@router.patch("/{device_id}/air-conditioners", response_model=AirtouchPowerResponse)
async def patch_all_air_conditioners(
    device_id: str,
    request: AcBulkPowerRequest,
    service: AcService = Depends(get_ac_service),
    registry: DeviceRegistry = Depends(get_registry),
) -> AirtouchPowerResponse:
    """Applies a bulk power update to all Air Conditioner units on a device console.

    Args:
        device_id: The AirTouch device ID (from device discovery).
        request: Request body specifying the power state to apply to all AC units.
        service: The injected AC service.
        registry: The injected device registry for resolving device_id to host IP.

    Returns:
        AirtouchPowerResponse: Operational status showing the applied power state per AC unit.
    """
    host = registry.resolve(device_id)
    status_info, action_results = await service.set_all_ac_power(host, request.power)
    return AirtouchPowerResponse(
        model=status_info.model,
        host=status_info.host,
        port=status_info.port,
        connected=status_info.connected,
        air_conditioners=action_results,
    )


@router.patch(
    "/{device_id}/air-conditioners/{air_conditioner_id}",
    response_model=ActionResponse,
)
async def patch_air_conditioner(
    device_id: str,
    air_conditioner_id: int,
    request: AcPatchRequest,
    service: AcService = Depends(get_ac_service),
    registry: DeviceRegistry = Depends(get_registry),
) -> ActionResponse:
    """Partially updates one or more properties of a specific Air Conditioner unit.

    At least one field (power, mode, fan_speed, or temperature) must be provided.
    Fields not included in the request body are left unchanged.

    Args:
        device_id: The AirTouch device ID (from device discovery).
        air_conditioner_id: ID of the Air Conditioner unit to update.
        request: Sparse domain model containing the fields to update.
        service: The injected AC service.
        registry: The injected device registry for resolving device_id to host IP.

    Returns:
        ActionResponse: A status confirmation listing the fields that were updated.
    """
    host = registry.resolve(device_id)
    applied = await service.update_air_conditioner(host, air_conditioner_id, request)
    return ActionResponse(
        status=ActionStatus.SUCCESS,
        message=f"AC {air_conditioner_id} updated: {', '.join(applied)}",
    )
