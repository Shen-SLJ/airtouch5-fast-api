from fastapi import Depends
from src.core.gateway import AirtouchGateway, get_gateway
from src.core.models import DiscoveryResponse


class DiscoveryService:
    """Service handling hardware console discovery logic on the local network."""

    def __init__(self, gateway: AirtouchGateway = Depends(get_gateway)) -> None:
        """Initializes the DiscoveryService with the hardware gateway dependency.

        Args:
            gateway: The hardware abstraction gateway.
        """
        self._gateway = gateway

    async def discover_devices(self) -> DiscoveryResponse:
        """Discovers all AirTouch consoles on the local network.

        Returns:
            DiscoveryResponse: Model containing details of all discovered devices.
        """
        discovered_airtouches = await self._gateway.discover_devices()

        return DiscoveryResponse(
            airtouch_devices=[device for device in discovered_airtouches]
        )
