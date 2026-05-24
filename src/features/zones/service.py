from src.core.gateway import IAirtouchGateway
from src.core.models import (
    ZonePowerState,
    ZoneStatus,
    ZoneControlMethod,
    AirtouchControlError,
)


class ZoneService:
    """Service handling hardware console control and management for Zone units."""

    def __init__(self, gateway: IAirtouchGateway) -> None:
        """Initializes the ZoneService with the hardware gateway dependency.

        Args:
            gateway: The hardware abstraction gateway.
        """
        self._gateway = gateway

    async def _get_zone_status(
        self, host: str, air_conditioner_id: int, zone_id: int
    ) -> ZoneStatus:
        """Retrieves the status of a specific zone, raising an error if the AC or zone does not exist."""
        status_info = await self._gateway.get_status(host)
        for ac in status_info.air_conditioners:
            if ac.ac_id == air_conditioner_id:
                for zone in ac.zones:
                    if zone.zone_id == zone_id:
                        return zone
                raise AirtouchControlError(
                    f"Zone {zone_id} does not exist on AC {air_conditioner_id}."
                )
        raise AirtouchControlError(
            f"AC {air_conditioner_id} does not exist on host {host}."
        )

    async def set_zone_power(
        self,
        host: str,
        air_conditioner_id: int,
        zone_id: int,
        power: ZonePowerState,
    ) -> None:
        """Sets the operational power state of a specific zone.

        Args:
            host: IP address or hostname of the AirTouch console.
            air_conditioner_id: ID of the parent Air Conditioner unit.
            zone_id: ID of the zone to control.
            power: Desired ZonePowerState.

        Raises:
            AirtouchControlError: If the AC or zone does not exist or the call fails.
        """
        await self._get_zone_status(host, air_conditioner_id, zone_id)

        is_successful = await self._gateway.set_zone_power(
            host, air_conditioner_id, zone_id, power
        )
        if not is_successful:
            raise AirtouchControlError(
                f"Failed to set zone {zone_id} power state to {power}."
            )

    async def set_zone_temp(
        self,
        host: str,
        air_conditioner_id: int,
        zone_id: int,
        temperature: float,
    ) -> None:
        """Sets the target temperature of a specific temperature-controlled zone.

        Args:
            host: IP address or hostname of the AirTouch console.
            air_conditioner_id: ID of the parent Air Conditioner unit.
            zone_id: ID of the zone to control.
            temperature: Target temperature value.

        Raises:
            AirtouchControlError: If AC or zone does not exist, zone is not temperature-controlled, or call fails.
        """
        zone = await self._get_zone_status(host, air_conditioner_id, zone_id)
        if zone.control_method != ZoneControlMethod.TEMPERATURE:
            raise AirtouchControlError(
                f"Zone {zone_id} is not in TEMPERATURE control mode (currently {zone.control_method})."
            )

        is_successful = await self._gateway.set_zone_temp(
            host, air_conditioner_id, zone_id, temperature
        )
        if not is_successful:
            raise AirtouchControlError(
                f"Failed to set zone {zone_id} temperature to {temperature}."
            )

    async def set_zone_damper(
        self,
        host: str,
        air_conditioner_id: int,
        zone_id: int,
        damper_percentage: int,
    ) -> None:
        """Sets the damper opening percentage of a specific damper-controlled zone.

        Args:
            host: IP address or hostname of the AirTouch console.
            air_conditioner_id: ID of the parent Air Conditioner unit.
            zone_id: ID of the zone to control.
            damper_percentage: Damper opening percentage (0-100).

        Raises:
            AirtouchControlError: If AC or zone does not exist, damper is out of bounds, or call fails.
        """
        if not (0 <= damper_percentage <= 100):
            raise AirtouchControlError(
                f"Damper percentage {damper_percentage} is out of bounds (0-100)."
            )

        await self._get_zone_status(host, air_conditioner_id, zone_id)

        is_successful = await self._gateway.set_zone_damper(
            host, air_conditioner_id, zone_id, damper_percentage
        )
        if not is_successful:
            raise AirtouchControlError(
                f"Failed to set zone {zone_id} damper percentage to {damper_percentage}."
            )
