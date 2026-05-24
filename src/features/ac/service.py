from typing import List, Tuple
from src.core.gateway import IAirtouchGateway
from src.core.models import (
    AirtouchStatus,
    AirtouchCapabilities,
    AcPowerControl,
    AcMode,
    AcFanSpeed,
    AcCapabilities,
    AcPowerActionResult,
    AirtouchControlError,
)


class AcService:
    """Service handling hardware console control and management for Air Conditioner units."""

    def __init__(self, gateway: IAirtouchGateway) -> None:
        """Initializes the AcService with the hardware gateway dependency.

        Args:
            gateway: The hardware abstraction gateway.
        """
        self._gateway = gateway

    async def _get_ac_capabilities(
        self, host: str, air_conditioner_id: int
    ) -> AcCapabilities:
        """Retrieves the capabilities of a specific AC, raising an error if it does not exist."""
        capabilities = await self._gateway.get_capabilities(host)
        for ac in capabilities.air_conditioners:
            if ac.ac_id == air_conditioner_id:
                return ac
        raise AirtouchControlError(
            f"AC {air_conditioner_id} does not exist on host {host}."
        )

    async def start_airtouch(
        self, host: str
    ) -> Tuple[AirtouchStatus, List[AcPowerActionResult]]:
        """Starts all Air Conditioner units on a given host console.

        Args:
            host: IP address or hostname of the AirTouch console.

        Returns:
            Tuple[AirtouchStatus, List[AcPowerActionResult]]: Console status and list of action results.
        """
        action_results = await self._gateway.set_all_ac_power(
            host, AcPowerControl.TURN_ON
        )
        status_info = await self._gateway.get_status(host)
        return status_info, action_results

    async def stop_airtouch(
        self, host: str
    ) -> Tuple[AirtouchStatus, List[AcPowerActionResult]]:
        """Stops all Air Conditioner units on a given host console.

        Args:
            host: IP address or hostname of the AirTouch console.

        Returns:
            Tuple[AirtouchStatus, List[AcPowerActionResult]]: Console status and list of action results.
        """
        action_results = await self._gateway.set_all_ac_power(
            host, AcPowerControl.TURN_OFF
        )
        status_info = await self._gateway.get_status(host)
        return status_info, action_results

    async def get_status(self, host: str) -> AirtouchStatus:
        """Retrieves the comprehensive status of all Air Conditioners and Zones on a host console.

        Args:
            host: IP address or hostname of the AirTouch console.

        Returns:
            AirtouchStatus: Detailed runtime status model.
        """
        return await self._gateway.get_status(host)

    async def get_capabilities(self, host: str) -> AirtouchCapabilities:
        """Retrieves supported hardware capabilities of a host console.

        Args:
            host: IP address or hostname of the AirTouch console.

        Returns:
            AirtouchCapabilities: Detailed hardware capabilities model.
        """
        return await self._gateway.get_capabilities(host)

    async def set_ac_power(
        self, host: str, air_conditioner_id: int, power: AcPowerControl
    ) -> None:
        """Sets the power state of a specific AC unit after performing capability checks.

        Args:
            host: IP address or hostname of the AirTouch console.
            air_conditioner_id: ID of the Air Conditioner unit to control.
            power: Desired AcPowerControl state.

        Raises:
            AirtouchControlError: If the AC does not exist, power command is unsupported, or call fails.
        """
        ac = await self._get_ac_capabilities(host, air_conditioner_id)
        if power not in ac.supported_power_controls:
            raise AirtouchControlError(
                f"Power control state {power} is not supported by AC {air_conditioner_id}."
            )

        is_successful = await self._gateway.set_ac_power(
            host, air_conditioner_id, power
        )
        if not is_successful:
            raise AirtouchControlError(
                f"Failed to set AC {air_conditioner_id} power state to {power}."
            )

    async def set_ac_mode(
        self, host: str, air_conditioner_id: int, mode: AcMode
    ) -> None:
        """Sets the operational mode of a specific AC unit after performing capability checks.

        Args:
            host: IP address or hostname of the AirTouch console.
            air_conditioner_id: ID of the Air Conditioner unit to control.
            mode: Desired AcMode.

        Raises:
            AirtouchControlError: If the AC does not exist, mode is unsupported, or call fails.
        """
        ac = await self._get_ac_capabilities(host, air_conditioner_id)
        if mode not in ac.supported_modes:
            raise AirtouchControlError(
                f"Operational mode {mode} is not supported by AC {air_conditioner_id}."
            )

        is_successful = await self._gateway.set_ac_mode(
            host, air_conditioner_id, mode
        )
        if not is_successful:
            raise AirtouchControlError(
                f"Failed to set AC {air_conditioner_id} mode to {mode}."
            )

    async def set_ac_fan_speed(
        self, host: str, air_conditioner_id: int, fan_speed: AcFanSpeed
    ) -> None:
        """Sets the fan speed of a specific AC unit after performing capability checks.

        Args:
            host: IP address or hostname of the AirTouch console.
            air_conditioner_id: ID of the Air Conditioner unit to control.
            fan_speed: Desired AcFanSpeed.

        Raises:
            AirtouchControlError: If the AC does not exist, fan speed is unsupported, or call fails.
        """
        ac = await self._get_ac_capabilities(host, air_conditioner_id)
        if fan_speed not in ac.supported_fan_speeds:
            raise AirtouchControlError(
                f"Fan speed {fan_speed} is not supported by AC {air_conditioner_id}."
            )

        is_successful = await self._gateway.set_ac_fan_speed(
            host, air_conditioner_id, fan_speed
        )
        if not is_successful:
            raise AirtouchControlError(
                f"Failed to set AC {air_conditioner_id} fan speed to {fan_speed}."
            )

    async def set_ac_temp(
        self, host: str, air_conditioner_id: int, temperature: float
    ) -> None:
        """Sets the target temperature of a specific AC unit after performing bounds checks.

        Args:
            host: IP address or hostname of the AirTouch console.
            air_conditioner_id: ID of the Air Conditioner unit to control.
            temperature: Target temperature value.

        Raises:
            AirtouchControlError: If AC does not exist, temp is out of bounds, or call fails.
        """
        ac = await self._get_ac_capabilities(host, air_conditioner_id)
        if not (ac.min_target_temperature <= temperature <= ac.max_target_temperature):
            raise AirtouchControlError(
                f"Temperature {temperature} is out of bounds for AC {air_conditioner_id} "
                f"({ac.min_target_temperature} - {ac.max_target_temperature})."
            )

        is_successful = await self._gateway.set_ac_temp(
            host, air_conditioner_id, temperature
        )
        if not is_successful:
            raise AirtouchControlError(
                f"Failed to set AC {air_conditioner_id} temperature to {temperature}."
            )
