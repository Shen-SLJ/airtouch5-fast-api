from typing import List
from pydantic import BaseModel

from src.core.models import DiscoveredDevice


class DiscoveryResponse(BaseModel):
    """List of all discovered AirTouch devices on the local network."""
    airtouch_devices: List[DiscoveredDevice]
