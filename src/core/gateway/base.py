from abc import ABC, abstractmethod
from typing import List
from fastapi import Request

from src.core.models import (
    DiscoveredDevice,
    AirtouchStatus,
    AirtouchCapabilities,
    AcPowerControl,
    AcMode,
    AcFanSpeed,
    ZonePowerState,
    AcPowerActionResult,
)


class AirtouchGateway(ABC):
    """Abstract base class that serves as the hardware abstraction layer

    for interacting with Airtouch 5 consoles. All features communicate with
    the physical device via implementations of this interface.
    """

    @abstractmethod
    async def discover_devices(self) -> List[DiscoveredDevice]:
        """Discover Airtouch consoles connected on the local network."""
        pass

    @abstractmethod
    async def get_status(self, host: str) -> AirtouchStatus:
        """Retrieve the detailed status of all air conditioners and zones for a given host."""
        pass

    @abstractmethod
    async def get_capabilities(self, host: str) -> AirtouchCapabilities:
        """Retrieve target temperature ranges, resolutions, modes, and fan speeds for a host."""
        pass

    @abstractmethod
    async def set_ac_power(
        self, host: str, air_conditioner_id: int, power_control: AcPowerControl
    ) -> bool:
        """Set the power control state of a specific air conditioner unit."""
        pass

    @abstractmethod
    async def set_all_ac_power(
        self, host: str, power_control: AcPowerControl
    ) -> List[AcPowerActionResult]:
        """Apply a power control command (e.g., TURN_ON, TURN_OFF) to all supported air conditioners."""
        pass

    @abstractmethod
    async def set_ac_mode(
        self, host: str, air_conditioner_id: int, mode: AcMode
    ) -> bool:
        """Set the operational mode (e.g. COOL, HEAT, FAN) of a specific air conditioner unit."""
        pass

    @abstractmethod
    async def set_ac_fan_speed(
        self, host: str, air_conditioner_id: int, fan_speed: AcFanSpeed
    ) -> bool:
        """Set the fan speed of a specific air conditioner unit."""
        pass

    @abstractmethod
    async def set_ac_temp(
        self, host: str, air_conditioner_id: int, temperature: float
    ) -> bool:
        """Set the target temperature for a specific air conditioner unit."""
        pass

    @abstractmethod
    async def set_zone_power(
        self,
        host: str,
        air_conditioner_id: int,
        zone_id: int,
        power_state: ZonePowerState,
    ) -> bool:
        """Set the power state (e.g., ON, OFF, TURBO) of a specific zone."""
        pass

    @abstractmethod
    async def set_zone_temp(
        self, host: str, air_conditioner_id: int, zone_id: int, temperature: float
    ) -> bool:
        """Set the target temperature of a specific temperature-controlled zone."""
        pass

    @abstractmethod
    async def set_zone_damper(
        self, host: str, air_conditioner_id: int, zone_id: int, damper_percentage: int
    ) -> bool:
        """Set the damper opening percentage of a specific damper-controlled zone."""
        pass

    @abstractmethod
    async def close_connection(self) -> None:
        """Close active socket connections and release hardware resources cleanly."""
        pass


def get_gateway(request: Request) -> AirtouchGateway:
    """Dependency injector that retrieves the stateful gateway from the application state."""
    gateway: AirtouchGateway = request.app.state.gateway

    return gateway
