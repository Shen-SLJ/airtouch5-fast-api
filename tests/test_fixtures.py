import pytest
from typing import List
from src.core.gateway import IAirtouchGateway
from src.core.models import (
    AirtouchConnectionError,
    DiscoveredDevice,
    AirtouchStatus,
    AirtouchCapabilities,
    AcStatus,
    ZoneStatus,
    AcCapabilities,
    AcPowerControl,
    AcPowerState,
    AcMode,
    AcFanSpeed,
    AcSpillState,
    ZonePowerState,
    ZoneControlMethod,
    SensorBatteryStatus,
    AcPowerActionResult,
)

class MockAirtouchGateway(IAirtouchGateway):
    """In-memory mock implementation of IAirtouchGateway for zero-overhead unit testing."""
    def __init__(self) -> None:
        self.calls = []
        self.connected_val = True
        
        self.devices_val = [
            DiscoveredDevice(
                name="Test AirTouch 5",
                model="AIRTOUCH_5",
                id="at5_9876",
                serial="98765432",
                device_handle="192.168.1.15",
            )
        ]
        
        self.status_val = AirtouchStatus(
            model="AIRTOUCH_5",
            device_handle="192.168.1.15",
            port=9005,
            connected=True,
            air_conditioners=[
                AcStatus(
                    ac_id=0,
                    name="Living AC",
                    power_state=AcPowerState.OFF,
                    error_info="OK",
                    spill_state=AcSpillState.NONE,
                    current_temperature=22.5,
                    target_temperature=24.0,
                    active_mode=AcMode.COOL,
                    selected_mode=AcMode.COOL,
                    active_fan_speed=AcFanSpeed.LOW,
                    selected_fan_speed=AcFanSpeed.LOW,
                    zones=[
                        ZoneStatus(
                            zone_id=1,
                            name="Master Bed",
                            power_state=ZonePowerState.OFF,
                            control_method=ZoneControlMethod.TEMPERATURE,
                            current_temperature=21.0,
                            target_temperature=23.0,
                            current_damper_percentage=100,
                            spill_active=False,
                            sensor_battery_status=SensorBatteryStatus.NORMAL,
                        ),
                        ZoneStatus(
                            zone_id=2,
                            name="Kitchen",
                            power_state=ZonePowerState.OFF,
                            control_method=ZoneControlMethod.DAMPER,
                            current_temperature=None,
                            target_temperature=None,
                            current_damper_percentage=50,
                            spill_active=False,
                            sensor_battery_status=SensorBatteryStatus.NORMAL,
                        )
                    ]
                )
            ]
        )
        
        self.capabilities_val = AirtouchCapabilities(
            model="AIRTOUCH_5",
            device_handle="192.168.1.15",
            port=9005,
            connected=True,
            air_conditioners=[
                AcCapabilities(
                    ac_id=0,
                    name="Living AC",
                    min_target_temperature=16.0,
                    max_target_temperature=32.0,
                    target_temperature_resolution=0.5,
                    supported_modes=[AcMode.COOL, AcMode.HEAT, AcMode.FAN],
                    supported_fan_speeds=[AcFanSpeed.LOW, AcFanSpeed.MEDIUM, AcFanSpeed.HIGH],
                    supported_power_controls=[AcPowerControl.TURN_ON, AcPowerControl.TURN_OFF],
                )
            ]
        )
        
        self.control_success = True

    async def discover_devices(self) -> List[DiscoveredDevice]:
        self.calls.append(("discover_devices", {}))
        return self.devices_val

    async def get_status(self, device_handle: str) -> AirtouchStatus:
        self.calls.append(("get_status", {"device_handle": device_handle}))
        if not self.connected_val:
            raise AirtouchConnectionError(device_handle)
        
        status_copy = self.status_val.model_copy(deep=True)
        status_copy.connected = self.connected_val
        status_copy.device_handle = device_handle
        return status_copy

    async def get_capabilities(self, device_handle: str) -> AirtouchCapabilities:
        self.calls.append(("get_capabilities", {"device_handle": device_handle}))
        if not self.connected_val:
            raise AirtouchConnectionError(device_handle)
        
        capabilities_copy = self.capabilities_val.model_copy(deep=True)
        capabilities_copy.connected = self.connected_val
        capabilities_copy.device_handle = device_handle
        return capabilities_copy

    async def set_ac_power(self, device_handle: str, air_conditioner_id: int, power_control: AcPowerControl) -> bool:
        self.calls.append(("set_ac_power", {"device_handle": device_handle, "air_conditioner_id": air_conditioner_id, "power_control": power_control}))
        return self.control_success

    async def set_all_ac_power(self, device_handle: str, power_control: AcPowerControl) -> List[AcPowerActionResult]:
        self.calls.append(("set_all_ac_power", {"device_handle": device_handle, "power_control": power_control}))
        if not self.connected_val:
            raise AirtouchConnectionError(device_handle)
        
        return [
            AcPowerActionResult(
                ac_id=air_conditioner.ac_id,
                name=air_conditioner.name,
                power_control=power_control,
                applied=self.control_success,
            )
            for air_conditioner in self.status_val.air_conditioners
        ]

    async def set_ac_mode(self, device_handle: str, air_conditioner_id: int, mode: AcMode) -> bool:
        self.calls.append(("set_ac_mode", {"device_handle": device_handle, "air_conditioner_id": air_conditioner_id, "mode": mode}))
        return self.control_success

    async def set_ac_fan_speed(self, device_handle: str, air_conditioner_id: int, fan_speed: AcFanSpeed) -> bool:
        self.calls.append(("set_ac_fan_speed", {"device_handle": device_handle, "air_conditioner_id": air_conditioner_id, "fan_speed": fan_speed}))
        return self.control_success

    async def set_ac_temp(self, device_handle: str, air_conditioner_id: int, temperature: float) -> bool:
        self.calls.append(("set_ac_temp", {"device_handle": device_handle, "air_conditioner_id": air_conditioner_id, "temperature": temperature}))
        return self.control_success

    async def set_zone_power(self, device_handle: str, air_conditioner_id: int, zone_id: int, power_state: ZonePowerState) -> bool:
        self.calls.append(("set_zone_power", {"device_handle": device_handle, "air_conditioner_id": air_conditioner_id, "zone_id": zone_id, "power_state": power_state}))
        return self.control_success

    async def set_zone_temp(self, device_handle: str, air_conditioner_id: int, zone_id: int, temperature: float) -> bool:
        self.calls.append(("set_zone_temp", {"device_handle": device_handle, "air_conditioner_id": air_conditioner_id, "zone_id": zone_id, "temperature": temperature}))
        return self.control_success

    async def set_zone_damper(self, device_handle: str, air_conditioner_id: int, zone_id: int, damper_percentage: int) -> bool:
        self.calls.append(("set_zone_damper", {"device_handle": device_handle, "air_conditioner_id": air_conditioner_id, "zone_id": zone_id, "damper_percentage": damper_percentage}))
        return self.control_success

    async def close_connection(self) -> None:
        self.calls.append(("close_connection", {}))


@pytest.fixture
def mock_gateway() -> MockAirtouchGateway:
    return MockAirtouchGateway()
