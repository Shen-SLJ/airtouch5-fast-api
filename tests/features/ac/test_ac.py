import pytest
from fastapi import HTTPException, status
from src.features.ac.router import (
    start_airtouch,
    stop_airtouch,
    get_airtouch_status,
    get_airtouch_capabilities,
    set_ac_power,
    set_ac_mode,
    set_ac_fan_speed,
    set_ac_temp,
    AcPowerRequest,
    AcModeRequest,
    AcFanSpeedRequest,
    AcTempRequest,
)
from src.core.models import AcPowerControl, AcMode, AcFanSpeed, AirtouchConnectionError


@pytest.mark.asyncio
async def test_start_airtouch_success(mock_gateway):
    # Arrange

    # Act
    result = await start_airtouch(host="192.168.1.15", gateway=mock_gateway)

    # Assert
    assert result.host == "192.168.1.15"
    assert result.connected is True
    assert len(result.air_conditioners) == 1
    assert result.air_conditioners[0].ac_id == 0
    assert result.air_conditioners[0].power_control == AcPowerControl.TURN_ON
    assert result.air_conditioners[0].applied is True

    assert (
        "set_all_ac_power",
        {"host": "192.168.1.15", "power_control": AcPowerControl.TURN_ON},
    ) in mock_gateway.calls
    assert ("get_status", {"host": "192.168.1.15"}) in mock_gateway.calls


@pytest.mark.asyncio
async def test_start_airtouch_raises_connection_error_when_gateway_disconnected(mock_gateway):
    # Arrange
    mock_gateway.connected_val = False

    # Act
    with pytest.raises(AirtouchConnectionError) as exception_info:
        await start_airtouch(host="192.168.1.15", gateway=mock_gateway)

    # Assert
    assert "Could not connect to Airtouch" in str(exception_info.value)


@pytest.mark.asyncio
async def test_stop_airtouch_success(mock_gateway):
    # Arrange

    # Act
    result = await stop_airtouch(host="192.168.1.15", gateway=mock_gateway)

    # Assert
    assert result.host == "192.168.1.15"
    assert result.air_conditioners[0].power_control == AcPowerControl.TURN_OFF
    assert (
        "set_all_ac_power",
        {"host": "192.168.1.15", "power_control": AcPowerControl.TURN_OFF},
    ) in mock_gateway.calls


@pytest.mark.asyncio
async def test_get_airtouch_status_success(mock_gateway):
    # Arrange

    # Act
    result = await get_airtouch_status(host="192.168.1.15", gateway=mock_gateway)

    # Assert
    assert result.connected is True
    assert len(result.air_conditioners) == 1
    assert result.air_conditioners[0].name == "Living AC"
    assert len(result.air_conditioners[0].zones) == 2
    assert ("get_status", {"host": "192.168.1.15"}) in mock_gateway.calls


@pytest.mark.asyncio
async def test_get_status_raises_connection_error_when_gateway_disconnected(mock_gateway):
    # Arrange
    mock_gateway.connected_val = False

    # Act
    with pytest.raises(AirtouchConnectionError) as exception_info:
        await get_airtouch_status(host="192.168.1.15", gateway=mock_gateway)

    # Assert
    assert "Could not connect to Airtouch" in str(exception_info.value)


@pytest.mark.asyncio
async def test_get_airtouch_capabilities_success(mock_gateway):
    # Arrange

    # Act
    result = await get_airtouch_capabilities(host="192.168.1.15", gateway=mock_gateway)

    # Assert
    assert result.connected is True
    assert result.air_conditioners[0].min_target_temperature == 16.0
    assert ("get_capabilities", {"host": "192.168.1.15"}) in mock_gateway.calls


@pytest.mark.asyncio
async def test_set_ac_power_success(mock_gateway):
    # Arrange
    power_request = AcPowerRequest(power=AcPowerControl.TURN_ON)

    # Act
    result = await set_ac_power(
        host="192.168.1.15",
        air_conditioner_id=0,
        request=power_request,
        gateway=mock_gateway,
    )

    # Assert
    assert result.status == "success"
    assert result.message == "AC 0 power state set to TURN_ON"
    assert (
        "set_ac_power",
        {
            "host": "192.168.1.15",
            "air_conditioner_id": 0,
            "power_control": AcPowerControl.TURN_ON,
        },
    ) in mock_gateway.calls


@pytest.mark.asyncio
async def test_set_ac_power_raises_http_exception_on_gateway_failure(mock_gateway):
    # Arrange
    mock_gateway.control_success = False
    power_request = AcPowerRequest(power=AcPowerControl.TURN_ON)

    # Act
    with pytest.raises(HTTPException) as exception_info:
        await set_ac_power(
            host="192.168.1.15",
            air_conditioner_id=0,
            request=power_request,
            gateway=mock_gateway,
        )

    # Assert
    assert exception_info.value.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_set_ac_mode_success(mock_gateway):
    # Arrange
    mode_request = AcModeRequest(mode=AcMode.COOL)

    # Act
    result = await set_ac_mode(
        host="192.168.1.15",
        air_conditioner_id=0,
        request=mode_request,
        gateway=mock_gateway,
    )

    # Assert
    assert result.status == "success"
    assert result.message == "AC 0 mode set to COOL"
    assert (
        "set_ac_mode",
        {"host": "192.168.1.15", "air_conditioner_id": 0, "mode": AcMode.COOL},
    ) in mock_gateway.calls


@pytest.mark.asyncio
async def test_set_ac_fan_speed_success(mock_gateway):
    # Arrange
    fan_speed_request = AcFanSpeedRequest(fan_speed=AcFanSpeed.HIGH)

    # Act
    result = await set_ac_fan_speed(
        host="192.168.1.15",
        air_conditioner_id=0,
        request=fan_speed_request,
        gateway=mock_gateway,
    )

    # Assert
    assert result.status == "success"
    assert result.message == "AC 0 fan speed set to HIGH"
    assert (
        "set_ac_fan_speed",
        {"host": "192.168.1.15", "air_conditioner_id": 0, "fan_speed": AcFanSpeed.HIGH},
    ) in mock_gateway.calls


@pytest.mark.asyncio
async def test_set_ac_temp_success(mock_gateway):
    # Arrange
    temp_request = AcTempRequest(temperature=24.0)

    # Act
    result = await set_ac_temp(
        host="192.168.1.15",
        air_conditioner_id=0,
        request=temp_request,
        gateway=mock_gateway,
    )

    # Assert
    assert result.status == "success"
    assert result.message == "AC 0 temperature set to 24.0"
    assert (
        "set_ac_temp",
        {"host": "192.168.1.15", "air_conditioner_id": 0, "temperature": 24.0},
    ) in mock_gateway.calls
