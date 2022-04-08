from __future__ import annotations

import asyncio
import enum
import os
from functools import lru_cache
from typing import Any

import aiohttp

BASE_API_URL = "https://eu.salusconnect.io"
BASE_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Heating state history script (Lukas Skala)",
}

EMAIL = "skala.lukas@gmail.com"
PASSWORD = os.environ["SALUS_PASSWORD"]


class DeviceProperties(enum.Enum):
    temperature = "ep_9:sIT600TH:LocalTemperature_x100"
    running_state = "ep_9:sIT600TH:RunningState"


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
        ],
        ssl=False,
    ) as response:
        return (await response.json())["datapoints"]["devices"]["device"]


async def main():
    async with aiohttp.ClientSession(headers=BASE_HEADERS) as session:
        auth_token = await get_auth_token(EMAIL, PASSWORD, session)

        device_map, device_properties = await asyncio.gather(
            *[
                get_device_map(auth_token, session),
                get_device_properties(auth_token, session),
            ]
        )

    for device in device_properties:
        name = device_map[device["id"]]
        temperature = device["properties"]["property"][0]["value"]
        running_state = device["properties"]["property"][1]["value"]
        state = "heating" if running_state else "idle"

        print(f"{name}: {temperature/100} {state}")


if __name__ == "__main__":
    asyncio.run(main())
