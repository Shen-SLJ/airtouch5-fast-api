from enum import StrEnum
from pydantic import BaseModel, Field
from typing import List, Optional

class AirtouchConnectionError(Exception):
    """Exception raised when connection to the AirTouch console fails."""
    def __init__(self, host: str) -> None:
        super().__init__(f"Could not connect to Airtouch console at {host}")
        self.host = host


class AcPowerControl(StrEnum):
    """Supported control commands for Air Conditioner power states."""
    TOGGLE = "TOGGLE"
    TURN_OFF = "TURN_OFF"
    TURN_ON = "TURN_ON"
    SET_TO_AWAY = "SET_TO_AWAY"
    SET_TO_SLEEP = "SET_TO_SLEEP"


class AcPowerState(StrEnum):
    """Possible runtime power states of an Air Conditioner unit."""
    OFF = "OFF"
    OFF_AWAY = "OFF_AWAY"
    OFF_FORCED = "OFF_FORCED"
    ON = "ON"
    ON_AWAY = "ON_AWAY"
    SLEEP = "SLEEP"


class AcMode(StrEnum):
    """Supported operational modes for an Air Conditioner unit."""
    AUTO = "AUTO"
    HEAT = "HEAT"
    DRY = "DRY"
    FAN = "FAN"
    COOL = "COOL"


class AcFanSpeed(StrEnum):
    """Supported fan speed settings for an Air Conditioner unit."""
    AUTO = "AUTO"
    QUIET = "QUIET"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    POWERFUL = "POWERFUL"
    TURBO = "TURBO"
    INTELLIGENT_AUTO = "INTELLIGENT_AUTO"


class AcSpillState(StrEnum):
    """Spill or bypass status for Air Conditioner zones."""
    NONE = "NONE"
    SPILL = "SPILL"
    BYPASS = "BYPASS"


class ZonePowerState(StrEnum):
    """Supported power and control states for a specific zone."""
    OFF = "OFF"
    ON = "ON"
    TURBO = "TURBO"


class ZoneControlMethod(StrEnum):
    """Supported control methods (damper vs temperature) for a zone."""
    DAMPER = "DAMPER"
    TEMPERATURE = "TEMPERATURE"


class SensorBatteryStatus(StrEnum):
    """Battery charge status of zone-assigned wireless sensors."""
    NORMAL = "NORMAL"
    LOW = "LOW"


class DiscoveredDevice(BaseModel):
    """Details of an AirTouch console discovered on the local network."""
    name: str
    model: str
    id: str
    serial: str
    host: str


class ZoneStatus(BaseModel):
    """Comprehensive runtime status of a single zone."""
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
    """Detailed runtime status of a single Air Conditioner unit, including its zones."""
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
    """Overall status response for an AirTouch console, containing all AC units."""
    model: str
    host: str
    port: int
    connected: bool
    air_conditioners: List[AcStatus]


class AcCapabilities(BaseModel):
    """Hardware capabilities and supported controls of a single Air Conditioner unit."""
    ac_id: int
    name: str
    min_target_temperature: float
    max_target_temperature: float
    target_temperature_resolution: float
    supported_modes: List[AcMode]
    supported_fan_speeds: List[AcFanSpeed]
    supported_power_controls: List[AcPowerControl]


class AirtouchCapabilities(BaseModel):
    """Overall capabilities response for an AirTouch console and its AC units."""
    model: str
    host: str
    port: int
    connected: bool
    air_conditioners: List[AcCapabilities]


class AcPowerActionResult(BaseModel):
    """Result details of a power state control request on a single AC unit."""
    ac_id: int
    name: str
    power_control: AcPowerControl
    applied: bool


class AirtouchPowerResponse(BaseModel):
    """Overall response for bulk AirTouch console power control operations."""
    model: str
    host: str
    port: int
    connected: bool
    air_conditioners: List[AcPowerActionResult]


class ActionResponse(BaseModel):
    """Generic status and message response for control operations."""
    status: str
    message: str


class DiscoveryResponse(BaseModel):
    """List of all discovered AirTouch devices on the local network."""
    airtouch_devices: List[DiscoveredDevice]


class SystemHealthResponse(BaseModel):
    """Health check response containing application runtime status."""
    status: str
