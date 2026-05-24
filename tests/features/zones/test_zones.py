import pytest
from src.features.zones.router import (
    set_zone_power,
    set_zone_temp,
    set_zone_damper,
    ZonePowerRequest,
    ZoneTempRequest,
    ZoneDamperRequest,
)
from src.features.zones.service import ZoneService
from src.core.models import ZonePowerState, AirtouchControlError


@pytest.mark.asyncio
async def test_set_zone_power_success(mock_gateway):
    # Arrange
    power_request = ZonePowerRequest(power=ZonePowerState.ON)
    service = ZoneService(gateway=mock_gateway)

    # Act
    result = await set_zone_power(
        host="192.168.1.15",
        air_conditioner_id=0,
        zone_id=1,
        request=power_request,
        service=service,
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
async def test_set_zone_power_raises_control_error_on_gateway_failure(mock_gateway):
    # Arrange
    mock_gateway.control_success = False
    power_request = ZonePowerRequest(power=ZonePowerState.ON)
    service = ZoneService(gateway=mock_gateway)

    # Act & Assert
    with pytest.raises(AirtouchControlError) as exception_info:
        await set_zone_power(
            host="192.168.1.15",
            air_conditioner_id=0,
            zone_id=1,
            request=power_request,
            service=service,
        )
    assert "Failed to set zone" in str(exception_info.value)


@pytest.mark.asyncio
async def test_set_zone_power_raises_control_error_on_invalid_ac(mock_gateway):
    # Arrange
    power_request = ZonePowerRequest(power=ZonePowerState.ON)
    service = ZoneService(gateway=mock_gateway)

    # Act & Assert
    with pytest.raises(AirtouchControlError) as exception_info:
        await set_zone_power(
            host="192.168.1.15",
            air_conditioner_id=99,
            zone_id=1,
            request=power_request,
            service=service,
        )
    assert "does not exist on host" in str(exception_info.value)


@pytest.mark.asyncio
async def test_set_zone_power_raises_control_error_on_invalid_zone(mock_gateway):
    # Arrange
    power_request = ZonePowerRequest(power=ZonePowerState.ON)
    service = ZoneService(gateway=mock_gateway)

    # Act & Assert
    with pytest.raises(AirtouchControlError) as exception_info:
        await set_zone_power(
            host="192.168.1.15",
            air_conditioner_id=0,
            zone_id=99,
            request=power_request,
            service=service,
        )
    assert "does not exist on AC" in str(exception_info.value)


@pytest.mark.asyncio
async def test_set_zone_temp_success(mock_gateway):
    # Arrange
    temperature_request = ZoneTempRequest(temperature=23.0)
    service = ZoneService(gateway=mock_gateway)

    # Act
    result = await set_zone_temp(
        host="192.168.1.15",
        air_conditioner_id=0,
        zone_id=1,
        request=temperature_request,
        service=service,
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
async def test_set_zone_temperature_raises_control_error_on_gateway_failure(
    mock_gateway,
):
    # Arrange
    mock_gateway.control_success = False
    temperature_request = ZoneTempRequest(temperature=23.0)
    service = ZoneService(gateway=mock_gateway)

    # Act & Assert
    with pytest.raises(AirtouchControlError) as exception_info:
        await set_zone_temp(
            host="192.168.1.15",
            air_conditioner_id=0,
            zone_id=1,
            request=temperature_request,
            service=service,
        )
    assert "Failed to set zone" in str(exception_info.value)


@pytest.mark.asyncio
async def test_set_zone_temp_raises_control_error_on_damper_controlled_zone(
    mock_gateway,
):
    # Arrange
    temperature_request = ZoneTempRequest(temperature=23.0)
    service = ZoneService(gateway=mock_gateway)

    # Act & Assert
    with pytest.raises(AirtouchControlError) as exception_info:
        await set_zone_temp(
            host="192.168.1.15",
            air_conditioner_id=0,
            zone_id=2,
            request=temperature_request,
            service=service,
        )
    assert "is not in TEMPERATURE control mode" in str(exception_info.value)


@pytest.mark.asyncio
async def test_set_zone_damper_success(mock_gateway):
    # Arrange
    damper_request = ZoneDamperRequest(damper_percentage=75)
    service = ZoneService(gateway=mock_gateway)

    # Act
    result = await set_zone_damper(
        host="192.168.1.15",
        air_conditioner_id=0,
        zone_id=2,
        request=damper_request,
        service=service,
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
async def test_set_zone_damper_raises_control_error_on_gateway_failure(mock_gateway):
    # Arrange
    mock_gateway.control_success = False
    damper_request = ZoneDamperRequest(damper_percentage=75)
    service = ZoneService(gateway=mock_gateway)

    # Act & Assert
    with pytest.raises(AirtouchControlError) as exception_info:
        await set_zone_damper(
            host="192.168.1.15",
            air_conditioner_id=0,
            zone_id=2,
            request=damper_request,
            service=service,
        )
    assert "Failed to set zone" in str(exception_info.value)


@pytest.mark.asyncio
async def test_set_zone_damper_raises_control_error_on_out_of_bounds(mock_gateway):
    # Arrange
    service = ZoneService(gateway=mock_gateway)

    # Act & Assert
    with pytest.raises(AirtouchControlError) as exception_info:
        await service.set_zone_damper(
            host="192.168.1.15",
            air_conditioner_id=0,
            zone_id=2,
            damper_percentage=105,
        )
    assert "is out of bounds" in str(exception_info.value)
