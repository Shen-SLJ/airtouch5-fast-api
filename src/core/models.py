from enum import StrEnum
from pydantic import BaseModel, Field
from typing import List, Optional

class AirtouchConnectionError(Exception):
    def __init__(self, host: str) -> None:
        super().__init__(f"Could not connect to Airtouch console at {host}")
        self.host = host


class AcPowerControl(StrEnum):
    TOGGLE = "TOGGLE"
    TURN_OFF = "TURN_OFF"
    TURN_ON = "TURN_ON"
    SET_TO_AWAY = "SET_TO_AWAY"
    SET_TO_SLEEP = "SET_TO_SLEEP"


class AcPowerState(StrEnum):
    OFF = "OFF"
    OFF_AWAY = "OFF_AWAY"
    OFF_FORCED = "OFF_FORCED"
    ON = "ON"
    ON_AWAY = "ON_AWAY"
    SLEEP = "SLEEP"


class AcMode(StrEnum):
    AUTO = "AUTO"
    HEAT = "HEAT"
    DRY = "DRY"
    FAN = "FAN"
    COOL = "COOL"


class AcFanSpeed(StrEnum):
    AUTO = "AUTO"
    QUIET = "QUIET"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    POWERFUL = "POWERFUL"
    TURBO = "TURBO"
    INTELLIGENT_AUTO = "INTELLIGENT_AUTO"


class AcSpillState(StrEnum):
    NONE = "NONE"
    SPILL = "SPILL"
    BYPASS = "BYPASS"


class ZonePowerState(StrEnum):
    OFF = "OFF"
    ON = "ON"
    TURBO = "TURBO"


class ZoneControlMethod(StrEnum):
    DAMPER = "DAMPER"
    TEMPERATURE = "TEMPERATURE"


class SensorBatteryStatus(StrEnum):
    NORMAL = "NORMAL"
    LOW = "LOW"


class DiscoveredDevice(BaseModel):
    name: str
    model: str
    id: str
    serial: str
    host: str


class ZoneStatus(BaseModel):
    zone_id: int
    name: str
    power_state: ZonePowerState
    control_method: ZoneControlMethod
    current_temperature: Optional[float] = None
    target_temperature: Optional[float] = None
    current_damper_percentage: int
    spill_active: bool
    sensor_battery_status: SensorBatteryStatus


class AcStatus(BaseModel):
    ac_id: int
    name: str
    power_state: AcPowerState
    error_info: str
    spill_state: AcSpillState
    current_temperature: float
    target_temperature: float
    active_mode: AcMode
    selected_mode: AcMode
    active_fan_speed: AcFanSpeed
    selected_fan_speed: AcFanSpeed
    zones: List[ZoneStatus]


class AirtouchStatus(BaseModel):
    model: str
    host: str
    port: int
    connected: bool
    air_conditioners: List[AcStatus]


class AcCapabilities(BaseModel):
    ac_id: int
    name: str
    min_target_temperature: float
    max_target_temperature: float
    target_temperature_resolution: float
    supported_modes: List[AcMode]
    supported_fan_speeds: List[AcFanSpeed]
    supported_power_controls: List[AcPowerControl]


class AirtouchCapabilities(BaseModel):
    model: str
    host: str
    port: int
    connected: bool
    air_conditioners: List[AcCapabilities]


class AcPowerActionResult(BaseModel):
    ac_id: int
    name: str
    power_control: AcPowerControl
    applied: bool


class AirtouchPowerResponse(BaseModel):
    model: str
    host: str
    port: int
    connected: bool
    air_conditioners: List[AcPowerActionResult]


class ActionResponse(BaseModel):
    status: str
    message: str


class DiscoveryResponse(BaseModel):
    airtouch_devices: List[DiscoveredDevice]

