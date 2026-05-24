import pytest
from src.features.zones.service import ZoneService
from src.features.zones.models import ZonePatchRequest, ZoneField
from src.core.models import ZonePowerState
from src.features.zones.exceptions import ZoneControlError


# ---------------------------------------------------------------------------
# update_zone — happy paths
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_zone_power_only_returns_power_field(mock_gateway):
    # Arrange
    service = ZoneService(gateway=mock_gateway)
    patch = ZonePatchRequest(power=ZonePowerState.ON)

    # Act
    applied = await service.update_zone("192.168.1.15", 0, 1, patch)

    # Assert
    assert applied == [ZoneField.POWER]
    assert (
        "set_zone_power",
        {
            "device_handle": "192.168.1.15",
            "air_conditioner_id": 0,
            "zone_id": 1,
            "power_state": ZonePowerState.ON,
        },
    ) in mock_gateway.calls


@pytest.mark.asyncio
async def test_update_zone_temperature_only_returns_temperature_field(mock_gateway):
    # Arrange
    service = ZoneService(gateway=mock_gateway)
    patch = ZonePatchRequest(temperature=23.0)

    # Act
    applied = await service.update_zone("192.168.1.15", 0, 1, patch)

    # Assert
    assert applied == [ZoneField.TEMPERATURE]
    assert (
        "set_zone_temp",
        {
            "device_handle": "192.168.1.15",
            "air_conditioner_id": 0,
            "zone_id": 1,
            "temperature": 23.0,
        },
    ) in mock_gateway.calls


@pytest.mark.asyncio
async def test_update_zone_damper_only_returns_damper_field(mock_gateway):
    # Arrange
    service = ZoneService(gateway=mock_gateway)
    patch = ZonePatchRequest(damper_percentage=75)

    # Act
    applied = await service.update_zone("192.168.1.15", 0, 2, patch)

    # Assert
    assert applied == [ZoneField.DAMPER_PERCENTAGE]
    assert (
        "set_zone_damper",
        {
            "device_handle": "192.168.1.15",
            "air_conditioner_id": 0,
            "zone_id": 2,
            "damper_percentage": 75,
        },
    ) in mock_gateway.calls


@pytest.mark.asyncio
async def test_update_zone_multiple_fields_returns_all_applied_fields(mock_gateway):
    # Arrange
    service = ZoneService(gateway=mock_gateway)
    patch = ZonePatchRequest(power=ZonePowerState.ON, damper_percentage=50)

    # Act
    applied = await service.update_zone("192.168.1.15", 0, 2, patch)

    # Assert
    assert ZoneField.POWER in applied
    assert ZoneField.DAMPER_PERCENTAGE in applied
    assert ZoneField.TEMPERATURE not in applied


# ---------------------------------------------------------------------------
# update_zone — error paths
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_zone_raises_control_error_on_invalid_ac(mock_gateway):
    # Arrange
    service = ZoneService(gateway=mock_gateway)
    patch = ZonePatchRequest(power=ZonePowerState.ON)

    # Act & Assert
    with pytest.raises(ZoneControlError) as exc_info:
        await service.update_zone("192.168.1.15", 99, 1, patch)
    assert "does not exist on the console" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_zone_raises_control_error_on_invalid_zone(mock_gateway):
    # Arrange
    service = ZoneService(gateway=mock_gateway)
    patch = ZonePatchRequest(power=ZonePowerState.ON)

    # Act & Assert
    with pytest.raises(ZoneControlError) as exc_info:
        await service.update_zone("192.168.1.15", 0, 99, patch)
    assert "does not exist on AC" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_zone_raises_control_error_on_temperature_in_damper_controlled_zone(
    mock_gateway,
):
    # Arrange
    service = ZoneService(gateway=mock_gateway)
    patch = ZonePatchRequest(temperature=23.0)  # zone 2 is DAMPER-controlled

    # Act & Assert
    with pytest.raises(ZoneControlError) as exc_info:
        await service.update_zone("192.168.1.15", 0, 2, patch)
    assert "is not in TEMPERATURE control mode" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_zone_raises_control_error_on_gateway_power_failure(mock_gateway):
    # Arrange
    mock_gateway.control_success = False
    service = ZoneService(gateway=mock_gateway)
    patch = ZonePatchRequest(power=ZonePowerState.ON)

    # Act & Assert
    with pytest.raises(ZoneControlError) as exc_info:
        await service.update_zone("192.168.1.15", 0, 1, patch)
    assert "Failed to set zone" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_zone_raises_control_error_on_gateway_temp_failure(mock_gateway):
    # Arrange
    mock_gateway.control_success = False
    service = ZoneService(gateway=mock_gateway)
    patch = ZonePatchRequest(temperature=23.0)

    # Act & Assert
    with pytest.raises(ZoneControlError) as exc_info:
        await service.update_zone("192.168.1.15", 0, 1, patch)
    assert "Failed to set zone" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_zone_raises_control_error_on_gateway_damper_failure(mock_gateway):
    # Arrange
    mock_gateway.control_success = False
    service = ZoneService(gateway=mock_gateway)
    patch = ZonePatchRequest(damper_percentage=75)

    # Act & Assert
    with pytest.raises(ZoneControlError) as exc_info:
        await service.update_zone("192.168.1.15", 0, 2, patch)
    assert "Failed to set zone" in str(exc_info.value)
