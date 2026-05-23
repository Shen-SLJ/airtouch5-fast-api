import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import pyairtouch

from src.core.gateway.pyairtouch import PyAirtouchGateway
from src.core.models import (
    AcPowerState,
    AcMode,
    AcFanSpeed,
    ZonePowerState,
)


def test_map_enum_success():
    """Verify that enums are successfully mapped from pyairtouch to domain enums."""
    # Arrange
    gateway = PyAirtouchGateway()

    # Act & Assert
    assert (
        gateway._map_enum(pyairtouch.AcPowerState.OFF, AcPowerState) == AcPowerState.OFF
    )
    assert (
        gateway._map_enum(pyairtouch.AcPowerState.ON, AcPowerState) == AcPowerState.ON
    )
    assert gateway._map_enum(pyairtouch.AcMode.COOL, AcMode) == AcMode.COOL
    assert gateway._map_enum(pyairtouch.AcFanSpeed.LOW, AcFanSpeed) == AcFanSpeed.LOW
    assert (
        gateway._map_enum(pyairtouch.ZonePowerState.OFF, ZonePowerState)
        == ZonePowerState.OFF
    )


def test_map_enum_fallback_on_none():
    """Verify that mapping a None value falls back safely to the first member of the target Enum."""
    # Arrange
    gateway = PyAirtouchGateway()

    # Act
    result = gateway._map_enum(None, AcPowerState)

    # Assert
    assert result == AcPowerState.OFF


def test_map_enum_fallback_on_invalid():
    """Verify that mapping an invalid value falls back safely to the first member of the target Enum."""
    # Arrange
    gateway = PyAirtouchGateway()

    # Act
    result = gateway._map_enum("SUPER_COOL", AcMode)

    # Assert
    assert result == AcMode.AUTO


@pytest.mark.asyncio
@patch("pyairtouch.connect")
async def test_get_connection_success(mock_connect):
    """Verify that get_connection correctly invokes pyairtouch.connect and initialization."""
    # Arrange
    mock_airtouch = MagicMock()
    mock_airtouch.init = AsyncMock(return_value=True)
    mock_connect.return_value = mock_airtouch
    gateway = PyAirtouchGateway()

    # Act
    airtouch_instance = await gateway._get_connection("192.168.1.50")

    # Assert
    mock_connect.assert_called_once_with(
        model=pyairtouch.AirTouchModel.AIRTOUCH_5,
        host="192.168.1.50",
        port=9005,
    )
    mock_airtouch.init.assert_called_once()
    assert airtouch_instance == mock_airtouch
