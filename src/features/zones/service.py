from abc import ABC, abstractmethod
from src.core.gateway import IAirtouchGateway
from src.core.models import (
    ZonePowerState,
    ZoneStatus,
    ZoneControlMethod,
    AirtouchControlError,
)
from src.features.zones.models import ZonePatchRequest, ZoneField


class IZoneService(ABC):
    """Abstract interface for the Zone control service."""

    @abstractmethod
    async def update_zone(
        self,
        device_handle: str,
        air_conditioner_id: int,
        zone_id: int,
        patch: ZonePatchRequest,
    ) -> list[ZoneField]:
        """Applies a sparse update to a specific zone."""
        pass


class ZoneService(IZoneService):
    """Service handling hardware console control and management for Zone units."""

    def __init__(self, gateway: IAirtouchGateway) -> None:
        """Initializes the ZoneService with the hardware gateway dependency.

        Args:
            gateway: The hardware abstraction gateway.
        """
        self._gateway = gateway

    async def _get_zone_status(
        self, device_handle: str, air_conditioner_id: int, zone_id: int
    ) -> ZoneStatus:
        """Retrieves the status of a specific zone, raising an error if the AC or zone does not exist."""
        status_info = await self._gateway.get_status(device_handle)
        for ac in status_info.air_conditioners:
            if ac.ac_id == air_conditioner_id:
                for zone in ac.zones:
                    if zone.zone_id == zone_id:
                        return zone
                raise AirtouchControlError(
                    f"Zone {zone_id} does not exist on AC {air_conditioner_id}."
                )
        raise AirtouchControlError(
            f"AC {air_conditioner_id} does not exist on the console."
        )

    async def update_zone(
        self,
        device_handle: str,
        air_conditioner_id: int,
        zone_id: int,
        patch: ZonePatchRequest,
    ) -> list[ZoneField]:
        """Applies a sparse update to a specific zone.

        Only the fields present in the patch are applied. Validates zone existence and
        control-mode compatibility before each control call. Fields are applied in the
        order: power → temperature → damper_percentage.

        Args:
            device_handle: The target device handle (resolved from device ID).
            air_conditioner_id: ID of the parent Air Conditioner unit.
            zone_id: ID of the zone to update.
            patch: Domain model containing the fields to update.

        Returns:
            list[ZoneField]: The fields that were successfully applied.

        Raises:
            AirtouchControlError: If the AC or zone does not exist, a value is incompatible, or a call fails.
        """
        applied: list[ZoneField] = []

        if patch.power is not None:
            await self._set_zone_power(device_handle, air_conditioner_id, zone_id, patch.power)
            applied.append(ZoneField.POWER)

        if patch.temperature is not None:
            await self._set_zone_temp(device_handle, air_conditioner_id, zone_id, patch.temperature)
            applied.append(ZoneField.TEMPERATURE)

        if patch.damper_percentage is not None:
            await self._set_zone_damper(device_handle, air_conditioner_id, zone_id, patch.damper_percentage)
            applied.append(ZoneField.DAMPER_PERCENTAGE)

        return applied

    async def _set_zone_power(
        self,
        device_handle: str,
        air_conditioner_id: int,
        zone_id: int,
        power: ZonePowerState,
    ) -> None:
        """Sets the operational power state of a specific zone.

        Args:
            device_handle: The target device handle (resolved from device ID).
            air_conditioner_id: ID of the parent Air Conditioner unit.
            zone_id: ID of the zone to control.
            power: Desired ZonePowerState.

        Raises:
            AirtouchControlError: If the AC or zone does not exist or the call fails.
        """
        await self._get_zone_status(device_handle, air_conditioner_id, zone_id)

        is_successful = await self._gateway.set_zone_power(
            device_handle, air_conditioner_id, zone_id, power
        )
        if not is_successful:
            raise AirtouchControlError(
                f"Failed to set zone {zone_id} power state to {power}."
            )

    async def _set_zone_temp(
        self,
        device_handle: str,
        air_conditioner_id: int,
        zone_id: int,
        temperature: float,
    ) -> None:
        """Sets the target temperature of a specific temperature-controlled zone.

        Args:
            device_handle: The target device handle (resolved from device ID).
            air_conditioner_id: ID of the parent Air Conditioner unit.
            zone_id: ID of the zone to control.
            temperature: Target temperature value.

        Raises:
            AirtouchControlError: If AC or zone does not exist, zone is not temperature-controlled, or call fails.
        """
        zone = await self._get_zone_status(device_handle, air_conditioner_id, zone_id)
        if zone.control_method != ZoneControlMethod.TEMPERATURE:
            raise AirtouchControlError(
                f"Zone {zone_id} is not in TEMPERATURE control mode (currently {zone.control_method})."
            )

        is_successful = await self._gateway.set_zone_temp(
            device_handle, air_conditioner_id, zone_id, temperature
        )
        if not is_successful:
            raise AirtouchControlError(
                f"Failed to set zone {zone_id} temperature to {temperature}."
            )

    async def _set_zone_damper(
        self,
        device_handle: str,
        air_conditioner_id: int,
        zone_id: int,
        damper_percentage: int,
    ) -> None:
        """Sets the damper opening percentage of a specific damper-controlled zone.

        Args:
            device_handle: The target device handle (resolved from device ID).
            air_conditioner_id: ID of the parent Air Conditioner unit.
            zone_id: ID of the zone to control.
            damper_percentage: Damper opening percentage (0-100).

        Raises:
            AirtouchControlError: If AC or zone does not exist or the call fails.
        """
        await self._get_zone_status(device_handle, air_conditioner_id, zone_id)

        is_successful = await self._gateway.set_zone_damper(
            device_handle, air_conditioner_id, zone_id, damper_percentage
        )
        if not is_successful:
            raise AirtouchControlError(
                f"Failed to set zone {zone_id} damper percentage to {damper_percentage}."
            )
