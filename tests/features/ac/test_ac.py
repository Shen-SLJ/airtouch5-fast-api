import pytest
from src.features.ac.service import AcService
from src.features.ac.models import AcPatchRequest, AcField
from src.core.models import (
    AcPowerControl,
    AcMode,
    AcFanSpeed,
    AirtouchConnectionError,
    AirtouchControlError,
)


# ---------------------------------------------------------------------------
# get_status
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_status_success(mock_gateway):
    # Arrange
    service = AcService(gateway=mock_gateway)

    # Act
    result = await service.get_status("192.168.1.15")

    # Assert
    assert result.connected is True
    assert len(result.air_conditioners) == 1
    assert result.air_conditioners[0].name == "Living AC"
    assert ("get_status", {"host": "192.168.1.15"}) in mock_gateway.calls


@pytest.mark.asyncio
async def test_get_status_raises_connection_error_when_gateway_disconnected(mock_gateway):
    # Arrange
    mock_gateway.connected_val = False
    service = AcService(gateway=mock_gateway)

    # Act & Assert
    with pytest.raises(AirtouchConnectionError) as exc_info:
        await service.get_status("192.168.1.15")
    assert "Could not connect to Airtouch" in str(exc_info.value)


# ---------------------------------------------------------------------------
# get_capabilities
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_capabilities_success(mock_gateway):
    # Arrange
    service = AcService(gateway=mock_gateway)

    # Act
    result = await service.get_capabilities("192.168.1.15")

    # Assert
    assert result.connected is True
    assert result.air_conditioners[0].min_target_temperature == 16.0
    assert ("get_capabilities", {"host": "192.168.1.15"}) in mock_gateway.calls


# ---------------------------------------------------------------------------
# set_all_ac_power
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_set_all_ac_power_turn_on_success(mock_gateway):
    # Arrange
    service = AcService(gateway=mock_gateway)

    # Act
    status_info, action_results = await service.set_all_ac_power(
        "192.168.1.15", AcPowerControl.TURN_ON
    )

    # Assert
    assert status_info.host == "192.168.1.15"
    assert status_info.connected is True
    assert len(action_results) == 1
    assert action_results[0].ac_id == 0
    assert action_results[0].power_control == AcPowerControl.TURN_ON
    assert action_results[0].applied is True
    assert (
        "set_all_ac_power",
        {"host": "192.168.1.15", "power_control": AcPowerControl.TURN_ON},
    ) in mock_gateway.calls


@pytest.mark.asyncio
async def test_set_all_ac_power_turn_off_success(mock_gateway):
    # Arrange
    service = AcService(gateway=mock_gateway)

    # Act
    status_info, action_results = await service.set_all_ac_power(
        "192.168.1.15", AcPowerControl.TURN_OFF
    )

    # Assert
    assert action_results[0].power_control == AcPowerControl.TURN_OFF
    assert (
        "set_all_ac_power",
        {"host": "192.168.1.15", "power_control": AcPowerControl.TURN_OFF},
    ) in mock_gateway.calls


@pytest.mark.asyncio
async def test_set_all_ac_power_raises_connection_error_when_gateway_disconnected(
    mock_gateway,
):
    # Arrange
    mock_gateway.connected_val = False
    service = AcService(gateway=mock_gateway)

    # Act & Assert
    with pytest.raises(AirtouchConnectionError):
        await service.set_all_ac_power("192.168.1.15", AcPowerControl.TURN_ON)


# ---------------------------------------------------------------------------
# update_air_conditioner — happy paths
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_ac_power_only_returns_power_field(mock_gateway):
    # Arrange
    service = AcService(gateway=mock_gateway)
    patch = AcPatchRequest(power=AcPowerControl.TURN_ON)

    # Act
    applied = await service.update_air_conditioner("192.168.1.15", 0, patch)

    # Assert
    assert applied == [AcField.POWER]
    assert (
        "set_ac_power",
        {"host": "192.168.1.15", "air_conditioner_id": 0, "power_control": AcPowerControl.TURN_ON},
    ) in mock_gateway.calls


@pytest.mark.asyncio
async def test_update_ac_mode_only_returns_mode_field(mock_gateway):
    # Arrange
    service = AcService(gateway=mock_gateway)
    patch = AcPatchRequest(mode=AcMode.COOL)

    # Act
    applied = await service.update_air_conditioner("192.168.1.15", 0, patch)

    # Assert
    assert applied == [AcField.MODE]
    assert (
        "set_ac_mode",
        {"host": "192.168.1.15", "air_conditioner_id": 0, "mode": AcMode.COOL},
    ) in mock_gateway.calls


@pytest.mark.asyncio
async def test_update_ac_fan_speed_only_returns_fan_speed_field(mock_gateway):
    # Arrange
    service = AcService(gateway=mock_gateway)
    patch = AcPatchRequest(fan_speed=AcFanSpeed.HIGH)

    # Act
    applied = await service.update_air_conditioner("192.168.1.15", 0, patch)

    # Assert
    assert applied == [AcField.FAN_SPEED]
    assert (
        "set_ac_fan_speed",
        {"host": "192.168.1.15", "air_conditioner_id": 0, "fan_speed": AcFanSpeed.HIGH},
    ) in mock_gateway.calls


@pytest.mark.asyncio
async def test_update_ac_temperature_only_returns_temperature_field(mock_gateway):
    # Arrange
    service = AcService(gateway=mock_gateway)
    patch = AcPatchRequest(temperature=24.0)

    # Act
    applied = await service.update_air_conditioner("192.168.1.15", 0, patch)

    # Assert
    assert applied == [AcField.TEMPERATURE]
    assert (
        "set_ac_temp",
        {"host": "192.168.1.15", "air_conditioner_id": 0, "temperature": 24.0},
    ) in mock_gateway.calls


@pytest.mark.asyncio
async def test_update_ac_multiple_fields_returns_all_applied_fields(mock_gateway):
    # Arrange
    service = AcService(gateway=mock_gateway)
    patch = AcPatchRequest(power=AcPowerControl.TURN_ON, mode=AcMode.COOL, temperature=22.0)

    # Act
    applied = await service.update_air_conditioner("192.168.1.15", 0, patch)

    # Assert
    assert AcField.POWER in applied
    assert AcField.MODE in applied
    assert AcField.TEMPERATURE in applied
    assert AcField.FAN_SPEED not in applied


# ---------------------------------------------------------------------------
# update_air_conditioner — error paths
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_ac_raises_control_error_on_invalid_ac(mock_gateway):
    # Arrange
    service = AcService(gateway=mock_gateway)
    patch = AcPatchRequest(power=AcPowerControl.TURN_ON)

    # Act & Assert
    with pytest.raises(AirtouchControlError) as exc_info:
        await service.update_air_conditioner("192.168.1.15", 99, patch)
    assert "does not exist on the console" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_ac_raises_control_error_on_unsupported_power(mock_gateway):
    # Arrange
    service = AcService(gateway=mock_gateway)
    patch = AcPatchRequest(power=AcPowerControl.TOGGLE)

    # Act & Assert
    with pytest.raises(AirtouchControlError) as exc_info:
        await service.update_air_conditioner("192.168.1.15", 0, patch)
    assert "is not supported by AC" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_ac_raises_control_error_on_unsupported_mode(mock_gateway):
    # Arrange
    service = AcService(gateway=mock_gateway)
    patch = AcPatchRequest(mode=AcMode.DRY)

    # Act & Assert
    with pytest.raises(AirtouchControlError) as exc_info:
        await service.update_air_conditioner("192.168.1.15", 0, patch)
    assert "is not supported by AC" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_ac_raises_control_error_on_unsupported_fan_speed(mock_gateway):
    # Arrange
    service = AcService(gateway=mock_gateway)
    patch = AcPatchRequest(fan_speed=AcFanSpeed.TURBO)

    # Act & Assert
    with pytest.raises(AirtouchControlError) as exc_info:
        await service.update_air_conditioner("192.168.1.15", 0, patch)
    assert "is not supported by AC" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_ac_raises_control_error_on_out_of_bounds_temperature(mock_gateway):
    # Arrange
    service = AcService(gateway=mock_gateway)
    patch = AcPatchRequest(temperature=15.0)  # below min of 16.0

    # Act & Assert
    with pytest.raises(AirtouchControlError) as exc_info:
        await service.update_air_conditioner("192.168.1.15", 0, patch)
    assert "is out of bounds for AC" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_ac_raises_control_error_on_gateway_failure(mock_gateway):
    # Arrange
    mock_gateway.control_success = False
    service = AcService(gateway=mock_gateway)
    patch = AcPatchRequest(power=AcPowerControl.TURN_ON)

    # Act & Assert
    with pytest.raises(AirtouchControlError) as exc_info:
        await service.update_air_conditioner("192.168.1.15", 0, patch)
    assert "Failed to set AC" in str(exc_info.value)
