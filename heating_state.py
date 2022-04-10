from __future__ import annotations

import asyncio
import enum
import os
import time
from functools import lru_cache
from pprint import pprint
from typing import Any

import aiohttp
import gspread

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


def get_auth_header(auth_token: str) -> str:
    return {"Authorization": f"auth_token {auth_token}"}


@lru_cache(maxsize=1)
async def get_auth_token(
    email: str, password: str, session: aiohttp.ClientSession
) -> str:
    """Obtain fresh auth token."""
    auth_payload = {"user": {"email": email, "password": password}}

    async with session.post(
        f"{BASE_API_URL}/users/sign_in.json", json=auth_payload, ssl=False
    ) as response:
        return (await response.json())["access_token"]


async def get_device_map(
    auth_token: str, session: aiohttp.ClientSession
) -> dict[str, Any]:
    """Get map of device IDs to names."""
    async with session.get(
        f"{BASE_API_URL}/apiv1/devices.json",
        headers=get_auth_header(auth_token),
        ssl=False,
    ) as response:
        devices = await response.json()

    return {
        device["device"]["key"]: device["device"]["product_name"] for device in devices
    }


async def get_device_properties(
    auth_token: str, session: aiohttp.ClientSession
) -> dict[str, Any]:
    """Get map of properties for each device"""
    async with session.get(
        f"{BASE_API_URL}/apiv1/groups/62774/datapoints.json",
        headers=get_auth_header(auth_token),
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
    worksheet_suteren,
    worksheet_prizemie_chodba,
    session: aiohttp.ClientSession,
    auth_token: str,
):
    """Create new sample and append rows to worksheet."""
    device_map, device_properties = await asyncio.gather(
        *[
            get_device_map(auth_token, session),
            get_device_properties(auth_token, session),
        ]
    )

    for device in device_properties:
        name = device_map[device["id"]]
        parsed_properties = {}

        for device_property in device["properties"]["property"]:
            value = device_property["value"]

            if device_property["name"].endswith("x100") and value is not None:
                value = value / 100

            parsed_properties[device_property["name"]] = value

        temperature = device["properties"]["property"][0]["value"]
        if temperature is not None:
            temperature = temperature / 10

        running_state = device["properties"]["property"][1]["value"]
        state = "heating" if running_state else "idle"

        print(f"{name}: {temperature} {state}")
        pprint(list(parsed_properties.values()))

        if name == Devices.suteren.value:
            worksheet_suteren.append_row(list(parsed_properties.values()))
        elif name == Devices.prizemie_chodba.value:
            worksheet_prizemie_chodba.append_row(list(parsed_properties.values()))


async def main():
    service_account = gspread.service_account(
        "/Users/michalcyprian/.config/gspread//heating-state-cd26626d379f.json"
    )
    sheet = service_account.open("HistoriaKureniaLukas")
    worksheet_suteren = sheet.worksheet("T. Suteren")
    worksheet_prizemie_chodba = sheet.worksheet("0.03 Prizemie chodba")

    async with aiohttp.ClientSession(headers=BASE_HEADERS) as session:
        auth_token = await get_auth_token(EMAIL, PASSWORD, session)

        while True:
            await create_sample(
                worksheet_suteren, worksheet_prizemie_chodba, session, auth_token
            )
            time.sleep(300)


if __name__ == "__main__":
    asyncio.run(main())
