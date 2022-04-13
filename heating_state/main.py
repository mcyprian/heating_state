from __future__ import annotations

import asyncio
import enum
import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pprint import pprint
from typing import Any

import aiohttp
import gspread

from fastapi import FastAPI


BASE_API_URL = "https://eu.salusconnect.io"
BASE_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Heating state history script (Lukas Skala)",
}

EMAIL = "skala.lukas@gmail.com"
PASSWORD = os.environ["SALUS_PASSWORD"]

class Devices(enum.Enum):
    prizemie_chodba = "0.03 Prízemie chodba"
    suteren = "T. Suterén"


ACTIVE_DEVICES = (Devices.suteren.value, Devices.prizemie_chodba.value)


class DeviceProperties(enum.Enum):
    temperature = "ep_9:sIT600TH:LocalTemperature_x100"
    running_state = "ep_9:sIT600TH:RunningState"

    cloudy_setpoint = "ep_9:sIT600TH:CloudySetpoint_x100"
    sunny_setpoint = "ep_9:sIT600TH:SunnySetpoint_x100"
    cooling_control = "ep_9:sIT600TH:CoolingControl"
    heating_control = "ep_9:sIT600TH:HeatingControl"
    hold_type = "ep_9:sIT600TH:HoldType"
    sensor_probe = "ep_9:sIT600TH:OUTSensorProbe"
    schedule_type = "ep_9:sIT600TH:ScheduleType"
    running_mode = "ep_9:sIT600TH:RunningMode"
    system_mode = "ep_9:sIT600TH:SystemMode"
    leave_network = "ep_9:sZDO:LeaveNetwork"
    online_status = "ep_9:sZDOInfo:OnlineStatus_i"


@dataclass
class DeviceStateWriter:
    name: str
    worksheet: gspread.worksheet.Worksheet
    parsed_properties: dict[str, Any] | None = None

    def add_property(self, name, value):
        if self.parsed_properties is None:
            self.parsed_properties = {name: value}
        else:
            self.parsed_properties[name] = value

    def create_sample(self):
        self.worksheet.append_row(list(self.parsed_properties.values()))


def get_auth_header(auth_token: str) -> str:
    return {"Authorization": f"auth_token {auth_token}"}


@lru_cache(maxsize=1)
async def get_auth_token(
    email: str,
    password: str,
) -> str:
    """Obtain fresh auth token."""
    async with aiohttp.ClientSession(headers=BASE_HEADERS) as session:
        auth_payload = {"user": {"email": email, "password": password}}

        async with session.post(
            f"{BASE_API_URL}/users/sign_in.json", json=auth_payload, ssl=False
        ) as response:
            return (await response.json())["access_token"]


async def get_device_map(session: aiohttp.ClientSession) -> dict[str, Any]:
    """Get map of device IDs to names."""
    async with session.get(
        f"{BASE_API_URL}/apiv1/devices.json",
        ssl=False,
    ) as response:
        devices = await response.json()

    return {
        device["device"]["key"]: device["device"]["product_name"] for device in devices
    }


async def get_device_properties(session: aiohttp.ClientSession) -> dict[str, Any]:
    """Get map of properties for each device"""
    async with session.get(
        f"{BASE_API_URL}/apiv1/groups/62774/datapoints.json",
        params=[
            ("property_names[]", DeviceProperties.temperature.value),
            ("property_names[]", DeviceProperties.running_state.value),
            ("property_names[]", DeviceProperties.cloudy_setpoint.value),
            ("property_names[]", DeviceProperties.sunny_setpoint.value),
            ("property_names[]", DeviceProperties.cooling_control.value),
            ("property_names[]", DeviceProperties.heating_control.value),
            ("property_names[]", DeviceProperties.hold_type.value),
            ("property_names[]", DeviceProperties.sensor_probe.value),
            ("property_names[]", DeviceProperties.schedule_type.value),
            ("property_names[]", DeviceProperties.running_mode.value),
            ("property_names[]", DeviceProperties.system_mode.value),
            ("property_names[]", DeviceProperties.leave_network.value),
            ("property_names[]", DeviceProperties.online_status.value),
        ],
        ssl=False,
    ) as response:
        return (await response.json())["datapoints"]["devices"]["device"]


async def create_sample(
    device_writers: dict[str, DeviceStateWriter],
    auth_token: str,
):
    """Create new sample and append rows to worksheet."""
    async with aiohttp.ClientSession(
        headers={**BASE_HEADERS, **get_auth_header(auth_token)}
    ) as session:
        device_map, device_properties = await asyncio.gather(
            *[
                get_device_map(session),
                get_device_properties(session),
            ]
        )

    for device in device_properties:
        name = device_map[device["id"]]
        device_writer = device_writers.get(name)

        if device_writer is None:
            continue

        for device_property in device["properties"]["property"]:
            value = device_property["value"]

            if device_property["name"].endswith("x100") and value is not None:
                value = value / 100

            device_writer.add_property(device_property["name"], value)

        pprint(list(device_writer.parsed_properties.values()))

        device_writer.create_sample()


app = FastAPI()


@app.get("/")
async def root():
    # gspread_credentials = json.loads(os.environ["GSPREAD_SA"])

    with open(
        "/Users/michalcyprian/.config/gspread/heating-state-cd26626d379f.json"
    ) as creds_fi:
        gspread_credentials = json.loads(creds_fi.read())

    service_account = gspread.service_account_from_dict(gspread_credentials)

    sheet = service_account.open("HistoriaKureniaLukas")

    devices = {
        device_name: DeviceStateWriter(device_name, sheet.worksheet(device_name))
        for device_name in ACTIVE_DEVICES
    }

    auth_token = await get_auth_token(EMAIL, PASSWORD)

    try:
        await create_sample(devices, auth_token)
        return {"status": "ok", "message": "sample created"}
    except Exception as exc:
        return {"status": "error", "message": f"ERROR: {type(exc)} {exc}"}
