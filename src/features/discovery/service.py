from typing import List
from fastapi import Depends
from src.core.gateway import AirtouchGateway, get_gateway
from src.core.models import DiscoveredDevice


class DiscoveryService:
    """Service handling hardware console discovery logic on the local network."""

    def __init__(self, gateway: AirtouchGateway = Depends(get_gateway)) -> None:
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
