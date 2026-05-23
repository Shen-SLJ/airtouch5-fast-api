import pyairtouch
from typing import List, Optional, Type, TypeVar
from enum import Enum

from src.core.gateway.base import AirtouchGateway
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

PORT = 9005
MODEL = pyairtouch.AirTouchModel.AIRTOUCH_5

EnumType = TypeVar("EnumType", bound=Enum)


class PyAirtouchGateway(AirtouchGateway):
    def __init__(self) -> None:
        self._airtouch_instance: Optional[pyairtouch.AirTouch] = None

    def _map_enum(
        self, source_enum: Optional[Enum], target_class: Type[EnumType]
    ) -> EnumType:
        if source_enum is None:
            return list(target_class)[0]

        enum_name = getattr(source_enum, "name", str(source_enum))
        try:
            return target_class(enum_name)
        except ValueError:
            return list(target_class)[0]

    def _map_discovered_device(
        self, discovered_device: pyairtouch.DiscoveredAirTouch
    ) -> DiscoveredDevice:
        return DiscoveredDevice(
            name=discovered_device.name,
            model=str(
                discovered_device.model.name
                if hasattr(discovered_device.model, "name")
                else discovered_device.model
            ),
            id=str(discovered_device.airtouch_id),
            serial=discovered_device.serial,
            host=discovered_device.host,
        )

    def _map_zone_status(self, zone: pyairtouch.Zone) -> ZoneStatus:
        return ZoneStatus(
            zone_id=zone.zone_id,
            name=zone.name,
            power_state=self._map_enum(zone.power_state, ZonePowerState),
            control_method=self._map_enum(zone.control_method, ZoneControlMethod),
            current_temperature=zone.current_temperature,
            target_temperature=zone.target_temperature,
            current_damper_percentage=zone.current_damper_percentage,
            spill_active=zone.spill_active,
            sensor_battery_status=self._map_enum(
                zone.sensor_battery_status, SensorBatteryStatus
            ),
        )

    def _map_air_conditioner_status(
        self, air_conditioner: pyairtouch.AirConditioner
    ) -> AcStatus:
        zone_statuses = [self._map_zone_status(zone) for zone in air_conditioner.zones]

        return AcStatus(
            ac_id=air_conditioner.ac_id,
            name=air_conditioner.name,
            power_state=self._map_enum(air_conditioner.power_state, AcPowerState),
            error_info=str(
                air_conditioner.error_info.name
                if hasattr(air_conditioner.error_info, "name")
                else air_conditioner.error_info
            ),
            spill_state=self._map_enum(air_conditioner.spill_state, AcSpillState),
            current_temperature=air_conditioner.current_temperature,
            target_temperature=air_conditioner.target_temperature,
            active_mode=self._map_enum(air_conditioner.active_mode, AcMode),
            selected_mode=self._map_enum(air_conditioner.selected_mode, AcMode),
            active_fan_speed=self._map_enum(
                air_conditioner.active_fan_speed, AcFanSpeed
            ),
            selected_fan_speed=self._map_enum(
                air_conditioner.selected_fan_speed, AcFanSpeed
            ),
            zones=zone_statuses,
        )

    def _map_air_conditioner_capabilities(
        self, air_conditioner: pyairtouch.AirConditioner
    ) -> AcCapabilities:
        return AcCapabilities(
            ac_id=air_conditioner.ac_id,
            name=air_conditioner.name,
            min_target_temperature=air_conditioner.min_target_temperature,
            max_target_temperature=air_conditioner.max_target_temperature,
            target_temperature_resolution=air_conditioner.target_temperature_resolution,
            supported_modes=[
                self._map_enum(mode, AcMode) for mode in air_conditioner.supported_modes
            ],
            supported_fan_speeds=[
                self._map_enum(fan_speed, AcFanSpeed)
                for fan_speed in air_conditioner.supported_fan_speeds
            ],
            supported_power_controls=[
                self._map_enum(power_control, AcPowerControl)
                for power_control in air_conditioner.supported_power_controls
            ],
        )

    async def _get_connection(self, host: str) -> pyairtouch.AirTouch:
        if self._airtouch_instance is not None:
            if (
                self._airtouch_instance.initialised
                and self._airtouch_instance.host == host
            ):
                return self._airtouch_instance

        airtouch_instance = pyairtouch.connect(model=MODEL, host=host, port=PORT)
        is_connected = await airtouch_instance.init()
        if not is_connected:
            raise AirtouchConnectionError(host)

        self._airtouch_instance = airtouch_instance

        return airtouch_instance

    async def _get_air_conditioner(
        self, host: str, air_conditioner_id: int
    ) -> Optional[pyairtouch.AirConditioner]:
        airtouch_instance = await self._get_connection(host)

        for air_conditioner in airtouch_instance.air_conditioners:
            if air_conditioner.ac_id == air_conditioner_id:
                return air_conditioner

        return None

    async def _get_zone(
        self, host: str, air_conditioner_id: int, zone_id: int
    ) -> Optional[pyairtouch.Zone]:
        air_conditioner = await self._get_air_conditioner(host, air_conditioner_id)
        if air_conditioner is None:
            return None

        for zone in air_conditioner.zones:
            if zone.zone_id == zone_id:
                return zone

        return None

    async def close_connection(self) -> None:
        if self._airtouch_instance is not None:
            await self._airtouch_instance.shutdown()
            self._airtouch_instance = None

    async def discover_devices(self) -> List[DiscoveredDevice]:
        devices = await pyairtouch.discover()

        return [
            self._map_discovered_device(discovered_device)
            for discovered_device in devices
        ]

    async def get_status(self, host: str) -> AirtouchStatus:
        airtouch_instance = await self._get_connection(host)

        air_conditioner_statuses = [
            self._map_air_conditioner_status(air_conditioner)
            for air_conditioner in airtouch_instance.air_conditioners
        ]

        return AirtouchStatus(
            model=str(
                airtouch_instance.model.name
                if hasattr(airtouch_instance.model, "name")
                else airtouch_instance.model
            ),
            host=airtouch_instance.host,
            port=PORT,
            connected=True,
            air_conditioners=air_conditioner_statuses,
        )

    async def get_capabilities(self, host: str) -> AirtouchCapabilities:
        airtouch_instance = await self._get_connection(host)

        air_conditioner_capabilities = [
            self._map_air_conditioner_capabilities(air_conditioner)
            for air_conditioner in airtouch_instance.air_conditioners
        ]

        return AirtouchCapabilities(
            model=str(
                airtouch_instance.model.name
                if hasattr(airtouch_instance.model, "name")
                else airtouch_instance.model
            ),
            host=airtouch_instance.host,
            port=PORT,
            connected=True,
            air_conditioners=air_conditioner_capabilities,
        )

    async def set_ac_power(
        self, host: str, air_conditioner_id: int, power_control: AcPowerControl
    ) -> bool:
        air_conditioner = await self._get_air_conditioner(host, air_conditioner_id)
        if air_conditioner is None:
            return False

        pyairtouch_power = getattr(pyairtouch.AcPowerControl, power_control.name)
        if pyairtouch_power in air_conditioner.supported_power_controls:
            await air_conditioner.set_power(pyairtouch_power)
            return True

        return False

    async def set_all_ac_power(
        self, host: str, power_control: AcPowerControl
    ) -> List[AcPowerActionResult]:
        airtouch_instance = await self._get_connection(host)
        action_results = []

        pyairtouch_power = getattr(pyairtouch.AcPowerControl, power_control.name)
        for air_conditioner in airtouch_instance.air_conditioners:
            is_supported = pyairtouch_power in air_conditioner.supported_power_controls
            if is_supported:
                await air_conditioner.set_power(pyairtouch_power)
            action_results.append(
                AcPowerActionResult(
                    ac_id=air_conditioner.ac_id,
                    name=air_conditioner.name,
                    power_control=power_control,
                    applied=is_supported,
                )
            )

        return action_results

    async def set_ac_mode(
        self, host: str, air_conditioner_id: int, mode: AcMode
    ) -> bool:
        air_conditioner = await self._get_air_conditioner(host, air_conditioner_id)
        if air_conditioner is None:
            return False

        pyairtouch_mode = getattr(pyairtouch.AcMode, mode.name)
        if pyairtouch_mode in air_conditioner.supported_modes:
            await air_conditioner.set_mode(pyairtouch_mode)
            return True

        return False

    async def set_ac_fan_speed(
        self, host: str, air_conditioner_id: int, fan_speed: AcFanSpeed
    ) -> bool:
        air_conditioner = await self._get_air_conditioner(host, air_conditioner_id)
        if air_conditioner is None:
            return False

        pyairtouch_fan = getattr(pyairtouch.AcFanSpeed, fan_speed.name)
        if pyairtouch_fan in air_conditioner.supported_fan_speeds:
            await air_conditioner.set_fan_speed(pyairtouch_fan)
            return True

        return False

    async def set_ac_temp(
        self, host: str, air_conditioner_id: int, temperature: float
    ) -> bool:
        air_conditioner = await self._get_air_conditioner(host, air_conditioner_id)
        if air_conditioner is None:
            return False

        if (
            air_conditioner.min_target_temperature
            <= temperature
            <= air_conditioner.max_target_temperature
        ):
            await air_conditioner.set_target_temperature(temperature)
            return True

        return False

    async def set_zone_power(
        self,
        host: str,
        air_conditioner_id: int,
        zone_id: int,
        power_state: ZonePowerState,
    ) -> bool:
        zone = await self._get_zone(host, air_conditioner_id, zone_id)
        if zone is None:
            return False

        pyairtouch_power = getattr(pyairtouch.ZonePowerState, power_state.name)
        if pyairtouch_power in zone.supported_power_states:
            await zone.set_power(pyairtouch_power)
            return True

        return False

    async def set_zone_temp(
        self, host: str, air_conditioner_id: int, zone_id: int, temperature: float
    ) -> bool:
        zone = await self._get_zone(host, air_conditioner_id, zone_id)
        if zone is None:
            return False

        if zone.control_method == pyairtouch.ZoneControlMethod.TEMPERATURE:
            await zone.set_target_temperature(temperature)
            return True

        return False

    async def set_zone_damper(
        self, host: str, air_conditioner_id: int, zone_id: int, damper_percentage: int
    ) -> bool:
        zone = await self._get_zone(host, air_conditioner_id, zone_id)
        if zone is None:
            return False

        if 0 <= damper_percentage <= 100:
            await zone.set_damper_percentage(damper_percentage)
            return True

        return False
