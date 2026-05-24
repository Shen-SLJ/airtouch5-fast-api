from fastapi import HTTPException, Request


class DeviceRegistry:
    """Hardcoded device registry mapping AirTouch device IDs to their private IP addresses.

    Maps the AirTouch device ID (``DiscoveredDevice.id``, i.e. the integer
    airtouch_id cast to string) to its static private IP on the local network.

    In production this would be backed by a persistent database or service
    discovery mechanism. Currently hardcoded for development.
    """

    _registry: dict[str, str] = {
        # airtouch_id (str) -> private IP address
        "1": "192.168.68.68",
    }

    def resolve(self, device_id: str) -> str:
        """Resolves a device ID to its private IP address.

        Args:
            device_id: The AirTouch device ID (matches ``DiscoveredDevice.id``).

        Returns:
            str: The private IP address of the device.

        Raises:
            HTTPException: 404 if the device ID is not found in the registry.
        """
        host = self._registry.get(device_id)
        if host is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Device with ID '{device_id}' is not registered. "
                    f"Known device IDs: {list(self._registry.keys())}"
                ),
            )
        return host


def get_registry(request: Request) -> DeviceRegistry:
    """FastAPI dependency that retrieves the shared DeviceRegistry from application state."""
    return request.app.state.device_registry
