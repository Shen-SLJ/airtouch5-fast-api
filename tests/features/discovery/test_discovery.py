import pytest
from src.features.discovery.router import get_airtouches
from src.features.discovery.service import DiscoveryService


@pytest.mark.asyncio
async def test_get_airtouches_success(mock_gateway):
    # Arrange
    service = DiscoveryService(gateway=mock_gateway)

    # Act
    result = await get_airtouches(service=service)

    # Assert
    devices = result.airtouch_devices

    assert len(devices) == 1
    assert devices[0].name == "Test AirTouch 5"
    assert devices[0].host == "192.168.1.15"
    assert devices[0].id == "at5_9876"
    assert devices[0].serial == "98765432"

    assert mock_gateway.calls == [("discover_devices", {})]
