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
    # Arrange
    gateway = PyAirtouchGateway()

    # Act
    mapped_power_off = gateway._map_enum(pyairtouch.AcPowerState.OFF, AcPowerState)
    mapped_power_on = gateway._map_enum(pyairtouch.AcPowerState.ON, AcPowerState)
    mapped_mode = gateway._map_enum(pyairtouch.AcMode.COOL, AcMode)
    mapped_fan = gateway._map_enum(pyairtouch.AcFanSpeed.LOW, AcFanSpeed)
    mapped_zone = gateway._map_enum(pyairtouch.ZonePowerState.OFF, ZonePowerState)

    # Assert
    assert mapped_power_off == AcPowerState.OFF
    assert mapped_power_on == AcPowerState.ON
    assert mapped_mode == AcMode.COOL
    assert mapped_fan == AcFanSpeed.LOW
    assert mapped_zone == ZonePowerState.OFF


def test_map_enum_fallback_on_none():
    # Arrange
    gateway = PyAirtouchGateway()

    # Act
    result = gateway._map_enum(None, AcPowerState)

    # Assert
    assert result == AcPowerState.OFF


def test_map_enum_fallback_on_invalid():
    # Arrange
    gateway = PyAirtouchGateway()

    # Act
    result = gateway._map_enum("SUPER_COOL", AcMode)

    # Assert
    assert result == AcMode.AUTO


@pytest.mark.asyncio
@patch("pyairtouch.connect")
async def test_get_connection_success(mock_connect):
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


@pytest.mark.asyncio
@patch("pyairtouch.connect")
async def test_get_connection_pooled_reuse(mock_connect):
    # Arrange
    mock_airtouch = MagicMock()
    mock_airtouch.initialised = True
    mock_airtouch.init = AsyncMock(return_value=True)
    mock_connect.return_value = mock_airtouch
    gateway = PyAirtouchGateway()

    # Act
    first_connection = await gateway._get_connection("192.168.1.50")
    second_connection = await gateway._get_connection("192.168.1.50")

    # Assert
    mock_connect.assert_called_once()
    assert first_connection == second_connection
    assert len(gateway._connection_pool._connections) == 1
    assert gateway._connection_pool._connections["192.168.1.50"] == first_connection


@pytest.mark.asyncio
@patch("pyairtouch.connect")
async def test_get_connection_multiple_hosts(mock_connect):
    # Arrange
    mock_airtouch_first = MagicMock()
    mock_airtouch_first.initialised = True
    mock_airtouch_first.init = AsyncMock(return_value=True)

    mock_airtouch_second = MagicMock()
    mock_airtouch_second.initialised = True
    mock_airtouch_second.init = AsyncMock(return_value=True)

    mock_connect.side_effect = [mock_airtouch_first, mock_airtouch_second]
    gateway = PyAirtouchGateway()

    # Act
    connection_first = await gateway._get_connection("192.168.1.50")
    connection_second = await gateway._get_connection("192.168.1.60")

    # Assert
    assert len(gateway._connection_pool._connections) == 2
    assert gateway._connection_pool._connections["192.168.1.50"] == connection_first
    assert gateway._connection_pool._connections["192.168.1.60"] == connection_second
    assert connection_first != connection_second


@pytest.mark.asyncio
@patch("pyairtouch.connect")
async def test_close_connection_shuts_down_all_pooled_connections(mock_connect):
    # Arrange
    mock_airtouch_first = MagicMock()
    mock_airtouch_first.initialised = True
    mock_airtouch_first.init = AsyncMock(return_value=True)
    mock_airtouch_first.shutdown = AsyncMock()

    mock_airtouch_second = MagicMock()
    mock_airtouch_second.initialised = True
    mock_airtouch_second.init = AsyncMock(return_value=True)
    mock_airtouch_second.shutdown = AsyncMock()

    mock_connect.side_effect = [mock_airtouch_first, mock_airtouch_second]
    gateway = PyAirtouchGateway()

    # Act
    await gateway._get_connection("192.168.1.50")
    await gateway._get_connection("192.168.1.60")
    await gateway.close_connection()

    # Assert
    mock_airtouch_first.shutdown.assert_called_once()
    mock_airtouch_second.shutdown.assert_called_once()
    assert len(gateway._connection_pool._connections) == 0


@pytest.mark.asyncio
@patch("pyairtouch.connect")
async def test_fastapi_lifespan_manages_connection_pool_lifecycle(mock_connect):
    # Arrange
    from src.core.gateway.pyairtouch import pyairtouch_lifespan
    from fastapi import FastAPI

    mock_airtouch = MagicMock()
    mock_airtouch.initialised = True
    mock_airtouch.init = AsyncMock(return_value=True)
    mock_airtouch.shutdown = AsyncMock()
    mock_connect.return_value = mock_airtouch

    app = FastAPI()

    # Act
    async with pyairtouch_lifespan(app):
        gateway = app.state.gateway
        assert gateway is not None
        await gateway._get_connection("192.168.1.50")
        assert len(gateway._connection_pool._connections) == 1

    # Assert
    mock_airtouch.shutdown.assert_called_once()
