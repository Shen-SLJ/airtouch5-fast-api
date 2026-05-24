from enum import StrEnum
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator

from src.core.models import (
    AcPowerControl,
    AcMode,
    AcFanSpeed,
    AcPowerActionResult,
)


class AcField(StrEnum):
    """Updatable fields on an Air Conditioner unit."""
    POWER = "power"
    MODE = "mode"
    FAN_SPEED = "fan_speed"
    TEMPERATURE = "temperature"


class AcPatchRequest(BaseModel):
    """Domain model for a sparse Air Conditioner update.

    All fields are optional — only fields present are applied by the service.
    At least one field must be provided.
    """

    power: Optional[AcPowerControl] = None
    mode: Optional[AcMode] = None
    fan_speed: Optional[AcFanSpeed] = None
    temperature: Optional[float] = Field(None, description="Target temperature value.")

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "AcPatchRequest":
        if all(
            v is None for v in [self.power, self.mode, self.fan_speed, self.temperature]
        ):
            raise ValueError(
                "At least one field must be provided: power, mode, fan_speed, temperature."
            )
        return self


class AirtouchPowerResponse(BaseModel):
    """Response for a bulk power control operation across all AC units on a console."""
    model: str
    device_handle: str
    port: int
    connected: bool
    air_conditioners: List[AcPowerActionResult]
