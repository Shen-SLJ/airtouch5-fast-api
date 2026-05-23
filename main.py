from fastapi import APIRouter, FastAPI
import pyairtouch

PORT = 9005
MODEL = pyairtouch.AirTouchModel.AIRTOUCH_5

app = FastAPI()
router = APIRouter(prefix="/api/v1/airtouches")


def serialize_enum(value):
    if hasattr(value, "name"):
        return value.name
    return str(value)


@app.get("/health")
def get_health():
    return {"status": "ok"}


@router.post("/{host}/start")
async def start_airtouch(host: str):
    airtouch = pyairtouch.connect(model=MODEL, host=host, port=PORT)
    connected = await airtouch.init()
    power_control = pyairtouch.AcPowerControl.TURN_ON

    air_conditioners = []
    if connected:
        for ac in airtouch.air_conditioners:
            supported = power_control in ac.supported_power_controls
            if supported:
                await ac.set_power(power_control)
            air_conditioners.append(
                {
                    "ac_id": ac.ac_id,
                    "name": ac.name,
                    "power_control": serialize_enum(power_control),
                    "applied": supported,
                }
            )

    return {
        "model": str(airtouch.model),
        "host": airtouch.host,
        "port": PORT,
        "connected": connected,
        "air_conditioners": air_conditioners,
    }


@router.post("/{host}/stop")
async def stop_airtouch(host: str):
    airtouch = pyairtouch.connect(model=MODEL, host=host, port=PORT)
    connected = await airtouch.init()
    power_control = pyairtouch.AcPowerControl.TURN_OFF

    air_conditioners = []
    if connected:
        for ac in airtouch.air_conditioners:
            supported = power_control in ac.supported_power_controls
            if supported:
                await ac.set_power(power_control)
            air_conditioners.append(
                {
                    "ac_id": ac.ac_id,
                    "name": ac.name,
                    "power_control": serialize_enum(power_control),
                    "applied": supported,
                }
            )

    return {
        "model": str(airtouch.model),
        "host": airtouch.host,
        "port": PORT,
        "connected": connected,
        "air_conditioners": air_conditioners,
    }


@router.get("/{host}/status")
async def get_airtouch_status(host: str):
    airtouch = pyairtouch.connect(model=MODEL, host=host, port=PORT)
    connected = await airtouch.init()

    status_data = {
        "model": str(airtouch.model),
        "host": airtouch.host,
        "port": PORT,
        "connected": connected,
        "air_conditioners": [
            {
                "ac_id": ac.ac_id,
                "name": ac.name,
                "power_state": serialize_enum(ac.power_state),
                "error_info": serialize_enum(ac.error_info),
                "spill_state": serialize_enum(ac.spill_state),
                "current_temperature": ac.current_temperature,
                "target_temperature": ac.target_temperature,
                "active_mode": serialize_enum(ac.active_mode),
                "selected_mode": serialize_enum(ac.selected_mode),
                "active_fan_speed": serialize_enum(ac.active_fan_speed),
                "selected_fan_speed": serialize_enum(ac.selected_fan_speed),
                "zones": [
                    {
                        "name": zone.name,
                        "power_state": serialize_enum(zone.power_state),
                        "current_temperature": zone.current_temperature,
                        "target_temperature": zone.target_temperature,
                        "current_damper_percentage": zone.current_damper_percentage,
                    }
                    for zone in ac.zones
                ],
            }
            for ac in airtouch.air_conditioners
        ],
    }

    return status_data


@router.get("/{host}/capabilities")
async def get_airtouch_capabilities(host: str):
    airtouch = pyairtouch.connect(model=MODEL, host=host, port=PORT)
    connected = await airtouch.init()

    capabilities_data = {
        "model": str(airtouch.model),
        "host": airtouch.host,
        "port": PORT,
        "connected": connected,
        "air_conditioners": [
            {
                "ac_id": ac.ac_id,
                "name": ac.name,
                "min_target_temperature": ac.min_target_temperature,
                "max_target_temperature": ac.max_target_temperature,
                "target_temperature_resolution": ac.target_temperature_resolution,
                "supported_modes": [serialize_enum(m) for m in ac.supported_modes],
                "supported_fan_speeds": [serialize_enum(f) for f in ac.supported_fan_speeds],
                "supported_power_controls": [serialize_enum(p) for p in ac.supported_power_controls],
            }
            for ac in airtouch.air_conditioners
        ]
    }
    return capabilities_data


@router.get("")
async def get_airtouches():
    discovered_airtouches = await pyairtouch.discover()

    airtouch_info_list = {
        "airtouch_devices": [
            {
                "name": airtouch.name,
                "model": airtouch.model,
                "id": airtouch.airtouch_id,
                "serial": airtouch.serial,
                "host": airtouch.host,
            }
            for airtouch in discovered_airtouches
        ]
    }

    return airtouch_info_list


app.include_router(router)