import pytest
from fastapi import HTTPException, status
from src.features.zones.router import (
    set_zone_power,
    set_zone_temp,
    set_zone_damper,
    ZonePowerRequest,
    ZoneTempRequest,
    ZoneDamperRequest,
)
from src.core.models import ZonePowerState


@pytest.mark.asyncio
async def test_set_zone_power_success(mock_gateway):
    """Verify that set_zone_power invokes gateway.set_zone_power with correct arguments."""
    # Arrange
    power_request = ZonePowerRequest(power=ZonePowerState.ON)

    # Act
    result = await set_zone_power(
        host="192.168.1.15",
        air_conditioner_id=0,
        zone_id=1,
        request=power_request,
        gateway=mock_gateway,
    )

    # Assert
    assert result.status == "success"
    assert result.message == "Zone 1 power state set to ON"
    assert (
        "set_zone_power",
        {
            "host": "192.168.1.15",
            "air_conditioner_id": 0,
            "zone_id": 1,
            "power_state": ZonePowerState.ON,
        },
    ) in mock_gateway.calls


@pytest.mark.asyncio
async def test_set_zone_power_failed(mock_gateway):
    """Verify set_zone_power raises 400 when gateway operation fails."""
    # Arrange
    mock_gateway.control_success = False
    power_request = ZonePowerRequest(power=ZonePowerState.ON)

    # Act & Assert
    with pytest.raises(HTTPException) as exception_info:
        await set_zone_power(
            host="192.168.1.15",
            air_conditioner_id=0,
            zone_id=1,
            request=power_request,
            gateway=mock_gateway,
        )

    assert exception_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Failed to set zone" in exception_info.value.detail


@pytest.mark.asyncio
async def test_set_zone_temp_success(mock_gateway):
    """Verify that set_zone_temp invokes gateway.set_zone_temp with correct arguments."""
    # Arrange
    temperature_request = ZoneTempRequest(temperature=23.0)

    # Act
    result = await set_zone_temp(
        host="192.168.1.15",
        air_conditioner_id=0,
        zone_id=1,
        request=temperature_request,
        gateway=mock_gateway,
    )

    # Assert
    assert result.status == "success"
    assert result.message == "Zone 1 temperature set to 23.0"
    assert (
        "set_zone_temp",
        {
            "host": "192.168.1.15",
            "air_conditioner_id": 0,
            "zone_id": 1,
            "temperature": 23.0,
        },
    ) in mock_gateway.calls


@pytest.mark.asyncio
async def test_set_zone_temp_failed(mock_gateway):
    """Verify set_zone_temp raises 400 when gateway operation fails."""
    # Arrange
    mock_gateway.control_success = False
    temperature_request = ZoneTempRequest(temperature=23.0)

    # Act & Assert
    with pytest.raises(HTTPException) as exception_info:
        await set_zone_temp(
            host="192.168.1.15",
            air_conditioner_id=0,
            zone_id=1,
            request=temperature_request,
            gateway=mock_gateway,
        )

    assert exception_info.value.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_set_zone_damper_success(mock_gateway):
    """Verify that set_zone_damper invokes gateway.set_zone_damper with correct arguments."""
    # Arrange
    damper_request = ZoneDamperRequest(damper_percentage=75)

    # Act
    result = await set_zone_damper(
        host="192.168.1.15",
        air_conditioner_id=0,
        zone_id=2,
        request=damper_request,
        gateway=mock_gateway,
    )

    # Assert
    assert result.status == "success"
    assert result.message == "Zone 2 damper percentage set to 75"
    assert (
        "set_zone_damper",
        {
            "host": "192.168.1.15",
            "air_conditioner_id": 0,
            "zone_id": 2,
            "damper_percentage": 75,
        },
    ) in mock_gateway.calls


@pytest.mark.asyncio
async def test_set_zone_damper_failed(mock_gateway):
    """Verify set_zone_damper raises 400 when gateway operation fails."""
    # Arrange
    mock_gateway.control_success = False
    damper_request = ZoneDamperRequest(damper_percentage=75)

    # Act & Assert
    with pytest.raises(HTTPException) as exception_info:
        await set_zone_damper(
            host="192.168.1.15",
            air_conditioner_id=0,
            zone_id=2,
            request=damper_request,
            gateway=mock_gateway,
        )

    assert exception_info.value.status_code == status.HTTP_400_BAD_REQUEST
