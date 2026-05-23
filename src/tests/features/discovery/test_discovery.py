import pytest
from src.features.discovery.router import get_airtouches


@pytest.mark.asyncio
async def test_get_airtouches_success(mock_gateway):
    """Verify that get_airtouches calls discover_devices on the gateway and returns the correct list structure."""
    # Arrange
    # Gateway setup is handled by mock_gateway fixture

    # Act
    result = await get_airtouches(gateway=mock_gateway)

    # Assert
    devices = result.airtouch_devices

    assert len(devices) == 1
    assert devices[0].name == "Test AirTouch 5"
    assert devices[0].host == "192.168.1.15"
    assert devices[0].id == "at5_9876"
    assert devices[0].serial == "98765432"

    # Assert gateway interaction
    assert mock_gateway.calls == [("discover_devices", {})]
