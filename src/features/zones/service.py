from fastapi import Depends, HTTPException, status
from src.core.gateway import AirtouchGateway, get_gateway
from src.core.models import ZonePowerState, ActionResponse


class ZoneService:
    """Service handling hardware console control and management for Zone units."""

    def __init__(self, gateway: AirtouchGateway = Depends(get_gateway)) -> None:
        """Initializes the ZoneService with the hardware gateway dependency.

        Args:
            gateway: The hardware abstraction gateway.
        """
        self._gateway = gateway

    async def set_zone_power(
        self,
        host: str,
        air_conditioner_id: int,
        zone_id: int,
        power: ZonePowerState,
    ) -> ActionResponse:
        """Sets the operational power state of a specific zone.

        Args:
            host: IP address or hostname of the AirTouch console.
            air_conditioner_id: ID of the parent Air Conditioner unit.
            zone_id: ID of the zone to control.
            power: Desired ZonePowerState.

        Returns:
            ActionResponse: A status confirmation of the command execution.

        Raises:
            HTTPException: 400 Bad Request if the zone/AC is invalid or state is unsupported.
        """
        is_successful = await self._gateway.set_zone_power(
            host, air_conditioner_id, zone_id, power
        )
        if not is_successful:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Failed to set zone {zone_id} power state to {power}. "
                    f"Zone might not exist, or power state is unsupported."
                ),
            )

        return ActionResponse(
            status="success",
            message=f"Zone {zone_id} power state set to {power}",
        )

    async def set_zone_temp(
        self,
        host: str,
        air_conditioner_id: int,
        zone_id: int,
        temperature: float,
    ) -> ActionResponse:
        """Sets the target temperature of a specific temperature-controlled zone.

        Args:
            host: IP address or hostname of the AirTouch console.
            air_conditioner_id: ID of the parent Air Conditioner unit.
            zone_id: ID of the zone to control.
            temperature: Target temperature value.

        Returns:
            ActionResponse: A status confirmation of the command execution.

        Raises:
            HTTPException: 400 Bad Request if the zone/AC is invalid or not in temperature control mode.
        """
        is_successful = await self._gateway.set_zone_temp(
            host, air_conditioner_id, zone_id, temperature
        )
        if not is_successful:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Failed to set zone {zone_id} temperature to {temperature}. "
                    f"Zone might not exist, or is not in TEMPERATURE control mode."
                ),
            )

        return ActionResponse(
            status="success",
            message=f"Zone {zone_id} temperature set to {temperature}",
        )

    async def set_zone_damper(
        self,
        host: str,
        air_conditioner_id: int,
        zone_id: int,
        damper_percentage: int,
    ) -> ActionResponse:
        """Sets the damper opening percentage of a specific damper-controlled zone.

        Args:
            host: IP address or hostname of the AirTouch console.
            air_conditioner_id: ID of the parent Air Conditioner unit.
            zone_id: ID of the zone to control.
            damper_percentage: Damper opening percentage (0-100).

        Returns:
            ActionResponse: A status confirmation of the command execution.

        Raises:
            HTTPException: 400 Bad Request if the zone/AC is invalid or percentage is out of range.
        """
        is_successful = await self._gateway.set_zone_damper(
            host, air_conditioner_id, zone_id, damper_percentage
        )
        if not is_successful:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Failed to set zone {zone_id} damper percentage to {damper_percentage}. "
                    f"Zone might not exist, or percentage value out of range (0-100)."
                ),
            )

        return ActionResponse(
            status="success",
            message=f"Zone {zone_id} damper percentage set to {damper_percentage}",
        )
