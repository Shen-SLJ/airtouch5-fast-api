from fastapi import FastAPI
import pyairtouch

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/airtouch/list")
async def read_airtouch_list():
    discovered_airtouches = await pyairtouch.discover()

    return_body = {
        "airtouch_devices": [{
            "name": airtouch.name,
            "model": airtouch.model,
            "id": airtouch.airtouch_id,
            "host": airtouch.host
        } for airtouch in discovered_airtouches]
    }

    return return_body