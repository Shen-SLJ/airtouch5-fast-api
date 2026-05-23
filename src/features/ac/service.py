from fastapi import Depends, HTTPException, status
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


class AcService:
    """Service handling hardware console control and management for Air Conditioner units."""

    def __init__(self, gateway: AirtouchGateway = Depends(get_gateway)) -> None:
        """Initializes the AcService with the hardware gateway dependency.

        Args:
            gateway: The hardware abstraction gateway.
        """
        self._gateway = gateway

    async def start_airtouch(self, host: str) -> AirtouchPowerResponse:
        """Starts all Air Conditioner units on a given host console.

        Args:
            host: IP address or hostname of the AirTouch console.

        Returns:
            AirtouchPowerResponse: Operational status showing which AC units were successfully turned on.
        """
        action_results = await self._gateway.set_all_ac_power(
            host, AcPowerControl.TURN_ON
        )
        status_info = await self._gateway.get_status(host)

        return AirtouchPowerResponse(
            model=status_info.model,
            host=status_info.host,
            port=status_info.port,
            connected=status_info.connected,
            air_conditioners=action_results,
        )

    async def stop_airtouch(self, host: str) -> AirtouchPowerResponse:
        """Stops all Air Conditioner units on a given host console.

        Args:
            host: IP address or hostname of the AirTouch console.

        Returns:
            AirtouchPowerResponse: Operational status showing which AC units were successfully turned off.
        """
        action_results = await self._gateway.set_all_ac_power(
            host, AcPowerControl.TURN_OFF
        )
        status_info = await self._gateway.get_status(host)

        return AirtouchPowerResponse(
            model=status_info.model,
            host=status_info.host,
            port=status_info.port,
            connected=status_info.connected,
            air_conditioners=action_results,
        )

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
    ) -> ActionResponse:
        """Sets the power state of a specific AC unit.

        Args:
            host: IP address or hostname of the AirTouch console.
            air_conditioner_id: ID of the Air Conditioner unit to control.
            power: Desired AcPowerControl state.

        Returns:
            ActionResponse: A status confirmation of the command execution.

        Raises:
            HTTPException: 400 Bad Request if the AC is invalid or command is unsupported.
        """
        is_successful = await self._gateway.set_ac_power(
            host, air_conditioner_id, power
        )
        if not is_successful:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Failed to set AC {air_conditioner_id} power state to {power}. "
                    f"AC might not exist, or control is unsupported."
                ),
            )

        return ActionResponse(
            status="success",
            message=f"AC {air_conditioner_id} power state set to {power}",
        )

    async def set_ac_mode(
        self, host: str, air_conditioner_id: int, mode: AcMode
    ) -> ActionResponse:
        """Sets the operational mode of a specific AC unit.

        Args:
            host: IP address or hostname of the AirTouch console.
            air_conditioner_id: ID of the Air Conditioner unit to control.
            mode: Desired AcMode.

        Returns:
            ActionResponse: A status confirmation of the command execution.

        Raises:
            HTTPException: 400 Bad Request if the AC is invalid or mode is unsupported.
        """
        is_successful = await self._gateway.set_ac_mode(
            host, air_conditioner_id, mode
        )
        if not is_successful:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Failed to set AC {air_conditioner_id} mode to {mode}. "
                    f"AC might not exist, or mode is unsupported."
                ),
            )

        return ActionResponse(
            status="success",
            message=f"AC {air_conditioner_id} mode set to {mode}",
        )

    async def set_ac_fan_speed(
        self, host: str, air_conditioner_id: int, fan_speed: AcFanSpeed
    ) -> ActionResponse:
        """Sets the fan speed of a specific AC unit.

        Args:
            host: IP address or hostname of the AirTouch console.
            air_conditioner_id: ID of the Air Conditioner unit to control.
            fan_speed: Desired AcFanSpeed.

        Returns:
            ActionResponse: A status confirmation of the command execution.

        Raises:
            HTTPException: 400 Bad Request if the AC is invalid or fan speed is unsupported.
        """
        is_successful = await self._gateway.set_ac_fan_speed(
            host, air_conditioner_id, fan_speed
        )
        if not is_successful:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Failed to set AC {air_conditioner_id} fan speed to {fan_speed}. "
                    f"AC might not exist, or speed is unsupported."
                ),
            )

        return ActionResponse(
            status="success",
            message=f"AC {air_conditioner_id} fan speed set to {fan_speed}",
        )

    async def set_ac_temp(
        self, host: str, air_conditioner_id: int, temperature: float
    ) -> ActionResponse:
        """Sets the target temperature of a specific AC unit.

        Args:
            host: IP address or hostname of the AirTouch console.
            air_conditioner_id: ID of the Air Conditioner unit to control.
            temperature: Target temperature value.

        Returns:
            ActionResponse: A status confirmation of the command execution.

        Raises:
            HTTPException: 400 Bad Request if the AC is invalid or target temperature is out of bounds.
        """
        is_successful = await self._gateway.set_ac_temp(
            host, air_conditioner_id, temperature
        )
        if not is_successful:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Failed to set AC {air_conditioner_id} temperature to {temperature}. "
                    f"Target value out of range or AC does not exist."
                ),
            )

        return ActionResponse(
            status="success",
            message=f"AC {air_conditioner_id} temperature set to {temperature}",
        )
