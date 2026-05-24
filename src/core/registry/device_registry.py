from abc import ABC, abstractmethod
from fastapi import HTTPException, Request


class IDeviceRegistry(ABC):
    """Abstract interface representing a device registry that maps

    AirTouch device IDs to generic device handles (e.g., connection targets).
    """

    @abstractmethod
    def resolve(self, device_id: str) -> str:
        """Resolves a device ID to its generic device handle (e.g. host IP, serial, etc.).

        Args:
            device_id: The AirTouch device ID.

        Returns:
            str: The device handle to connect to the physical unit.
        """
        pass


class DeviceRegistry(IDeviceRegistry):
    """Hardcoded device registry mapping AirTouch device IDs to their device handles.

    Maps the AirTouch device ID (``DiscoveredDevice.id``, i.e. the integer
    airtouch_id cast to string) to its static connection target (IP) on the local network.

    In production this would be backed by a persistent database or service
    discovery mechanism. Currently hardcoded for development.
    """

    # Maps device_id -> device_handle (currently static IP)
    _registry: dict[str, str] = {
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
        device_handle = self._registry.get(device_id)
        if device_handle is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Device with ID '{device_id}' is not registered. "
                    f"Known device IDs: {list(self._registry.keys())}"
                ),
            )
        return device_handle


def get_registry(request: Request) -> IDeviceRegistry:
    """FastAPI dependency that retrieves the shared DeviceRegistry from application state."""
    return request.app.state.device_registry
