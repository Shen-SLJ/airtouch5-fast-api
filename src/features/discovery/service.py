from abc import ABC, abstractmethod
from typing import List
from src.core.gateway import IAirtouchGateway
from src.core.models import DiscoveredDevice


class IDiscoveryService(ABC):
    """Abstract interface for device discovery service."""

    @abstractmethod
    async def discover_devices(self) -> List[DiscoveredDevice]:
        """Discovers all AirTouch consoles on the local network.

        Returns:
            List[DiscoveredDevice]: List containing details of all discovered devices.
        """
        pass


class DiscoveryService(IDiscoveryService):
    """Service handling hardware console discovery logic on the local network."""

    def __init__(self, gateway: IAirtouchGateway) -> None:
        """Initializes the DiscoveryService with the hardware gateway dependency.

        Args:
            gateway: The hardware abstraction gateway.
        """
        self._gateway = gateway

    async def discover_devices(self) -> List[DiscoveredDevice]:
        """Discovers all AirTouch consoles on the local network.

        Returns:
            List[DiscoveredDevice]: List containing details of all discovered devices.
        """
        discovered_airtouches = await self._gateway.discover_devices()
        return list(discovered_airtouches)
