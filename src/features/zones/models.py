from enum import StrEnum
from typing import Optional
from pydantic import BaseModel, Field, model_validator

from src.core.models import ZonePowerState


class ZoneField(StrEnum):
    """Updatable fields on a Zone."""
    POWER = "power"
    TEMPERATURE = "temperature"
    DAMPER_PERCENTAGE = "damper_percentage"


class ZonePatchRequest(BaseModel):
    """Domain model for a sparse Zone update.

    All fields are optional — only fields present are applied by the service.
    At least one field must be provided.
    """

    power: Optional[ZonePowerState] = None
    temperature: Optional[float] = Field(None, description="Target temperature for the zone.")
    damper_percentage: Optional[int] = Field(
        None, ge=0, le=100, description="Damper opening percentage (0-100)."
    )

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "ZonePatchRequest":
        if all(
            v is None for v in [self.power, self.temperature, self.damper_percentage]
        ):
            raise ValueError(
                "At least one field must be provided: power, temperature, damper_percentage."
            )
        return self
